#!/usr/bin/env python3
"""
THALOS Prime - Matrix Codex Integration
Integration layer for matrix codex operations.
"""

from matrix_codex import MatrixCodex
from typing import Dict, Any


class MatrixCodexIntegration:
    """Integration layer for matrix codex."""
    
    def __init__(self):
        self.matrices: Dict[str, MatrixCodex] = {}
        self.operations_log = []
    
    def create_matrix(self, name: str, data: list) -> MatrixCodex:
        """Create and register a matrix."""
        matrix = MatrixCodex.from_list(data)
        self.matrices[name] = matrix
        self.operations_log.append(f"Created matrix: {name}")
        return matrix
    
    def multiply_matrices(self, name1: str, name2: str, result_name: str) -> MatrixCodex:
        """Multiply two matrices and store result."""
        m1 = self.matrices.get(name1)
        m2 = self.matrices.get(name2)
        
        if m1 is None or m2 is None:
            raise ValueError("Matrix not found")
        
        result = m1.multiply(m2)
        self.matrices[result_name] = result
        self.operations_log.append(f"Multiplied {name1} x {name2} = {result_name}")
        return result
    
    def get_log(self) -> list:
        """Get operations log."""
        return self.operations_log


def main():
    integration = MatrixCodexIntegration()
    integration.create_matrix("A", [[1, 2], [3, 4]])
    integration.create_matrix("B", [[5, 6], [7, 8]])
    integration.multiply_matrices("A", "B", "C")
    print("Operations:", integration.get_log())


if __name__ == '__main__':
    main()
