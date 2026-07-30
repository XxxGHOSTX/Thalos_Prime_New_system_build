#!/usr/bin/env python3
"""
THALOS Prime Math Module
Complete mathematical foundations for THALOS Prime system
"""

# Core tensor operations
from .tensor import (
    Tensor,
    Shape,
    randn,
    zeros,
    ones,
    eye,
    uniform
)

# Linear algebra
from .linear_algebra import LinearAlgebra

# Activation functions
from .activations import Activations

# Distributions and initialization
from .distributions import Distributions

# Attention mechanisms
from .attention import AttentionMechanisms

__all__ = [
    # Tensor types
    'Tensor',
    'Shape',
    
    # Tensor creation functions
    'randn',
    'zeros',
    'ones',
    'eye',
    'uniform',
    
    # Classes
    'LinearAlgebra',
    'Activations',
    'Distributions',
    'AttentionMechanisms',
]

__version__ = '1.0.0'
__author__ = 'THALOS Prime Team'
