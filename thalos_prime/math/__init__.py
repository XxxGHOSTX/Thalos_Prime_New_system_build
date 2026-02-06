"""
THALOS Prime - Math Module
Mathematical foundations for the THALOS Prime system.
"""

from .tensor import (
    Shape,
    Tensor,
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
    'arange',
    'linspace',
    'cat',
    'stack',
    # Linear algebra
    'LinearAlgebra',
    # Activations and normalizations
    'Activations',
    'LayerNorm',
    'BatchNorm',
    'RMSNorm',
    # Distributions
    'Distributions',
    'Initializers',
    'Dropout',
    'ProbabilityFunctions',
    # Attention
    'AttentionMechanisms',
    'MultiHeadAttention',
    'CrossAttention',
    'LinearAttention',
    'AttentionMetrics',
]
