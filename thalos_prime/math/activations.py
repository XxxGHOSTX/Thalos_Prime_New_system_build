"""
Activation functions for THALOS Prime
"""
import math
from .tensor import Tensor


class Activations:
    """Activation functions"""
    
    @staticmethod
    def relu(x):
        """ReLU activation"""
        if isinstance(x, Tensor):
            result_data = [max(0, val) for val in x.data]
            return Tensor(result_data, x.shape)
        return max(0, x)
    
    @staticmethod
    def sigmoid(x):
        """Sigmoid activation"""
        if isinstance(x, Tensor):
            result_data = [1 / (1 + math.exp(-val)) for val in x.data]
            return Tensor(result_data, x.shape)
        return 1 / (1 + math.exp(-x))
    
    @staticmethod
    def tanh(x):
        """Tanh activation"""
        if isinstance(x, Tensor):
            result_data = [math.tanh(val) for val in x.data]
            return Tensor(result_data, x.shape)
        return math.tanh(x)
    
    @staticmethod
    def softmax(x):
        """Softmax activation"""
        if isinstance(x, Tensor):
            exp_values = [math.exp(val) for val in x.data]
            sum_exp = sum(exp_values)
            result_data = [val / sum_exp for val in exp_values]
            return Tensor(result_data, x.shape)
        return x
