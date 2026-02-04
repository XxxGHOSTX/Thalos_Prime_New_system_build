"""
Configuration Management for THALOS Prime
Handles loading, validation, and access to application settings
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration with environment-specific overrides"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self.environment = os.getenv("THALOS_ENV", "development")
        self._load_config()
    
    def _load_config(self):
        """Load base config and environment-specific overrides"""
        # Load base configuration
        base_config_path = self.config_dir / "settings.yaml"
        if base_config_path.exists():
            with open(base_config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        
        # Load environment-specific overrides
        env_config_path = self.config_dir / self.environment / "settings.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                self._merge_config(self.config, env_config)
        
        # Override with environment variables
        self._apply_env_overrides()
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge override config into base config"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # Example: THALOS_LOGGING_LEVEL overrides logging.level
        for key, value in os.environ.items():
            if key.startswith("THALOS_"):
                config_key = key[7:].lower().replace("_", ".")
                self._set_nested(config_key, value)
    
    def _set_nested(self, key: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = key.split(".")
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split(".")
        current = self.config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        self._set_nested(key, value)
    
    def reload(self):
        """Reload configuration from disk"""
        self.config = {}
        self._load_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style setting"""
        self.set(key, value)


# Global config instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global config instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


def init_config(config_dir: str = "config") -> ConfigManager:
    """Initialize configuration with custom directory"""
    global _config
    _config = ConfigManager(config_dir)
    return _config
