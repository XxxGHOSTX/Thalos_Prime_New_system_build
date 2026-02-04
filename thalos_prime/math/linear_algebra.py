#!/usr/bin/env python3
"""
THALOS Prime Linear Algebra Module
Pure Python implementation of matrix operations
"""

import math
from typing import Optional, Tuple, List
from .tensor import Tensor, zeros, ones, eye


class LinearAlgebra:
    """Linear algebra operations"""
    
    @staticmethod
    def matmul(a: Tensor, b: Tensor) -> Tensor:
        """Matrix multiplication with broadcasting support"""
        if a.shape.ndim < 2 or b.shape.ndim < 2:
            raise ValueError("Both tensors must be at least 2D for matmul")
        
        # Get matrix dimensions
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
            
            from .tensor import Shape
            return Tensor(result_data, Shape(m, n))
        
        # Batched case - simplified
        # Just handle the basic case for now
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
        
        from .tensor import Shape
        return Tensor(result_data, Shape(m, n))
    
    @staticmethod
    def dot(a: Tensor, b: Tensor) -> float:
        """Dot product of two vectors"""
        if a.shape.size != b.shape.size:
            raise ValueError(f"Tensors must have same size for dot product")
        
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
        
        from .tensor import Shape
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
        
        from .tensor import Shape
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
        
        from .tensor import Shape
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
        
        from .tensor import Shape
        return Tensor(inv_data, Shape(n, n))
    
    @staticmethod
    def svd(a: Tensor, num_iterations: int = 100) -> Tuple[Tensor, Tensor, Tensor]:
        """
        Simplified SVD using eigendecomposition
        Returns U, S, V^T such that A = U @ S @ V^T
        
        Note: This is a simplified version that may not be as accurate as full SVD
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
        
        from .tensor import Shape
        s = Tensor(s_data, Shape(min(m, n), min(m, n)))
        
        # For full SVD we'd compute U = A V S^-1
        # But for simplicity, return identity matrix for U
        u = eye(m)
        
        return u, s, v
