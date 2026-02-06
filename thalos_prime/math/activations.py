#!/usr/bin/env python3
"""
THALOS Prime Activations Module
Pure Python implementation of activation functions and normalization
"""

import math
from typing import Optional
from .tensor import Tensor, zeros

# Constants for numerical stability
SIGMOID_CLIP_MIN = -500
SIGMOID_CLIP_MAX = 500


class Activations:
    """Collection of activation functions"""
    
    @staticmethod
    def relu(x: Tensor) -> Tensor:
        """ReLU activation: max(0, x)"""
        return Tensor([max(0.0, val) for val in x.data], x.shape)
    
    @staticmethod
    def relu_derivative(x: Tensor) -> Tensor:
        """Derivative of ReLU"""
        return Tensor([1.0 if val > 0 else 0.0 for val in x.data], x.shape)
    
    @staticmethod
    def leaky_relu(x: Tensor, alpha: float = 0.01) -> Tensor:
        """Leaky ReLU: max(alpha*x, x)"""
        return Tensor([val if val > 0 else alpha * val for val in x.data], x.shape)
    
    @staticmethod
    def leaky_relu_derivative(x: Tensor, alpha: float = 0.01) -> Tensor:
        """Derivative of Leaky ReLU"""
        return Tensor([1.0 if val > 0 else alpha for val in x.data], x.shape)
    
    @staticmethod
    def sigmoid(x: Tensor) -> Tensor:
        """Sigmoid activation: 1 / (1 + exp(-x))"""
        def _sigmoid(val):
            # Clip to prevent overflow
            val = max(SIGMOID_CLIP_MIN, min(SIGMOID_CLIP_MAX, val))
            return 1.0 / (1.0 + math.exp(-val))
        
        return Tensor([_sigmoid(val) for val in x.data], x.shape)
    
    @staticmethod
    def sigmoid_derivative(x: Tensor) -> Tensor:
        """Derivative of sigmoid: sigmoid(x) * (1 - sigmoid(x))"""
        sig = Activations.sigmoid(x)
        return sig * (1.0 - sig)
    
    @staticmethod
    def tanh(x: Tensor) -> Tensor:
        """Tanh activation"""
        return Tensor([math.tanh(val) for val in x.data], x.shape)
    
    @staticmethod
    def tanh_derivative(x: Tensor) -> Tensor:
        """Derivative of tanh: 1 - tanh(x)^2"""
        tanh_x = Activations.tanh(x)
        return 1.0 - (tanh_x * tanh_x)
    
    @staticmethod
    def gelu(x: Tensor) -> Tensor:
        """
        GELU activation (Gaussian Error Linear Unit)
        Approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        """
        def _gelu(val):
            # GELU approximation
            coef = math.sqrt(2.0 / math.pi)
            inner = coef * (val + 0.044715 * val ** 3)
            return 0.5 * val * (1.0 + math.tanh(inner))
        
        return Tensor([_gelu(val) for val in x.data], x.shape)
    
    @staticmethod
    def gelu_derivative(x: Tensor) -> Tensor:
        """Derivative of GELU (approximation)"""
        def _gelu_deriv(val):
            coef = math.sqrt(2.0 / math.pi)
            inner = coef * (val + 0.044715 * val ** 3)
            tanh_inner = math.tanh(inner)
            sech_squared = 1.0 - tanh_inner ** 2
            
            dinput = coef * (1.0 + 3.0 * 0.044715 * val ** 2)
            
            return 0.5 * (1.0 + tanh_inner) + 0.5 * val * sech_squared * dinput
        
        return Tensor([_gelu_deriv(val) for val in x.data], x.shape)
    
    @staticmethod
    def swish(x: Tensor, beta: float = 1.0) -> Tensor:
        """Swish activation: x * sigmoid(beta * x)"""
        sigmoid_x = Activations.sigmoid(x * beta)
        return x * sigmoid_x
    
    @staticmethod
    def swish_derivative(x: Tensor, beta: float = 1.0) -> Tensor:
        """Derivative of Swish"""
        sigmoid_x = Activations.sigmoid(x * beta)
        return sigmoid_x + x * beta * sigmoid_x * (1.0 - sigmoid_x)
    
    @staticmethod
    def elu(x: Tensor, alpha: float = 1.0) -> Tensor:
        """
        ELU activation (Exponential Linear Unit)
        f(x) = x if x > 0 else alpha * (exp(x) - 1)
        """
        def _elu(val):
            if val > 0:
                return val
            return alpha * (math.exp(val) - 1.0)
        
        return Tensor([_elu(val) for val in x.data], x.shape)
    
    @staticmethod
    def elu_derivative(x: Tensor, alpha: float = 1.0) -> Tensor:
        """Derivative of ELU"""
        def _elu_deriv(val):
            if val > 0:
                return 1.0
            return alpha * math.exp(val)
        
        return Tensor([_elu_deriv(val) for val in x.data], x.shape)
    
    @staticmethod
    def softmax(x: Tensor, axis: int = -1) -> Tensor:
        """
        Softmax activation with numerical stability
        
        Args:
            x: Input tensor
            axis: Axis along which to apply softmax (default: last axis)
        """
        if axis < 0:
            axis = x.shape.ndim + axis
        
        # For 1D case
        if x.shape.ndim == 1:
            # Subtract max for numerical stability
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
