# Ansible Vault Secrets Provider — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Ansible Vault secrets provider so Python services can read encrypted-at-rest secrets from Ansible Vault files without a dedicated secrets server.

**Architecture:** New `AnsibleVaultProvider` implementing the existing `SecretProvider` ABC. Thin wrapper around the `ansible-vault` PyPI package for decryption. Follows exact patterns from existing providers (FileProvider for file I/O, graceful imports in `__init__.py`, config parsing in manager). Password resolved from environment variables at init time.

**Tech Stack:** `ansible-vault>=4.0.0` (optional dependency), `pyyaml` (already a core dependency)

**Spec:** `docs/superpowers/specs/2026-04-10-ansible-vault-provider-design.md`

---

## File Structure

### New files

| File | Responsibility |
|---|---|
| `src/hyperi_pylib/secrets/providers/ansible_vault.py` | Provider implementation — decryption, password resolution, content auto-detection |
| `tests/unit/test_secrets_ansible_vault_provider.py` | Unit tests — happy path and expected failures |

### Modified files

| File | Change |
|---|---|
| `src/hyperi_pylib/secrets/types.py` | Add `AnsibleVaultConfig` dataclass, add `ANSIBLE_VAULT` to `ProviderType` enum, update `__all__` |
| `src/hyperi_pylib/secrets/providers/__init__.py` | Add graceful import for `AnsibleVaultProvider`, update `__all__` |
| `src/hyperi_pylib/secrets/manager.py` | Add `ansible_vault` block in `from_config()`, add `_parse_ansible_vault_config()`, update imports |
| `pyproject.toml` | Add `secrets-ansible-vault` optional extra, add `ansible-vault` to `dev` dependencies |

---

## Task 1: Add `AnsibleVaultConfig` and `ProviderType` Entry

**Files:**
- Modify: `src/hyperi_pylib/secrets/types.py`

- [ ] **Step 1: Add `ANSIBLE_VAULT` to `ProviderType` enum**

In `src/hyperi_pylib/secrets/types.py`, add the new enum member after `AZURE`:

```python
class ProviderType(Enum):
    """Secret provider types."""

    FILE = "file"
    OPENBAO = "openbao"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ANSIBLE_VAULT = "ansible_vault"
```

- [ ] **Step 2: Add `AnsibleVaultConfig` dataclass**

Add after the `AzureConfig` dataclass (before the `RotationCallback` type alias):

```python
@dataclass
class AnsibleVaultConfig:
    """Ansible Vault provider configuration.

    Designed primarily for SME networks that need encrypted-at-rest secrets
    without the operational overhead of a dedicated secrets server. Also suitable
    for dev/test environments, CI pipelines, or any setup where Ansible Vault is
    already the team's standard for secret management.
    """

    password: str | None = None
    """Resolved vault password (from env var or file)."""

    password_file: str | None = None
    """Path to file containing the vault password (fallback)."""
```

- [ ] **Step 3: Update `__all__`**

Add `"AnsibleVaultConfig"` to the `__all__` list:

```python
__all__ = [
    "ProviderType",
    "SecretValue",
    "RotationEvent",
    "CacheConfig",
    "SourceConfig",
    "OpenBaoConfig",
    "AWSConfig",
    "GCPConfig",
    "AzureConfig",
    "AnsibleVaultConfig",
    "RotationCallback",
]
```

- [ ] **Step 4: Verify lint passes**

Run: `ruff check src/hyperi_pylib/secrets/types.py`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add src/hyperi_pylib/secrets/types.py
git commit -m "feat(secrets): add AnsibleVaultConfig and ProviderType entry"
```

---

## Task 2: Implement `AnsibleVaultProvider`

**Files:**
- Create: `src/hyperi_pylib/secrets/providers/ansible_vault.py`

- [ ] **Step 1: Create the provider file with availability check and password resolution**

Create `src/hyperi_pylib/secrets/providers/ansible_vault.py`:

```python
"""Ansible Vault secret provider.

Designed primarily for SME networks that need encrypted-at-rest secrets without
the operational overhead of a dedicated secrets server (OpenBao, AWS Secrets
Manager, etc.). Also suitable for any environment where Ansible Vault is already
the team's standard for secret management — dev/test environments, CI pipelines,
or hybrid setups where some secrets live in vault files alongside
infrastructure-as-code.

When to use this provider:
- Small-to-medium deployments where running a secrets server is overkill
- Teams already using Ansible for configuration management
- Environments transitioning from plaintext config files to encrypted secrets
- Dev/test environments that need secrets but not full secrets infrastructure
- Air-gapped or restricted networks where SaaS secrets managers aren't available

When NOT to use this provider:
- High-availability requirements (use OpenBao or a cloud secrets manager)
- Dynamic secret generation / rotation (use OpenBao)
- Fine-grained access control per secret (use OpenBao or cloud provider)

Dependencies:
    pip install hyperi-pylib[secrets-ansible-vault]
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

import yaml

from ..exceptions import ProviderError, ProviderNotAvailableError, SecretNotFoundError
from ..types import AnsibleVaultConfig, SecretValue
from .base import SecretProvider

logger = logging.getLogger(__name__)

try:
    from ansible_vault import Vault

    ANSIBLE_VAULT_AVAILABLE = True
except ImportError:
    ANSIBLE_VAULT_AVAILABLE = False


def _resolve_password(config: AnsibleVaultConfig) -> str:
    """Resolve vault password from environment or config.

    Priority order:
    1. ANSIBLE_VAULT_PASSWORD env var
    2. ANSIBLE_VAULT_PASS env var (common shorthand)
    3. ANSIBLE_VAULT_PASSWORD_FILE env var -> read file
    4. config.password_file -> read file

    Args:
        config: Provider configuration.

    Returns:
        Resolved password string.

    Raises:
        ProviderError: No password source found, or password file unreadable.
    """
    # Direct password from config (already resolved by manager)
    if config.password:
        return config.password

    # Env var: ANSIBLE_VAULT_PASSWORD
    password = os.environ.get("ANSIBLE_VAULT_PASSWORD")
    if password:
        return password

    # Env var: ANSIBLE_VAULT_PASS (common shorthand)
    password = os.environ.get("ANSIBLE_VAULT_PASS")
    if password:
        return password

    # Env var: ANSIBLE_VAULT_PASSWORD_FILE -> read file
    password_file_env = os.environ.get("ANSIBLE_VAULT_PASSWORD_FILE")
    if password_file_env:
        return _read_password_file(password_file_env)

    # Config: password_file -> read file
    if config.password_file:
        return _read_password_file(config.password_file)

    raise ProviderError("ansible_vault", "no vault password configured — set ANSIBLE_VAULT_PASSWORD or provide password_file")


def _read_password_file(path: str) -> str:
    """Read vault password from a file.

    Args:
        path: Path to the password file.

    Returns:
        Password string (stripped of trailing whitespace).

    Raises:
        ProviderError: File missing, empty, or unreadable.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise ProviderError("ansible_vault", f"password file not found: {path}")

    try:
        password = file_path.read_text().strip()
    except OSError as e:
        raise ProviderError("ansible_vault", f"failed to read password file {path}: {e}")

    if not password:
        raise ProviderError("ansible_vault", f"password file is empty: {path}")

    return password


class AnsibleVaultProvider(SecretProvider):
    """Ansible Vault secret provider.

    Reads secrets from Ansible Vault-encrypted files on the local filesystem.
    Supports both single-value encrypted files and encrypted YAML files with
    key extraction.
    """

    def __init__(self, config: AnsibleVaultConfig) -> None:
        """Initialize Ansible Vault provider.

        Args:
            config: Provider configuration.

        Raises:
            ProviderNotAvailableError: ansible-vault package not installed.
            ProviderError: No vault password configured.
        """
        if not ANSIBLE_VAULT_AVAILABLE:
            raise ProviderNotAvailableError(
                "ansible_vault",
                "ansible-vault",
                "pip install hyperi-pylib[secrets-ansible-vault]",
            )
        self._config = config
        self._password = _resolve_password(config)

    @property
    def name(self) -> str:
        """Provider name."""
        return "ansible_vault"

    def _compute_version(self, path: Path) -> str:
        """Compute version from file mtime and size."""
        stat = path.stat()
        return f"{stat.st_mtime}:{stat.st_size}"

    def _decrypt(self, content: str) -> bytes:
        """Decrypt vault-encrypted content.

        Args:
            content: Raw vault-encrypted file content.

        Returns:
            Decrypted bytes.

        Raises:
            ProviderError: Decryption failed (wrong password or corrupted).
        """
        try:
            vault = Vault(self._password)
            decrypted = vault.load_raw(content)
            if isinstance(decrypted, str):
                return decrypted.encode("utf-8")
            return bytes(decrypted)
        except Exception as e:
            raise ProviderError("ansible_vault", f"decryption failed: {e}")

    def _extract(self, decrypted: bytes, key: str | None) -> bytes:
        """Extract value from decrypted content.

        If key is provided, parses decrypted content as YAML and extracts
        the specified key. If no key, returns raw decrypted bytes.

        Auto-detection logic:
        - Try yaml.safe_load() on decrypted content
        - If valid YAML dict and key provided: extract field
        - If valid YAML dict and no key: return full YAML as bytes
        - If not a YAML dict: return raw decrypted bytes

        Args:
            decrypted: Decrypted bytes.
            key: Optional key to extract from YAML content.

        Returns:
            Extracted bytes.

        Raises:
            ProviderError: Key requested but content is not a YAML dict.
            SecretNotFoundError: Key not found in YAML dict.
        """
        if key is None:
            return decrypted

        # Key requested — must be a YAML dict
        try:
            parsed = yaml.safe_load(decrypted.decode("utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError):
            raise ProviderError("ansible_vault", f"key '{key}' requested but content is not valid YAML")

        if not isinstance(parsed, dict):
            raise ProviderError("ansible_vault", f"key '{key}' requested but content is not a YAML mapping")

        if key not in parsed:
            raise SecretNotFoundError(key, "ansible_vault")

        value = parsed[key]
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode("utf-8")
        # For nested structures, serialize back to YAML
        return yaml.dump(value, default_flow_style=False).encode("utf-8")

    async def get_async(self, path: str, key: str | None = None) -> SecretValue:
        """Async get (delegates to sync since file I/O is fast)."""
        return self.get_sync(path, key)

    def get_sync(self, path: str, key: str | None = None) -> SecretValue:
        """Read and decrypt secret from an Ansible Vault-encrypted file.

        Args:
            path: Path to the vault-encrypted file.
            key: Optional key to extract from decrypted YAML content.

        Returns:
            SecretValue with decrypted data and metadata.

        Raises:
            SecretNotFoundError: File does not exist, or key not in YAML.
            ProviderError: Decryption or read failed.
        """
        file_path = Path(path)

        if not file_path.exists():
            raise SecretNotFoundError(path, self.name)

        try:
            content = file_path.read_text()
        except OSError as e:
            raise ProviderError(self.name, f"failed to read {path}: {e}")

        decrypted = self._decrypt(content)
        data = self._extract(decrypted, key)

        return SecretValue(
            data=data,
            fetched_at=datetime.now(UTC),
            version=self._compute_version(file_path),
            source=self.name,
        )

    async def health_check_async(self) -> bool:
        """Check if provider is healthy."""
        return self.health_check_sync()

    def health_check_sync(self) -> bool:
        """Check if provider is healthy.

        Verifies password is available and ansible-vault is importable.
        """
        return ANSIBLE_VAULT_AVAILABLE and self._password is not None


__all__ = ["ANSIBLE_VAULT_AVAILABLE", "AnsibleVaultProvider"]
```

- [ ] **Step 2: Verify lint passes**

Run: `ruff check src/hyperi_pylib/secrets/providers/ansible_vault.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add src/hyperi_pylib/secrets/providers/ansible_vault.py
git commit -m "feat(secrets): implement AnsibleVaultProvider"
```

---

## Task 3: Register Provider in `__init__.py`

**Files:**
- Modify: `src/hyperi_pylib/secrets/providers/__init__.py`

- [ ] **Step 1: Add graceful import**

Add after the Azure import block (before `__all__`):

```python
try:
    from .ansible_vault import ANSIBLE_VAULT_AVAILABLE, AnsibleVaultProvider
except ImportError:
    AnsibleVaultProvider = None  # type: ignore[assignment,misc]
    ANSIBLE_VAULT_AVAILABLE = False
```

- [ ] **Step 2: Update `__all__`**

Add `"AnsibleVaultProvider"` and `"ANSIBLE_VAULT_AVAILABLE"` to the `__all__` list:

```python
__all__ = [
    "SecretProvider",
    "FileProvider",
    "OpenBaoProvider",
    "AWSProvider",
    "GCPProvider",
    "AzureProvider",
    "AnsibleVaultProvider",
    "HTTPX_AVAILABLE",
    "BOTO3_AVAILABLE",
    "AIOBOTOCORE_AVAILABLE",
    "GCP_AVAILABLE",
    "AZURE_AVAILABLE",
    "AZURE_ASYNC_AVAILABLE",
    "ANSIBLE_VAULT_AVAILABLE",
]
```

- [ ] **Step 3: Verify lint passes**

Run: `ruff check src/hyperi_pylib/secrets/providers/__init__.py`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add src/hyperi_pylib/secrets/providers/__init__.py
git commit -m "feat(secrets): register AnsibleVaultProvider in providers init"
```

---

## Task 4: Add Manager Config Parsing

**Files:**
- Modify: `src/hyperi_pylib/secrets/manager.py`

- [ ] **Step 1: Add `AnsibleVaultConfig` to imports**

In `src/hyperi_pylib/secrets/manager.py`, add `AnsibleVaultConfig` to the imports from `.types`:

```python
from .types import (
    AWSConfig,
    AnsibleVaultConfig,
    AzureConfig,
    CacheConfig,
    GCPConfig,
    OpenBaoConfig,
    ProviderType,
    RotationCallback,
    RotationEvent,
    SecretValue,
    SourceConfig,
)
```

- [ ] **Step 2: Add `ansible_vault` block to `from_config()`**

Add after the Azure provider block (before the `# Parse sources` comment, around line 159):

```python
        # Ansible Vault provider
        if "ansible_vault" in config:
            try:
                from .providers.ansible_vault import AnsibleVaultProvider

                av_config = cls._parse_ansible_vault_config(config["ansible_vault"])
                providers["ansible_vault"] = AnsibleVaultProvider(av_config)
            except ImportError:
                logger.warning(
                    "Ansible Vault provider not available. Install with: pip install hyperi-pylib[secrets-ansible-vault]"
                )
```

- [ ] **Step 3: Add `_parse_ansible_vault_config()` static method**

Add after `_parse_azure_config()` (around line 244):

```python
    @staticmethod
    def _parse_ansible_vault_config(cfg: dict) -> AnsibleVaultConfig:
        """Parse Ansible Vault config with env var fallbacks."""
        return AnsibleVaultConfig(
            password=cfg.get("password") or os.environ.get("ANSIBLE_VAULT_PASSWORD") or os.environ.get("ANSIBLE_VAULT_PASS"),
            password_file=cfg.get("password_file"),
        )
```

- [ ] **Step 4: Verify lint passes**

Run: `ruff check src/hyperi_pylib/secrets/manager.py`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add src/hyperi_pylib/secrets/manager.py
git commit -m "feat(secrets): add Ansible Vault config parsing to SecretsManager"
```

---

## Task 5: Add Optional Dependency Extra

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add `secrets-ansible-vault` optional extra**

Add after the `secrets-vault` line (around line 95) in `[project.optional-dependencies]`:

```toml
secrets-ansible-vault = [
    "ansible-vault>=4.0.0",
]
```

- [ ] **Step 2: Add `ansible-vault` to `secrets` meta-extra**

Add `"ansible-vault>=4.0.0",` to the `secrets` combined extra:

```toml
secrets = [
    "ansible-vault>=4.0.0",
    "boto3>=1.35.0",
    "aiobotocore>=2.15.0",
    "google-cloud-secret-manager>=2.26.0",
    "azure-keyvault-secrets>=4.9.0",
    "azure-identity>=1.25.1",
]
```

- [ ] **Step 3: Add `ansible-vault` to `dev` dependencies**

Add `"ansible-vault>=4.0.0",` to the `dev` optional extra:

```toml
dev = [
    "ansible-vault>=4.0.0",
    "setuptools>=70.0.0",
    ...
]
```

- [ ] **Step 4: Install the new dependency**

Run: `uv pip install -e ".[dev,secrets-ansible-vault]"`
Expected: `ansible-vault` installed successfully

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "feat(secrets): add secrets-ansible-vault optional dependency"
```

---

## Task 6: Unit Tests — Happy Path

**Files:**
- Create: `tests/unit/test_secrets_ansible_vault_provider.py`

- [ ] **Step 1: Write happy path tests**

Create `tests/unit/test_secrets_ansible_vault_provider.py`:

```python
"""Unit tests for Ansible Vault secret provider."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from hyperi_pylib.secrets.exceptions import ProviderError, SecretNotFoundError
from hyperi_pylib.secrets.providers.ansible_vault import (
    ANSIBLE_VAULT_AVAILABLE,
    AnsibleVaultProvider,
    _read_password_file,
    _resolve_password,
)
from hyperi_pylib.secrets.types import AnsibleVaultConfig

# Skip entire module if ansible-vault not installed
pytestmark = pytest.mark.skipif(not ANSIBLE_VAULT_AVAILABLE, reason="ansible-vault not installed")

TEST_PASSWORD = "test-vault-password-42"


def _create_vault_file(tmp_path: Path, content: str | dict, filename: str = "secret.vault") -> Path:
    """Create an Ansible Vault-encrypted file for testing.

    Args:
        tmp_path: Pytest tmp_path fixture.
        content: String or dict to encrypt. Dicts are YAML-serialized first.
        filename: Output filename.

    Returns:
        Path to the encrypted file.
    """
    from ansible_vault import Vault

    vault = Vault(TEST_PASSWORD)
    if isinstance(content, dict):
        raw = yaml.dump(content, default_flow_style=False)
    else:
        raw = content
    encrypted = vault.dump_raw(raw)
    vault_file = tmp_path / filename
    if isinstance(encrypted, bytes):
        vault_file.write_bytes(encrypted)
    else:
        vault_file.write_text(encrypted)
    return vault_file


def _make_provider(password: str = TEST_PASSWORD) -> AnsibleVaultProvider:
    """Create a provider with a direct password."""
    return AnsibleVaultProvider(AnsibleVaultConfig(password=password))


class TestAnsibleVaultProviderHappyPath:
    """Happy path tests for AnsibleVaultProvider."""

    def test_provider_name(self):
        """Provider name is 'ansible_vault'."""
        provider = _make_provider()
        assert provider.name == "ansible_vault"

    def test_decrypt_single_value_file(self, tmp_path):
        """Decrypt a single-value vault file and return raw bytes."""
        vault_file = _create_vault_file(tmp_path, "my-secret-value")

        provider = _make_provider()
        result = provider.get_sync(str(vault_file))

        assert result.decode() == "my-secret-value"
        assert result.source == "ansible_vault"

    def test_decrypt_yaml_file_extract_key(self, tmp_path):
        """Decrypt YAML vault file and extract a specific key."""
        vault_file = _create_vault_file(tmp_path, {"db_password": "hunter2", "api_key": "secret123"})

        provider = _make_provider()
        result = provider.get_sync(str(vault_file), key="db_password")

        assert result.decode() == "hunter2"

    def test_decrypt_yaml_file_no_key(self, tmp_path):
        """Decrypt YAML vault file without key returns raw decrypted bytes."""
        data = {"db_password": "hunter2", "api_key": "secret123"}
        vault_file = _create_vault_file(tmp_path, data)

        provider = _make_provider()
        result = provider.get_sync(str(vault_file))

        # Should be the raw YAML content (no key extraction)
        parsed = yaml.safe_load(result.data)
        assert parsed["db_password"] == "hunter2"
        assert parsed["api_key"] == "secret123"

    def test_decrypt_yaml_nested_value(self, tmp_path):
        """Extracting a nested YAML value returns YAML-serialized bytes."""
        data = {"database": {"host": "localhost", "port": 5432}}
        vault_file = _create_vault_file(tmp_path, data)

        provider = _make_provider()
        result = provider.get_sync(str(vault_file), key="database")

        parsed = yaml.safe_load(result.data)
        assert parsed["host"] == "localhost"
        assert parsed["port"] == 5432

    def test_password_from_env_var(self, tmp_path):
        """Password resolved from ANSIBLE_VAULT_PASSWORD env var."""
        vault_file = _create_vault_file(tmp_path, "env-secret")

        with patch.dict(os.environ, {"ANSIBLE_VAULT_PASSWORD": TEST_PASSWORD}, clear=False):
            provider = AnsibleVaultProvider(AnsibleVaultConfig())
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "env-secret"

    def test_password_from_fallback_env_var(self, tmp_path):
        """Password resolved from ANSIBLE_VAULT_PASS env var."""
        vault_file = _create_vault_file(tmp_path, "fallback-secret")

        env = {"ANSIBLE_VAULT_PASS": TEST_PASSWORD}
        with patch.dict(os.environ, env, clear=False):
            # Ensure ANSIBLE_VAULT_PASSWORD is not set
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            provider = AnsibleVaultProvider(AnsibleVaultConfig())
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "fallback-secret"

    def test_password_from_env_password_file(self, tmp_path):
        """Password file path from ANSIBLE_VAULT_PASSWORD_FILE env var."""
        vault_file = _create_vault_file(tmp_path, "file-env-secret")

        pass_file = tmp_path / "vault_pass"
        pass_file.write_text(TEST_PASSWORD)

        env = {"ANSIBLE_VAULT_PASSWORD_FILE": str(pass_file)}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            provider = AnsibleVaultProvider(AnsibleVaultConfig())
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "file-env-secret"

    def test_password_from_config_file(self, tmp_path):
        """Password from password_file config."""
        vault_file = _create_vault_file(tmp_path, "config-file-secret")

        pass_file = tmp_path / "vault_pass"
        pass_file.write_text(TEST_PASSWORD)

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)
            provider = AnsibleVaultProvider(AnsibleVaultConfig(password_file=str(pass_file)))
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "config-file-secret"

    def test_password_priority_order(self, tmp_path):
        """Env var takes precedence over password file."""
        # Encrypt with TEST_PASSWORD
        vault_file = _create_vault_file(tmp_path, "priority-secret")

        pass_file = tmp_path / "vault_pass"
        pass_file.write_text("wrong-password")

        # ANSIBLE_VAULT_PASSWORD should win over password_file
        with patch.dict(os.environ, {"ANSIBLE_VAULT_PASSWORD": TEST_PASSWORD}, clear=False):
            provider = AnsibleVaultProvider(AnsibleVaultConfig(password_file=str(pass_file)))
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "priority-secret"

    def test_health_check_passes(self):
        """Health check returns True when password is configured."""
        provider = _make_provider()
        assert provider.health_check_sync() is True

    def test_version_tracking(self, tmp_path):
        """Version string is in mtime:size format."""
        vault_file = _create_vault_file(tmp_path, "version-test")

        provider = _make_provider()
        result = provider.get_sync(str(vault_file))

        assert result.version is not None
        parts = result.version.split(":")
        assert len(parts) == 2
        float(parts[0])  # mtime is a float
        int(parts[1])    # size is an int

    @pytest.mark.asyncio
    async def test_async_delegates_to_sync(self, tmp_path):
        """Async get returns same result as sync get."""
        vault_file = _create_vault_file(tmp_path, "async-test")

        provider = _make_provider()
        sync_result = provider.get_sync(str(vault_file))
        async_result = await provider.get_async(str(vault_file))

        assert sync_result.data == async_result.data
        assert sync_result.source == async_result.source

    @pytest.mark.asyncio
    async def test_health_check_async(self):
        """Async health check delegates to sync."""
        provider = _make_provider()
        assert await provider.health_check_async() is True

    def test_password_file_strips_whitespace(self, tmp_path):
        """Password file content is stripped of trailing whitespace."""
        vault_file = _create_vault_file(tmp_path, "strip-test")

        pass_file = tmp_path / "vault_pass"
        pass_file.write_text(f"{TEST_PASSWORD}\n\n")

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)
            provider = AnsibleVaultProvider(AnsibleVaultConfig(password_file=str(pass_file)))
            result = provider.get_sync(str(vault_file))

        assert result.decode() == "strip-test"
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/unit/test_secrets_ansible_vault_provider.py::TestAnsibleVaultProviderHappyPath -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_secrets_ansible_vault_provider.py
git commit -m "test(secrets): add Ansible Vault provider happy path tests"
```

---

## Task 7: Unit Tests — Expected Failures

**Files:**
- Modify: `tests/unit/test_secrets_ansible_vault_provider.py`

- [ ] **Step 1: Add expected failure tests**

Append to `tests/unit/test_secrets_ansible_vault_provider.py`:

```python
class TestAnsibleVaultProviderFailures:
    """Expected failure tests for AnsibleVaultProvider."""

    def test_no_password_source_raises(self):
        """No password configured raises ProviderError at init."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)

            with pytest.raises(ProviderError) as exc_info:
                AnsibleVaultProvider(AnsibleVaultConfig())

            assert "no vault password configured" in str(exc_info.value)

    def test_file_not_found_raises(self, tmp_path):
        """Vault file missing raises SecretNotFoundError."""
        provider = _make_provider()

        with pytest.raises(SecretNotFoundError) as exc_info:
            provider.get_sync(str(tmp_path / "nonexistent.vault"))

        assert "nonexistent.vault" in str(exc_info.value)
        assert exc_info.value.provider == "ansible_vault"

    def test_wrong_password_raises(self, tmp_path):
        """Wrong password raises ProviderError."""
        vault_file = _create_vault_file(tmp_path, "secret-data")

        provider = _make_provider(password="wrong-password")

        with pytest.raises(ProviderError) as exc_info:
            provider.get_sync(str(vault_file))

        assert "decryption failed" in str(exc_info.value)

    def test_key_from_non_yaml_raises(self, tmp_path):
        """Key requested but content is not YAML raises ProviderError."""
        # Encrypt raw binary-like content that won't parse as YAML dict
        vault_file = _create_vault_file(tmp_path, "just-a-plain-string")

        provider = _make_provider()

        with pytest.raises(ProviderError) as exc_info:
            provider.get_sync(str(vault_file), key="some_key")

        assert "not a YAML mapping" in str(exc_info.value)

    def test_missing_key_in_yaml_raises(self, tmp_path):
        """Key not found in YAML raises SecretNotFoundError."""
        vault_file = _create_vault_file(tmp_path, {"existing_key": "value"})

        provider = _make_provider()

        with pytest.raises(SecretNotFoundError) as exc_info:
            provider.get_sync(str(vault_file), key="nonexistent_key")

        assert "nonexistent_key" in str(exc_info.value)

    def test_password_file_missing_raises(self, tmp_path):
        """Password file doesn't exist raises ProviderError at init."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)

            with pytest.raises(ProviderError) as exc_info:
                AnsibleVaultProvider(AnsibleVaultConfig(password_file="/nonexistent/path"))

            assert "password file not found" in str(exc_info.value)

    def test_password_file_empty_raises(self, tmp_path):
        """Password file is empty raises ProviderError at init."""
        pass_file = tmp_path / "empty_pass"
        pass_file.write_text("")

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANSIBLE_VAULT_PASSWORD", None)
            os.environ.pop("ANSIBLE_VAULT_PASS", None)
            os.environ.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)

            with pytest.raises(ProviderError) as exc_info:
                AnsibleVaultProvider(AnsibleVaultConfig(password_file=str(pass_file)))

            assert "password file is empty" in str(exc_info.value)

    def test_corrupted_vault_file_raises(self, tmp_path):
        """Corrupted vault file content raises ProviderError."""
        vault_file = tmp_path / "corrupted.vault"
        vault_file.write_text("$ANSIBLE_VAULT;1.1;AES256\ncorrupted-garbage-data")

        provider = _make_provider()

        with pytest.raises(ProviderError) as exc_info:
            provider.get_sync(str(vault_file))

        assert "decryption failed" in str(exc_info.value)

    def test_permission_denied_raises(self, tmp_path):
        """Unreadable vault file raises ProviderError."""
        vault_file = _create_vault_file(tmp_path, "secret")
        vault_file.chmod(0o000)

        provider = _make_provider()

        try:
            with pytest.raises((ProviderError, SecretNotFoundError)):
                provider.get_sync(str(vault_file))
        finally:
            # Restore permissions so tmp_path cleanup works
            vault_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_file_not_found_async_raises(self, tmp_path):
        """Async version also raises SecretNotFoundError for missing files."""
        provider = _make_provider()

        with pytest.raises(SecretNotFoundError):
            await provider.get_async(str(tmp_path / "missing.vault"))


class TestResolvePassword:
    """Tests for _resolve_password helper."""

    def test_config_password_takes_priority(self):
        """Direct password in config is used first."""
        config = AnsibleVaultConfig(password="direct-pass")
        with patch.dict(os.environ, {"ANSIBLE_VAULT_PASSWORD": "env-pass"}, clear=False):
            assert _resolve_password(config) == "direct-pass"

    def test_env_over_file(self, tmp_path):
        """ANSIBLE_VAULT_PASSWORD env var beats password file."""
        pass_file = tmp_path / "vault_pass"
        pass_file.write_text("file-pass")

        config = AnsibleVaultConfig(password_file=str(pass_file))
        with patch.dict(os.environ, {"ANSIBLE_VAULT_PASSWORD": "env-pass"}, clear=False):
            assert _resolve_password(config) == "env-pass"


class TestReadPasswordFile:
    """Tests for _read_password_file helper."""

    def test_reads_and_strips_trailing(self, tmp_path):
        """Reads file and strips trailing whitespace only."""
        f = tmp_path / "pass"
        f.write_text("my-password  \n")
        assert _read_password_file(str(f)) == "my-password"

    def test_missing_file(self):
        """Missing file raises ProviderError."""
        with pytest.raises(ProviderError, match="password file not found"):
            _read_password_file("/nonexistent/file")

    def test_empty_file(self, tmp_path):
        """Empty file raises ProviderError."""
        f = tmp_path / "empty"
        f.write_text("")
        with pytest.raises(ProviderError, match="password file is empty"):
            _read_password_file(str(f))
```

- [ ] **Step 2: Run all tests to verify they pass**

Run: `pytest tests/unit/test_secrets_ansible_vault_provider.py -v`
Expected: All tests PASS (happy path + expected failures)

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_secrets_ansible_vault_provider.py
git commit -m "test(secrets): add Ansible Vault provider failure and helper tests"
```

---

## Task 8: Run Full Quality Suite and Fix Issues

**Files:**
- All modified files from previous tasks

- [ ] **Step 1: Run full test suite**

Run: `make test`
Expected: All tests pass, no regressions

- [ ] **Step 2: Run quality checks**

Run: `make quality`
Expected: Lint, type-check, and security audit all pass

- [ ] **Step 3: Fix any issues found**

If any lint or test failures, fix them and re-run.

- [ ] **Step 4: Final commit if fixes were needed**

```bash
git add -u
git commit -m "fix(secrets): address lint/quality issues in Ansible Vault provider"
```
