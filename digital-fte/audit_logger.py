#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger - Centralized Logging for AI Employee Actions
Yeh saare AI Employee actions ko log karta hai audit trail ke liye
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps

# Roman Urdu: Configuration aur global variables
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_LOG_FILE = os.path.join(LOG_DIR, "audit.log")

# Roman Urdu: Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


class AuditLogger:
    """
    Centralized Audit Logger for AI Employee System
    AI Employee System ke liye centralized audit logger
    """

    _instance = None
    _logger = None

    def __new__(cls):
        """Singleton pattern - ensure only one logger instance"""
        # Roman Urdu: Singleton instance ensure karna
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the audit logger"""
        if self._initialized:
            return
        
        # Roman Urdu: Logger configuration setup
        self._logger = logging.getLogger("AuditLogger")
        self._logger.setLevel(logging.INFO)
        
        # Roman Urdu: Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Roman Urdu: File handler for audit.log
        file_handler = logging.FileHandler(AUDIT_LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Roman Urdu: Console handler for real-time monitoring
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Roman Urdu: Custom format for audit logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        self._initialized = True
        
        # Roman Urdu: Startup log entry
        self.log_system_start()

    def _format_log(self, action_type: str, file_involved: str = "", 
                    result: str = "", error: str = "", **kwargs) -> str:
        """
        Format log message with all required fields
        Log message ko saare required fields ke saath format karna
        """
        # Roman Urdu: Extra fields ko handle karna
        extra_info = ""
        if kwargs:
            extra_parts = [f"{k}={v}" for k, v in kwargs.items()]
            extra_info = f" | {', '.join(extra_parts)}"
        
        # Roman Urdu: Error indicator
        error_indicator = f" | ERROR: {error}" if error else ""
        
        # Roman Urdu: Formatted log entry
        log_entry = f"{action_type} | File: {file_involved} | Result: {result}{extra_info}{error_indicator}"
        return log_entry

    def log_task_start(self, task_name: str, task_file: str = "", 
                       task_id: str = "", source: str = "", **kwargs) -> None:
        """
        Log when a task starts
        Jab task start hota hai toh log karna
        """
        # Roman Urdu: Task start log entry
        log_entry = self._format_log(
            action_type=f"TASK_START | {task_name}",
            file_involved=task_file,
            result="INITIATED",
            task_id=task_id,
            source=source,
            **kwargs
        )
        self._logger.info(log_entry)

    def log_task_complete(self, task_name: str, task_file: str = "", 
                          task_id: str = "", result: str = "SUCCESS",
                          steps_completed: int = 0, total_steps: int = 0,
                          error: str = "", **kwargs) -> None:
        """
        Log when a task completes
        Jab task complete hota hai toh log karna
        """
        # Roman Urdu: Task completion log entry
        log_entry = self._format_log(
            action_type=f"TASK_COMPLETE | {task_name}",
            file_involved=task_file,
            result=result,
            task_id=task_id,
            steps_completed=f"{steps_completed}/{total_steps}",
            error=error,
            **kwargs
        )
        self._logger.info(log_entry)

    def log_file_operation(self, operation: str, file_path: str, 
                           result: str = "", error: str = "",
                           file_size: int = 0, destination: str = "",
                           **kwargs) -> None:
        """
        Log file operations (read, write, move, delete)
        File operations ko log karna (read, write, move, delete)
        """
        # Roman Urdu: File operation log entry
        log_entry = self._format_log(
            action_type=f"FILE_{operation.upper()}",
            file_involved=file_path,
            result=result,
            error=error,
            file_size=f"{file_size} bytes" if file_size else "",
            destination=destination,
            **kwargs
        )
        self._logger.info(log_entry)

    def log_email_sent(self, recipient: str, subject: str, 
                       email_id: str = "", result: str = "SUCCESS",
                       error: str = "", **kwargs) -> None:
        """
        Log email sending operations
        Email bhejne ki operations ko log karna
        """
        # Roman Urdu: Email sent log entry
        log_entry = self._format_log(
            action_type=f"EMAIL_SENT | {subject}",
            file_involved=email_id,
            result=result,
            error=error,
            recipient=recipient
        )
        self._logger.info(log_entry)

    def log_error(self, error_type: str, error_message: str, 
                  file_involved: str = "", action: str = "",
                  stack_trace: str = "") -> None:
        """
        Log errors with detailed information
        Errors ko detailed information ke saath log karna
        """
        # Roman Urdu: Error log entry
        log_entry = self._format_log(
            action_type=f"ERROR | {error_type}",
            file_involved=file_involved,
            result="FAILED",
            error=error_message,
            action=action,
            stack_trace=stack_trace[:200] if stack_trace else ""
        )
        self._logger.error(log_entry)

    def log_system_start(self) -> None:
        """Log system startup"""
        # Roman Urdu: System startup log
        log_entry = self._format_log(
            action_type="SYSTEM_START",
            file_involved="",
            result="AI Employee System Started",
            version="Gold Tier"
        )
        self._logger.info(log_entry)

    def log_system_shutdown(self) -> None:
        """Log system shutdown"""
        # Roman Urdu: System shutdown log
        log_entry = self._format_log(
            action_type="SYSTEM_SHUTDOWN",
            file_involved="",
            result="AI Employee System Stopped"
        )
        self._logger.info(log_entry)

    def log_api_call(self, api_name: str, endpoint: str = "", 
                     method: str = "", result: str = "",
                     response_time: float = 0, error: str = "") -> None:
        """
        Log API calls
        API calls ko log karna
        """
        # Roman Urdu: API call log entry
        log_entry = self._format_log(
            action_type=f"API_CALL | {api_name}",
            file_involved=endpoint,
            result=result,
            error=error,
            method=method,
            response_time=f"{response_time}ms" if response_time else ""
        )
        self._logger.info(log_entry)

    def log_database_operation(self, operation: str, table: str = "",
                               record_id: str = "", result: str = "",
                               error: str = "") -> None:
        """
        Log database operations
        Database operations ko log karna
        """
        # Roman Urdu: Database operation log entry
        log_entry = self._format_log(
            action_type=f"DB_{operation.upper()}",
            file_involved=table,
            result=result,
            error=error,
            record_id=record_id
        )
        self._logger.info(log_entry)

    def log_user_action(self, user_id: str, action: str, 
                        resource: str = "", result: str = "",
                        error: str = "") -> None:
        """
        Log user actions
        User actions ko log karna
        """
        # Roman Urdu: User action log entry
        log_entry = self._format_log(
            action_type=f"USER_ACTION | {action}",
            file_involved=resource,
            result=result,
            error=error,
            user_id=user_id
        )
        self._logger.info(log_entry)

    def log_security_event(self, event_type: str, source_ip: str = "",
                           user_id: str = "", resource: str = "",
                           result: str = "", error: str = "") -> None:
        """
        Log security-related events
        Security-related events ko log karna
        """
        # Roman Urdu: Security event log entry
        log_entry = self._format_log(
            action_type=f"SECURITY | {event_type}",
            file_involved=resource,
            result=result,
            error=error,
            source_ip=source_ip,
            user_id=user_id
        )
        self._logger.warning(log_entry)


# Roman Urdu: Global audit logger instance
audit_logger = AuditLogger()


# Roman Urdu: Convenience functions for easy importing
def log_task_start(task_name: str, task_file: str = "", **kwargs) -> None:
    """Convenience function for logging task start"""
    audit_logger.log_task_start(task_name, task_file, **kwargs)


def log_task_complete(task_name: str, task_file: str = "", **kwargs) -> None:
    """Convenience function for logging task completion"""
    audit_logger.log_task_complete(task_name, task_file, **kwargs)


def log_file_operation(operation: str, file_path: str, **kwargs) -> None:
    """Convenience function for logging file operations"""
    audit_logger.log_file_operation(operation, file_path, **kwargs)


def log_email_sent(recipient: str, subject: str, **kwargs) -> None:
    """Convenience function for logging email sent"""
    audit_logger.log_email_sent(recipient, subject, **kwargs)


def log_error(error_type: str, error_message: str, **kwargs) -> None:
    """Convenience function for logging errors"""
    audit_logger.log_error(error_type, error_message, **kwargs)


# Roman Urdu: Decorator for automatic logging
def audit_log_action(action_type: str):
    """
    Decorator for automatically logging function calls
    Function calls ko automatically log karne ke liye decorator
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Roman Urdu: Function start log karna
            log_task_start(
                task_name=f"{action_type} | {func.__name__}",
                source="decorator"
            )
            
            try:
                # Roman Urdu: Function execute karna
                result = func(*args, **kwargs)
                
                # Roman Urdu: Success log karna
                log_task_complete(
                    task_name=f"{action_type} | {func.__name__}",
                    result="SUCCESS"
                )
                
                return result
            except Exception as e:
                # Roman Urdu: Error log karna
                log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    action=func.__name__
                )
                raise
        
        return wrapper
    return decorator


# Roman Urdu: Context manager for audit trails
class AuditTrail:
    """
    Context manager for creating audit trails
    Audit trails banane ke liye context manager
    """

    def __init__(self, action_name: str, file_involved: str = ""):
        self.action_name = action_name
        self.file_involved = file_involved
        self.start_time = None

    def __enter__(self):
        """Enter context - log start"""
        # Roman Urdu: Context start log karna
        self.start_time = datetime.now()
        log_task_start(
            task_name=self.action_name,
            task_file=self.file_involved,
            source="context_manager"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - log completion or error"""
        # Roman Urdu: Context end log karna
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            log_task_complete(
                task_name=self.action_name,
                task_file=self.file_involved,
                result="SUCCESS",
                duration=f"{duration}s"
            )
        else:
            log_error(
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                action=self.action_name,
                file_involved=self.file_involved
            )
        
        # Roman Urdu: Exception ko suppress nahi karna
        return False


def main():
    """
    Test the audit logger
    Audit logger ko test karna
    """
    print("=" * 60)
    print("Audit Logger - Test Mode")
    print("=" * 60)
    
    # Roman Urdu: Test various logging functions
    print("\nTesting audit logger functions...\n")
    
    # Test task logging
    log_task_start("Test Task", "test_file.md", task_id="TEST001")
    log_task_complete("Test Task", "test_file.md", result="SUCCESS", 
                     steps_completed=5, total_steps=5)
    
    # Test file operation logging
    log_file_operation("WRITE", "D:/test/file.txt", result="SUCCESS", file_size=1024)
    log_file_operation("READ", "D:/test/file.txt", result="SUCCESS", file_size=2048)
    log_file_operation("MOVE", "D:/test/file.txt", result="SUCCESS", 
                      destination="D:/test/new_file.txt")
    
    # Test email logging
    log_email_sent("test@example.com", "Test Subject", result="SUCCESS")
    
    # Test error logging
    log_error("TestError", "This is a test error message", 
             file_involved="test_file.md", action="test_action")
    
    # Test with context manager
    print("\nTesting context manager...")
    with AuditTrail("Context Manager Test", "context_file.md"):
        import time
        time.sleep(0.1)  # Simulate work
    
    # Test with decorator
    print("\nTesting decorator...")
    @audit_log_action("Decorated Function")
    def test_function():
        return "Success"
    
    test_function()
    
    print("\n" + "=" * 60)
    print("Audit Logger Test Complete!")
    print(f"Check audit.log at: {AUDIT_LOG_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
