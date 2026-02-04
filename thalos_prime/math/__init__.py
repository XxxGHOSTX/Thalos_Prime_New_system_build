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
    arange,
    linspace,
    cat,
    stack
)

from .linear_algebra import LinearAlgebra

from .activations import (
    Activations,
    LayerNorm,
    BatchNorm,
    RMSNorm
)

from .distributions import (
    Distributions,
    Initializers,
    Dropout,
    ProbabilityFunctions
)

from .attention import (
    AttentionMechanisms,
    MultiHeadAttention,
    CrossAttention,
    LinearAttention,
    AttentionMetrics
)

__all__ = [
    # Tensor operations
    'Shape',
    'Tensor',
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
