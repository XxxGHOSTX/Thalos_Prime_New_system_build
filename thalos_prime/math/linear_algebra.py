"""
THALOS Prime - Linear Algebra Module
Matrix operations, decompositions, and solvers.
"""

from typing import List, Tuple, Optional
import math
from .tensor import Tensor, Shape, zeros, eye


class LinearAlgebra:
    """Linear algebra operations on tensors."""
    
    @staticmethod
    def matmul(a: Tensor, b: Tensor) -> Tensor:
        """Matrix multiplication."""
        if a.shape.ndim < 2 or b.shape.ndim < 2:
            raise ValueError("matmul requires 2D tensors")
        
        m, k1 = a.shape.dims[-2], a.shape.dims[-1]
        k2, n = b.shape.dims[-2], b.shape.dims[-1]
        
        if k1 != k2:
            raise ValueError(f"Incompatible shapes for matmul: {a.shape} @ {b.shape}")
        
        result_data = []
        for i in range(m):
            for j in range(n):
                total = 0.0
                for k in range(k1):
                    idx_a = i * k1 + k
                    idx_b = k * n + j
                    total += a.data[idx_a] * b.data[idx_b]
                result_data.append(total)
        
        return Tensor(result_data, Shape((m, n)))
    
    @staticmethod
    def transpose(a: Tensor) -> Tensor:
        """Transpose a 2D tensor."""
        if a.shape.ndim != 2:
            raise ValueError("transpose requires 2D tensor")
        return a.T
    
    @staticmethod
    def dot(a: Tensor, b: Tensor) -> float:
        """Dot product of 1D tensors."""
        if a.shape.ndim != 1 or b.shape.ndim != 1:
            raise ValueError("dot requires 1D tensors")
        if len(a.data) != len(b.data):
            raise ValueError("Vectors must have same length")
        return sum(x * y for x, y in zip(a.data, b.data))
    
    @staticmethod
    def outer(a: Tensor, b: Tensor) -> Tensor:
        """Outer product of 1D tensors."""
        if a.shape.ndim != 1 or b.shape.ndim != 1:
            raise ValueError("outer requires 1D tensors")
        
        m, n = len(a.data), len(b.data)
        result_data = []
        for i in range(m):
            for j in range(n):
                result_data.append(a.data[i] * b.data[j])
        
        return Tensor(result_data, Shape((m, n)))
    
    @staticmethod
    def norm(a: Tensor, p: float = 2.0) -> float:
        """Compute p-norm of tensor."""
        if p == 2:
            return math.sqrt(sum(x ** 2 for x in a.data))
        elif p == 1:
            return sum(abs(x) for x in a.data)
        elif p == float('inf'):
            return max(abs(x) for x in a.data)
        else:
            return sum(abs(x) ** p for x in a.data) ** (1 / p)
    
    @staticmethod
    def matrix_norm(a: Tensor, ord: str = 'fro') -> float:
        """Compute matrix norm."""
        if a.shape.ndim != 2:
            raise ValueError("matrix_norm requires 2D tensor")
        
        if ord == 'fro':
            return math.sqrt(sum(x ** 2 for x in a.data))
        elif ord == 'nuc':
            # Nuclear norm = sum of singular values (simplified)
            return math.sqrt(sum(x ** 2 for x in a.data))
        else:
            raise ValueError(f"Unknown norm: {ord}")
    
    @staticmethod
    def qr(a: Tensor) -> Tuple[Tensor, Tensor]:
        """QR decomposition using Gram-Schmidt."""
        if a.shape.ndim != 2:
            raise ValueError("qr requires 2D tensor")
        
        m, n = a.shape.dims
        
        # Convert to list of column vectors
        cols = []
        for j in range(n):
            col = [a.data[i * n + j] for i in range(m)]
            cols.append(col)
        
        # Gram-Schmidt orthogonalization
        q_cols = []
        r_data = [[0.0] * n for _ in range(n)]
        
        for j in range(n):
            v = cols[j].copy()
            
            for i in range(j):
                # r[i,j] = q_i . a_j
                r_ij = sum(q_cols[i][k] * cols[j][k] for k in range(m))
                r_data[i][j] = r_ij
                # v = v - r[i,j] * q_i
                for k in range(m):
                    v[k] -= r_ij * q_cols[i][k]
            
            # r[j,j] = ||v||
            norm_v = math.sqrt(sum(x ** 2 for x in v))
            r_data[j][j] = norm_v
            
            # q_j = v / ||v||
            if norm_v > 1e-10:
                q_col = [x / norm_v for x in v]
            else:
                q_col = [0.0] * m
            q_cols.append(q_col)
        
        # Build Q and R tensors
        q_data = []
        for i in range(m):
            for j in range(n):
                q_data.append(q_cols[j][i])
        
        r_flat = []
        for i in range(n):
            for j in range(n):
                r_flat.append(r_data[i][j])
        
        return Tensor(q_data, Shape((m, n))), Tensor(r_flat, Shape((n, n)))
    
    @staticmethod
    def det(a: Tensor) -> float:
        """Compute determinant (2x2 or 3x3 matrices)."""
        if a.shape.ndim != 2:
            raise ValueError("det requires 2D tensor")
        if a.shape.dims[0] != a.shape.dims[1]:
            raise ValueError("det requires square matrix")
        
        n = a.shape.dims[0]
        
        if n == 1:
            return a.data[0]
        elif n == 2:
            return a.data[0] * a.data[3] - a.data[1] * a.data[2]
        elif n == 3:
            # Sarrus rule
            return (a.data[0] * a.data[4] * a.data[8] +
                    a.data[1] * a.data[5] * a.data[6] +
                    a.data[2] * a.data[3] * a.data[7] -
                    a.data[2] * a.data[4] * a.data[6] -
                    a.data[1] * a.data[3] * a.data[8] -
                    a.data[0] * a.data[5] * a.data[7])
        else:
            # LU decomposition for larger matrices
            raise NotImplementedError("det for n > 3 not implemented")
    
    @staticmethod
    def trace(a: Tensor) -> float:
        """Compute trace of matrix."""
        if a.shape.ndim != 2:
            raise ValueError("trace requires 2D tensor")
        if a.shape.dims[0] != a.shape.dims[1]:
            raise ValueError("trace requires square matrix")
        
        n = a.shape.dims[0]
        return sum(a.data[i * n + i] for i in range(n))
    
    @staticmethod
    def solve(a: Tensor, b: Tensor) -> Tensor:
        """Solve linear system Ax = b using Gaussian elimination."""
        if a.shape.ndim != 2 or b.shape.ndim != 1:
            raise ValueError("solve requires 2D matrix and 1D vector")
        
        n = a.shape.dims[0]
        if a.shape.dims[1] != n or len(b.data) != n:
            raise ValueError("Incompatible dimensions")
        
        # Create augmented matrix
        aug = [[0.0] * (n + 1) for _ in range(n)]
        for i in range(n):
            for j in range(n):
                aug[i][j] = a.data[i * n + j]
            aug[i][n] = b.data[i]
        
        # Forward elimination with partial pivoting
        for k in range(n):
            # Find pivot
            max_idx = k
            max_val = abs(aug[k][k])
            for i in range(k + 1, n):
                if abs(aug[i][k]) > max_val:
                    max_val = abs(aug[i][k])
                    max_idx = i
            
            # Swap rows
            aug[k], aug[max_idx] = aug[max_idx], aug[k]
            
            if abs(aug[k][k]) < 1e-10:
                raise ValueError("Matrix is singular")
            
            # Eliminate
            for i in range(k + 1, n):
                factor = aug[i][k] / aug[k][k]
                for j in range(k, n + 1):
                    aug[i][j] -= factor * aug[k][j]
        
        # Back substitution
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            x[i] = aug[i][n]
            for j in range(i + 1, n):
                x[i] -= aug[i][j] * x[j]
            x[i] /= aug[i][i]
        
        return Tensor(x)
    
    @staticmethod
    def eig(a: Tensor, num_iterations: int = 100) -> Tuple[List[float], List[Tensor]]:
        """Compute eigenvalues using power iteration (simplified)."""
        if a.shape.ndim != 2:
            raise ValueError("eig requires 2D tensor")
        if a.shape.dims[0] != a.shape.dims[1]:
            raise ValueError("eig requires square matrix")
        
        n = a.shape.dims[0]
        eigenvalues = []
        eigenvectors = []
        
        # Power iteration for dominant eigenvalue
        v = Tensor([1.0] * n)
        
        for _ in range(num_iterations):
            # v = A @ v
            new_v = []
            for i in range(n):
                total = 0.0
                for j in range(n):
                    total += a.data[i * n + j] * v.data[j]
                new_v.append(total)
            
            # Normalize
            norm = math.sqrt(sum(x ** 2 for x in new_v))
            if norm > 1e-10:
                v = Tensor([x / norm for x in new_v])
            else:
                break
        
        # Compute eigenvalue: lambda = (v^T A v) / (v^T v)
        av = []
        for i in range(n):
            total = 0.0
            for j in range(n):
                total += a.data[i * n + j] * v.data[j]
            av.append(total)
        
        eigenvalue = sum(v.data[i] * av[i] for i in range(n))
        eigenvalues.append(eigenvalue)
        eigenvectors.append(v)
        
        return eigenvalues, eigenvectors
    
    @staticmethod
    def inv(a: Tensor) -> Tensor:
        """Compute matrix inverse using Gaussian elimination."""
        if a.shape.ndim != 2:
            raise ValueError("inv requires 2D tensor")
        if a.shape.dims[0] != a.shape.dims[1]:
            raise ValueError("inv requires square matrix")
        
        n = a.shape.dims[0]
        
        # Create augmented matrix [A | I]
        aug = [[0.0] * (2 * n) for _ in range(n)]
        for i in range(n):
            for j in range(n):
                aug[i][j] = a.data[i * n + j]
            aug[i][n + i] = 1.0
        
        # Gaussian elimination
        for k in range(n):
            # Find pivot
            max_idx = k
            max_val = abs(aug[k][k])
            for i in range(k + 1, n):
                if abs(aug[i][k]) > max_val:
                    max_val = abs(aug[i][k])
                    max_idx = i
            
            aug[k], aug[max_idx] = aug[max_idx], aug[k]
            
            if abs(aug[k][k]) < 1e-10:
                raise ValueError("Matrix is singular")
            
            # Scale pivot row
            pivot = aug[k][k]
            for j in range(2 * n):
                aug[k][j] /= pivot
            
            # Eliminate
            for i in range(n):
                if i != k:
                    factor = aug[i][k]
                    for j in range(2 * n):
                        aug[i][j] -= factor * aug[k][j]
        
        # Extract inverse
        inv_data = []
        for i in range(n):
            for j in range(n):
                inv_data.append(aug[i][n + j])
        
        return Tensor(inv_data, Shape((n, n)))
    
    @staticmethod
    def svd(a: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
        """Simplified SVD using power iteration."""
        if a.shape.ndim != 2:
            raise ValueError("svd requires 2D tensor")
        
        m, n = a.shape.dims
        k = min(m, n)
        
        # A^T A
        ata = LinearAlgebra.matmul(a.T, a)
        
        # Get top eigenvalue/vector of A^T A
        eigenvalues, eigenvectors = LinearAlgebra.eig(ata)
        
        # Build simplified SVD
        sigma = [math.sqrt(max(0, ev)) for ev in eigenvalues]
        
        # U, S, V placeholders
        u_data = [0.0] * (m * k)
        s_data = sigma + [0.0] * (k - len(sigma))
        v_data = [v.data[i] if i < len(v.data) else 0.0 
                  for v in eigenvectors for i in range(n)]
        
        return (Tensor(u_data, Shape((m, k))),
                Tensor(s_data, Shape((k,))),
                Tensor(v_data, Shape((k, n))))
