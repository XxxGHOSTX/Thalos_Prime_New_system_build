"""
THALOS Prime - Utilities Module
Logging, profiling, and validation utilities.
"""

from typing import Any, Optional, List, Dict, Callable
import time
import functools


class Logger:
    """Simple logging utility."""
    
    LEVELS = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
    
    def __init__(self, name: str = 'THALOS', level: str = 'INFO'):
        self.name = name
        self.level = level
        self.handlers: List[Callable] = []
        self._add_default_handler()
    
    def _add_default_handler(self) -> None:
        """Add default console handler."""
        def console_handler(level: str, message: str):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{self.name}] [{level}] {message}")
        self.handlers.append(console_handler)
    
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged."""
        return self.LEVELS.get(level, 0) >= self.LEVELS.get(self.level, 0)
    
    def _log(self, level: str, message: str) -> None:
        """Log a message."""
        if self._should_log(level):
            for handler in self.handlers:
                handler(level, message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self._log('DEBUG', message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self._log('INFO', message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self._log('WARNING', message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self._log('ERROR', message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self._log('CRITICAL', message)
    
    def set_level(self, level: str) -> None:
        """Set logging level."""
        if level in self.LEVELS:
            self.level = level
    
    def add_handler(self, handler: Callable) -> None:
        """Add a custom handler."""
        self.handlers.append(handler)


class Profiler:
    """Performance profiling utility."""
    
    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
        self.active_timers: Dict[str, float] = {}
    
    def start(self, name: str) -> None:
        """Start timing a section."""
        self.active_timers[name] = time.time()
    
    def stop(self, name: str) -> float:
        """Stop timing and record duration."""
        if name not in self.active_timers:
            return 0.0
        
        duration = time.time() - self.active_timers[name]
        del self.active_timers[name]
        
        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(duration)
        
        return duration
    
    def profile(self, name: str) -> Callable:
        """Decorator to profile a function."""
        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.start(name)
                result = fn(*args, **kwargs)
                self.stop(name)
                return result
            return wrapper
        return decorator
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a profiled section."""
        timings = self.timings.get(name, [])
        if not timings:
            return {'count': 0, 'total': 0, 'avg': 0, 'min': 0, 'max': 0}
        
        return {
            'count': len(timings),
            'total': sum(timings),
            'avg': sum(timings) / len(timings),
            'min': min(timings),
            'max': max(timings)
        }
    
    def report(self) -> str:
        """Generate profiling report."""
        lines = ["Profiling Report", "=" * 50]
        
        for name in sorted(self.timings.keys()):
            stats = self.get_stats(name)
            lines.append(
                f"{name}: {stats['count']} calls, "
                f"avg={stats['avg']*1000:.2f}ms, "
                f"total={stats['total']:.3f}s"
            )
        
        return '\n'.join(lines)
    
    def reset(self) -> None:
        """Reset all timings."""
        self.timings.clear()
        self.active_timers.clear()


class Validator:
    """Input validation utility."""
    
    @staticmethod
    def is_non_empty_string(value: Any) -> bool:
        """Check if value is a non-empty string."""
        return isinstance(value, str) and len(value.strip()) > 0
    
    @staticmethod
    def is_positive_int(value: Any) -> bool:
        """Check if value is a positive integer."""
        return isinstance(value, int) and value > 0
    
    @staticmethod
    def is_in_range(value: Any, min_val: float, max_val: float) -> bool:
        """Check if value is within range."""
        try:
            return min_val <= float(value) <= max_val
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_valid_email(value: str) -> bool:
        """Check if value is a valid email format."""
        import re
        pattern = r'^[\w.-]+@[\w.-]+\.\w+$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input."""
        # Remove control characters
        cleaned = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')
        # Trim whitespace
        cleaned = cleaned.strip()
        return cleaned
    
    @staticmethod
    def validate_config(config: Dict[str, Any], schema: Dict[str, type]) -> List[str]:
        """Validate configuration against schema."""
        errors = []
        
        for key, expected_type in schema.items():
            if key not in config:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(config[key], expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        
        return errors


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self, name: str = "Timer", logger: Optional[Logger] = None):
        self.name = name
        self.logger = logger
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self) -> 'Timer':
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args) -> None:
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if self.logger:
            self.logger.debug(f"{self.name}: {duration:.4f} seconds")
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time


class Cache:
    """Simple in-memory cache."""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check TTL
        if self.ttl and time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        # Evict if at capacity
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), 
                            key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (value, time.time())
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


# Export classes
__all__ = [
    'Logger',
    'Profiler',
    'Validator',
    'Timer',
    'Cache',
]
