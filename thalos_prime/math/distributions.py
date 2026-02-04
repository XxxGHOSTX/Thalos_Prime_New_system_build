"""
Probability distributions for THALOS Prime
"""
import random
import math
from .tensor import Tensor


class Distributions:
    """Probability distributions"""
    
    @staticmethod
    def normal(mean=0, std=1, size=None):
        """Normal distribution"""
        if size is None:
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            return mean + std * z
        else:
            data = []
            for _ in range(size):
                u1 = random.random()
                u2 = random.random()
                z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
                data.append(mean + std * z)
            return Tensor(data, (size,))
    
    @staticmethod
    def uniform(low=0, high=1, size=None):
        """Uniform distribution"""
        if size is None:
            return low + (high - low) * random.random()
        else:
            data = [low + (high - low) * random.random() for _ in range(size)]
            return Tensor(data, (size,))
    
    @staticmethod
    def xavier_uniform(fan_in, fan_out):
        """Xavier/Glorot uniform initialization"""
        limit = math.sqrt(6 / (fan_in + fan_out))
        size = fan_in * fan_out
        data = [random.uniform(-limit, limit) for _ in range(size)]
        return Tensor(data, (fan_in, fan_out))
