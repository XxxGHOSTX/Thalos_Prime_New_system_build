"""
THALOS Prime - Core AI System Package

This package contains the core modules for the THALOS Prime AI system.

Modules:
    - math: Tensor operations, linear algebra, activations
    - nn: Neural network layers, transformers
    - encoding: Text tokenization (BPE, character, word)
    - crypto: Encryption and hashing (AES-256, SHA-256)
    - kernel: Memory management, virtual filesystem
    - reasoning: Semantic Behavioral Integration
    - core: Main orchestration engine
    - config: Configuration management
    - storage: Data persistence
    - inference: Text generation
    - utils: Utilities
    - database: Database operations
    - wetware: Bio-inspired computing
"""

__version__ = "3.1.0"
__author__ = "THALOS Prime Systems"

# Make key components easily accessible
try:
    from .core import THALOSPrimeEngine
except ImportError:
    THALOSPrimeEngine = None

__all__ = [
    'THALOSPrimeEngine',
]
