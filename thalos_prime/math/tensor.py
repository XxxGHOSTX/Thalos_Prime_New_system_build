#!/usr/bin/env python3
"""
THALOS Prime Tensor Module
Pure Python implementation of N-dimensional tensor operations
"""

import math
import random
from typing import Union, List, Tuple, Optional, Callable


class Shape:
    """Represents the shape of a tensor"""
    
    def __init__(self, *dims: int):
        """
        Initialize shape with dimensions
        
        Args:
            *dims: Variable number of dimension sizes
        """
        self.dims = tuple(dims)
    
    @property
    def ndim(self) -> int:
        """Number of dimensions"""
        return len(self.dims)
    
    @property
    def size(self) -> int:
        """Total number of elements"""
        result = 1
        for d in self.dims:
            result *= d
        return result
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Shape):
            return self.dims == other.dims
        return self.dims == tuple(other)
    
    def __repr__(self) -> str:
        return f"Shape{self.dims}"
    
    def __str__(self) -> str:
        return str(self.dims)
    
    def __getitem__(self, idx: int) -> int:
        return self.dims[idx]
    
    def __len__(self) -> int:
        return len(self.dims)


class Tensor:
    """N-dimensional tensor with operations"""
    
    def __init__(self, data: Union[List, float, int], shape: Optional[Shape] = None):
        """
        Initialize tensor from data
        
        Args:
            data: Nested list or scalar value
            shape: Optional shape specification
        """
        if isinstance(data, (int, float)):
            self.data = [float(data)]
            self.shape = Shape(1) if shape is None else shape
        elif isinstance(data, list):
            self.data = self._flatten(data)
            if shape is None:
                inferred_shape = self._infer_shape(data)
                self.shape = Shape(*inferred_shape)
            else:
                self.shape = shape
                if len(self.data) != shape.size:
                    raise ValueError(f"Data size {len(self.data)} doesn't match shape size {shape.size}")
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
    
    def _flatten(self, data: Union[List, float, int]) -> List[float]:
        """Recursively flatten nested lists"""
        if isinstance(data, (int, float)):
            return [float(data)]
        
        result = []
        for item in data:
            if isinstance(item, list):
                result.extend(self._flatten(item))
            else:
                result.append(float(item))
        return result
    
    def _infer_shape(self, data: Union[List, float, int]) -> List[int]:
        """Infer shape from nested list structure"""
        if isinstance(data, (int, float)):
            return []
        
        if not isinstance(data, list):
            return []
        
        if len(data) == 0:
            return [0]
        
        shape = [len(data)]
        if isinstance(data[0], list):
            shape.extend(self._infer_shape(data[0]))
        
        return shape
    
    def _get_strides(self) -> Tuple[int, ...]:
        """Calculate strides for indexing"""
        strides = []
        stride = 1
        for dim in reversed(self.shape.dims):
            strides.append(stride)
            stride *= dim
        return tuple(reversed(strides))
    
    def _multi_index_to_flat(self, indices: Tuple[int, ...]) -> int:
        """Convert multi-dimensional index to flat index"""
        strides = self._get_strides()
        flat_idx = 0
        for idx, stride in zip(indices, strides):
            flat_idx += idx * stride
        return flat_idx
    
    def _flat_to_multi_index(self, flat_idx: int) -> Tuple[int, ...]:
        """Convert flat index to multi-dimensional index"""
        indices = []
        for dim in reversed(self.shape.dims):
            indices.append(flat_idx % dim)
            flat_idx //= dim
        return tuple(reversed(indices))
    
    def get(self, *indices: int) -> float:
        """Get value at multi-dimensional index"""
        if len(indices) != self.shape.ndim:
            raise ValueError(f"Expected {self.shape.ndim} indices, got {len(indices)}")
        flat_idx = self._multi_index_to_flat(indices)
        return self.data[flat_idx]
    
    def set(self, *args) -> None:
        """Set value at multi-dimensional index"""
        *indices, value = args
        if len(indices) != self.shape.ndim:
            raise ValueError(f"Expected {self.shape.ndim} indices, got {len(indices)}")
        flat_idx = self._multi_index_to_flat(tuple(indices))
        self.data[flat_idx] = float(value)
    
    def reshape(self, *new_shape: int) -> 'Tensor':
        """Reshape tensor to new dimensions"""
        new_size = 1
        for d in new_shape:
            new_size *= d
        
        if new_size != self.shape.size:
            raise ValueError(f"Cannot reshape tensor of size {self.shape.size} to {new_shape}")
        
        return Tensor(self.data.copy(), Shape(*new_shape))
    
    def flatten(self) -> 'Tensor':
        """Flatten tensor to 1D"""
        return self.reshape(self.shape.size)
    
    def transpose(self, dim0: int = 0, dim1: int = 1) -> 'Tensor':
        """Transpose two dimensions"""
        if self.shape.ndim < 2:
            return Tensor(self.data.copy(), self.shape)
        
        # For 2D case
        if self.shape.ndim == 2:
            rows, cols = self.shape.dims
            new_data = [0.0] * self.shape.size
            for i in range(rows):
                for j in range(cols):
                    new_data[j * rows + i] = self.data[i * cols + j]
            return Tensor(new_data, Shape(cols, rows))
        
        # General case
        new_dims = list(self.shape.dims)
        new_dims[dim0], new_dims[dim1] = new_dims[dim1], new_dims[dim0]
        
        new_data = [0.0] * self.shape.size
        for flat_idx in range(self.shape.size):
            old_indices = list(self._flat_to_multi_index(flat_idx))
            old_indices[dim0], old_indices[dim1] = old_indices[dim1], old_indices[dim0]
            
            # Create temporary tensor with new shape to calculate new flat index
            temp = Tensor([0.0] * self.shape.size, Shape(*new_dims))
            new_flat_idx = temp._multi_index_to_flat(tuple(old_indices))
            new_data[new_flat_idx] = self.data[flat_idx]
        
        return Tensor(new_data, Shape(*new_dims))
    
    def __add__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        """Element-wise addition"""
        if isinstance(other, (int, float)):
            return Tensor([x + other for x in self.data], self.shape)
        
        if not isinstance(other, Tensor):
            raise TypeError(f"Unsupported type for addition: {type(other)}")
        
        if self.shape != other.shape:
            return self._broadcast_op(other, lambda x, y: x + y)
        
        result_data = [x + y for x, y in zip(self.data, other.data)]
        return Tensor(result_data, self.shape)
    
    def __sub__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        """Element-wise subtraction"""
        if isinstance(other, (int, float)):
            return Tensor([x - other for x in self.data], self.shape)
        
        if not isinstance(other, Tensor):
            raise TypeError(f"Unsupported type for subtraction: {type(other)}")
        
        if self.shape != other.shape:
            return self._broadcast_op(other, lambda x, y: x - y)
        
        result_data = [x - y for x, y in zip(self.data, other.data)]
        return Tensor(result_data, self.shape)
    
    def __mul__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        """Element-wise multiplication"""
        if isinstance(other, (int, float)):
            return Tensor([x * other for x in self.data], self.shape)
        
        if not isinstance(other, Tensor):
            raise TypeError(f"Unsupported type for multiplication: {type(other)}")
        
        if self.shape != other.shape:
            return self._broadcast_op(other, lambda x, y: x * y)
        
        result_data = [x * y for x, y in zip(self.data, other.data)]
        return Tensor(result_data, self.shape)
    
    def __truediv__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        """Element-wise division"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Division by zero")
            return Tensor([x / other for x in self.data], self.shape)
        
        if not isinstance(other, Tensor):
            raise TypeError(f"Unsupported type for division: {type(other)}")
        
        if self.shape != other.shape:
            return self._broadcast_op(other, lambda x, y: x / y if y != 0 else float('inf'))
        
        result_data = [x / y if y != 0 else float('inf') for x, y in zip(self.data, other.data)]
        return Tensor(result_data, self.shape)
    
    def __radd__(self, other: Union[float, int]) -> 'Tensor':
        return self.__add__(other)
    
    def __rsub__(self, other: Union[float, int]) -> 'Tensor':
        return Tensor([other - x for x in self.data], self.shape)
    
    def __rmul__(self, other: Union[float, int]) -> 'Tensor':
        return self.__mul__(other)
    
    def __rtruediv__(self, other: Union[float, int]) -> 'Tensor':
        return Tensor([other / x if x != 0 else float('inf') for x in self.data], self.shape)
    
    def _broadcast_op(self, other: 'Tensor', op: Callable) -> 'Tensor':
        """Apply operation with broadcasting"""
        # Simple broadcasting for common cases
        if self.shape.size == 1:
            val = self.data[0]
            return Tensor([op(val, y) for y in other.data], other.shape)
        
        if other.shape.size == 1:
            val = other.data[0]
            return Tensor([op(x, val) for x in self.data], self.shape)
        
        # More complex broadcasting
        if self.shape.ndim == other.shape.ndim:
            can_broadcast = True
            result_shape = []
            for d1, d2 in zip(self.shape.dims, other.shape.dims):
                if d1 == d2:
                    result_shape.append(d1)
                elif d1 == 1:
                    result_shape.append(d2)
                elif d2 == 1:
                    result_shape.append(d1)
                else:
                    can_broadcast = False
                    break
            
            if can_broadcast:
                result_data = []
                result_size = 1
                for d in result_shape:
                    result_size *= d
                
                for i in range(result_size):
                    temp_tensor = Tensor([0.0] * result_size, Shape(*result_shape))
                    indices = temp_tensor._flat_to_multi_index(i)
                    
                    self_indices = tuple(idx if self.shape.dims[j] > 1 else 0 
                                        for j, idx in enumerate(indices))
                    self_val = self.data[self._multi_index_to_flat(self_indices)]
                    
                    other_indices = tuple(idx if other.shape.dims[j] > 1 else 0 
                                         for j, idx in enumerate(indices))
                    other_val = other.data[other._multi_index_to_flat(other_indices)]
                    
                    result_data.append(op(self_val, other_val))
                
                return Tensor(result_data, Shape(*result_shape))
        
        raise ValueError(f"Cannot broadcast shapes {self.shape} and {other.shape}")
    
    def sum(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Tensor', float]:
        """Sum over axis or all elements"""
        if axis is None:
            result = sum(self.data)
            if keepdims:
                return Tensor([result], Shape(*([1] * self.shape.ndim)))
            return result
        
        return self._reduce_op(sum, axis, keepdims)
    
    def mean(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Tensor', float]:
        """Mean over axis or all elements"""
        if axis is None:
            return sum(self.data) / len(self.data)
        
        result = self._reduce_op(sum, axis, keepdims)
        if isinstance(result, Tensor):
            size = self.shape.dims[axis]
            return Tensor([x / size for x in result.data], result.shape)
        return result / self.shape.dims[axis]
    
    def std(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Tensor', float]:
        """Standard deviation over axis or all elements"""
        if axis is None:
            mean_val = self.mean()
            variance = sum((x - mean_val) ** 2 for x in self.data) / len(self.data)
            return math.sqrt(variance)
        
        mean_tensor = self.mean(axis, keepdims=True)
        if isinstance(mean_tensor, (int, float)):
            mean_tensor = Tensor([mean_tensor])
        
        diff_squared = (self - mean_tensor) * (self - mean_tensor)
        variance = diff_squared.mean(axis, keepdims)
        
        if isinstance(variance, Tensor):
            return Tensor([math.sqrt(x) for x in variance.data], variance.shape)
        return math.sqrt(variance)
    
    def min(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Tensor', float]:
        """Minimum over axis or all elements"""
        if axis is None:
            return min(self.data)
        return self._reduce_op(min, axis, keepdims)
    
    def max(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Tensor', float]:
        """Maximum over axis or all elements"""
        if axis is None:
            return max(self.data)
        return self._reduce_op(max, axis, keepdims)
    
    def _reduce_op(self, op: Callable, axis: int, keepdims: bool) -> 'Tensor':
        """Generic reduction operation along axis"""
        if axis < 0:
            axis = self.shape.ndim + axis
        
        if axis >= self.shape.ndim:
            raise ValueError(f"axis {axis} is out of bounds")
        
        new_dims = list(self.shape.dims)
        reduced_size = new_dims[axis]
        if keepdims:
            new_dims[axis] = 1
        else:
            new_dims.pop(axis)
        
        if not new_dims:
            new_dims = [1]
        
        result_data = []
        
        # Calculate total number of output elements
        output_size = 1
        for d in new_dims:
            output_size *= d
        
        # For each output position, collect values along the reduction axis
        for out_idx in range(output_size):
            values = []
            
            for axis_idx in range(reduced_size):
                # Calculate input index
                in_indices = []
                temp_idx = out_idx
                
                for dim_idx, dim_size in enumerate(new_dims if not keepdims else self.shape.dims):
                    if keepdims and dim_idx == axis:
                        in_indices.append(axis_idx)
                    elif not keepdims and dim_idx >= axis:
                        # Adjust for removed dimension
                        actual_dim_idx = dim_idx + 1
                        if actual_dim_idx == axis:
                            in_indices.append(axis_idx)
                        else:
                            idx_val = temp_idx % self.shape.dims[actual_dim_idx]
                            in_indices.append(idx_val)
                            temp_idx //= self.shape.dims[actual_dim_idx]
                    else:
                        idx_val = temp_idx % self.shape.dims[dim_idx]
                        in_indices.append(idx_val)
                        temp_idx //= self.shape.dims[dim_idx]
                
                if not keepdims:
                    in_indices.insert(axis, axis_idx)
                
                if len(in_indices) == self.shape.ndim:
                    flat_idx = self._multi_index_to_flat(tuple(in_indices))
                    if flat_idx < len(self.data):
                        values.append(self.data[flat_idx])
            
            if values:
                result_data.append(op(values))
        
        return Tensor(result_data, Shape(*new_dims))
    
    def __repr__(self) -> str:
        return f"Tensor(shape={self.shape}, data={self.data[:10]}{'...' if len(self.data) > 10 else ''})"
    
    def __str__(self) -> str:
        return self._format_data(self.data, self.shape.dims)
    
    def _format_data(self, data: List[float], shape: Tuple[int, ...], indent: int = 0) -> str:
        """Format tensor data for printing"""
        if len(shape) == 1:
            return "[" + ", ".join(f"{x:.4f}" for x in data[:shape[0]]) + "]"
        
        result = "[\n"
        stride = 1
        for d in shape[1:]:
            stride *= d
        
        for i in range(shape[0]):
            result += "  " * (indent + 1)
            subset = data[i * stride:(i + 1) * stride]
            result += self._format_data(subset, shape[1:], indent + 1)
            if i < shape[0] - 1:
                result += ",\n"
        
        result += "\n" + "  " * indent + "]"
        return result


# Initialization functions
def randn(*shape: int, mean: float = 0.0, std: float = 1.0) -> Tensor:
    """Create tensor with random normal distribution"""
    size = 1
    for d in shape:
        size *= d
    
    # Box-Muller transform for normal distribution
    data = []
    for _ in range((size + 1) // 2):
        u1 = random.random()
        u2 = random.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
        data.append(mean + z0 * std)
        data.append(mean + z1 * std)
    
    return Tensor(data[:size], Shape(*shape))


def zeros(*shape: int) -> Tensor:
    """Create tensor filled with zeros"""
    size = 1
    for d in shape:
        size *= d
    return Tensor([0.0] * size, Shape(*shape))


def ones(*shape: int) -> Tensor:
    """Create tensor filled with ones"""
    size = 1
    for d in shape:
        size *= d
    return Tensor([1.0] * size, Shape(*shape))


def eye(n: int) -> Tensor:
    """Create identity matrix"""
    data = []
    for i in range(n):
        for j in range(n):
            data.append(1.0 if i == j else 0.0)
    return Tensor(data, Shape(n, n))


def uniform(*shape: int, low: float = 0.0, high: float = 1.0) -> Tensor:
    """Create tensor with uniform random distribution"""
    size = 1
    for d in shape:
        size *= d
    data = [low + random.random() * (high - low) for _ in range(size)]
    return Tensor(data, Shape(*shape))
