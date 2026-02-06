#!/usr/bin/env python3
"""
THALOS Prime Neural Network Module
Pure Python implementation of neural network components
"""

# Layer components
from .layer import (
    Layer,
    Linear,
    Embedding,
    PositionalEncoding,
    Dropout,
    Flatten,
    Reshape,
    LayerNorm,
    BatchNorm1d,
    Sequential,
)

# Transformer components
from .transformer import (
    MultiHeadAttention,
    FeedForwardNetwork,
    TransformerBlock,
    TransformerEncoder,
    TransformerDecoder,
    CrossAttentionBlock,
)

# Models and training utilities
from .model import (
    THALOSPrimeModel,
    ModelOptimizer,
    LossFunction,
    SimpleClassifier,
    Seq2SeqModel,
)

__all__ = [
    # Base layer
    'Layer',
    
    # Core layers
    'Linear',
    'Embedding',
    'PositionalEncoding',
    'Dropout',
    'Flatten',
    'Reshape',
    'LayerNorm',
    'BatchNorm1d',
    'Sequential',
    
    # Transformer components
    'MultiHeadAttention',
    'FeedForwardNetwork',
    'TransformerBlock',
    'TransformerEncoder',
    'TransformerDecoder',
    'CrossAttentionBlock',
    
    # Models
    'THALOSPrimeModel',
    'SimpleClassifier',
    'Seq2SeqModel',
    
    # Training utilities
    'ModelOptimizer',
    'LossFunction',
]

__version__ = '1.0.0'
__author__ = 'THALOS Prime Team'
