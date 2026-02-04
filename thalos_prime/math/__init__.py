"""
Math module for THALOS Prime
Provides tensor operations, linear algebra, activations, distributions, and attention
"""
from .tensor import Tensor, Shape, randn, zeros, ones
from .linear_algebra import LinearAlgebra
from .activations import Activations
from .distributions import Distributions
from .attention import AttentionMechanisms

__all__ = [
    'Tensor', 'Shape', 'randn', 'zeros', 'ones',
    'LinearAlgebra', 'Activations', 'Distributions', 'AttentionMechanisms'
]
