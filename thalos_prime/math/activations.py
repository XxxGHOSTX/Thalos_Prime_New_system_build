"""
THALOS Prime - Activation Functions Module
Neural network activation functions and normalizations.
"""

from typing import Optional
import math
from .tensor import Tensor, Shape


class Activations:
    """Collection of activation functions."""
    
    @staticmethod
    def relu(x: Tensor) -> Tensor:
        """Rectified Linear Unit."""
        return Tensor([max(0, val) for val in x.data], x.shape)
    
    @staticmethod
    def relu_derivative(x: Tensor) -> Tensor:
        """ReLU derivative."""
        return Tensor([1.0 if val > 0 else 0.0 for val in x.data], x.shape)
    
    @staticmethod
    def leaky_relu(x: Tensor, alpha: float = 0.01) -> Tensor:
        """Leaky ReLU with negative slope alpha."""
        return Tensor([val if val > 0 else alpha * val for val in x.data], x.shape)
    
    @staticmethod
    def leaky_relu_derivative(x: Tensor, alpha: float = 0.01) -> Tensor:
        """Leaky ReLU derivative."""
        return Tensor([1.0 if val > 0 else alpha for val in x.data], x.shape)
    
    @staticmethod
    def sigmoid(x: Tensor) -> Tensor:
        """Sigmoid activation."""
        def safe_sigmoid(val):
            if val >= 0:
                return 1.0 / (1.0 + math.exp(-val))
            else:
                exp_val = math.exp(val)
                return exp_val / (1.0 + exp_val)
        return Tensor([safe_sigmoid(val) for val in x.data], x.shape)
    
    @staticmethod
    def sigmoid_derivative(x: Tensor) -> Tensor:
        """Sigmoid derivative: s(x) * (1 - s(x))."""
        s = Activations.sigmoid(x)
        return Tensor([val * (1 - val) for val in s.data], x.shape)
    
    @staticmethod
    def tanh(x: Tensor) -> Tensor:
        """Hyperbolic tangent."""
        return Tensor([math.tanh(val) for val in x.data], x.shape)
    
    @staticmethod
    def tanh_derivative(x: Tensor) -> Tensor:
        """Tanh derivative: 1 - tanh(x)^2."""
        t = Activations.tanh(x)
        return Tensor([1 - val ** 2 for val in t.data], x.shape)
    
    @staticmethod
    def gelu(x: Tensor) -> Tensor:
        """Gaussian Error Linear Unit."""
        def gelu_val(val):
            return 0.5 * val * (1 + math.tanh(math.sqrt(2 / math.pi) * (val + 0.044715 * val ** 3)))
        return Tensor([gelu_val(val) for val in x.data], x.shape)
    
    @staticmethod
    def swish(x: Tensor, beta: float = 1.0) -> Tensor:
        """Swish activation: x * sigmoid(beta * x)."""
        def safe_sigmoid(val):
            if val >= 0:
                return 1.0 / (1.0 + math.exp(-val))
            else:
                exp_val = math.exp(val)
                return exp_val / (1.0 + exp_val)
        return Tensor([val * safe_sigmoid(beta * val) for val in x.data], x.shape)
    
    @staticmethod
    def elu(x: Tensor, alpha: float = 1.0) -> Tensor:
        """Exponential Linear Unit."""
        return Tensor([val if val > 0 else alpha * (math.exp(val) - 1) for val in x.data], x.shape)
    
    @staticmethod
    def elu_derivative(x: Tensor, alpha: float = 1.0) -> Tensor:
        """ELU derivative."""
        return Tensor([1.0 if val > 0 else alpha * math.exp(val) for val in x.data], x.shape)
    
    @staticmethod
    def selu(x: Tensor) -> Tensor:
        """Scaled Exponential Linear Unit."""
        alpha = 1.6732632423543772848170429916717
        scale = 1.0507009873554804934193349852946
        return Tensor([scale * (val if val > 0 else alpha * (math.exp(val) - 1)) 
                       for val in x.data], x.shape)
    
    @staticmethod
    def softplus(x: Tensor) -> Tensor:
        """Softplus: log(1 + exp(x))."""
        def safe_softplus(val):
            if val > 20:
                return val
            return math.log(1 + math.exp(val))
        return Tensor([safe_softplus(val) for val in x.data], x.shape)
    
    @staticmethod
    def softmax(x: Tensor, dim: int = -1) -> Tensor:
        """Softmax activation along dimension."""
        if x.shape.ndim == 1:
            max_val = max(x.data)
            exp_vals = [math.exp(val - max_val) for val in x.data]
            sum_exp = sum(exp_vals)
            return Tensor([val / sum_exp for val in exp_vals], x.shape)
        
        elif x.shape.ndim == 2:
            if dim == -1 or dim == 1:
                # Softmax along last dimension (rows)
                rows, cols = x.shape.dims
                result = []
                for i in range(rows):
                    row = [x.data[i * cols + j] for j in range(cols)]
                    max_val = max(row)
                    exp_vals = [math.exp(val - max_val) for val in row]
                    sum_exp = sum(exp_vals)
                    result.extend([val / sum_exp for val in exp_vals])
                return Tensor(result, x.shape)
            else:
                # Softmax along first dimension (columns)
                rows, cols = x.shape.dims
                result = [0.0] * (rows * cols)
                for j in range(cols):
                    col = [x.data[i * cols + j] for i in range(rows)]
                    max_val = max(col)
                    exp_vals = [math.exp(val - max_val) for val in col]
                    sum_exp = sum(exp_vals)
                    for i in range(rows):
                        result[i * cols + j] = exp_vals[i] / sum_exp
                return Tensor(result, x.shape)
        else:
            raise ValueError("Softmax currently supports 1D and 2D tensors")
    
    @staticmethod
    def log_softmax(x: Tensor, dim: int = -1) -> Tensor:
        """Log-softmax for numerical stability."""
        if x.shape.ndim == 1:
            max_val = max(x.data)
            log_sum_exp = max_val + math.log(sum(math.exp(val - max_val) for val in x.data))
            return Tensor([val - log_sum_exp for val in x.data], x.shape)
        elif x.shape.ndim == 2:
            rows, cols = x.shape.dims
            result = []
            for i in range(rows):
                row = [x.data[i * cols + j] for j in range(cols)]
                max_val = max(row)
                log_sum_exp = max_val + math.log(sum(math.exp(val - max_val) for val in row))
                result.extend([val - log_sum_exp for val in row])
            return Tensor(result, x.shape)
        else:
            raise ValueError("Log-softmax currently supports 1D and 2D tensors")


class LayerNorm:
    """Layer Normalization."""
    
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.gamma = Tensor([1.0] * normalized_shape)
        self.beta = Tensor([0.0] * normalized_shape)
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply layer normalization."""
        if x.shape.ndim == 1:
            mean = sum(x.data) / len(x.data)
            var = sum((val - mean) ** 2 for val in x.data) / len(x.data)
            std = math.sqrt(var + self.eps)
            normalized = [(val - mean) / std for val in x.data]
            return Tensor([n * g + b for n, g, b in zip(normalized, self.gamma.data, self.beta.data)],
                         x.shape)
        elif x.shape.ndim == 2:
            rows, cols = x.shape.dims
            result = []
            for i in range(rows):
                row = [x.data[i * cols + j] for j in range(cols)]
                mean = sum(row) / len(row)
                var = sum((val - mean) ** 2 for val in row) / len(row)
                std = math.sqrt(var + self.eps)
                normalized = [(val - mean) / std for val in row]
                result.extend([n * g + b for n, g, b in zip(normalized, self.gamma.data, self.beta.data)])
            return Tensor(result, x.shape)
        else:
            raise ValueError("LayerNorm currently supports 1D and 2D tensors")
    
    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


class BatchNorm:
    """Batch Normalization."""
    
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.gamma = Tensor([1.0] * num_features)
        self.beta = Tensor([0.0] * num_features)
        self.running_mean = Tensor([0.0] * num_features)
        self.running_var = Tensor([1.0] * num_features)
        self.training = True
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply batch normalization."""
        if x.shape.ndim != 2:
            raise ValueError("BatchNorm expects 2D input (batch, features)")
        
        batch_size, features = x.shape.dims
        
        if self.training:
            # Compute batch statistics
            means = []
            vars_ = []
            for j in range(features):
                col = [x.data[i * features + j] for i in range(batch_size)]
                mean = sum(col) / len(col)
                var = sum((val - mean) ** 2 for val in col) / len(col)
                means.append(mean)
                vars_.append(var)
            
            # Update running statistics
            for j in range(features):
                self.running_mean.data[j] = (1 - self.momentum) * self.running_mean.data[j] + self.momentum * means[j]
                self.running_var.data[j] = (1 - self.momentum) * self.running_var.data[j] + self.momentum * vars_[j]
        else:
            means = self.running_mean.data
            vars_ = self.running_var.data
        
        # Normalize
        result = []
        for i in range(batch_size):
            for j in range(features):
                val = x.data[i * features + j]
                normalized = (val - means[j]) / math.sqrt(vars_[j] + self.eps)
                result.append(normalized * self.gamma.data[j] + self.beta.data[j])
        
        return Tensor(result, x.shape)
    
    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)
    
    def eval(self):
        self.training = False
        return self
    
    def train(self):
        self.training = True
        return self


class RMSNorm:
    """Root Mean Square Layer Normalization."""
    
    def __init__(self, normalized_shape: int, eps: float = 1e-6):
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.weight = Tensor([1.0] * normalized_shape)
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply RMS normalization."""
        if x.shape.ndim == 1:
            rms = math.sqrt(sum(val ** 2 for val in x.data) / len(x.data) + self.eps)
            return Tensor([val / rms * w for val, w in zip(x.data, self.weight.data)], x.shape)
        elif x.shape.ndim == 2:
            rows, cols = x.shape.dims
            result = []
            for i in range(rows):
                row = [x.data[i * cols + j] for j in range(cols)]
                rms = math.sqrt(sum(val ** 2 for val in row) / len(row) + self.eps)
                result.extend([val / rms * w for val, w in zip(row, self.weight.data)])
            return Tensor(result, x.shape)
        else:
            raise ValueError("RMSNorm currently supports 1D and 2D tensors")
    
    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)
