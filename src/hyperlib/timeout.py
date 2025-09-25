"""
HyperLib Smart Timeout System - Generic Intelligent Process Monitoring
Replaces simple timeouts with intelligent activity detection for any long-running process
"""

import time
import threading
import subprocess
import os
import signal
import io
import sys
from typing import Any, Callable
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum
import functools
import contextlib

class TimeoutReason(Enum):
    """Reasons for timeout termination"""
    NO_ACTIVITY = "no_activity"
    TOTAL_EXECUTION = "total_execution" 
    MANUAL_STOP = "manual_stop"
    COMPLETED = "completed"

@dataclass
class ActivityIndicator:
    """Defines what constitutes activity for monitoring"""
    log_patterns: list[str] = None  # Regex patterns in logs to detect activity
    file_monitors: list[str] = None  # File paths to monitor for changes
    output_monitors: list[str] = None  # Output patterns to monitor
    
    def __post_init__(self):
        if self.log_patterns is None:
            self.log_patterns = []
        if self.file_monitors is None:
            self.file_monitors = []
        if self.output_monitors is None:
            self.output_monitors = []

@dataclass
class TimeoutResult:
    """Result of smart timeout execution"""
    success: bool
    timeout_reason: TimeoutReason
    total_duration: float
    last_activity_time: float
    activity_count: int
    final_output: str
    return_code: int | None = None
    error_message: str | None = None

class SmartTimeoutMonitor:
    """
    Smart timeout system with dual-level monitoring:
    1. Activity timeout - detects hangs early
    2. Total execution timeout - generous backup timeout
    """
    
    def __init__(self, 
                 activity_timeout: int = 120,  # 2 minutes no activity = hang
                 total_timeout: int = 1800,    # 30 minutes total = generous backup
                 activity_check_interval: int = 5):  # Check every 5 seconds
        
        self.activity_timeout = activity_timeout
        self.total_timeout = total_timeout  
        self.activity_check_interval = activity_check_interval
        
        # Monitoring state
        self.start_time = None
        self.last_activity_time = None
        self.activity_count = 0
        self.monitoring = False
        self.process = None
        self.output_buffer = []
        
        # File monitoring
        self.file_timestamps = {}
        
    def run_with_smart_timeout(self, 
                              command: list[str],
                              activity_indicators: ActivityIndicator,
                              working_dir: str | None = None,
                              env: dict | None = None) -> TimeoutResult:
        """
        Run command with smart timeout monitoring
        
        Args:
            command: Command to execute
            activity_indicators: What constitutes activity
            working_dir: Working directory for command
            env: Environment variables
            
        Returns:
            TimeoutResult with execution details
        """
        
        self.start_time = time.time()
        self.last_activity_time = self.start_time
        self.activity_count = 0
        self.monitoring = True
        self.output_buffer = []
        
        # Initialize file monitoring
        self._initialize_file_monitoring(activity_indicators.file_monitors)
        
        try:
            # Start process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=working_dir,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_activity,
                args=(activity_indicators,),
                daemon=True
            )
            monitor_thread.start()
            
            # Read output in real-time
            timeout_reason = self._read_output_with_monitoring(activity_indicators)
            
            # Wait for process completion or timeout
            if timeout_reason == TimeoutReason.COMPLETED:
                return_code = self.process.wait()
            else:
                # Terminate process due to timeout
                self._terminate_process()
                return_code = -1
                
            total_duration = time.time() - self.start_time
            
            return TimeoutResult(
                success=(timeout_reason == TimeoutReason.COMPLETED and return_code == 0),
                timeout_reason=timeout_reason,
                total_duration=total_duration,
                last_activity_time=time.time() - self.last_activity_time,
                activity_count=self.activity_count,
                final_output='\n'.join(self.output_buffer),
                return_code=return_code
            )
            
        except Exception as e:
            return TimeoutResult(
                success=False,
                timeout_reason=TimeoutReason.MANUAL_STOP,
                total_duration=time.time() - self.start_time if self.start_time else 0,
                last_activity_time=0,
                activity_count=self.activity_count,
                final_output='\n'.join(self.output_buffer),
                error_message=str(e)
            )
        finally:
            self.monitoring = False
            
    def _initialize_file_monitoring(self, file_paths: list[str]):
        """Initialize file modification time tracking"""
        self.file_timestamps = {}
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                self.file_timestamps[str(path)] = path.stat().st_mtime
                
    def _monitor_activity(self, activity_indicators: ActivityIndicator):
        """Monitor for activity indicators in separate thread"""
        
        while self.monitoring and self.process and self.process.poll() is None:
            current_time = time.time()
            
            # Check file modifications
            if self._check_file_activity(activity_indicators.file_monitors):
                self._register_activity("file_modification")
                
            # Check total timeout
            if current_time - self.start_time > self.total_timeout:
                logger.warning(f"⏰ Total execution timeout ({self.total_timeout}s) reached")
        
    def _terminate_process(self):
        """Terminate the monitored process"""
        if self.process:
            try:
                # Graceful termination first
                self.process.terminate()
                
                # Wait briefly for graceful exit
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    self.process.kill()
                    self.process.wait()
                    
            except Exception as e:
                logger.error(f"Error terminating process: {e}")

def smart_run(command: list[str],
                                         description: str,
                                         activity_timeout: int = 60,   # 1 minute no activity
                                         total_timeout: int = 300,     # 5 minutes total
                                         failure_patterns: list[str] = None,
                                         success_patterns: list[str] = None,
                                         progress_patterns: list[str] = None) -> TimeoutResult:
    """
    Generic smart timeout for any command with stdout/stderr monitoring
    
    Args:
        command: Command to run (e.g., ['python', 'script.py'])
        description: Description for logging
        activity_timeout: Seconds without activity before timeout
        total_timeout: Total execution time limit
        failure_patterns: Patterns that indicate immediate failure
        success_patterns: Patterns that indicate success
        progress_patterns: Patterns that indicate progress
        
    Returns:
        TimeoutResult with execution details
    """
    
    # Default patterns if not provided
    if failure_patterns is None:
        failure_patterns = [
            r"Error:",
            r"Exception:",
            r"❌",
            r"FAILED",
            r"Traceback",
            r"VIOLATION",
            r"No models returned",
            r"Empty response"
        ]
    
    if success_patterns is None:
        success_patterns = [
            r"SUCCESS",
            r"WORKING",
            r"models ranked",
            r"completed successfully"
        ]
    
    if progress_patterns is None:
        progress_patterns = [
            r"Testing",
            r"Executing",
            r"Response:",
            r"Found:",
            r"models returned",
            r"INFO",
            r"PROGRESS"
        ]
    
    activity_indicators = ActivityIndicator(
        output_monitors=failure_patterns + success_patterns + progress_patterns
    )
    
    timeout_manager = SmartTimeoutMonitor(
        activity_timeout=activity_timeout,
        total_timeout=total_timeout
    )
    
    return timeout_manager.run_with_smart_timeout(
        command=command,
        activity_indicators=activity_indicators,
        working_directory=os.getcwd()
    )

# Removed LLM-specific function - use generic smart_run() instead

# Convenience functions for common test patterns using generic smart_run
def run_baseline_test() -> TimeoutResult:
    """Run Stage 1 baseline test with appropriate timeouts"""
    return smart_run(
        command=["uv", "run", "python", "-m", "pytest", "tests/test_baseline_generation.py", "-v", "-s"],
        description="Stage 1 Baseline VRL Generation",
        activity_timeout=60,   # 1 minute no activity
        total_timeout=300,     # 5 minutes total
        success_patterns=[r"✅", r"PASSED", r"models ranked", r"SUCCESS"],
        failure_patterns=[r"❌", r"FAILED", r"ERROR", r"Exception", r"No models"]
    )

def run_incremental_test() -> TimeoutResult:
    """Run Stage 2 incremental test with appropriate timeouts"""
    return run_llm_test_with_smart_timeout(
        test_command=["uv", "run", "python", "-m", "pytest", "tests/test_llm_2_incremental.py", "-v", "-s"],
        test_name="Stage 2 Incremental Improvement",
        activity_timeout=180,  # 3 minutes no activity (iterations take time)
        total_timeout=1800,    # 30 minutes total (up to 5 iterations)
        result_files=["tests/incremental_results.json", "tests/baseline_results.json"]
    )

def run_research_test() -> TimeoutResult:
    """Run Stage 3 research test with appropriate timeouts"""  
    return run_llm_test_with_smart_timeout(
        test_command=["uv", "run", "python", "-m", "pytest", "tests/test_llm_3_research.py", "-v", "-s"],
        test_name="Stage 3 Research-Enhanced Discovery",
        activity_timeout=240,  # 4 minutes no activity (research takes time)
        total_timeout=2400,    # 40 minutes total (research + iterations)
        result_files=["tests/research_results.json", "tests/incremental_results.json"]
    )

def run_tree_based_test() -> TimeoutResult:
    """Run tree-based multi-candidate exploration test with appropriate timeouts"""
    return run_llm_test_with_smart_timeout(
        test_command=["uv", "run", "python", "-c", """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from dfe_ai_parser_vrl.core.tree_optimization import TreeBasedVRLImprover
import json

# Load baseline VRL
with open('tests/baseline_results.json', 'r') as f:
    baseline = json.load(f)

# Load test logs
import random
from . import logger
logs = []
for i in range(100):
    logs.append({
        'message': f'SSH test log {i}',
        'hostname': f'test-server-{i:02d}'
    })

# Run tree-based improvement
improver = TreeBasedVRLImprover()
result = improver.improve_with_tree_exploration(
    baseline['vrl_code'], logs, 'ssh', 15.0
)

logger.info(f'Tree exploration result: {result[\"success\"]}')
logger.info(f'Final score: {result.get(\"final_score\", 0.0):.3f}')
logger.info(f'Candidates explored: {result.get(\"tree_summary\", {}).get(\"total_candidates\", 0)}')
"""],
        test_name="Tree-Based Multi-Candidate Exploration",
        activity_timeout=300,  # 5 minutes no activity (multiple branches take time)
        total_timeout=3600,    # 60 minutes total (20 iterations across branches)
        result_files=["tests/baseline_results.json"]
    )

class FunctionTimeoutMonitor:
    """
    Smart timeout system for Python functions with progress monitoring
    """
    
    def __init__(self, 
                 activity_timeout: int = 120,
                 total_timeout: int = 600,
                 progress_check_interval: int = 5):
        
        self.activity_timeout = activity_timeout
        self.total_timeout = total_timeout
        self.progress_check_interval = progress_check_interval
        
        # Monitoring state
        self.start_time = None
        self.last_activity_time = None
        self.activity_count = 0
        self.monitoring = False
        self.function_thread = None
        self.result = None
        self.exception = None
        self.output_buffer = []
        
        # Progress callback state
        self.progress_callback_called = False
        
    def run_function_with_timeout(self,
                                func: Callable,
                                args: tuple = (),
                                kwargs: dict = None,
                                description: str = "",
                                capture_output: bool = True) -> TimeoutResult:
        """
        Run Python function with smart timeout monitoring
        
        Args:
            func: Function to execute
            args: Function positional arguments
            kwargs: Function keyword arguments
            description: Description for logging
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            TimeoutResult with execution details
        """
        
        if kwargs is None:
            kwargs = {}
            
        self.start_time = time.time()
        self.last_activity_time = self.start_time
        self.activity_count = 0
        self.monitoring = True
        self.result = None
        self.exception = None
        self.output_buffer = []
        self.progress_callback_called = False
        
        logger.info(f"Starting function: {description}")

def smart_run_function(func: Callable,
                      args: tuple = (),
                      kwargs: dict = None,
                      description: str = "",
                      activity_timeout: int = 60,
                      total_timeout: int = 300,
                      capture_output: bool = True) -> TimeoutResult:
    """
    Smart timeout for Python functions with intelligent monitoring
    
    Args:
        func: Python function to execute
        args: Function positional arguments  
        kwargs: Function keyword arguments
        description: Description for logging
        activity_timeout: Seconds without progress before timeout
        total_timeout: Total execution time limit
        capture_output: Whether to capture stdout/stderr from function
        
    Returns:
        TimeoutResult with execution details
        
    Example:
        # Test a /src component directly
        def test_function():
            from dfe_ai.vector.parser.vrl.baseline import VRLBaselineGenerator
            generator = VRLBaselineGenerator() 
            return generator.generate_vrl(logs, device_type="ssh")
            
        result = smart_run_function(
            func=test_function,
            description="Test VRL baseline generation",
            activity_timeout=120,
            total_timeout=600
        )
    """
    
    if kwargs is None:
        kwargs = {}
    
    monitor = FunctionTimeoutMonitor(
        activity_timeout=activity_timeout,
        total_timeout=total_timeout
    )
    
    return monitor.run_function_with_timeout(
        func=func,
        args=args,
        kwargs=kwargs,
        description=description,
        capture_output=capture_output
    )