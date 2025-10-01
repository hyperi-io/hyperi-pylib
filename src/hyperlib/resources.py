"""
HyperLib Container Resource Management
Abstract resource handling for config, data, tmp, and cache with thread safety
"""

import os
import threading
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

try:
    from filelock import FileLock

    FILELOCK_AVAILABLE = True
except ImportError:
    FILELOCK_AVAILABLE = False

from .logger import logger


class ContainerResource:
    """
    Abstract container resource management with thread safety and auto-cleanup

    Handles:
    - READ-ONLY: /container/app/config/* (never writes)
    - PERSISTENT: /container/app/data/* (thread-safe concurrent access)
    - EPHEMERAL: /container/app/tmp/* (unique workspaces, auto-cleanup)
    - CACHE: /container/app/data/*/cache/* (retention management)
    """

    def __init__(self, resource_type: str):
        """
        Initialize container resource manager

        Args:
            resource_type: 'config', 'data', 'tmp', 'cache'
        """
        self.resource_type = resource_type
        self.base_path = self._resolve_container_path(resource_type)
        self._lock = threading.RLock()  # Re-entrant lock for nested calls
        self._cleanup_registry = []  # Track resources for cleanup
        self._thread_local = threading.local()  # Thread-local storage

        logger.debug(f"🏗️ ContainerResource initialized: {resource_type} → {self.base_path}")

    def _resolve_container_path(self, resource_type: str) -> Path:
        """Resolve container path for resource type"""

        # Detect container root (same logic as config)
        current_file = Path(__file__)
        if "/src/hyperlib/" in str(current_file):
            # Development: use container simulation
            project_root = current_file.parent.parent.parent
            container_root = project_root / "container"
        else:
            # Production: use actual container paths
            container_root = Path("/")

        # Map resource types to container paths
        path_mapping = {
            "config": container_root / "app" / "config" / "dfe_ai",
            "external": container_root / "app" / "config" / "external",
            "data": container_root / "app" / "data" / "dfe_ai",
            "tmp": container_root / "app" / "tmp" / "dfe_ai",
            "cache": container_root / "app" / "data" / "dfe_ai" / "cache",
            "logs": container_root / "var" / "log" / "dfe_ai",
        }

        if resource_type not in path_mapping:
            raise ValueError(f"Unknown resource type: {resource_type}")

        return path_mapping[resource_type]

    @contextmanager
    def get_unique_workspace(self, prefix: str = "workspace") -> Generator[Path, None, None]:
        """
        Get unique workspace with automatic cleanup

        Returns unique directory: /container/app/tmp/dfe_ai/working/{prefix}_{PID}_{TID}_{UUID}/
        Automatically cleaned up on exit
        """

        # Create unique workspace identifier
        pid = os.getpid()
        tid = threading.get_ident()
        unique_id = str(uuid.uuid4())[:8]

        workspace_name = f"{prefix}_{pid}_{tid}_{unique_id}"
        workspace_path = self.base_path / "working" / workspace_name

        try:
            # Create workspace with proper permissions
            workspace_path.mkdir(parents=True, exist_ok=True)

            # Register for cleanup
            with self._lock:
                self._cleanup_registry.append(workspace_path)

            logger.debug(f"📁 Created unique workspace: {workspace_path}")

            yield workspace_path

        finally:
            # Automatic cleanup (C-style memory management)
            try:
                if workspace_path.exists():
                    import shutil

                    shutil.rmtree(workspace_path)
                    logger.debug(f"🧹 Cleaned up workspace: {workspace_path}")

                # Remove from cleanup registry
                with self._lock:
                    if workspace_path in self._cleanup_registry:
                        self._cleanup_registry.remove(workspace_path)

            except Exception as e:
                logger.warning(f"⚠️ Workspace cleanup failed: {workspace_path}: {e}")

    @contextmanager
    def concurrent_file_access(
        self, file_path: str, mode: str = "r", encoding: str = "utf-8", timeout: float = 30.0
    ) -> Generator:
        """
        Thread-safe file access with locking for concurrent operations

        Perfect for dfe_knowledge.yaml concurrent writes

        Args:
            file_path: Relative path from resource base
            mode: File open mode ('r', 'w', 'a')
            encoding: File encoding
            timeout: Lock timeout in seconds
        """

        full_path = self.base_path / file_path
        lock_path = full_path.with_suffix(f"{full_path.suffix}.lock")

        # Ensure parent directory exists for writes
        if "w" in mode or "a" in mode:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        # Use filelock for cross-process safety, threading.Lock for fallback
        if FILELOCK_AVAILABLE and ("w" in mode or "a" in mode):
            # Use file-based locking for writes (cross-process safe)
            file_lock = FileLock(str(lock_path), timeout=timeout)

            try:
                with file_lock:
                    logger.debug(f"🔒 Acquired file lock: {full_path}")
                    with open(full_path, mode, encoding=encoding) as f:
                        yield f
                    logger.debug(f"🔓 Released file lock: {full_path}")

            except Exception as e:
                logger.error(f"❌ Concurrent file access failed: {full_path}: {e}")
                raise

        else:
            # Use threading lock for reads or when filelock unavailable
            with self._lock:
                try:
                    with open(full_path, mode, encoding=encoding) as f:
                        yield f

                except Exception as e:
                    logger.error(f"❌ File access failed: {full_path}: {e}")
                    raise

    def cleanup_all(self):
        """Manual cleanup of all registered resources"""
        with self._lock:
            for resource_path in self._cleanup_registry[:]:  # Copy list to avoid modification during iteration
                try:
                    if resource_path.exists():
                        import shutil

                        shutil.rmtree(resource_path)
                        logger.debug(f"🧹 Manual cleanup: {resource_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Manual cleanup failed: {resource_path}: {e}")

            self._cleanup_registry.clear()

    def __del__(self):
        """Destructor cleanup (Python garbage collection)"""
        try:
            self.cleanup_all()
        except:
            pass  # Don't raise exceptions in destructor


# Factory functions for different resource types
def get_config_resource() -> ContainerResource:
    """Get READ-ONLY config resource manager"""
    return ContainerResource("config")


def get_data_resource() -> ContainerResource:
    """Get PERSISTENT data resource manager with thread safety"""
    return ContainerResource("data")


def get_tmp_resource() -> ContainerResource:
    """Get EPHEMERAL temp resource manager with auto-cleanup"""
    return ContainerResource("tmp")


def get_cache_resource() -> ContainerResource:
    """Get PERSISTENT cache resource manager with retention"""
    return ContainerResource("cache")
