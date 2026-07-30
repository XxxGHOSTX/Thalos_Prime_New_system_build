"""
THALOS Prime - Utilities Module

Provides logging, profiling, validation, and utility functions.

Components:
    - Logger: Multi-level logging system
    - Profiler: Performance measurement
    - Validator: Input validation

Author: THALOS Prime Development Team
License: MIT
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path


class Logger:
    """
    Multi-level logging system with file and console output.
    
    Features:
        - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - File and console output
        - Timestamped logs
        - Log filtering
    """
    
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self, name: str = "THALOS", level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logging
        """
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level, logging.INFO))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.LEVELS.get(level, logging.INFO))
        formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.LEVELS.get(level, logging.INFO))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)
    
    def set_level(self, level: str):
        """
        Set logging level.
        
        Args:
            level: New log level
        """
        self.level = level
        self.logger.setLevel(self.LEVELS.get(level, logging.INFO))


class Profiler:
    """
    Performance measurement and profiling.
    
    Features:
        - Function execution timing
        - Memory usage tracking
        - Operation statistics
        - Context manager support
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize profiler.
        
        Args:
            name: Profiler name
        """
        self.name = name
        self.timings: Dict[str, List[float]] = {}
        self.counts: Dict[str, int] = {}
        self.current_operation: Optional[str] = None
        self.start_time: Optional[float] = None
    
    def start(self, operation: str):
        """
        Start timing an operation.
        
        Args:
            operation: Operation name
        """
        self.current_operation = operation
        self.start_time = time.time()
    
    def stop(self) -> float:
        """
        Stop timing current operation.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None or self.current_operation is None:
            return 0.0
        
        elapsed = time.time() - self.start_time
        
        if self.current_operation not in self.timings:
            self.timings[self.current_operation] = []
            self.counts[self.current_operation] = 0
        
        self.timings[self.current_operation].append(elapsed)
        self.counts[self.current_operation] += 1
        
        self.current_operation = None
        self.start_time = None
        
        return elapsed
    
    def profile(self, operation: str):
        """
        Context manager for profiling operations.
        
        Args:
            operation: Operation name
            
        Example:
            with profiler.profile("inference"):
                # code to profile
                pass
        """
        return ProfilerContext(self, operation)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """
        Get statistics for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with min, max, avg, total, count
        """
        if operation not in self.timings:
            return {}
        
        times = self.timings[operation]
        return {
            'count': self.counts[operation],
            'total': sum(times),
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self.timings.keys()}
    
    def reset(self):
        """Reset all profiling data."""
        self.timings.clear()
        self.counts.clear()


class ProfilerContext:
    """Context manager for profiler."""
    
    def __init__(self, profiler: Profiler, operation: str):
        self.profiler = profiler
        self.operation = operation
    
    def __enter__(self):
        self.profiler.start(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.stop()


class Validator:
    """
    Input validation and sanitization.
    
    Features:
        - Type checking
        - Range validation
        - Format validation
        - Custom validators
    """
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: int = 10000) -> bool:
        """
        Validate string input.
        
        Args:
            value: Value to validate
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        length = len(value)
        return min_length <= length <= max_length
    
    @staticmethod
    def validate_number(value: Any, min_val: Optional[float] = None, 
                       max_val: Optional[float] = None) -> bool:
        """
        Validate numeric input.
        
        Args:
            value: Value to validate
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, (int, float)):
            return False
        
        if min_val is not None and value < min_val:
            return False
        
        if max_val is not None and value > max_val:
            return False
        
        return True
    
    @staticmethod
    def validate_list(value: Any, min_length: int = 0, max_length: Optional[int] = None,
                     element_validator: Optional[Callable] = None) -> bool:
        """
        Validate list input.
        
        Args:
            value: Value to validate
            min_length: Minimum list length
            max_length: Maximum list length
            element_validator: Optional validator for elements
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, list):
            return False
        
        length = len(value)
        
        if length < min_length:
            return False
        
        if max_length is not None and length > max_length:
            return False
        
        if element_validator:
            return all(element_validator(elem) for elem in value)
        
        return True
    
    @staticmethod
    def validate_dict(value: Any, required_keys: Optional[List[str]] = None) -> bool:
        """
        Validate dictionary input.
        
        Args:
            value: Value to validate
            required_keys: Optional list of required keys
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, dict):
            return False
        
        if required_keys:
            return all(key in value for key in required_keys)
        
        return True
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """
        Sanitize string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum length
            
        Returns:
            Sanitized string
        """
        # Remove control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char == '\n')
        
        # Truncate to max length
        return sanitized[:max_length]


__all__ = ['Logger', 'Profiler', 'Validator']
__version__ = '1.0.0'
