#!/usr/bin/env python3
"""
THALOS Prime Activations Module
Pure Python implementation of activation functions and normalization
"""

import math
from typing import Optional
from .tensor import Tensor, zeros


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
            val = max(-500, min(500, val))
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
        
        # For 2D case (most common in neural networks)
        if x.shape.ndim == 2:
            if axis == 1:
                # Softmax along last dimension (each row independently)
                rows, cols = x.shape.dims
                result = []
                for i in range(rows):
                    row_data = [x.data[i * cols + j] for j in range(cols)]
                    max_val = max(row_data)
                    exp_vals = [math.exp(val - max_val) for val in row_data]
                    sum_exp = sum(exp_vals)
                    result.extend([val / sum_exp for val in exp_vals])
                
                from .tensor import Shape
                return Tensor(result, Shape(rows, cols))
            elif axis == 0:
                # Softmax along first dimension (each column independently)
                rows, cols = x.shape.dims
                result = [0.0] * (rows * cols)
                for j in range(cols):
                    col_data = [x.data[i * cols + j] for i in range(rows)]
                    max_val = max(col_data)
                    exp_vals = [math.exp(val - max_val) for val in col_data]
                    sum_exp = sum(exp_vals)
                    for i in range(rows):
                        result[i * cols + j] = exp_vals[i] / sum_exp
                
                from .tensor import Shape
                return Tensor(result, Shape(rows, cols))
        
        # General case: treat as 1D
        max_val = max(x.data)
        exp_vals = [math.exp(val - max_val) for val in x.data]
        sum_exp = sum(exp_vals)
        return Tensor([val / sum_exp for val in exp_vals], x.shape)
    
    @staticmethod
    def softmax_derivative(x: Tensor) -> Tensor:
        """
        Derivative of softmax (Jacobian diagonal approximation)
        For efficiency, returns element-wise: softmax(x) * (1 - softmax(x))
        """
        sm = Activations.softmax(x)
        return sm * (1.0 - sm)
    
    @staticmethod
    def log_softmax(x: Tensor, axis: int = -1) -> Tensor:
        """Log-softmax for numerical stability"""
        if axis < 0:
            axis = x.shape.ndim + axis
        
        # For 1D case
        if x.shape.ndim == 1 or axis == x.shape.ndim - 1:
            max_val = max(x.data)
            log_sum_exp = math.log(sum(math.exp(val - max_val) for val in x.data))
            return Tensor([val - max_val - log_sum_exp for val in x.data], x.shape)
        
        # For 2D case
        if x.shape.ndim == 2:
            rows, cols = x.shape.dims
            if axis == 1:
                result = []
                for i in range(rows):
                    row_data = [x.data[i * cols + j] for j in range(cols)]
                    max_val = max(row_data)
                    log_sum_exp = math.log(sum(math.exp(val - max_val) for val in row_data))
                    result.extend([val - max_val - log_sum_exp for val in row_data])
                
                from .tensor import Shape
                return Tensor(result, Shape(rows, cols))
        
        # Fallback
        return Activations.softmax(x, axis)
    
    @staticmethod
    def layer_norm(x: Tensor, eps: float = 1e-5) -> Tensor:
        """
        Layer normalization: normalize across features
        
        Args:
            x: Input tensor
            eps: Small constant for numerical stability
        """
        # Compute mean and std
        mean = x.mean()
        
        # Compute variance
        centered = x - mean
        variance = (centered * centered).mean()
        std = math.sqrt(variance + eps)
        
        # Normalize
        return centered / std
    
    @staticmethod
    def batch_norm(x: Tensor, eps: float = 1e-5, axis: int = 0) -> Tensor:
        """
        Batch normalization: normalize across batch dimension
        
        Args:
            x: Input tensor (batch_size, features)
            eps: Small constant for numerical stability
            axis: Batch axis (default: 0)
        """
        if x.shape.ndim == 1:
            # Single dimension - just do layer norm
            return Activations.layer_norm(x, eps)
        
        if x.shape.ndim == 2:
            rows, cols = x.shape.dims
            
            if axis == 0:
                # Normalize each feature across batch
                result = []
                for j in range(cols):
                    # Extract column
                    col_data = [x.data[i * cols + j] for i in range(rows)]
                    
                    # Compute mean and std
                    mean = sum(col_data) / len(col_data)
                    variance = sum((val - mean) ** 2 for val in col_data) / len(col_data)
                    std = math.sqrt(variance + eps)
                    
                    # Normalize
                    normalized = [(val - mean) / std for val in col_data]
                    result.append(normalized)
                
                # Reconstruct tensor
                final_data = []
                for i in range(rows):
                    for j in range(cols):
                        final_data.append(result[j][i])
                
                from .tensor import Shape
                return Tensor(final_data, Shape(rows, cols))
            else:
                # Normalize each sample
                result = []
                for i in range(rows):
                    row_data = [x.data[i * cols + j] for j in range(cols)]
                    
                    mean = sum(row_data) / len(row_data)
                    variance = sum((val - mean) ** 2 for val in row_data) / len(row_data)
                    std = math.sqrt(variance + eps)
                    
                    normalized = [(val - mean) / std for val in row_data]
                    result.extend(normalized)
                
                from .tensor import Shape
                return Tensor(result, Shape(rows, cols))
        
        # Fallback to layer norm
        return Activations.layer_norm(x, eps)
    
    @staticmethod
    def selu(x: Tensor) -> Tensor:
        """
        SELU activation (Scaled Exponential Linear Unit)
        alpha ≈ 1.6733, lambda ≈ 1.0507
        """
        alpha = 1.6732632423543772848170429916717
        scale = 1.0507009873554804934193349852946
        
        def _selu(val):
            if val > 0:
                return scale * val
            return scale * alpha * (math.exp(val) - 1.0)
        
        return Tensor([_selu(val) for val in x.data], x.shape)
    
    @staticmethod
    def softplus(x: Tensor) -> Tensor:
        """Softplus activation: log(1 + exp(x))"""
        def _softplus(val):
            # Numerical stability
            if val > 20:
                return val
            return math.log(1.0 + math.exp(val))
        
        return Tensor([_softplus(val) for val in x.data], x.shape)
    
    @staticmethod
    def mish(x: Tensor) -> Tensor:
        """Mish activation: x * tanh(softplus(x))"""
        softplus_x = Activations.softplus(x)
        tanh_softplus = Activations.tanh(softplus_x)
        return x * tanh_softplus
