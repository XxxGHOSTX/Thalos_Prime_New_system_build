"""THALOS Prime - Main Package"""
__version__ = "3.2.0"
__author__ = "THALOS Prime Systems"

from .config_manager import ConfigManager, get_config, init_config
from .logger import LogManager, get_logger, init_logging

__all__ = [
    'ConfigManager', 'get_config', 'init_config',
    'LogManager', 'get_logger', 'init_logging'
]
