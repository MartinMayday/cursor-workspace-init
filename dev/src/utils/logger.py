"""
Structured logging system for cursor workspace initialization.

Provides structured logging to artifacts directory with timestamps and operation tracking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StructuredLogger:
    """
    Structured logger that writes JSONL (JSON Lines) format logs.
    
    Each log entry is a JSON object with:
    - timestamp: ISO8601 timestamp
    - operation: Operation name
    - status: success|error|warning
    - level: Log level
    - details: Additional details dictionary
    - duration_ms: Duration in milliseconds (if applicable)
    """
    
    def __init__(self, log_dir: Optional[str] = None, log_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory for log files (default: artifacts/logs/)
            log_file: Log file name (default: init-cursorworkspace-{timestamp}.jsonl)
        """
        # Determine log directory
        if log_dir is None:
            log_dir = os.getenv('CURSOR_ARTIFACTS_DIR', 'artifacts')
            log_dir = os.path.join(log_dir, 'logs')
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine log file name
        if log_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'init-cursorworkspace-{timestamp}.jsonl'
        
        self.log_file = self.log_dir / log_file
        self._operation_start_times: Dict[str, datetime] = {}
    
    def _write_log(self, operation: str, status: str, level: LogLevel, 
                   details: Optional[Dict[str, Any]] = None, 
                   duration_ms: Optional[float] = None):
        """
        Write a log entry.
        
        Args:
            operation: Operation name
            status: Status (success, error, warning, info)
            level: Log level
            details: Additional details
            duration_ms: Duration in milliseconds
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'status': status,
            'level': level.value,
        }
        
        if details:
            log_entry['details'] = details
        
        if duration_ms is not None:
            log_entry['duration_ms'] = round(duration_ms, 2)
        
        # Write as JSON line
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def start_operation(self, operation: str):
        """
        Start timing an operation.
        
        Args:
            operation: Operation name
        """
        self._operation_start_times[operation] = datetime.now()
        self._write_log(operation, 'started', LogLevel.INFO, {'phase': 'start'})
    
    def end_operation(self, operation: str, status: str = 'success', 
                     details: Optional[Dict[str, Any]] = None):
        """
        End timing an operation and log result.
        
        Args:
            operation: Operation name
            status: Status (success, error, warning)
            details: Additional details
        """
        duration_ms = None
        if operation in self._operation_start_times:
            start_time = self._operation_start_times[operation]
            duration = datetime.now() - start_time
            duration_ms = duration.total_seconds() * 1000
            del self._operation_start_times[operation]
        
        level = LogLevel.INFO
        if status == 'error':
            level = LogLevel.ERROR
        elif status == 'warning':
            level = LogLevel.WARNING
        
        self._write_log(operation, status, level, details, duration_ms)
    
    def debug(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        details = details or {}
        details['message'] = message
        self._write_log(operation, 'info', LogLevel.DEBUG, details)
    
    def info(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log info message."""
        details = details or {}
        details['message'] = message
        self._write_log(operation, 'success', LogLevel.INFO, details)
    
    def warning(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        details = details or {}
        details['message'] = message
        self._write_log(operation, 'warning', LogLevel.WARNING, details)
    
    def error(self, operation: str, message: str, error: Optional[Exception] = None, 
             details: Optional[Dict[str, Any]] = None):
        """Log error message."""
        details = details or {}
        details['message'] = message
        if error:
            details['error_type'] = type(error).__name__
            details['error_message'] = str(error)
            import traceback
            details['traceback'] = traceback.format_exc()
        self._write_log(operation, 'error', LogLevel.ERROR, details)
    
    def critical(self, operation: str, message: str, error: Optional[Exception] = None,
                details: Optional[Dict[str, Any]] = None):
        """Log critical error message."""
        details = details or {}
        details['message'] = message
        if error:
            details['error_type'] = type(error).__name__
            details['error_message'] = str(error)
            import traceback
            details['traceback'] = traceback.format_exc()
        self._write_log(operation, 'error', LogLevel.CRITICAL, details)
    
    def get_log_path(self) -> Path:
        """Get the path to the log file."""
        return self.log_file


# Global logger instance (can be overridden)
_default_logger: Optional[StructuredLogger] = None


def get_logger(log_dir: Optional[str] = None, log_file: Optional[str] = None) -> StructuredLogger:
    """
    Get or create the global logger instance.
    
    Args:
        log_dir: Directory for log files
        log_file: Log file name
        
    Returns:
        Logger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = StructuredLogger(log_dir, log_file)
    return _default_logger


def reset_logger():
    """Reset the global logger instance (useful for testing)."""
    global _default_logger
    _default_logger = None
