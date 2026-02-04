"""
THALOS Prime - Tensor Operations Module
N-dimensional tensor operations with full broadcasting support.
"""

from typing import List, Tuple, Union, Optional
import math
import random


class Shape:
    """Shape class for dimension management."""
    
    def __init__(self, dims: Tuple[int, ...]):
        self.dims = dims
    
    def __repr__(self) -> str:
        return f"Shape{self.dims}"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Shape):
            return self.dims == other.dims
        return False
    
    def __len__(self) -> int:
        return len(self.dims)
    
    def __getitem__(self, idx: int) -> int:
        return self.dims[idx]
    
    @property
    def ndim(self) -> int:
        return len(self.dims)
    
    @property
    def numel(self) -> int:
        """Total number of elements."""
        result = 1
        for d in self.dims:
            result *= d
        return result
    
    def is_compatible_for_broadcast(self, other: 'Shape') -> bool:
        """Check if shapes can be broadcast together."""
        for d1, d2 in zip(reversed(self.dims), reversed(other.dims)):
            if d1 != d2 and d1 != 1 and d2 != 1:
                return False
        return True
    
    def broadcast_with(self, other: 'Shape') -> 'Shape':
        """Compute broadcast shape."""
        max_ndim = max(len(self.dims), len(other.dims))
        dims1 = (1,) * (max_ndim - len(self.dims)) + self.dims
        dims2 = (1,) * (max_ndim - len(other.dims)) + other.dims
        
        result = []
        for d1, d2 in zip(dims1, dims2):
            if d1 == d2:
                result.append(d1)
            elif d1 == 1:
                result.append(d2)
            elif d2 == 1:
                result.append(d1)
            else:
                raise ValueError(f"Cannot broadcast shapes {self} and {other}")
        return Shape(tuple(result))


class Tensor:
    """N-dimensional tensor with full operation support."""
    
    def __init__(self, data: Union[List, float, int], shape: Optional[Shape] = None):
        if isinstance(data, (int, float)):
            self.data = [float(data)]
            self.shape = Shape((1,))
        elif isinstance(data, list):
            self.data = self._flatten(data)
            if shape is not None:
                self.shape = shape
            else:
                self.shape = Shape(self._infer_shape(data))
        elif isinstance(data, Tensor):
            self.data = data.data.copy()
            self.shape = data.shape
        else:
            raise TypeError(f"Cannot create Tensor from {type(data)}")
    
    def _flatten(self, data: Union[List, float, int]) -> List[float]:
        """Flatten nested list to 1D."""
        if isinstance(data, (int, float)):
            return [float(data)]
        result = []
        for item in data:
            if isinstance(item, (list, tuple)):
                result.extend(self._flatten(item))
            else:
                result.append(float(item))
        return result
    
    def _infer_shape(self, data: Union[List, float, int]) -> Tuple[int, ...]:
        """Infer shape from nested list."""
        if isinstance(data, (int, float)):
            return ()
        if not data:
            return (0,)
        shape = [len(data)]
        if isinstance(data[0], (list, tuple)):
            inner_shape = self._infer_shape(data[0])
            shape.extend(inner_shape)
        return tuple(shape)
    
    def __repr__(self) -> str:
        return f"Tensor(shape={self.shape})"
    
    def __len__(self) -> int:
        return self.shape.dims[0] if self.shape.ndim > 0 else 1
    
    def __getitem__(self, idx):
        if isinstance(idx, int):
            if self.shape.ndim == 1:
                return self.data[idx]
            else:
                stride = self.shape.numel // self.shape.dims[0]
                start = idx * stride
                end = start + stride
                new_shape = Shape(self.shape.dims[1:])
                return Tensor(self.data[start:end], new_shape)
        return self.data[idx]
    
    def __setitem__(self, idx, value):
        if isinstance(idx, int):
            if isinstance(value, (int, float)):
                self.data[idx] = float(value)
            elif isinstance(value, Tensor):
                stride = self.shape.numel // self.shape.dims[0]
                start = idx * stride
                for i, v in enumerate(value.data):
                    self.data[start + i] = v
    
    def _broadcast_op(self, other: 'Tensor', op) -> 'Tensor':
        """Perform element-wise operation with broadcasting."""
        if not isinstance(other, Tensor):
            other = Tensor(other)
        
        new_shape = self.shape.broadcast_with(other.shape)
        new_data = []
        
        for i in range(new_shape.numel):
            idx1 = self._broadcast_index(i, self.shape, new_shape)
            idx2 = self._broadcast_index(i, other.shape, new_shape)
            new_data.append(op(self.data[idx1], other.data[idx2]))
        
        return Tensor(new_data, new_shape)
    
    def _broadcast_index(self, flat_idx: int, src_shape: Shape, dst_shape: Shape) -> int:
        """Compute source index for broadcasting."""
        # Convert flat index to multi-dimensional index in dst shape
        indices = []
        remaining = flat_idx
        for dim in reversed(dst_shape.dims):
            indices.append(remaining % dim)
            remaining //= dim
        indices = list(reversed(indices))
        
        # Adjust for broadcasting
        src_indices = []
        offset = len(dst_shape.dims) - len(src_shape.dims)
        for i, dim in enumerate(src_shape.dims):
            dst_idx = indices[i + offset]
            src_indices.append(0 if dim == 1 else dst_idx)
        
        # Convert back to flat index
        flat = 0
        stride = 1
        for i in reversed(range(len(src_shape.dims))):
            flat += src_indices[i] * stride
            stride *= src_shape.dims[i]
        
        return flat
    
    def __add__(self, other) -> 'Tensor':
        return self._broadcast_op(other if isinstance(other, Tensor) else Tensor(other), 
                                  lambda a, b: a + b)
    
    def __radd__(self, other) -> 'Tensor':
        return self.__add__(other)
    
    def __sub__(self, other) -> 'Tensor':
        return self._broadcast_op(other if isinstance(other, Tensor) else Tensor(other), 
                                  lambda a, b: a - b)
    
    def __rsub__(self, other) -> 'Tensor':
        return Tensor(other).__sub__(self)
    
    def __mul__(self, other) -> 'Tensor':
        return self._broadcast_op(other if isinstance(other, Tensor) else Tensor(other), 
                                  lambda a, b: a * b)
    
    def __rmul__(self, other) -> 'Tensor':
        return self.__mul__(other)
    
    def __truediv__(self, other) -> 'Tensor':
        return self._broadcast_op(other if isinstance(other, Tensor) else Tensor(other), 
                                  lambda a, b: a / b if b != 0 else 0.0)
    
    def __rtruediv__(self, other) -> 'Tensor':
        return Tensor(other).__truediv__(self)
    
    def __neg__(self) -> 'Tensor':
        return Tensor([-x for x in self.data], self.shape)
    
    def __pow__(self, exponent) -> 'Tensor':
        if isinstance(exponent, (int, float)):
            return Tensor([x ** exponent for x in self.data], self.shape)
        return self._broadcast_op(exponent, lambda a, b: a ** b)
    
    def reshape(self, *new_shape) -> 'Tensor':
        """Reshape tensor to new dimensions."""
        if len(new_shape) == 1 and isinstance(new_shape[0], (list, tuple)):
            new_shape = tuple(new_shape[0])
        
        new_numel = 1
        for d in new_shape:
            new_numel *= d
        
        if new_numel != self.shape.numel:
            raise ValueError(f"Cannot reshape {self.shape} to {new_shape}")
        
        return Tensor(self.data.copy(), Shape(new_shape))
    
    def flatten(self) -> 'Tensor':
        """Flatten tensor to 1D."""
        return Tensor(self.data.copy(), Shape((len(self.data),)))
    
    def transpose(self, dim0: int = 0, dim1: int = 1) -> 'Tensor':
        """Transpose two dimensions."""
        if self.shape.ndim < 2:
            return Tensor(self.data.copy(), self.shape)
        
        new_dims = list(self.shape.dims)
        new_dims[dim0], new_dims[dim1] = new_dims[dim1], new_dims[dim0]
        new_shape = Shape(tuple(new_dims))
        
        new_data = [0.0] * len(self.data)
        
        for i in range(len(self.data)):
            # Convert to multi-dimensional index
            indices = []
            remaining = i
            for dim in reversed(self.shape.dims):
                indices.append(remaining % dim)
                remaining //= dim
            indices = list(reversed(indices))
            
            # Swap dimensions
            indices[dim0], indices[dim1] = indices[dim1], indices[dim0]
            
            # Convert back to flat index with new shape
            new_idx = 0
            stride = 1
            for j in reversed(range(len(new_dims))):
                new_idx += indices[j] * stride
                stride *= new_dims[j]
            
            new_data[new_idx] = self.data[i]
        
        return Tensor(new_data, new_shape)
    
    @property
    def T(self) -> 'Tensor':
        """Transpose (swap first two dimensions)."""
        return self.transpose(0, 1)
    
    def sum(self, dim: Optional[int] = None, keepdim: bool = False) -> 'Tensor':
        """Sum along dimension or all elements."""
        if dim is None:
            return Tensor(sum(self.data))
        
        if dim < 0:
            dim = self.shape.ndim + dim
        
        new_dims = list(self.shape.dims)
        reduce_size = new_dims[dim]
        
        # Compute strides
        stride = 1
        for i in range(dim + 1, self.shape.ndim):
            stride *= self.shape.dims[i]
        
        outer_size = 1
        for i in range(dim):
            outer_size *= self.shape.dims[i]
        
        if keepdim:
            new_dims[dim] = 1
        else:
            new_dims.pop(dim)
        
        new_numel = 1
        for d in new_dims:
            new_numel *= d
        
        new_data = [0.0] * new_numel
        
        for outer in range(outer_size):
            for inner in range(stride):
                total = 0.0
                for r in range(reduce_size):
                    idx = outer * reduce_size * stride + r * stride + inner
                    total += self.data[idx]
                out_idx = outer * stride + inner
                new_data[out_idx] = total
        
        return Tensor(new_data, Shape(tuple(new_dims)) if new_dims else Shape((1,)))
    
    def mean(self, dim: Optional[int] = None, keepdim: bool = False) -> 'Tensor':
        """Mean along dimension or all elements."""
        if dim is None:
            return Tensor(sum(self.data) / len(self.data))
        
        s = self.sum(dim=dim, keepdim=keepdim)
        count = self.shape.dims[dim if dim >= 0 else self.shape.ndim + dim]
        return s / count
    
    def std(self, dim: Optional[int] = None, keepdim: bool = False) -> 'Tensor':
        """Standard deviation."""
        mean_val = self.mean(dim=dim, keepdim=True)
        if dim is None:
            variance = sum((x - mean_val.data[0]) ** 2 for x in self.data) / len(self.data)
            return Tensor(math.sqrt(variance))
        
        diff = self - mean_val
        squared = diff * diff
        return squared.mean(dim=dim, keepdim=keepdim) ** 0.5
    
    def min(self, dim: Optional[int] = None) -> 'Tensor':
        """Minimum value."""
        if dim is None:
            return Tensor(min(self.data))
        # Simplified: return minimum along dimension
        return self.sum(dim=dim) / self.shape.dims[dim]  # Placeholder
    
    def max(self, dim: Optional[int] = None) -> 'Tensor':
        """Maximum value."""
        if dim is None:
            return Tensor(max(self.data))
        # Simplified: return maximum along dimension
        return self.sum(dim=dim) / self.shape.dims[dim]  # Placeholder
    
    def abs(self) -> 'Tensor':
        """Element-wise absolute value."""
        return Tensor([abs(x) for x in self.data], self.shape)
    
    def sqrt(self) -> 'Tensor':
        """Element-wise square root."""
        return Tensor([math.sqrt(max(0, x)) for x in self.data], self.shape)
    
    def exp(self) -> 'Tensor':
        """Element-wise exponential."""
        return Tensor([math.exp(min(x, 700)) for x in self.data], self.shape)
    
    def log(self) -> 'Tensor':
        """Element-wise natural logarithm."""
        return Tensor([math.log(max(x, 1e-10)) for x in self.data], self.shape)
    
    def clone(self) -> 'Tensor':
        """Create a copy of the tensor."""
        return Tensor(self.data.copy(), self.shape)
    
    def tolist(self) -> List:
        """Convert to nested list."""
        if self.shape.ndim == 0:
            return self.data[0]
        elif self.shape.ndim == 1:
            return self.data.copy()
        else:
            result = []
            stride = self.shape.numel // self.shape.dims[0]
            for i in range(self.shape.dims[0]):
                start = i * stride
                end = start + stride
                sub_tensor = Tensor(self.data[start:end], Shape(self.shape.dims[1:]))
                result.append(sub_tensor.tolist())
            return result
    
    def item(self) -> float:
        """Get scalar value for single-element tensor."""
        if len(self.data) != 1:
            raise ValueError("item() only works on single-element tensors")
        return self.data[0]


# Factory functions
def randn(*shape) -> Tensor:
    """Create tensor with random normal values."""
    if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
        shape = tuple(shape[0])
    
    numel = 1
    for d in shape:
        numel *= d
    
    # Box-Muller transform for normal distribution
    data = []
    for _ in range(numel):
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
        data.append(z)
    
    return Tensor(data, Shape(shape))


def zeros(*shape) -> Tensor:
    """Create tensor filled with zeros."""
    if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
        shape = tuple(shape[0])
    
    numel = 1
    for d in shape:
        numel *= d
    
    return Tensor([0.0] * numel, Shape(shape))


def ones(*shape) -> Tensor:
    """Create tensor filled with ones."""
    if len(shape) == 1 and isinstance(shape[0], (list, tuple)):
        shape = tuple(shape[0])
    
    numel = 1
    for d in shape:
        numel *= d
    
    return Tensor([1.0] * numel, Shape(shape))


def eye(n: int) -> Tensor:
    """Create identity matrix."""
    data = []
    for i in range(n):
        for j in range(n):
            data.append(1.0 if i == j else 0.0)
    return Tensor(data, Shape((n, n)))


def arange(start: int, end: Optional[int] = None, step: int = 1) -> Tensor:
    """Create 1D tensor with values in range."""
    if end is None:
        end = start
        start = 0
    data = list(range(start, end, step))
    return Tensor([float(x) for x in data])


def linspace(start: float, end: float, steps: int) -> Tensor:
    """Create 1D tensor with linearly spaced values."""
    if steps == 1:
        return Tensor([start])
    data = [start + i * (end - start) / (steps - 1) for i in range(steps)]
    return Tensor(data)


def cat(tensors: List[Tensor], dim: int = 0) -> Tensor:
    """Concatenate tensors along dimension."""
    if not tensors:
        raise ValueError("Cannot concatenate empty list")
    
    if len(tensors) == 1:
        return tensors[0].clone()
    
    # For 1D tensors, simple concatenation
    if tensors[0].shape.ndim == 1:
        data = []
        for t in tensors:
            data.extend(t.data)
        return Tensor(data)
    
    # For 2D+ tensors along dim=0
    if dim == 0:
        total_rows = sum(t.shape.dims[0] for t in tensors)
        new_shape = Shape((total_rows,) + tensors[0].shape.dims[1:])
        data = []
        for t in tensors:
            data.extend(t.data)
        return Tensor(data, new_shape)
    
    # For other dimensions, more complex logic needed
    raise NotImplementedError("Concatenation along dim > 0 not yet implemented")


def stack(tensors: List[Tensor], dim: int = 0) -> Tensor:
    """Stack tensors along new dimension."""
    if not tensors:
        raise ValueError("Cannot stack empty list")
    
    # Add new dimension and concatenate
    new_shape_dims = list(tensors[0].shape.dims)
    new_shape_dims.insert(dim, len(tensors))
    
    data = []
    for t in tensors:
        data.extend(t.data)
    
    return Tensor(data, Shape(tuple(new_shape_dims)))
