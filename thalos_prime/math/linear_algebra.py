"""
Linear algebra operations for THALOS Prime
"""
from .tensor import Tensor


class LinearAlgebra:
    """Linear algebra operations"""
    
    @staticmethod
    def matmul(a, b):
        """Matrix multiplication"""
        if isinstance(a, Tensor) and isinstance(b, Tensor):
            # Simple matrix multiplication for 2D tensors
            if len(a.shape.dims) == 2 and len(b.shape.dims) == 2:
                m, n = a.shape.dims
                n2, p = b.shape.dims
                if n != n2:
                    raise ValueError(f"Incompatible shapes for matmul: {a.shape} and {b.shape}")
                
                result = []
                for i in range(m):
                    for j in range(p):
                        val = 0
                        for k in range(n):
                            val += a.data[i * n + k] * b.data[k * p + j]
                        result.append(val)
                return Tensor(result, (m, p))
        return None
    
    @staticmethod
    def transpose(x):
        """Transpose a 2D tensor"""
        if isinstance(x, Tensor) and len(x.shape.dims) == 2:
            m, n = x.shape.dims
            result = []
            for j in range(n):
                for i in range(m):
                    result.append(x.data[i * n + j])
            return Tensor(result, (n, m))
        return x
    
    @staticmethod
    def dot(a, b):
        """Dot product"""
        if isinstance(a, Tensor) and isinstance(b, Tensor):
            return sum(x * y for x, y in zip(a.data, b.data))
        return 0
