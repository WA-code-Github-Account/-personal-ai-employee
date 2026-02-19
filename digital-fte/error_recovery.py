#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Recovery Module - Graceful Degradation and Recovery System
Yeh error recovery aur graceful degradation provide karta hai
"""

import os
import sys
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

# Roman Urdu: Audit logger ko import karna
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_logger import log_error, log_task_start, log_task_complete, log_file_operation

# Roman Urdu: Configuration aur global variables
LOG_FILE = "error_recovery.log"
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 30.0  # seconds

# Roman Urdu: Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RecoveryResult:
    """
    Result of a recovery attempt
    Recovery attempt ka result
    """
    def __init__(self, success: bool, value: Any = None, 
                 error: str = "", recovery_method: str = ""):
        self.success = success
        self.value = value
        self.error = error
        self.recovery_method = recovery_method
        self.timestamp = datetime.now()
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"RecoveryResult({status}, method={self.recovery_method})"


class CircuitBreaker:
    """
    Circuit Breaker pattern for preventing cascade failures
    Cascade failures ko rokne ke liye Circuit Breaker pattern
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker
        Circuit breaker ko initialize karna
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        Function ko circuit breaker ke through execute karna
        """
        if self.state == "OPEN":
            # Roman Urdu: Check if recovery timeout has passed
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                # Roman Urdu: Circuit abhi bhi open hai
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        # Roman Urdu: Check if recovery timeout has passed
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        # Roman Urdu: Success par failure count reset karo
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call"""
        # Roman Urdu: Failure count badhao aur last failure time update karo
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")


# Roman Urdu: Global circuit breakers for different services
circuit_breakers = {
    "vault": CircuitBreaker(failure_threshold=5, recovery_timeout=30),
    "mcp_server": CircuitBreaker(failure_threshold=3, recovery_timeout=60),
    "email": CircuitBreaker(failure_threshold=3, recovery_timeout=120),
    "database": CircuitBreaker(failure_threshold=5, recovery_timeout=30)
}


def retry_with_backoff(max_retries: int = MAX_RETRIES, 
                       base_delay: float = BASE_DELAY,
                       max_delay: float = MAX_DELAY,
                       exceptions: Tuple = (Exception,),
                       log_retries: bool = True):
    """
    Decorator that retries failed operations with exponential backoff
    Failed operations ko retry karta hai exponential backoff ke saath
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 30.0)
        exceptions: Tuple of exceptions to catch and retry
        log_retries: Whether to log retry attempts
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Roman Urdu: Retry logic with exponential backoff
            last_exception = None
            current_delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    # Roman Urdu: Pehla attempt ya retry attempt
                    if attempt == 0:
                        return func(*args, **kwargs)
                    else:
                        # Roman Urdu: Retry se pehle delay
                        if log_retries:
                            logger.info(f"Retry {attempt}/{max_retries} for {func.__name__} "
                                       f"after {current_delay:.2f}s delay")
                        time.sleep(current_delay)
                        return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Roman Urdu: Retry se pehle log karo
                        if log_retries:
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                        
                        # Roman Urdu: Exponential backoff calculate karo
                        current_delay = min(current_delay * 2, max_delay)
                    else:
                        # Roman Urdu: Saare attempts fail ho gaye
                        error_msg = f"All {max_retries + 1} attempts failed for {func.__name__}"
                        logger.error(error_msg)
                        log_error("MAX_RETRIES_EXCEEDED", error_msg, 
                                 action=func.__name__, 
                                 last_error=str(e))
                        raise
            
            # Roman Urdu: Yeh line theoretically unreachable hai
            raise last_exception
        
        return wrapper
    return decorator


def fallback_handler(primary_func: Callable, 
                     fallback_funcs: List[Callable],
                     fallback_names: Optional[List[str]] = None):
    """
    Decorator that switches to fallback methods if primary fails
    Primary fail hone par fallback methods pe switch karta hai
    
    Args:
        primary_func: Primary function to try first
        fallback_funcs: List of fallback functions in order of preference
        fallback_names: Optional names for fallback functions for logging
    
    Returns:
        Wrapped function with fallback logic
    """
    @wraps(primary_func)
    def wrapper(*args, **kwargs) -> Any:
        # Roman Urdu: Primary function ko try karo
        all_errors = []
        
        # Try primary function
        try:
            logger.info(f"Attempting primary method: {primary_func.__name__}")
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary method failed: {primary_func.__name__} - {str(e)}")
            all_errors.append(("primary", str(e)))
        
        # Roman Urdu: Fallback functions ko try karo
        for i, fallback_func in enumerate(fallback_funcs):
            fallback_name = fallback_names[i] if fallback_names else fallback_func.__name__
            
            try:
                logger.info(f"Attempting fallback #{i+1}: {fallback_name}")
                result = fallback_func(*args, **kwargs)
                
                # Roman Urdu: Fallback success - log karo
                logger.info(f"Fallback #{i+1} ({fallback_name}) succeeded")
                return result
            
            except Exception as e:
                logger.warning(f"Fallback #{i+1} ({fallback_name}) failed: {str(e)}")
                all_errors.append((fallback_name, str(e)))
        
        # Roman Urdu: Saare methods fail ho gaye
        error_summary = "; ".join([f"{name}: {error}" for name, error in all_errors])
        error_msg = f"All methods failed: {error_summary}"
        logger.error(error_msg)
        log_error("ALL_FALLBACKS_FAILED", error_msg, 
                 action=primary_func.__name__)
        
        raise Exception(error_msg)
    
    return wrapper


def safe_execute(func: Callable, 
                 default_value: Any = None,
                 log_errors: bool = True,
                 raise_on_error: bool = False) -> Callable:
    """
    Wrapper that catches exceptions and returns default value
    Exceptions ko catch karta hai aur default value return karta hai
    
    Args:
        func: Function to wrap
        default_value: Value to return on error (default: None)
        log_errors: Whether to log errors
        raise_on_error: Whether to raise exception after logging
    
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            # Roman Urdu: Function ko execute karo
            return func(*args, **kwargs)
        except Exception as e:
            # Roman Urdu: Error ko handle karo
            if log_errors:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                log_error("SAFE_EXECUTE_ERROR", str(e), 
                         action=func.__name__)
            
            if raise_on_error:
                raise
            
            # Roman Urdu: Default value return karo
            logger.info(f"Returning default value for {func.__name__}")
            return default_value
    
    return wrapper


def health_check(component: str = "all") -> Dict[str, Any]:
    """
    Test all system components for health
    Saare system components ko test karta hai
    
    Args:
        component: Specific component to check or "all" for all
    
    Returns:
        Dictionary with health status for each component
    """
    # Roman Urdu: Health check results
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Roman Urdu: Components to check
    components_to_check = {
        "vault": _check_vault_health,
        "mcp_server": _check_mcp_health,
        "skills": _check_skills_health,
        "filesystem": _check_filesystem_health,
        "logging": _check_logging_health
    }
    
    if component != "all":
        if component in components_to_check:
            components_to_check = {component: components_to_check[component]}
        else:
            return {"error": f"Unknown component: {component}"}
    
    # Roman Urdu: Har component ko check karo
    all_healthy = True
    for comp_name, check_func in components_to_check.items():
        try:
            status = check_func()
            results["components"][comp_name] = status
            
            if not status["healthy"]:
                all_healthy = False
                results["overall_status"] = "degraded"
        
        except Exception as e:
            results["components"][comp_name] = {
                "healthy": False,
                "error": str(e),
                "message": "Health check failed"
            }
            all_healthy = False
            results["overall_status"] = "unhealthy"
    
    # Roman Urdu: Overall status update
    if all_healthy:
        results["overall_status"] = "healthy"
    
    return results


def _check_vault_health() -> Dict[str, Any]:
    """Check vault accessibility"""
    # Roman Urdu: Vault directory ko check karo
    vault_path = "D:/AI_Workspace_bronze_silver_gold/AI_Employee_Vault"
    
    try:
        if os.path.exists(vault_path):
            if os.path.isdir(vault_path):
                # Roman Urdu: Directory accessible hai
                files = os.listdir(vault_path)
                return {
                    "healthy": True,
                    "path": vault_path,
                    "file_count": len(files),
                    "message": "Vault accessible"
                }
            else:
                return {
                    "healthy": False,
                    "message": "Vault path is not a directory"
                }
        else:
            return {
                "healthy": False,
                "message": "Vault directory does not exist"
            }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Vault access failed"
        }


def _check_mcp_health() -> Dict[str, Any]:
    """Check MCP server accessibility"""
    # Roman Urdu: MCP server ko check karo
    try:
        import requests
        
        # Roman Urdu: MCP server health endpoint check karo
        health_url = "http://localhost:3000/health"
        
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return {
                    "healthy": True,
                    "url": health_url,
                    "response": response.json(),
                    "message": "MCP server healthy"
                }
            else:
                return {
                    "healthy": False,
                    "message": f"MCP server returned status {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "healthy": False,
                "message": "MCP server not reachable (connection refused)"
            }
        except requests.exceptions.Timeout:
            return {
                "healthy": False,
                "message": "MCP server timeout"
            }
    
    except ImportError:
        return {
            "healthy": True,
            "message": "Requests library not available, skipping MCP check"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "MCP health check failed"
        }


def _check_skills_health() -> Dict[str, Any]:
    """Check skills module accessibility"""
    # Roman Urdu: Skills module ko check karo
    try:
        from skills.vault_skill import read_file, write_file, list_folder
        
        # Roman Urdu: Test file operations
        test_dir = "D:/AI_Workspace_bronze_silver_gold/AI_Employee_Vault"
        files = list_folder(test_dir)
        
        return {
            "healthy": True,
            "modules_loaded": ["read_file", "write_file", "list_folder"],
            "test_list_count": len(files),
            "message": "Skills module accessible"
        }
    
    except ImportError as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Skills module import failed"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Skills test failed"
        }


def _check_filesystem_health() -> Dict[str, Any]:
    """Check filesystem accessibility"""
    # Roman Urdu: Filesystem ko check karo
    try:
        # Roman Urdu: Test directory access
        test_dir = "D:/AI_Workspace_bronze_silver_gold/digital-fte"
        
        if os.path.exists(test_dir):
            # Roman Urdu: Read/write test
            test_file = os.path.join(test_dir, ".health_check")
            
            try:
                # Write test
                with open(test_file, 'w') as f:
                    f.write("health_check")
                
                # Read test
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Cleanup
                os.remove(test_file)
                
                if content == "health_check":
                    return {
                        "healthy": True,
                        "test_dir": test_dir,
                        "read_write": "OK",
                        "message": "Filesystem healthy"
                    }
                else:
                    return {
                        "healthy": False,
                        "message": "File content mismatch"
                    }
            
            except Exception as e:
                return {
                    "healthy": False,
                    "error": str(e),
                    "message": "Read/write test failed"
                }
        else:
            return {
                "healthy": False,
                "message": "Test directory does not exist"
            }
    
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Filesystem check failed"
        }


def _check_logging_health() -> Dict[str, Any]:
    """Check logging system"""
    # Roman Urdu: Logging system ko check karo
    try:
        # Roman Urdu: Test logging
        logger.info("Health check: Testing logging system")
        
        return {
            "healthy": True,
            "log_file": LOG_FILE,
            "logger_level": logger.level,
            "handlers": len(logger.handlers),
            "message": "Logging system healthy"
        }
    
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Logging check failed"
        }


# Roman Urdu: Recovery strategies for common failures
recovery_strategies: Dict[str, Dict[str, Any]] = {
    "file_not_found": {
        "description": "File does not exist - create or use alternative",
        "actions": [
            "Check if file path is correct",
            "Try creating the file if appropriate",
            "Use default/backup file",
            "Notify user of missing file"
        ],
        "fallback": "use_default_content"
    },
    "permission_denied": {
        "description": "Permission denied - check access rights",
        "actions": [
            "Verify file permissions",
            "Try running with elevated privileges",
            "Use alternative location",
            "Queue operation for later"
        ],
        "fallback": "queue_for_later"
    },
    "network_timeout": {
        "description": "Network timeout - retry with backoff",
        "actions": [
            "Wait and retry with exponential backoff",
            "Check network connectivity",
            "Use cached/offline mode",
            "Notify user of connectivity issues"
        ],
        "fallback": "offline_mode"
    },
    "database_connection_lost": {
        "description": "Database connection lost - reconnect or use cache",
        "actions": [
            "Attempt to reconnect",
            "Use local cache if available",
            "Queue operations for sync later",
            "Alert administrator"
        ],
        "fallback": "use_cache"
    },
    "mcp_server_unavailable": {
        "description": "MCP server unavailable - use local processing",
        "actions": [
            "Check if MCP server is running",
            "Restart MCP server if possible",
            "Use local processing instead",
            "Queue requests for later"
        ],
        "fallback": "local_processing"
    },
    "email_send_failed": {
        "description": "Email sending failed - queue or notify",
        "actions": [
            "Verify SMTP credentials",
            "Check network connectivity",
            "Queue email for retry",
            "Use alternative email method"
        ],
        "fallback": "queue_email"
    },
    "api_rate_limit": {
        "description": "API rate limit exceeded - wait and retry",
        "actions": [
            "Wait for rate limit reset",
            "Reduce request frequency",
            "Use cached responses",
            "Upgrade API tier if needed"
        ],
        "fallback": "use_cache"
    },
    "memory_low": {
        "description": "Low memory - free resources",
        "actions": [
            "Clear caches",
            "Release unused resources",
            "Process in smaller batches",
            "Alert administrator"
        ],
        "fallback": "batch_processing"
    }
}


def get_recovery_strategy(error_type: str) -> Optional[Dict[str, Any]]:
    """
    Get recovery strategy for a specific error type
    Specific error type ke liye recovery strategy hasil karo
    
    Args:
        error_type: Type of error (e.g., "file_not_found", "permission_denied")
    
    Returns:
        Recovery strategy dictionary or None
    """
    # Roman Urdu: Error type ke liye strategy return karo
    return recovery_strategies.get(error_type.lower())


def execute_recovery_strategy(error_type: str, 
                              context: Dict[str, Any]) -> RecoveryResult:
    """
    Execute a recovery strategy for an error
    Error ke liye recovery strategy execute karo
    
    Args:
        error_type: Type of error
        context: Additional context for recovery
    
    Returns:
        RecoveryResult with success status
    """
    # Roman Urdu: Recovery strategy obtain karo
    strategy = get_recovery_strategy(error_type)
    
    if not strategy:
        return RecoveryResult(
            success=False,
            error=f"No recovery strategy for: {error_type}"
        )
    
    try:
        logger.info(f"Executing recovery strategy for: {error_type}")
        
        # Roman Urdu: Strategy ke actions log karo
        for i, action in enumerate(strategy["actions"]):
            logger.info(f"  Action {i+1}: {action}")
        
        # Roman Urdu: Fallback action determine karo
        fallback = strategy.get("fallback", "")
        
        # Roman Urdu: Specific recovery logic
        if fallback == "use_default_content":
            return RecoveryResult(
                success=True,
                value=context.get("default_content", ""),
                recovery_method="use_default_content"
            )
        elif fallback == "queue_for_later":
            return RecoveryResult(
                success=True,
                value={"queued": True, "context": context},
                recovery_method="queue_for_later"
            )
        elif fallback == "offline_mode":
            return RecoveryResult(
                success=True,
                value={"mode": "offline"},
                recovery_method="offline_mode"
            )
        elif fallback == "use_cache":
            return RecoveryResult(
                success=True,
                value={"from_cache": True},
                recovery_method="use_cache"
            )
        elif fallback == "local_processing":
            return RecoveryResult(
                success=True,
                value={"mode": "local"},
                recovery_method="local_processing"
            )
        elif fallback == "queue_email":
            return RecoveryResult(
                success=True,
                value={"queued": True},
                recovery_method="queue_email"
            )
        elif fallback == "batch_processing":
            return RecoveryResult(
                success=True,
                value={"mode": "batch"},
                recovery_method="batch_processing"
            )
        else:
            return RecoveryResult(
                success=False,
                error=f"Unknown fallback: {fallback}"
            )
    
    except Exception as e:
        logger.error(f"Recovery strategy failed: {str(e)}")
        return RecoveryResult(
            success=False,
            error=str(e),
            recovery_method=error_type
        )


def graceful_degradation(mode: str = "partial") -> Dict[str, Any]:
    """
    Enable graceful degradation mode when system is under stress
    System stress ke time graceful degradation mode enable karo
    
    Args:
        mode: Degradation mode ("minimal", "partial", "full")
    
    Returns:
        Dictionary with current degradation settings
    """
    # Roman Urdu: Degradation modes
    modes = {
        "minimal": {
            "description": "Minimal functionality only",
            "disable": ["email", "notifications", "analytics", "logging_verbose"],
            "enable": ["core_operations", "error_handling"],
            "retry_count": 1,
            "timeout_multiplier": 0.5
        },
        "partial": {
            "description": "Partial functionality",
            "disable": ["analytics", "logging_verbose"],
            "enable": ["core_operations", "email", "error_handling"],
            "retry_count": 2,
            "timeout_multiplier": 0.75
        },
        "full": {
            "description": "Full functionality",
            "disable": [],
            "enable": ["all"],
            "retry_count": MAX_RETRIES,
            "timeout_multiplier": 1.0
        }
    }
    
    selected_mode = modes.get(mode, modes["partial"])
    
    logger.info(f"Graceful degradation mode: {mode}")
    logger.info(f"  Description: {selected_mode['description']}")
    logger.info(f"  Disabled: {selected_mode['disable']}")
    logger.info(f"  Enabled: {selected_mode['enable']}")
    
    return selected_mode


def main():
    """
    Test the error recovery module
    Error recovery module ko test karo
    """
    print("=" * 60)
    print("Error Recovery Module - Test Mode")
    print("=" * 60)
    
    # Roman Urdu: Test retry_with_backoff
    print("\n[1/6] Testing retry_with_backoff decorator...")
    
    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed after retries: {e}")
    
    # Roman Urdu: Test safe_execute
    print("\n[2/6] Testing safe_execute wrapper...")
    
    def failing_function():
        raise ValueError("Intentional failure")
    
    safe_failing = safe_execute(failing_function, default_value="Default Result", log_errors=True)
    result = safe_failing()
    print(f"  Result: {result}")
    
    # Roman Urdu: Test health_check
    print("\n[3/6] Testing health_check...")
    health = health_check()
    print(f"  Overall Status: {health['overall_status']}")
    for comp, status in health.get("components", {}).items():
        health_status = "[OK]" if status["healthy"] else "[FAIL]"
        print(f"  {health_status} {comp}: {status['message']}")
    
    # Roman Urdu: Test recovery strategies
    print("\n[4/6] Testing recovery strategies...")
    for error_type in ["file_not_found", "permission_denied", "network_timeout"]:
        strategy = get_recovery_strategy(error_type)
        if strategy:
            print(f"  {error_type}: {strategy['description']}")
    
    # Roman Urdu: Test execute_recovery_strategy
    print("\n[5/6] Testing execute_recovery_strategy...")
    result = execute_recovery_strategy("file_not_found", 
                                       {"default_content": "backup"})
    print(f"  Recovery Result: {result}")
    
    # Roman Urdu: Test graceful_degradation
    print("\n[6/6] Testing graceful_degradation...")
    degradation = graceful_degradation("partial")
    print(f"  Mode: partial")
    print(f"  Disabled: {degradation['disable']}")
    
    print("\n" + "=" * 60)
    print("Error Recovery Module Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
