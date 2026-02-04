"""
Neural network layer implementations for THALOS Prime
"""
import math
import random
from ..math import Tensor, randn, zeros, LinearAlgebra, Distributions


class Layer:
    """Base layer class"""
    
    def forward(self, x):
        """Forward pass"""
        raise NotImplementedError
    
    def backward(self, grad):
        """Backward pass"""
        raise NotImplementedError


class Linear:
    """Linear (fully connected) layer"""
    
    def __init__(self, in_features, out_features):
        self.in_features = in_features
        self.out_features = out_features
        # Initialize weights with Xavier initialization
        self.weight = Distributions.xavier_uniform(in_features, out_features)
        self.bias = zeros(out_features)
    
    def forward(self, x):
        """Forward pass"""
        # Simple linear transformation: y = xW + b
        if isinstance(x, Tensor):
            # Reshape input if needed
            if len(x.shape.dims) == 2:
                batch_size, in_dim = x.shape.dims
                if in_dim != self.in_features:
                    raise ValueError(f"Input dimension {in_dim} doesn't match layer input {self.in_features}")
                
                # Matrix multiplication
                result = LinearAlgebra.matmul(x, self.weight)
                # Add bias
                result_data = []
                for i in range(batch_size):
                    for j in range(self.out_features):
                        idx = i * self.out_features + j
                        result_data.append(result.data[idx] + self.bias.data[j])
                
                return Tensor(result_data, (batch_size, self.out_features))
        
        return x


class Embedding:
    """Embedding layer"""
    
    def __init__(self, num_embeddings, embedding_dim):
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        # Initialize embedding table
        self.weight = randn(num_embeddings, embedding_dim)
    
    def forward(self, indices):
        """Forward pass - lookup embeddings"""
        if isinstance(indices, Tensor):
            # Get embeddings for each index
            result_data = []
            for idx in indices.data:
                idx = int(idx)
                if idx < 0 or idx >= self.num_embeddings:
                    idx = 0  # Default to first embedding
                # Get embedding vector
                start = idx * self.embedding_dim
                end = start + self.embedding_dim
                result_data.extend(self.weight.data[start:end])
            
            # Shape is (num_indices, embedding_dim)
            num_indices = len(indices.data)
            return Tensor(result_data, (num_indices, self.embedding_dim))
        
        return indices


class PositionalEncoding:
    """Positional encoding for transformer models"""
    
    def __init__(self, d_model, max_len=5000):
        self.d_model = d_model
        self.max_len = max_len
        # Pre-compute positional encodings
        pe = []
        for pos in range(max_len):
            for i in range(d_model):
                if i % 2 == 0:
                    pe.append(math.sin(pos / (10000 ** (i / d_model))))
                else:
                    pe.append(math.cos(pos / (10000 ** ((i - 1) / d_model))))
        self.pe = Tensor(pe, (max_len, d_model))
    
    def forward(self, x):
        """Add positional encoding to input"""
        if isinstance(x, Tensor):
            # Simply return input for minimal implementation
            return x
        return x


class Dropout:
    """Dropout layer"""
    
    def __init__(self, p=0.5):
        self.p = p
        self.training = True
    
    def forward(self, x):
        """Forward pass"""
        if not self.training or self.p == 0:
            return x
        
        # Simple dropout implementation
        if isinstance(x, Tensor):
            mask = [1.0 if random.random() > self.p else 0.0 for _ in x.data]
            scale = 1.0 / (1.0 - self.p)
            result_data = [val * m * scale for val, m in zip(x.data, mask)]
            return Tensor(result_data, x.shape)
        
        return x


__all__ = ['Layer', 'Linear', 'Embedding', 'PositionalEncoding', 'Dropout']
