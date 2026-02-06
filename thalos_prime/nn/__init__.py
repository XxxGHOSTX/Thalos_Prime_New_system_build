#!/usr/bin/env python3
"""
THALOS Prime Neural Network Module
Pure Python implementation of neural network components
"""

# Layer components
"""
THALOS Prime - Neural Network Module
Neural network layers, transformers, and model utilities.
"""

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
    LayerNormLayer,
    Sequential
)

from .transformer import (
    MultiHeadAttention,
    FeedForwardNetwork,
    TransformerBlock,
    TransformerEncoder,
    TransformerDecoder,
    CrossAttentionBlock,
)

# Models and training utilities
    CrossAttentionBlock
)

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
    LearningRateScheduler,
    KVCache
)

__all__ = [
    # Layers
    'Layer',
    'Linear',
    'Embedding',
    'PositionalEncoding',
    'Dropout',
    'Flatten',
    'Reshape',
    'LayerNorm',
    'BatchNorm1d',
    'Sequential',
    
    'LayerNormLayer',
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
    # Model and training
    'THALOSPrimeModel',
    'ModelOptimizer',
    'LossFunction',
    'LearningRateScheduler',
    'KVCache',
]
