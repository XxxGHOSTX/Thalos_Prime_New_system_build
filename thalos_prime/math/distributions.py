#!/usr/bin/env python3
"""
THALOS Prime Distributions Module
Pure Python implementation of probability distributions and initialization methods
"""

import math
import random
from typing import Optional
from .tensor import Tensor, zeros, ones


class Distributions:
    """Probability distributions and initialization methods"""
    
    @staticmethod
    def normal(mean: float = 0.0, std: float = 1.0, size: int = 1) -> Tensor:
        """
        Sample from normal distribution using Box-Muller transform
        
        Args:
            mean: Mean of distribution
            std: Standard deviation
            size: Number of samples
        """
        samples = []
        for _ in range((size + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            
            # Box-Muller transform
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
            
            samples.append(mean + z0 * std)
            samples.append(mean + z1 * std)
        
        from .tensor import Shape
        return Tensor(samples[:size], Shape(size))
    
    @staticmethod
    def uniform(low: float = 0.0, high: float = 1.0, size: int = 1) -> Tensor:
        """
        Sample from uniform distribution
        
        Args:
            low: Lower bound
            high: Upper bound
            size: Number of samples
        """
        samples = [low + random.random() * (high - low) for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(size))
    
    @staticmethod
    def truncated_normal(mean: float = 0.0, std: float = 1.0, 
                        low: float = -2.0, high: float = 2.0, 
                        size: int = 1) -> Tensor:
        """
        Sample from truncated normal distribution
        Uses rejection sampling
        
        Args:
            mean: Mean of distribution
            std: Standard deviation
            low: Lower truncation bound (in std units)
            high: Upper truncation bound (in std units)
            size: Number of samples
        """
        samples = []
        max_attempts = size * 10
        attempts = 0
        
        while len(samples) < size and attempts < max_attempts:
            # Generate from normal
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            
            # Accept if within bounds
            if low <= z <= high:
                samples.append(mean + z * std)
            
            attempts += 1
        
        # Fill remaining with boundary values if needed
        while len(samples) < size:
            samples.append(mean)
        
        from .tensor import Shape
        return Tensor(samples[:size], Shape(size))
    
    @staticmethod
    def exponential(rate: float = 1.0, size: int = 1) -> Tensor:
        """
        Sample from exponential distribution
        
        Args:
            rate: Rate parameter (lambda)
            size: Number of samples
        """
        samples = [-math.log(random.random()) / rate for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(size))
    
    @staticmethod
    def gamma(shape: float = 2.0, scale: float = 1.0, size: int = 1) -> Tensor:
        """
        Sample from gamma distribution using Marsaglia and Tsang method
        
        Args:
            shape: Shape parameter (k)
            scale: Scale parameter (theta)
            size: Number of samples
        """
        samples = []
        
        # Use simple method for integer shape
        if shape == int(shape):
            k = int(shape)
            for _ in range(size):
                # Sum of k exponential random variables
                s = sum(-math.log(random.random()) for _ in range(k))
                samples.append(s * scale)
        else:
            # Marsaglia and Tsang method for non-integer shape
            d = shape - 1.0/3.0
            c = 1.0 / math.sqrt(9.0 * d)
            
            for _ in range(size):
                while True:
                    # Generate from normal
                    u1 = random.random()
                    u2 = random.random()
                    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
                    
                    v = (1.0 + c * z) ** 3
                    if v > 0:
                        u = random.random()
                        if u < 1.0 - 0.0331 * z**4 or math.log(u) < 0.5 * z**2 + d * (1.0 - v + math.log(v)):
                            samples.append(d * v * scale)
                            break
        
        from .tensor import Shape
        return Tensor(samples, Shape(size))
    
    @staticmethod
    def bernoulli(p: float = 0.5, size: int = 1) -> Tensor:
        """
        Sample from Bernoulli distribution
        
        Args:
            p: Probability of 1
            size: Number of samples
        """
        samples = [1.0 if random.random() < p else 0.0 for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(size))
    
    @staticmethod
    def xavier_uniform(fan_in: int, fan_out: int) -> Tensor:
        """
        Xavier/Glorot uniform initialization
        U(-sqrt(6/(fan_in + fan_out)), sqrt(6/(fan_in + fan_out)))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        limit = math.sqrt(6.0 / (fan_in + fan_out))
        size = fan_in * fan_out
        samples = [random.uniform(-limit, limit) for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(fan_out, fan_in))
    
    @staticmethod
    def xavier_normal(fan_in: int, fan_out: int) -> Tensor:
        """
        Xavier/Glorot normal initialization
        N(0, sqrt(2/(fan_in + fan_out)))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        std = math.sqrt(2.0 / (fan_in + fan_out))
        size = fan_in * fan_out
        
        samples = []
        for _ in range((size + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
            samples.append(z0 * std)
            samples.append(z1 * std)
        
        from .tensor import Shape
        return Tensor(samples[:size], Shape(fan_out, fan_in))
    
    @staticmethod
    def he_uniform(fan_in: int, fan_out: int) -> Tensor:
        """
        He uniform initialization
        U(-sqrt(6/fan_in), sqrt(6/fan_in))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        limit = math.sqrt(6.0 / fan_in)
        size = fan_in * fan_out
        samples = [random.uniform(-limit, limit) for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(fan_out, fan_in))
    
    @staticmethod
    def he_normal(fan_in: int, fan_out: int) -> Tensor:
        """
        He normal initialization
        N(0, sqrt(2/fan_in))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        std = math.sqrt(2.0 / fan_in)
        size = fan_in * fan_out
        
        samples = []
        for _ in range((size + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
            samples.append(z0 * std)
            samples.append(z1 * std)
        
        from .tensor import Shape
        return Tensor(samples[:size], Shape(fan_out, fan_in))
    
    @staticmethod
    def lecun_uniform(fan_in: int, fan_out: int) -> Tensor:
        """
        LeCun uniform initialization
        U(-sqrt(3/fan_in), sqrt(3/fan_in))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        limit = math.sqrt(3.0 / fan_in)
        size = fan_in * fan_out
        samples = [random.uniform(-limit, limit) for _ in range(size)]
        from .tensor import Shape
        return Tensor(samples, Shape(fan_out, fan_in))
    
    @staticmethod
    def lecun_normal(fan_in: int, fan_out: int) -> Tensor:
        """
        LeCun normal initialization
        N(0, sqrt(1/fan_in))
        
        Args:
            fan_in: Number of input units
            fan_out: Number of output units
        """
        std = math.sqrt(1.0 / fan_in)
        size = fan_in * fan_out
        
        samples = []
        for _ in range((size + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
            samples.append(z0 * std)
            samples.append(z1 * std)
        
        from .tensor import Shape
        return Tensor(samples[:size], Shape(fan_out, fan_in))
    
    @staticmethod
    def orthogonal(rows: int, cols: int, gain: float = 1.0) -> Tensor:
        """
        Orthogonal initialization using QR decomposition
        
        Args:
            rows: Number of rows
            cols: Number of columns
            gain: Scaling factor
        """
        # Generate random matrix
        from .tensor import randn, Shape
        a = randn(rows, cols)
        
        # QR decomposition
        from .linear_algebra import LinearAlgebra
        try:
            q, r = LinearAlgebra.qr_decomposition(a)
            
            # Ensure diagonal of R is positive
            d = []
            for i in range(min(rows, cols)):
                d.append(1.0 if r.data[i * cols + i] >= 0 else -1.0)
            
            # Scale Q by diagonal signs
            q_data = q.data[:]
            for i in range(rows):
                for j in range(cols):
                    if j < len(d):
                        q_data[i * cols + j] *= d[j] * gain
            
            return Tensor(q_data, Shape(rows, cols))
        except Exception:
            # Fallback to xavier if QR fails
            return Distributions.xavier_normal(cols, rows)
    
    @staticmethod
    def dropout(x: Tensor, p: float = 0.5, training: bool = True) -> Tensor:
        """
        Dropout regularization
        
        Args:
            x: Input tensor
            p: Probability of dropping a unit
            training: Whether in training mode
        """
        if not training or p == 0:
            return Tensor(x.data[:], x.shape)
        
        if p == 1:
            return zeros(*x.shape.dims)
        
        # Inverted dropout
        scale = 1.0 / (1.0 - p)
        mask = [0.0 if random.random() < p else scale for _ in range(x.shape.size)]
        
        result = []
        for val, m in zip(x.data, mask):
            result.append(val * m)
        
        return Tensor(result, x.shape)
    
    @staticmethod
    def pdf_normal(x: float, mean: float = 0.0, std: float = 1.0) -> float:
        """
        Probability density function for normal distribution
        
        Args:
            x: Value to evaluate
            mean: Mean of distribution
            std: Standard deviation
        """
        coef = 1.0 / (std * math.sqrt(2.0 * math.pi))
        exponent = -0.5 * ((x - mean) / std) ** 2
        return coef * math.exp(exponent)
    
    @staticmethod
    def log_pdf_normal(x: float, mean: float = 0.0, std: float = 1.0) -> float:
        """
        Log probability density function for normal distribution
        
        Args:
            x: Value to evaluate
            mean: Mean of distribution
            std: Standard deviation
        """
        log_coef = -math.log(std) - 0.5 * math.log(2.0 * math.pi)
        log_exp = -0.5 * ((x - mean) / std) ** 2
        return log_coef + log_exp
    
    @staticmethod
    def cdf_normal(x: float, mean: float = 0.0, std: float = 1.0) -> float:
        """
        Cumulative distribution function for normal distribution
        Uses error function approximation
        
        Args:
            x: Value to evaluate
            mean: Mean of distribution
            std: Standard deviation
        """
        z = (x - mean) / (std * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))
    
    @staticmethod
    def pdf_uniform(x: float, low: float = 0.0, high: float = 1.0) -> float:
        """Probability density function for uniform distribution"""
        if low <= x <= high:
            return 1.0 / (high - low)
        return 0.0
    
    @staticmethod
    def pdf_exponential(x: float, rate: float = 1.0) -> float:
        """Probability density function for exponential distribution"""
        if x < 0:
            return 0.0
        return rate * math.exp(-rate * x)
    
    @staticmethod
    def kl_divergence_normal(mean1: float, std1: float, 
                            mean2: float, std2: float) -> float:
        """
        KL divergence between two normal distributions
        KL(N1||N2) = log(std2/std1) + (std1^2 + (mean1-mean2)^2)/(2*std2^2) - 0.5
        """
        var1 = std1 ** 2
        var2 = std2 ** 2
        
        kl = math.log(std2 / std1) + (var1 + (mean1 - mean2) ** 2) / (2.0 * var2) - 0.5
        return kl
    
    @staticmethod
    def sample_gumbel(size: int, loc: float = 0.0, scale: float = 1.0) -> Tensor:
        """
        Sample from Gumbel distribution
        Used for Gumbel-Softmax trick
        """
        samples = []
        for _ in range(size):
            u = random.random()
            # Avoid log(0)
            u = max(1e-20, min(1.0 - 1e-20, u))
            g = -math.log(-math.log(u))
            samples.append(loc + scale * g)
        
        from .tensor import Shape
        return Tensor(samples, Shape(size))
