#!/usr/bin/env python3
"""
THALOS Prime Linear Algebra Module
Pure Python implementation of matrix operations
"""

import math
from typing import Optional, Tuple, List
from .tensor import Tensor, zeros, ones, eye, Shape


class LinearAlgebra:
    """Linear algebra operations"""
    
    @staticmethod
    def matmul(a: Tensor, b: Tensor) -> Tensor:
        """Matrix multiplication with broadcasting support"""
        if a.shape.ndim < 2 or b.shape.ndim < 2:
            raise ValueError("Both tensors must be at least 2D for matmul")
        
        # Get matrix dimensions
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
            raise ValueError(f"Cannot multiply matrices with shapes {a.shape} and {b.shape}: "
                           f"inner dimensions {k1} and {k2} don't match")
        
        # Simple 2D case
        if a.shape.ndim == 2 and b.shape.ndim == 2:
            result_data = []
            for i in range(m):
                for j in range(n):
                    total = 0.0
                    for k in range(k1):
                        total += a.data[i * k1 + k] * b.data[k * n + j]
                    result_data.append(total)
            
            # Shape imported at module level
            return Tensor(result_data, Shape(m, n))
        
        # Batched case - simplified
        # Just handle the basic case for now
            raise ValueError(f"Incompatible shapes for matmul: {a.shape} @ {b.shape}")
        
        result_data = []
        for i in range(m):
            for j in range(n):
                total = 0.0
                for k in range(k1):
                    a_idx = i * k1 + k
                    b_idx = k * n + j
                    if a_idx < len(a.data) and b_idx < len(b.data):
                        total += a.data[a_idx] * b.data[b_idx]
                result_data.append(total)
        
        # Shape imported at module level
        return Tensor(result_data, Shape(m, n))
    
    @staticmethod
    def dot(a: Tensor, b: Tensor) -> float:
        """Dot product of two vectors"""
        if a.shape.size != b.shape.size:
            raise ValueError(f"Tensors must have same size for dot product")
        
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
        """Outer product of two vectors"""
        a_flat = a.flatten()
        b_flat = b.flatten()
        
        result_data = []
        for a_val in a_flat.data:
            for b_val in b_flat.data:
                result_data.append(a_val * b_val)
        
        # Shape imported at module level
        return Tensor(result_data, Shape(len(a_flat.data), len(b_flat.data)))
    
    @staticmethod
    def transpose(x: Tensor) -> Tensor:
        """Transpose matrix"""
        return x.transpose()
    
    @staticmethod
    def norm(x: Tensor, ord: Optional[int] = None, axis: Optional[int] = None) -> float:
        """
        Compute norm of tensor
        
        Args:
            x: Input tensor
            ord: Order of norm (None=Frobenius, 2=L2, 1=L1, float('inf')=max)
            axis: Axis along which to compute norm
        """
        if axis is not None:
            # Compute along specific axis
            if ord is None or ord == 2:
                # L2 norm
                squared = x * x
                sum_squared = squared.sum(axis=axis)
                if isinstance(sum_squared, Tensor):
                    return Tensor([math.sqrt(v) for v in sum_squared.data], sum_squared.shape)
                return math.sqrt(sum_squared)
            elif ord == 1:
                # L1 norm
                abs_vals = Tensor([abs(v) for v in x.data], x.shape)
                return abs_vals.sum(axis=axis)
            elif ord == float('inf'):
                # Max norm
                abs_vals = Tensor([abs(v) for v in x.data], x.shape)
                return abs_vals.max(axis=axis)
        else:
            # Compute over entire tensor
            if ord is None or ord == 2:
                # Frobenius/L2 norm
                return math.sqrt(sum(v * v for v in x.data))
            elif ord == 1:
                # L1 norm
                return sum(abs(v) for v in x.data)
            elif ord == float('inf'):
                # Max norm
                return max(abs(v) for v in x.data)
        
        raise ValueError(f"Unsupported norm order: {ord}")
    
    @staticmethod
    def qr_decomposition(a: Tensor) -> Tuple[Tensor, Tensor]:
        """
        QR decomposition using Gram-Schmidt process
        
        Returns:
            Q: Orthogonal matrix
            R: Upper triangular matrix
        """
        if a.shape.ndim != 2:
            raise ValueError("QR decomposition requires 2D matrix")
        
        m, n = a.shape.dims
        
        # Extract columns
        columns = []
        for j in range(n):
            col = [a.data[i * n + j] for i in range(m)]
            columns.append(col)
        
        # Gram-Schmidt process
        q_columns = []
        r_data = [0.0] * (n * n)
        
        for j in range(n):
            # Start with original column
            q_col = columns[j][:]
            
            # Subtract projections onto previous Q columns
            for i in range(j):
                # Compute dot product
                r_ij = sum(columns[j][k] * q_columns[i][k] for k in range(m))
                r_data[i * n + j] = r_ij
                
                # Subtract projection
                for k in range(m):
                    q_col[k] -= r_ij * q_columns[i][k]
            
            # Compute norm
            norm = math.sqrt(sum(v * v for v in q_col))
            r_data[j * n + j] = norm
            
            # Normalize
            if norm > 1e-10:
                q_col = [v / norm for v in q_col]
            
            q_columns.append(q_col)
        
        # Construct Q matrix
        q_data = []
        for i in range(m):
            for j in range(n):
                q_data.append(q_columns[j][i])
        
        # Shape imported at module level
        Q = Tensor(q_data, Shape(m, n))
        R = Tensor(r_data, Shape(n, n))
        
        return Q, R
    
    @staticmethod
    def det(a: Tensor) -> float:
        """
        Compute determinant
        Supports 2x2 and 3x3 matrices
        """
        if a.shape.ndim != 2:
            raise ValueError("Determinant requires 2D matrix")
        
        m, n = a.shape.dims
        if m != n:
            raise ValueError("Determinant requires square matrix")
        
        if n == 2:
            # 2x2 determinant
            return a.data[0] * a.data[3] - a.data[1] * a.data[2]
        
        elif n == 3:
            # 3x3 determinant using rule of Sarrus
            return (a.data[0] * a.data[4] * a.data[8] +
                   a.data[1] * a.data[5] * a.data[6] +
                   a.data[2] * a.data[3] * a.data[7] -
                   a.data[2] * a.data[4] * a.data[6] -
                   a.data[1] * a.data[3] * a.data[8] -
                   a.data[0] * a.data[5] * a.data[7])
        
        else:
            # General case using LU decomposition
            return LinearAlgebra._det_lu(a)
    
    @staticmethod
    def _det_lu(a: Tensor) -> float:
        """Compute determinant using LU decomposition"""
        n = a.shape.dims[0]
        
        # Copy matrix
        lu = a.data[:]
        
        det = 1.0
        for i in range(n):
            # Partial pivoting
            max_idx = i
            max_val = abs(lu[i * n + i])
            for k in range(i + 1, n):
                if abs(lu[k * n + i]) > max_val:
                    max_val = abs(lu[k * n + i])
                    max_idx = k
            
            if max_idx != i:
                # Swap rows
                for j in range(n):
                    lu[i * n + j], lu[max_idx * n + j] = lu[max_idx * n + j], lu[i * n + j]
                det *= -1
            
            # Check for singular matrix
            if abs(lu[i * n + i]) < 1e-10:
                return 0.0
            
            det *= lu[i * n + i]
            
            # Eliminate below
            for k in range(i + 1, n):
                factor = lu[k * n + i] / lu[i * n + i]
                for j in range(i, n):
                    lu[k * n + j] -= factor * lu[i * n + j]
        
        return det
    
    @staticmethod
    def trace(a: Tensor) -> float:
        """Compute trace (sum of diagonal elements)"""
        if a.shape.ndim != 2:
            raise ValueError("Trace requires 2D matrix")
        
        m, n = a.shape.dims
        if m != n:
            raise ValueError("Trace requires square matrix")
        
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
        """
        Solve linear system Ax = b using Gaussian elimination
        
        Args:
            a: Coefficient matrix (n x n)
            b: Right-hand side vector or matrix (n x m)
        
        Returns:
            Solution tensor x
        """
        if a.shape.ndim != 2:
            raise ValueError("Coefficient matrix must be 2D")
        
        m, n = a.shape.dims
        if m != n:
            raise ValueError("Coefficient matrix must be square")
        
        # Handle vector or matrix RHS
        if b.shape.ndim == 1:
            b = b.reshape(b.shape.size, 1)
        
        if b.shape.dims[0] != n:
            raise ValueError(f"Dimensions don't match: A is {a.shape}, b is {b.shape}")
        
        num_rhs = b.shape.dims[1]
        
        # Create augmented matrix
        aug = []
        for i in range(n):
            for j in range(n):
                aug.append(a.data[i * n + j])
            for j in range(num_rhs):
                aug.append(b.data[i * num_rhs + j])
        
        # Gaussian elimination with partial pivoting
        cols = n + num_rhs
        for i in range(n):
            # Find pivot
            max_idx = i
            max_val = abs(aug[i * cols + i])
            for k in range(i + 1, n):
                if abs(aug[k * cols + i]) > max_val:
                    max_val = abs(aug[k * cols + i])
                    max_idx = k
            
            # Swap rows
            if max_idx != i:
                for j in range(cols):
                    aug[i * cols + j], aug[max_idx * cols + j] = aug[max_idx * cols + j], aug[i * cols + j]
            
            # Check for singular matrix
            if abs(aug[i * cols + i]) < 1e-10:
                raise ValueError("Matrix is singular")
            
            # Eliminate below
            for k in range(i + 1, n):
                factor = aug[k * cols + i] / aug[i * cols + i]
                for j in range(i, cols):
                    aug[k * cols + j] -= factor * aug[i * cols + j]
        
        # Back substitution
        solution = [0.0] * (n * num_rhs)
        for i in range(n - 1, -1, -1):
            for j in range(num_rhs):
                val = aug[i * cols + n + j]
                for k in range(i + 1, n):
                    val -= aug[i * cols + k] * solution[k * num_rhs + j]
                solution[i * num_rhs + j] = val / aug[i * cols + i]
        
        # Shape imported at module level
        if num_rhs == 1:
            return Tensor(solution, Shape(n,))
        return Tensor(solution, Shape(n, num_rhs))
    
    @staticmethod
    def eig(a: Tensor, num_iterations: int = 100) -> Tuple[List[float], Tensor]:
        """
        Compute eigenvalues and eigenvectors using power iteration
        
        Args:
            a: Square matrix
            num_iterations: Number of iterations for power method
        
        Returns:
            eigenvalues: List of eigenvalues (may be incomplete)
            eigenvectors: Matrix of eigenvectors as columns
        """
        if a.shape.ndim != 2:
            raise ValueError("Eigendecomposition requires 2D matrix")
        
        m, n = a.shape.dims
        if m != n:
            raise ValueError("Eigendecomposition requires square matrix")
        
        # Use power iteration to find dominant eigenvector
        from .tensor import randn, Shape
        
        # Start with random vector
        v = randn(n)
        v_data = v.data
        
        # Power iteration
        for _ in range(num_iterations):
            # Matrix-vector multiply
            new_v = [0.0] * n
            for i in range(n):
                for j in range(n):
                    new_v[i] += a.data[i * n + j] * v_data[j]
            
            # Normalize
            norm = math.sqrt(sum(x * x for x in new_v))
            if norm > 1e-10:
                v_data = [x / norm for x in new_v]
            else:
                break
        
        # Compute eigenvalue: λ = v^T A v / v^T v
        av = [0.0] * n
        for i in range(n):
            for j in range(n):
                av[i] += a.data[i * n + j] * v_data[j]
        
        eigenvalue = sum(v_data[i] * av[i] for i in range(n))
        
        # Return first eigenvalue and eigenvector
        eigenvector = Tensor(v_data, Shape(n, 1))
        
        return [eigenvalue], eigenvector
    
    @staticmethod
    def inv(a: Tensor) -> Tensor:
        """
        Compute matrix inverse using Gauss-Jordan elimination
        
        Args:
            a: Square matrix to invert
        
        Returns:
            Inverse matrix
        """
        if a.shape.ndim != 2:
            raise ValueError("Inverse requires 2D matrix")
        
        m, n = a.shape.dims
        if m != n:
            raise ValueError("Inverse requires square matrix")
        
        # Create augmented matrix [A | I]
        aug = []
        for i in range(n):
            for j in range(n):
                aug.append(a.data[i * n + j])
            for j in range(n):
                aug.append(1.0 if i == j else 0.0)
        
        cols = 2 * n
        
        # Gauss-Jordan elimination
        for i in range(n):
            # Find pivot
            max_idx = i
            max_val = abs(aug[i * cols + i])
            for k in range(i + 1, n):
                if abs(aug[k * cols + i]) > max_val:
                    max_val = abs(aug[k * cols + i])
                    max_idx = k
            
            # Swap rows
            if max_idx != i:
                for j in range(cols):
                    aug[i * cols + j], aug[max_idx * cols + j] = aug[max_idx * cols + j], aug[i * cols + j]
            
            # Check for singular matrix
            pivot = aug[i * cols + i]
            if abs(pivot) < 1e-10:
                raise ValueError("Matrix is singular")
            
            # Scale row
            for j in range(cols):
                aug[i * cols + j] /= pivot
            
            # Eliminate column
            for k in range(n):
                if k != i:
                    factor = aug[k * cols + i]
                    for j in range(cols):
                        aug[k * cols + j] -= factor * aug[i * cols + j]
        
        # Extract inverse from right half
        inv_data = []
        for i in range(n):
            for j in range(n):
                inv_data.append(aug[i * cols + n + j])
        
        # Shape imported at module level
        return Tensor(inv_data, Shape(n, n))
    
    @staticmethod
    def svd(a: Tensor, num_iterations: int = 100) -> Tuple[Tensor, Tensor, Tensor]:
        """
        Simplified SVD using eigendecomposition
        Returns U, S, V^T such that A = U @ S @ V^T
        
        Note: This is a SIMPLIFIED implementation for educational purposes.
        It only computes the first singular value/vector via power iteration.
        For production use, implement full SVD or use a library.
        The U matrix returned is currently just an identity placeholder.
        """
        if a.shape.ndim != 2:
            raise ValueError("SVD requires 2D matrix")
        
        m, n = a.shape.dims
        
        # Compute A^T A
        at = a.transpose()
        ata = LinearAlgebra.matmul(at, a)
        
        # Get eigenvalues/vectors of A^T A (these give us V and S^2)
        s_squared, v = LinearAlgebra.eig(ata, num_iterations)
        
        # Singular values
        singular_values = [math.sqrt(abs(val)) for val in s_squared]
        
        # Create S matrix (diagonal)
        s_data = [0.0] * (min(m, n) ** 2)
        for i in range(min(len(singular_values), min(m, n))):
            s_data[i * min(m, n) + i] = singular_values[i]
        
        # Shape imported at module level
        s = Tensor(s_data, Shape(min(m, n), min(m, n)))
        
        # For full SVD we'd compute U = A V S^-1
        # But for simplicity, return identity matrix for U
        u = eye(m)
        
        return u, s, v
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
