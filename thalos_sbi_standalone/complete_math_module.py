"""
THALOS SBI Standalone - Complete Math Module
Extended mathematical operations and utilities.
"""

from typing import List, Tuple, Optional, Union
import math


class ExtendedMath:
    """Extended mathematical operations."""
    
    @staticmethod
    def factorial(n: int) -> int:
        """Compute factorial."""
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def combination(n: int, k: int) -> int:
        """Compute n choose k."""
        if k > n or k < 0:
            return 0
        return ExtendedMath.factorial(n) // (ExtendedMath.factorial(k) * ExtendedMath.factorial(n - k))
    
    @staticmethod
    def permutation(n: int, k: int) -> int:
        """Compute n permute k."""
        if k > n or k < 0:
            return 0
        return ExtendedMath.factorial(n) // ExtendedMath.factorial(n - k)
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Greatest common divisor."""
        while b:
            a, b = b, a % b
        return abs(a)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Least common multiple."""
        return abs(a * b) // ExtendedMath.gcd(a, b)
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def prime_factors(n: int) -> List[int]:
        """Get prime factors."""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """Compute nth Fibonacci number."""
        if n <= 0:
            return 0
        if n == 1:
            return 1
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


class VectorMath:
    """Vector mathematical operations."""
    
    @staticmethod
    def dot(v1: List[float], v2: List[float]) -> float:
        """Dot product."""
        return sum(a * b for a, b in zip(v1, v2))
    
    @staticmethod
    def cross(v1: List[float], v2: List[float]) -> List[float]:
        """Cross product (3D vectors)."""
        if len(v1) != 3 or len(v2) != 3:
            raise ValueError("Cross product requires 3D vectors")
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]
    
    @staticmethod
    def magnitude(v: List[float]) -> float:
        """Vector magnitude."""
        return math.sqrt(sum(x ** 2 for x in v))
    
    @staticmethod
    def normalize(v: List[float]) -> List[float]:
        """Normalize vector."""
        mag = VectorMath.magnitude(v)
        return [x / mag for x in v] if mag > 0 else v
    
    @staticmethod
    def angle(v1: List[float], v2: List[float]) -> float:
        """Angle between vectors in radians."""
        dot = VectorMath.dot(v1, v2)
        mag1 = VectorMath.magnitude(v1)
        mag2 = VectorMath.magnitude(v2)
        if mag1 == 0 or mag2 == 0:
            return 0.0
        cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
        return math.acos(cos_angle)


class StatisticalMath:
    """Statistical mathematical operations."""
    
    @staticmethod
    def mean(data: List[float]) -> float:
        """Calculate mean."""
        return sum(data) / len(data) if data else 0
    
    @staticmethod
    def median(data: List[float]) -> float:
        """Calculate median."""
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n == 0:
            return 0
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        return sorted_data[mid]
    
    @staticmethod
    def mode(data: List[float]) -> float:
        """Calculate mode."""
        if not data:
            return 0
        counts = {}
        for x in data:
            counts[x] = counts.get(x, 0) + 1
        return max(counts.keys(), key=lambda k: counts[k])
    
    @staticmethod
    def variance(data: List[float]) -> float:
        """Calculate variance."""
        if len(data) < 2:
            return 0
        m = StatisticalMath.mean(data)
        return sum((x - m) ** 2 for x in data) / (len(data) - 1)
    
    @staticmethod
    def std_dev(data: List[float]) -> float:
        """Calculate standard deviation."""
        return math.sqrt(StatisticalMath.variance(data))
    
    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        mean_x = StatisticalMath.mean(x)
        mean_y = StatisticalMath.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        
        if denom_x == 0 or denom_y == 0:
            return 0
        
        return numerator / (denom_x * denom_y)


# Export classes
__all__ = [
    'ExtendedMath',
    'VectorMath',
    'StatisticalMath'
]
