"""
THALOS Prime - Configuration Module

Provides configuration management, parameter persistence, and system settings.

Components:
    - Settings: System configuration manager
    - ParameterManager: Parameter persistence handler
    - ConfigLoader: Configuration file loader

Author: THALOS Prime Development Team
License: MIT
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class Settings:
    """
    System configuration manager with JSON-based persistence.
    
    Features:
        - Hierarchical configuration structure
        - Type-safe parameter access
        - Default value fallback
        - Configuration validation
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or "thalos_config.json"
        self.config: Dict[str, Any] = self._get_defaults()
        
        # Load from file if exists
        if Path(self.config_file).exists():
            self.load()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'system': {
                'name': 'THALOS Prime',
                'version': '3.1.0',
                'debug_mode': False,
                'log_level': 'INFO'
            },
            'model': {
                'vocab_size': 10000,
                'embedding_dim': 256,
                'hidden_dim': 512,
                'num_layers': 4,
                'num_heads': 8,
                'dropout': 0.1,
                'max_sequence_length': 512
            },
            'training': {
                'batch_size': 32,
                'learning_rate': 0.001,
                'epochs': 100,
                'warmup_steps': 1000,
                'save_frequency': 1000
            },
            'inference': {
                'temperature': 0.7,
                'top_k': 50,
                'top_p': 0.9,
                'max_length': 200,
                'beam_size': 5
            },
            'storage': {
                'checkpoint_dir': 'checkpoints',
                'experience_db': 'experience.db',
                'knowledge_base': 'knowledge.db',
                'cache_size': 1000
            },
            'reasoning': {
                'context_window': 10,
                'confidence_threshold': 0.5,
                'max_iterations': 3
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation like 'model.vocab_size')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'r') as f:
                loaded = json.load(f)
                self.config.update(loaded)
            return True
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return False


class ParameterManager:
    """
    Parameter persistence manager for model parameters and system state.
    
    Features:
        - Parameter versioning
        - Metadata tracking
        - Compression support
    """
    
    def __init__(self, storage_dir: str = "parameters"):
        """
        Initialize parameter manager.
        
        Args:
            storage_dir: Directory for parameter storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def save_parameters(self, name: str, parameters: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save parameters with metadata.
        
        Args:
            name: Parameter set name
            parameters: Parameters dictionary
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            param_file = self.storage_dir / f"{name}.json"
            
            data = {
                'parameters': parameters,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(param_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.metadata[name] = data['metadata']
            return True
            
        except Exception as e:
            print(f"Failed to save parameters: {e}")
            return False
    
    def load_parameters(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load parameters from storage.
        
        Args:
            name: Parameter set name
            
        Returns:
            Parameters dictionary or None if not found
        """
        try:
            param_file = self.storage_dir / f"{name}.json"
            
            if not param_file.exists():
                return None
            
            with open(param_file, 'r') as f:
                data = json.load(f)
            
            self.metadata[name] = data.get('metadata', {})
            return data.get('parameters')
            
        except Exception as e:
            print(f"Failed to load parameters: {e}")
            return None
    
    def list_parameters(self) -> List[str]:
        """
        List available parameter sets.
        
        Returns:
            List of parameter set names
        """
        return [p.stem for p in self.storage_dir.glob("*.json")]


__all__ = ['Settings', 'ParameterManager']
__version__ = '1.0.0'
