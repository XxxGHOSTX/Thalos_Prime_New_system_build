#!/usr/bin/env python3
"""
THALOS Prime Neural Network Layers
Pure Python implementation of core NN layer components
"""

import math
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from ..math import Tensor, Shape, randn, zeros, ones
from ..math.distributions import Distributions
from ..math.linear_algebra import LinearAlgebra


class Layer(ABC):
    """Base abstract class for neural network layers"""
    
    def __init__(self):
        """Initialize base layer"""
        self.training = True
    
    @abstractmethod
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass through the layer
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor
        """
        pass
    
    def train(self):
        """Set layer to training mode"""
        self.training = True
    
    def eval(self):
        """Set layer to evaluation mode"""
        self.training = False


class Linear(Layer):
    """
    Fully connected (dense) linear layer
    Implements: y = xW^T + b
    """
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        """
        Initialize linear layer
        
        Args:
            in_features: Size of input features
            out_features: Size of output features
            bias: Whether to include bias term
        """
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.use_bias = bias
        
        # Initialize weights using He initialization
        self.weight = Distributions.he_normal(in_features, out_features)
        
        # Initialize bias to zeros
        if self.use_bias:
            self.bias = zeros(out_features)
        else:
            self.bias = None
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass: y = xW^T + b
        
        Args:
            x: Input tensor of shape (..., in_features)
            
        Returns:
            Output tensor of shape (..., out_features)
        """
        # Handle different input shapes
        original_shape = x.shape.dims
        
        if x.shape.ndim == 1:
            # Single vector: (in_features,) -> (1, in_features)
            x_reshaped = x.reshape(1, self.in_features)
            batch_size = 1
        elif x.shape.ndim == 2:
            # Batch of vectors: (batch_size, in_features)
            x_reshaped = x
            batch_size = x.shape.dims[0]
        else:
            # Flatten all dimensions except last
            total_elements = x.shape.size
            batch_size = total_elements // self.in_features
            x_reshaped = x.reshape(batch_size, self.in_features)
        
        # Transpose weight for matrix multiplication: (out_features, in_features)
        weight_t = self.weight.transpose()
        
        # Matrix multiplication: (batch_size, in_features) @ (in_features, out_features)
        output = LinearAlgebra.matmul(x_reshaped, weight_t)
        
        # Add bias if present
        if self.use_bias:
            # Broadcast bias across batch dimension
            output_data = []
            for i in range(batch_size):
                for j in range(self.out_features):
                    idx = i * self.out_features + j
                    output_data.append(output.data[idx] + self.bias.data[j])
            output = Tensor(output_data, Shape(batch_size, self.out_features))
        
        # Reshape output to match input batch shape if needed
        if len(original_shape) == 1 and batch_size == 1:
            # Return flat vector
            output = output.reshape(self.out_features)
        
        return output


class Embedding(Layer):
    """
    Embedding layer for vocabulary lookup
    Converts token IDs to dense vector representations
    """
    
    def __init__(self, vocab_size: int, embedding_dim: int):
        """
        Initialize embedding layer
        
        Args:
            vocab_size: Size of vocabulary
            embedding_dim: Dimension of embedding vectors
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        
        # Initialize embedding table with normal distribution
        self.embedding_table = Distributions.normal(0.0, 1.0 / math.sqrt(embedding_dim), 
                                                     vocab_size * embedding_dim)
        self.embedding_table = self.embedding_table.reshape(vocab_size, embedding_dim)
    
    def forward(self, token_ids: Tensor) -> Tensor:
        """
        Look up embeddings for token IDs
        
        Args:
            token_ids: Tensor of token IDs, shape (seq_len,) or (batch_size, seq_len)
            
        Returns:
            Embeddings tensor of shape (seq_len, embedding_dim) or (batch_size, seq_len, embedding_dim)
        """
        # Convert token IDs to integers
        ids = [int(x) for x in token_ids.data]
        
        # Handle 1D and 2D input
        if token_ids.shape.ndim == 1:
            # Single sequence: (seq_len,)
            seq_len = len(ids)
            output_data = []
            
            for token_id in ids:
                if token_id < 0 or token_id >= self.vocab_size:
                    raise ValueError(f"Token ID {token_id} out of range [0, {self.vocab_size})")
                
                # Get embedding vector for this token
                start_idx = token_id * self.embedding_dim
                end_idx = start_idx + self.embedding_dim
                output_data.extend(self.embedding_table.data[start_idx:end_idx])
            
            return Tensor(output_data, Shape(seq_len, self.embedding_dim))
        
        elif token_ids.shape.ndim == 2:
            # Batch of sequences: (batch_size, seq_len)
            batch_size, seq_len = token_ids.shape.dims
            output_data = []
            
            for token_id in ids:
                if token_id < 0 or token_id >= self.vocab_size:
                    raise ValueError(f"Token ID {token_id} out of range [0, {self.vocab_size})")
                
                start_idx = token_id * self.embedding_dim
                end_idx = start_idx + self.embedding_dim
                output_data.extend(self.embedding_table.data[start_idx:end_idx])
            
            return Tensor(output_data, Shape(batch_size, seq_len, self.embedding_dim))
        
        else:
            raise ValueError(f"Token IDs must be 1D or 2D, got shape {token_ids.shape}")


class PositionalEncoding(Layer):
    """
    Sinusoidal positional encoding for transformer models
    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """
    
    def __init__(self, d_model: int, max_seq_len: int = 5000):
        """
        Initialize positional encoding
        
        Args:
            d_model: Dimension of model embeddings
            max_seq_len: Maximum sequence length
        """
        super().__init__()
        self.d_model = d_model
        self.max_seq_len = max_seq_len
        
        # Precompute positional encodings
        self.pe = self._create_positional_encoding(max_seq_len, d_model)
    
    def _create_positional_encoding(self, max_len: int, d_model: int) -> Tensor:
        """
        Create positional encoding matrix
        
        Args:
            max_len: Maximum sequence length
            d_model: Model dimension
            
        Returns:
            Positional encoding tensor of shape (max_len, d_model)
        """
        pe_data = []
        
        for pos in range(max_len):
            for i in range(d_model):
                # Calculate position encoding
                if i % 2 == 0:
                    # Even indices: sin
                    angle = pos / math.pow(10000, i / d_model)
                    pe_data.append(math.sin(angle))
                else:
                    # Odd indices: cos
                    angle = pos / math.pow(10000, (i - 1) / d_model)
                    pe_data.append(math.cos(angle))
        
        return Tensor(pe_data, Shape(max_len, d_model))
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Add positional encoding to input
        
        Args:
            x: Input tensor of shape (seq_len, d_model) or (batch_size, seq_len, d_model)
            
        Returns:
            Output tensor with positional encoding added
        """
        if x.shape.ndim == 2:
            # (seq_len, d_model)
            seq_len, d_model = x.shape.dims
            
            if seq_len > self.max_seq_len:
                raise ValueError(f"Sequence length {seq_len} exceeds maximum {self.max_seq_len}")
            
            # Add positional encoding
            output_data = []
            for i in range(seq_len):
                for j in range(d_model):
                    x_idx = i * d_model + j
                    pe_idx = i * d_model + j
                    output_data.append(x.data[x_idx] + self.pe.data[pe_idx])
            
            return Tensor(output_data, Shape(seq_len, d_model))
        
        elif x.shape.ndim == 3:
            # (batch_size, seq_len, d_model)
            batch_size, seq_len, d_model = x.shape.dims
            
            if seq_len > self.max_seq_len:
                raise ValueError(f"Sequence length {seq_len} exceeds maximum {self.max_seq_len}")
            
            # Add positional encoding to each batch item
            output_data = []
            for b in range(batch_size):
                for i in range(seq_len):
                    for j in range(d_model):
                        x_idx = b * seq_len * d_model + i * d_model + j
                        pe_idx = i * d_model + j
                        output_data.append(x.data[x_idx] + self.pe.data[pe_idx])
            
            return Tensor(output_data, Shape(batch_size, seq_len, d_model))
        
        else:
            raise ValueError(f"Input must be 2D or 3D, got shape {x.shape}")


class Dropout(Layer):
    """
    Dropout layer for regularization
    Randomly sets elements to zero during training
    """
    
    def __init__(self, p: float = 0.5):
        """
        Initialize dropout layer
        
        Args:
            p: Probability of dropping a unit (0 to 1)
        """
        super().__init__()
        if not 0 <= p <= 1:
            raise ValueError(f"Dropout probability must be in [0, 1], got {p}")
        self.p = p
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply dropout to input
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with dropout applied
        """
        if not self.training or self.p == 0:
            return x
        
        return Distributions.dropout(x, self.p, training=self.training)


class Flatten(Layer):
    """
    Flatten layer to reshape multidimensional input to 1D or 2D
    """
    
    def __init__(self, start_dim: int = 1):
        """
        Initialize flatten layer
        
        Args:
            start_dim: Dimension to start flattening from
        """
        super().__init__()
        self.start_dim = start_dim
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Flatten input tensor
        
        Args:
            x: Input tensor
            
        Returns:
            Flattened tensor
        """
        if x.shape.ndim <= self.start_dim:
            return x
        
        # Calculate new shape
        if self.start_dim == 0:
            # Flatten everything to 1D
            return x.flatten()
        else:
            # Keep first start_dim dimensions, flatten rest
            preserved_dims = x.shape.dims[:self.start_dim]
            flattened_size = 1
            for d in x.shape.dims[self.start_dim:]:
                flattened_size *= d
            
            new_shape = preserved_dims + (flattened_size,)
            return x.reshape(*new_shape)


class Reshape(Layer):
    """
    Reshape layer to change tensor dimensions
    """
    
    def __init__(self, *target_shape: int):
        """
        Initialize reshape layer
        
        Args:
            *target_shape: Target shape dimensions
        """
        super().__init__()
        self.target_shape = target_shape
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Reshape input tensor
        
        Args:
            x: Input tensor
            
        Returns:
            Reshaped tensor
        """
        # Handle -1 in target shape (infer dimension)
        if -1 in self.target_shape:
            if self.target_shape.count(-1) > 1:
                raise ValueError("Only one dimension can be -1")
            
            known_size = 1
            unknown_idx = -1
            for i, dim in enumerate(self.target_shape):
                if dim == -1:
                    unknown_idx = i
                else:
                    known_size *= dim
            
            inferred_dim = x.shape.size // known_size
            actual_shape = list(self.target_shape)
            actual_shape[unknown_idx] = inferred_dim
            return x.reshape(*actual_shape)
        else:
            return x.reshape(*self.target_shape)


class LayerNorm(Layer):
    """
    Layer normalization
    Normalizes across the feature dimension
    """
    
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        """
        Initialize layer normalization
        
        Args:
            normalized_shape: Size of the feature dimension to normalize
            eps: Small constant for numerical stability
        """
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        
        # Learnable parameters (initialized to 1 and 0)
        self.gamma = ones(normalized_shape)
        self.beta = zeros(normalized_shape)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply layer normalization
        
        Args:
            x: Input tensor of shape (..., normalized_shape)
            
        Returns:
            Normalized tensor
        """
        from ..math.activations import Activations
        return Activations.layer_norm(x, eps=self.eps)


class BatchNorm1d(Layer):
    """
    Batch normalization for 1D data
    Normalizes across the batch dimension
    """
    
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """
        Initialize batch normalization
        
        Args:
            num_features: Number of features (channels)
            eps: Small constant for numerical stability
            momentum: Momentum for running statistics
        """
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        
        # Learnable parameters
        self.gamma = ones(num_features)
        self.beta = zeros(num_features)
        
        # Running statistics
        self.running_mean = zeros(num_features)
        self.running_var = ones(num_features)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply batch normalization
        
        Args:
            x: Input tensor of shape (batch_size, num_features)
            
        Returns:
            Normalized tensor
        """
        from ..math.activations import Activations
        return Activations.batch_norm(x, eps=self.eps)


class Sequential(Layer):
    """
    Sequential container for layers
    Applies layers in sequence
    """
    
    def __init__(self, *layers: Layer):
        """
        Initialize sequential container
        
        Args:
            *layers: Variable number of layers to apply in sequence
        """
        super().__init__()
        self.layers = layers
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply all layers in sequence
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor after all layers
        """
        output = x
        for layer in self.layers:
            output = layer.forward(output)
        return output
    
    def train(self):
        """Set all layers to training mode"""
        super().train()
        for layer in self.layers:
            layer.train()
    
    def eval(self):
        """Set all layers to evaluation mode"""
        super().eval()
        for layer in self.layers:
            layer.eval()


__all__ = [
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
]
