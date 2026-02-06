"""
THALOS Prime - Configuration Module
System configuration and parameter management.
"""

from typing import Dict, Any, Optional
import json
import os


class Settings:
    """System configuration settings."""
    
    DEFAULT_CONFIG = {
        'system': {
            'name': 'THALOS Prime',
            'version': '3.1.0',
            'debug': False,
            'log_level': 'INFO',
        },
        'model': {
            'vocab_size': 50000,
            'd_model': 512,
            'num_heads': 8,
            'num_layers': 6,
            'd_ff': 2048,
            'max_seq_len': 2048,
            'dropout': 0.1,
        },
        'training': {
            'batch_size': 32,
            'learning_rate': 0.0001,
            'warmup_steps': 4000,
            'max_epochs': 100,
            'gradient_clip': 1.0,
        },
        'inference': {
            'temperature': 0.7,
            'top_k': 50,
            'top_p': 0.9,
            'max_length': 512,
        },
        'storage': {
            'checkpoint_dir': './checkpoints',
            'log_dir': './logs',
            'data_dir': './data',
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = dict(self.DEFAULT_CONFIG)
        self.config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self.load(config_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def load(self, path: str) -> None:
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            loaded = json.load(f)
            self._merge(self.config, loaded)
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to JSON file."""
        save_path = path or self.config_path
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)
    
    def _merge(self, base: Dict, update: Dict) -> None:
        """Merge update into base configuration."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return dict(self.config)


class ParameterManager:
    """Manage model and system parameters."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.parameters: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
    
    def register(self, name: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Register a parameter."""
        self.parameters[name] = value
        if metadata:
            self.metadata[name] = metadata
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get parameter value."""
        return self.parameters.get(name, default)
    
    def set(self, name: str, value: Any) -> None:
        """Set parameter value."""
        self.parameters[name] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save parameters to file."""
        save_path = path or self.storage_path
        if save_path:
            with open(save_path, 'w') as f:
                json.dump({
                    'parameters': self.parameters,
                    'metadata': self.metadata
                }, f, indent=2)
    
    def load(self, path: Optional[str] = None) -> None:
        """Load parameters from file."""
        load_path = path or self.storage_path
        if load_path and os.path.exists(load_path):
            with open(load_path, 'r') as f:
                data = json.load(f)
                self.parameters = data.get('parameters', {})
                self.metadata = data.get('metadata', {})
    
    def list_parameters(self) -> list:
        """List all registered parameters."""
        return list(self.parameters.keys())


class Environment:
    """Environment configuration."""
    
    def __init__(self):
        self.env_vars: Dict[str, str] = {}
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load relevant environment variables."""
        relevant_prefixes = ['THALOS_', 'MODEL_', 'SYSTEM_']
        
        for key, value in os.environ.items():
            for prefix in relevant_prefixes:
                if key.startswith(prefix):
                    self.env_vars[key] = value
                    break
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return self.env_vars.get(key, os.environ.get(key, default))
    
    def set(self, key: str, value: str) -> None:
        """Set environment variable."""
        os.environ[key] = value
        self.env_vars[key] = value
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.get('THALOS_ENV', 'development').lower() == 'production'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('THALOS_DEBUG', 'false').lower() == 'true'


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Export classes
__all__ = [
    'Settings',
    'ParameterManager',
    'Environment',
    'get_settings',
]
