"""
Tensor implementation for THALOS Prime
"""
import random
import math
from typing import List, Tuple, Union


class Shape:
    """Shape class for dimension management"""
    def __init__(self, *dims):
        self.dims = tuple(dims)
    
    def __repr__(self):
        return f"Shape{self.dims}"
    
    def __str__(self):
        return str(self.dims)
    
    def __eq__(self, other):
        if isinstance(other, Shape):
            return self.dims == other.dims
        return self.dims == other


class Tensor:
    """Basic Tensor implementation"""
    def __init__(self, data, shape=None):
        if isinstance(data, (list, tuple)):
            self.data = self._flatten(data)
            if shape is None:
                shape = self._infer_shape(data)
        else:
            self.data = data if isinstance(data, list) else [data]
            if shape is None:
                shape = (len(self.data),)
        
        if isinstance(shape, tuple):
            self.shape = Shape(*shape)
        elif isinstance(shape, Shape):
            self.shape = shape
        else:
            self.shape = Shape(shape)
    
    def _flatten(self, data):
        """Flatten nested lists"""
        if not isinstance(data, (list, tuple)):
            return [data]
        result = []
        for item in data:
            if isinstance(item, (list, tuple)):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result
    
    def _infer_shape(self, data):
        """Infer shape from nested lists"""
        if not isinstance(data, (list, tuple)):
            return ()
        shape = [len(data)]
        if len(data) > 0 and isinstance(data[0], (list, tuple)):
            inner_shape = self._infer_shape(data[0])
            if isinstance(inner_shape, (list, tuple)):
                shape.extend(inner_shape)
        return tuple(shape)
    
    def __repr__(self):
        return f"Tensor(shape={self.shape}, data={self.data[:5]}...)" if len(self.data) > 5 else f"Tensor(shape={self.shape}, data={self.data})"
    
    def __add__(self, other):
        if isinstance(other, Tensor):
            result_data = [a + b for a, b in zip(self.data, other.data)]
        else:
            result_data = [a + other for a in self.data]
        return Tensor(result_data, self.shape)
    
    def __sub__(self, other):
        if isinstance(other, Tensor):
            result_data = [a - b for a, b in zip(self.data, other.data)]
        else:
            result_data = [a - other for a in self.data]
        return Tensor(result_data, self.shape)
    
    def __mul__(self, other):
        if isinstance(other, Tensor):
            result_data = [a * b for a, b in zip(self.data, other.data)]
        else:
            result_data = [a * other for a in self.data]
        return Tensor(result_data, self.shape)
    
    def reshape(self, *new_shape):
        """Reshape tensor"""
        return Tensor(self.data, new_shape)
    
    def flatten(self):
        """Flatten tensor to 1D"""
        return Tensor(self.data, (len(self.data),))


def randn(*dims):
    """Create tensor with random normal values"""
    size = 1
    for d in dims:
        size *= d
    # Box-Muller transform for normal distribution
    data = []
    for _ in range(size):
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        data.append(z)
    return Tensor(data, dims)


def zeros(*dims):
    """Create tensor of zeros"""
    size = 1
    for d in dims:
        size *= d
    return Tensor([0.0] * size, dims)


def ones(*dims):
    """Create tensor of ones"""
    size = 1
    for d in dims:
        size *= d
    return Tensor([1.0] * size, dims)
