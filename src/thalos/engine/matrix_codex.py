"""
Matrix Codex Engine for THALOS Prime
Advanced 3D matrix visualization and processing system
"""
import time
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MatrixCell:
    """Represents a single cell in the matrix"""
    x: int
    y: int
    z: int
    value: float
    intensity: float
    age: int = 0


class MatrixCodex:
    """
    Matrix Codex Engine - Creates dynamic 3D matrix visualizations
    with cascading effects and data processing capabilities
    """
    
    def __init__(self, dimensions: Tuple[int, int, int] = (512, 512, 512),
                 complexity: int = 3, quality: str = "high"):
        self.dimensions = dimensions
        self.complexity = complexity
        self.quality = quality
        self.cells: List[MatrixCell] = []
        self.frame_count = 0
        self.running = False
        self.update_interval = 1.0 / 60.0  # 60 FPS
        self._initialize_matrix()
    
    def _initialize_matrix(self):
        """Initialize the matrix with initial cells"""
        w, h, d = self.dimensions
        # Create initial cells based on complexity
        num_cells = min(1000 * self.complexity, w * h * d // 100)
        
        for _ in range(num_cells):
            cell = MatrixCell(
                x=random.randint(0, w - 1),
                y=random.randint(0, h - 1),
                z=random.randint(0, d - 1),
                value=random.random(),
                intensity=random.random()
            )
            self.cells.append(cell)
    
    def start(self):
        """Start the matrix engine"""
        self.running = True
        self._log("Matrix Codex Engine started")
    
    def stop(self):
        """Stop the matrix engine"""
        self.running = False
        self._log("Matrix Codex Engine stopped")
    
    def update(self):
        """Update matrix state for one frame"""
        if not self.running:
            return
        
        self.frame_count += 1
        
        # Update existing cells
        for cell in self.cells:
            cell.age += 1
            # Gravity effect - cells fall
            cell.y = (cell.y + 1) % self.dimensions[1]
            # Fade out over time
            cell.intensity *= 0.98
        
        # Remove old cells
        self.cells = [cell for cell in self.cells if cell.intensity > 0.01]
        
        # Spawn new cells based on complexity
        spawn_rate = self.complexity * 2
        for _ in range(spawn_rate):
            if random.random() < 0.3:  # 30% spawn chance
                cell = MatrixCell(
                    x=random.randint(0, self.dimensions[0] - 1),
                    y=0,  # Spawn at top
                    z=random.randint(0, self.dimensions[2] - 1),
                    value=random.random(),
                    intensity=1.0
                )
                self.cells.append(cell)
        
        # Limit total cells
        max_cells = 5000 * self.complexity
        if len(self.cells) > max_cells:
            # Keep the brightest cells
            self.cells.sort(key=lambda c: c.intensity, reverse=True)
            self.cells = self.cells[:max_cells]
    
    def process_data(self, data: List[float]) -> List[float]:
        """
        Process data through the matrix codex
        Applies matrix transformations and effects
        """
        if not data:
            return []
        
        # Apply matrix transformations
        processed = []
        for i, value in enumerate(data):
            # Use nearby cells to influence processing
            influence = self._get_cell_influence(i)
            transformed = value * (1.0 + 0.1 * influence)
            processed.append(transformed)
        
        return processed
    
    def _get_cell_influence(self, index: int) -> float:
        """Get influence from nearby cells"""
        if not self.cells:
            return 0.0
        
        # Sample a few nearby cells
        nearby = min(10, len(self.cells))
        total_influence = sum(cell.intensity for cell in self.cells[:nearby])
        return total_influence / nearby
    
    def get_visualization_data(self) -> List[dict]:
        """Get current matrix state for visualization"""
        return [
            {
                'position': [cell.x, cell.y, cell.z],
                'intensity': cell.intensity,
                'value': cell.value,
                'age': cell.age
            }
            for cell in self.cells
        ]
    
    def get_stats(self) -> dict:
        """Get engine statistics"""
        return {
            'frame_count': self.frame_count,
            'active_cells': len(self.cells),
            'dimensions': self.dimensions,
            'complexity': self.complexity,
            'running': self.running
        }
    
    def _log(self, message: str):
        """Internal logging"""
        print(f"[MatrixCodex] {message}")


class MatrixRenderer:
    """Handles rendering of the matrix codex"""
    
    def __init__(self, codex: MatrixCodex):
        self.codex = codex
        self.render_quality = codex.quality
    
    def render_ascii(self, width: int = 80, height: int = 24) -> str:
        """Render matrix as ASCII art for terminal"""
        # Create 2D projection
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Project 3D cells onto 2D grid
        for cell in self.codex.cells:
            x = int((cell.x / self.codex.dimensions[0]) * (width - 1))
            y = int((cell.y / self.codex.dimensions[1]) * (height - 1))
            
            if 0 <= x < width and 0 <= y < height:
                # Choose character based on intensity
                if cell.intensity > 0.7:
                    grid[y][x] = '#'
                elif cell.intensity > 0.4:
                    grid[y][x] = '*'
                elif cell.intensity > 0.2:
                    grid[y][x] = '.'
                else:
                    grid[y][x] = ','
        
        return '\n'.join(''.join(row) for row in grid)
    
    def render_stats(self) -> str:
        """Render statistics"""
        stats = self.codex.get_stats()
        return (
            f"Frame: {stats['frame_count']} | "
            f"Cells: {stats['active_cells']} | "
            f"Complexity: {stats['complexity']}"
        )
