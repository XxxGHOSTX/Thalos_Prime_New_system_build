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
    LayerNormLayer,
    Sequential
)

from .transformer import (
    MultiHeadAttention,
    FeedForwardNetwork,
    TransformerBlock,
    TransformerEncoder,
    TransformerDecoder,
    CrossAttentionBlock
)

from .model import (
    THALOSPrimeModel,
    ModelOptimizer,
    LossFunction,
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
    'LayerNormLayer',
    'Sequential',
    # Transformer components
    'MultiHeadAttention',
    'FeedForwardNetwork',
    'TransformerBlock',
    'TransformerEncoder',
    'TransformerDecoder',
    'CrossAttentionBlock',
    # Model and training
    'THALOSPrimeModel',
    'ModelOptimizer',
    'LossFunction',
    'LearningRateScheduler',
    'KVCache',
]
