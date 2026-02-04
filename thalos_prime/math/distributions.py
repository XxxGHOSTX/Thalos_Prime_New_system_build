"""
THALOS Prime - Probability Distributions Module
Random sampling and initialization schemes.
"""

from typing import Tuple, Optional
import math
import random
from .tensor import Tensor, Shape


class Distributions:
    """Probability distributions for sampling."""
    
    @staticmethod
    def normal(mean: float = 0.0, std: float = 1.0, size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from normal distribution using Box-Muller transform."""
        numel = 1
        for d in size:
            numel *= d
        
        data = []
        for _ in range(numel):
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
            data.append(mean + std * z)
        
        return Tensor(data, Shape(size))
    
    @staticmethod
    def uniform(low: float = 0.0, high: float = 1.0, size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from uniform distribution."""
        numel = 1
        for d in size:
            numel *= d
        
        data = [random.uniform(low, high) for _ in range(numel)]
        return Tensor(data, Shape(size))
    
    @staticmethod
    def truncated_normal(mean: float = 0.0, std: float = 1.0, 
                         low: float = -2.0, high: float = 2.0,
                         size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from truncated normal distribution."""
        numel = 1
        for d in size:
            numel *= d
        
        data = []
        for _ in range(numel):
            while True:
                u1 = random.random()
                u2 = random.random()
                z = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
                val = mean + std * z
                if low <= val <= high:
                    data.append(val)
                    break
        
        return Tensor(data, Shape(size))
    
    @staticmethod
    def exponential(rate: float = 1.0, size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from exponential distribution."""
        numel = 1
        for d in size:
            numel *= d
        
        data = [-math.log(max(random.random(), 1e-10)) / rate for _ in range(numel)]
        return Tensor(data, Shape(size))
    
    @staticmethod
    def gamma(shape: float, scale: float = 1.0, size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from gamma distribution using Marsaglia and Tsang's method."""
        numel = 1
        for d in size:
            numel *= d
        
        data = []
        for _ in range(numel):
            if shape >= 1:
                d = shape - 1/3
                c = 1 / math.sqrt(9 * d)
                while True:
                    x = Distributions._standard_normal()
                    v = (1 + c * x) ** 3
                    if v > 0:
                        u = random.random()
                        if u < 1 - 0.0331 * (x ** 2) ** 2:
                            data.append(d * v * scale)
                            break
                        if math.log(u) < 0.5 * x ** 2 + d * (1 - v + math.log(v)):
                            data.append(d * v * scale)
                            break
            else:
                # For shape < 1, use shape + 1 and adjust
                val = Distributions.gamma(shape + 1, 1.0, (1,)).data[0]
                data.append(val * random.random() ** (1 / shape) * scale)
        
        return Tensor(data, Shape(size))
    
    @staticmethod
    def _standard_normal() -> float:
        """Generate standard normal sample."""
        u1 = random.random()
        u2 = random.random()
        return math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
    
    @staticmethod
    def bernoulli(p: float = 0.5, size: Tuple[int, ...] = (1,)) -> Tensor:
        """Sample from Bernoulli distribution."""
        numel = 1
        for d in size:
            numel *= d
        
        data = [1.0 if random.random() < p else 0.0 for _ in range(numel)]
        return Tensor(data, Shape(size))
    
    @staticmethod
    def categorical(probs: Tensor) -> int:
        """Sample from categorical distribution."""
        cumsum = 0.0
        u = random.random()
        for i, p in enumerate(probs.data):
            cumsum += p
            if u <= cumsum:
                return i
        return len(probs.data) - 1


class Initializers:
    """Weight initialization schemes."""
    
    @staticmethod
    def xavier_uniform(fan_in: int, fan_out: int, size: Tuple[int, ...]) -> Tensor:
        """Xavier/Glorot uniform initialization."""
        limit = math.sqrt(6.0 / (fan_in + fan_out))
        return Distributions.uniform(-limit, limit, size)
    
    @staticmethod
    def xavier_normal(fan_in: int, fan_out: int, size: Tuple[int, ...]) -> Tensor:
        """Xavier/Glorot normal initialization."""
        std = math.sqrt(2.0 / (fan_in + fan_out))
        return Distributions.normal(0.0, std, size)
    
    @staticmethod
    def he_uniform(fan_in: int, size: Tuple[int, ...]) -> Tensor:
        """He uniform initialization (for ReLU)."""
        limit = math.sqrt(6.0 / fan_in)
        return Distributions.uniform(-limit, limit, size)
    
    @staticmethod
    def he_normal(fan_in: int, size: Tuple[int, ...]) -> Tensor:
        """He normal initialization (for ReLU)."""
        std = math.sqrt(2.0 / fan_in)
        return Distributions.normal(0.0, std, size)
    
    @staticmethod
    def lecun_uniform(fan_in: int, size: Tuple[int, ...]) -> Tensor:
        """LeCun uniform initialization."""
        limit = math.sqrt(3.0 / fan_in)
        return Distributions.uniform(-limit, limit, size)
    
    @staticmethod
    def lecun_normal(fan_in: int, size: Tuple[int, ...]) -> Tensor:
        """LeCun normal initialization."""
        std = math.sqrt(1.0 / fan_in)
        return Distributions.normal(0.0, std, size)
    
    @staticmethod
    def orthogonal(rows: int, cols: int) -> Tensor:
        """Orthogonal initialization."""
        # Generate random matrix
        flat = [Distributions._standard_normal() for _ in range(rows * cols)]
        
        # Simple Gram-Schmidt for small matrices
        if rows <= cols:
            # QR on random matrix
            q = []
            for i in range(rows):
                v = flat[i * cols:(i + 1) * cols]
                for j in range(i):
                    dot = sum(q[j][k] * v[k] for k in range(cols))
                    v = [v[k] - dot * q[j][k] for k in range(cols)]
                norm = math.sqrt(sum(x ** 2 for x in v))
                if norm > 1e-10:
                    v = [x / norm for x in v]
                q.append(v)
            flat = [x for row in q for x in row]
        
        return Tensor(flat, Shape((rows, cols)))


class Dropout:
    """Dropout regularization."""
    
    def __init__(self, p: float = 0.5):
        self.p = p
        self.training = True
    
    def forward(self, x: Tensor) -> Tensor:
        """Apply dropout."""
        if not self.training or self.p == 0:
            return x
        
        scale = 1.0 / (1.0 - self.p)
        mask = [scale if random.random() > self.p else 0.0 for _ in x.data]
        return Tensor([v * m for v, m in zip(x.data, mask)], x.shape)
    
    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)
    
    def eval(self):
        self.training = False
        return self
    
    def train(self):
        self.training = True
        return self


class ProbabilityFunctions:
    """Probability density and related functions."""
    
    @staticmethod
    def normal_pdf(x: Tensor, mean: float = 0.0, std: float = 1.0) -> Tensor:
        """Normal probability density function."""
        coef = 1.0 / (std * math.sqrt(2 * math.pi))
        return Tensor([coef * math.exp(-0.5 * ((v - mean) / std) ** 2) for v in x.data], x.shape)
    
    @staticmethod
    def normal_log_pdf(x: Tensor, mean: float = 0.0, std: float = 1.0) -> Tensor:
        """Log of normal probability density function."""
        log_coef = -math.log(std) - 0.5 * math.log(2 * math.pi)
        return Tensor([log_coef - 0.5 * ((v - mean) / std) ** 2 for v in x.data], x.shape)
    
    @staticmethod
    def uniform_pdf(x: Tensor, low: float = 0.0, high: float = 1.0) -> Tensor:
        """Uniform probability density function."""
        density = 1.0 / (high - low)
        return Tensor([density if low <= v <= high else 0.0 for v in x.data], x.shape)
    
    @staticmethod
    def bernoulli_log_prob(x: Tensor, p: float) -> Tensor:
        """Log probability of Bernoulli distribution."""
        return Tensor([math.log(p + 1e-10) if v > 0.5 else math.log(1 - p + 1e-10) for v in x.data], x.shape)
    
    @staticmethod
    def kl_divergence(p: Tensor, q: Tensor) -> float:
        """KL divergence between two distributions."""
        kl = 0.0
        for p_i, q_i in zip(p.data, q.data):
            if p_i > 0 and q_i > 0:
                kl += p_i * (math.log(p_i) - math.log(q_i))
        return kl
    
    @staticmethod
    def entropy(p: Tensor) -> float:
        """Entropy of a distribution."""
        return -sum(p_i * math.log(p_i + 1e-10) for p_i in p.data if p_i > 0)
