"""
Logging System for THALOS Prime
Provides structured logging with rotation, filtering, and multiple outputs
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Preserve the original level name so other handlers see an unmodified record
        original_levelname = record.levelname
        try:
            if sys.stdout.isatty():  # Only add colors if output is a terminal
                levelname = record.levelname
                if levelname in self.COLORS:
                    record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            return super().format(record)
        finally:
            # Restore the original level name to avoid leaking ANSI codes to other handlers
            record.levelname = original_levelname


class LogManager:
    """Manages application logging configuration"""
    
    def __init__(self, config: dict):
        self.config = config
        self.loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger with file and console handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config.get('level', 'INFO'))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        console_formatter = ColoredFormatter(
            self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        file_formatter = logging.Formatter(
            self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Console handler
        if self.config.get('console', True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.config.get('file', 'logs/thalos_prime.log')
        if log_file:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.get('max_bytes', 10485760),  # 10MB
                backupCount=self.config.get('backup_count', 5)
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def set_level(self, level: str):
        """Change logging level at runtime"""
        logging.getLogger().setLevel(level.upper())
        self.config['level'] = level.upper()


# Global log manager instance
_log_manager: Optional[LogManager] = None


def init_logging(config: dict) -> LogManager:
    """Initialize logging system"""
    global _log_manager
    _log_manager = LogManager(config)
    return _log_manager


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance"""
    global _log_manager
    if _log_manager is None:
        # Default initialization if not configured
        init_logging({
            'level': 'INFO',
            'console': True,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        })
    return _log_manager.get_logger(name)


class LogContext:
    """Context manager for temporary log level changes"""
    
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
