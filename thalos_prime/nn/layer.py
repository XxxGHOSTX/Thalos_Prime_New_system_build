"""
THALOS Prime - Neural Network Layers Module
Base layer classes and common layer implementations.
"""

from typing import Optional, List, Tuple, Dict, Any
import math
import random
from abc import ABC, abstractmethod

# Import from math module
import sys
sys.path.insert(0, '..')
from ..math.tensor import Tensor, Shape, zeros, randn


class Layer(ABC):
    """Abstract base class for neural network layers."""
    
    def __init__(self):
        self.training = True
        self._parameters: Dict[str, Tensor] = {}
        self._buffers: Dict[str, Tensor] = {}
    
    @abstractmethod
    def forward(self, x: Tensor) -> Tensor:
        """Forward pass."""
        pass
    
    def __call__(self, *args, **kwargs) -> Tensor:
        return self.forward(*args, **kwargs)
    
    def parameters(self) -> List[Tensor]:
        """Get all trainable parameters."""
        return list(self._parameters.values())
    
    def train(self) -> 'Layer':
        """Set layer to training mode."""
        self.training = True
        return self
    
    def eval(self) -> 'Layer':
        """Set layer to evaluation mode."""
        self.training = False
        return self


class Linear(Layer):
    """Fully connected layer."""
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Xavier initialization
        std = math.sqrt(2.0 / (in_features + out_features))
        weight_data = []
        for _ in range(in_features * out_features):
            u1 = max(1e-10, random.random())
            u2 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            weight_data.append(std * z)
        
        self.weight = Tensor(weight_data, Shape((in_features, out_features)))
        self._parameters['weight'] = self.weight
        
        if bias:
            self.bias = zeros(out_features)
            self._parameters['bias'] = self.bias
        else:
            self.bias = None
    
    def forward(self, x: Tensor) -> Tensor:
        """Forward pass: y = x @ W + b."""
        # Determine input dimensions
        if x.shape.ndim == 1:
            batch_size = 1
            seq_len = len(x.data) // self.in_features
            input_data = x.data
        else:
            batch_size = x.shape.dims[0]
            seq_len = 1 if x.shape.ndim == 2 else x.shape.dims[1]
            input_data = x.data
        
        # Simple matrix multiplication
        if x.shape.ndim == 2:
            batch_size, in_feat = x.shape.dims
            output_data = []
            
            for i in range(batch_size):
                for j in range(self.out_features):
                    val = self.bias.data[j] if self.bias else 0.0
                    for k in range(self.in_features):
                        val += x.data[i * in_feat + k] * self.weight.data[k * self.out_features + j]
                    output_data.append(val)
            
            return Tensor(output_data, Shape((batch_size, self.out_features)))
        else:
            # 1D input
            output_data = []
            for j in range(self.out_features):
                val = self.bias.data[j] if self.bias else 0.0
                for k in range(min(len(x.data), self.in_features)):
                    val += x.data[k] * self.weight.data[k * self.out_features + j]
                output_data.append(val)
            return Tensor(output_data, Shape((self.out_features,)))


class Embedding(Layer):
    """Embedding layer for vocabulary lookup."""
    
    def __init__(self, num_embeddings: int, embedding_dim: int, 
                 padding_idx: Optional[int] = None):
        super().__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.padding_idx = padding_idx
        
        # Initialize embeddings
        std = 1.0 / math.sqrt(embedding_dim)
        embed_data = []
        for _ in range(num_embeddings * embedding_dim):
            u1 = max(1e-10, random.random())
            u2 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            embed_data.append(std * z)
        
        self.weight = Tensor(embed_data, Shape((num_embeddings, embedding_dim)))
        self._parameters['weight'] = self.weight
        
        # Zero out padding embedding
        if padding_idx is not None:
            for i in range(embedding_dim):
                self.weight.data[padding_idx * embedding_dim + i] = 0.0
    
    def forward(self, x: Tensor) -> Tensor:
        """Forward pass: lookup embeddings for token IDs."""
        # x contains integer token IDs
        output_data = []
        
        for idx in x.data:
            idx = int(idx)
            if 0 <= idx < self.num_embeddings:
                start = idx * self.embedding_dim
                output_data.extend(self.weight.data[start:start + self.embedding_dim])
            else:
                output_data.extend([0.0] * self.embedding_dim)
        
        seq_len = len(x.data)
        return Tensor(output_data, Shape((seq_len, self.embedding_dim)))


class PositionalEncoding(Layer):
    """Sinusoidal positional encoding."""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.0):
        super().__init__()
        self.d_model = d_model
        self.max_len = max_len
        self.dropout_rate = dropout
        
        # Compute positional encodings
        pe_data = []
        for pos in range(max_len):
            for i in range(d_model):
                if i % 2 == 0:
                    val = math.sin(pos / (10000 ** (i / d_model)))
                else:
                    val = math.cos(pos / (10000 ** ((i - 1) / d_model)))
                pe_data.append(val)
        
        self.pe = Tensor(pe_data, Shape((max_len, d_model)))
        self._buffers['pe'] = self.pe
    
    def forward(self, x: Tensor) -> Tensor:
        """Add positional encoding to input."""
        seq_len = x.shape.dims[0]
        d_model = x.shape.dims[1] if x.shape.ndim > 1 else len(x.data)
        
        output_data = []
        for i in range(seq_len):
            for j in range(d_model):
                val = x.data[i * d_model + j] + self.pe.data[i * self.d_model + j]
                
                # Apply dropout during training
                if self.training and self.dropout_rate > 0:
                    if random.random() < self.dropout_rate:
                        val = 0.0
                    else:
                        val = val / (1 - self.dropout_rate)
                
                output_data.append(val)
        
        return Tensor(output_data, Shape((seq_len, d_model)))


class Dropout(Layer):
    """Dropout regularization layer."""
    
    def __init__(self, p: float = 0.5):
        super().__init__()
        self.p = p
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply dropout during training."""
        if not self.training or self.p == 0:
            return x
        
        scale = 1.0 / (1.0 - self.p)
        output_data = []
        for val in x.data:
            if random.random() > self.p:
                output_data.append(val * scale)
            else:
                output_data.append(0.0)
        
        return Tensor(output_data, x.shape)


class Flatten(Layer):
    """Flatten layer."""
    
    def __init__(self, start_dim: int = 0, end_dim: int = -1):
        super().__init__()
        self.start_dim = start_dim
        self.end_dim = end_dim
    
    def forward(self, x: Tensor) -> Tensor:
        """Flatten tensor."""
        return Tensor(x.data.copy(), Shape((len(x.data),)))


class Reshape(Layer):
    """Reshape layer."""
    
    def __init__(self, shape: Tuple[int, ...]):
        super().__init__()
        self.shape = shape
    
    def forward(self, x: Tensor) -> Tensor:
        """Reshape tensor."""
        return x.reshape(self.shape)


class LayerNormLayer(Layer):
    """Layer normalization as a layer."""
    
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.gamma = Tensor([1.0] * normalized_shape)
        self.beta = Tensor([0.0] * normalized_shape)
        self._parameters['gamma'] = self.gamma
        self._parameters['beta'] = self.beta
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply layer normalization."""
        if x.shape.ndim == 1:
            mean = sum(x.data) / len(x.data)
            var = sum((val - mean) ** 2 for val in x.data) / len(x.data)
            std = math.sqrt(var + self.eps)
            return Tensor([(val - mean) / std * g + b 
                          for val, g, b in zip(x.data, self.gamma.data, self.beta.data)],
                         x.shape)
        elif x.shape.ndim == 2:
            rows, cols = x.shape.dims
            result = []
            for i in range(rows):
                row = [x.data[i * cols + j] for j in range(cols)]
                mean = sum(row) / len(row)
                var = sum((val - mean) ** 2 for val in row) / len(row)
                std = math.sqrt(var + self.eps)
                result.extend([(val - mean) / std * g + b 
                              for val, g, b in zip(row, self.gamma.data, self.beta.data)])
            return Tensor(result, x.shape)
        return x


class Sequential(Layer):
    """Sequential container for layers."""
    
    def __init__(self, *layers: Layer):
        super().__init__()
        self.layers = list(layers)
    
    def forward(self, x: Tensor) -> Tensor:
        """Forward through all layers."""
        for layer in self.layers:
            x = layer(x)
        return x
    
    def add(self, layer: Layer) -> 'Sequential':
        """Add a layer."""
        self.layers.append(layer)
        return self
    
    def parameters(self) -> List[Tensor]:
        """Get all parameters from all layers."""
        params = []
        for layer in self.layers:
            params.extend(layer.parameters())
        return params
    
    def train(self) -> 'Sequential':
        """Set all layers to training mode."""
        self.training = True
        for layer in self.layers:
            layer.train()
        return self
    
    def eval(self) -> 'Sequential':
        """Set all layers to evaluation mode."""
        self.training = False
        for layer in self.layers:
            layer.eval()
        return self
