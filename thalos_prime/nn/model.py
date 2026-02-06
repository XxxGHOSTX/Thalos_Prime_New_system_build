"""
THALOS Prime - Model Module
Main transformer model and optimization utilities.
"""

from typing import Optional, List, Dict, Any, Tuple
import math
import random
from .layer import Layer, Linear, Embedding, PositionalEncoding
from .transformer import TransformerDecoder, TransformerEncoder
from ..math.tensor import Tensor, Shape, zeros
from ..math.activations import Activations


class THALOSPrimeModel(Layer):
    """Main THALOS Prime transformer model."""
    
    def __init__(self, 
                 vocab_size: int = 50000,
                 d_model: int = 512,
                 num_heads: int = 8,
                 num_layers: int = 6,
                 d_ff: int = 2048,
                 max_seq_len: int = 2048,
                 dropout: float = 0.1):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.d_ff = d_ff
        self.max_seq_len = max_seq_len
        
        # Embedding layers
        self.token_embedding = Embedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_seq_len)
        
        # Transformer decoder
        self.decoder = TransformerDecoder(num_layers, d_model, num_heads, d_ff, dropout)
        
        # Output projection
        self.output_projection = Linear(d_model, vocab_size)
        
        # Collect parameters
        self._parameters.update(self.token_embedding._parameters)
        self._parameters.update(self.decoder._parameters)
        self._parameters.update(self.output_projection._parameters)
    
    def forward(self, input_ids: Tensor) -> Tensor:
        """Forward pass through the model."""
        # Token embeddings
        x = self.token_embedding(input_ids)
        
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Transformer decoder
        x = self.decoder(x)
        
        # Output projection to vocabulary
        logits = self.output_projection(x)
        
        return logits
    
    def generate(self, input_ids: Tensor, max_length: int = 100,
                 temperature: float = 1.0, top_k: int = 50,
                 top_p: float = 0.9) -> List[int]:
        """Autoregressive text generation."""
        self.eval()
        
        generated = list(int(x) for x in input_ids.data)
        
        for _ in range(max_length):
            # Get logits for last position
            x = Tensor([float(x) for x in generated])
            logits = self.forward(x)
            
            # Get logits for last token
            last_logits_start = (len(generated) - 1) * self.vocab_size
            last_logits = logits.data[last_logits_start:last_logits_start + self.vocab_size]
            
            # Apply temperature
            if temperature != 1.0:
                last_logits = [l / temperature for l in last_logits]
            
            # Top-K filtering
            if top_k > 0:
                sorted_indices = sorted(range(len(last_logits)), 
                                        key=lambda i: last_logits[i], reverse=True)
                for i in sorted_indices[top_k:]:
                    last_logits[i] = -1e9
            
            # Top-P (nucleus) filtering
            if top_p < 1.0:
                sorted_probs = sorted(enumerate(last_logits), 
                                     key=lambda x: x[1], reverse=True)
                cumsum = 0.0
                max_val = max(last_logits)
                exp_vals = [math.exp(l - max_val) for l in last_logits]
                sum_exp = sum(exp_vals)
                probs = [e / sum_exp for e in exp_vals]
                
                for i, (idx, _) in enumerate(sorted_probs):
                    cumsum += probs[idx]
                    if cumsum > top_p:
                        for j in range(i + 1, len(sorted_probs)):
                            last_logits[sorted_probs[j][0]] = -1e9
                        break
            
            # Sample from distribution
            max_val = max(last_logits)
            exp_vals = [math.exp(l - max_val) for l in last_logits]
            sum_exp = sum(exp_vals)
            probs = [e / sum_exp for e in exp_vals]
            
            # Sample token
            r = random.random()
            cumsum = 0.0
            next_token = 0
            for i, p in enumerate(probs):
                cumsum += p
                if r <= cumsum:
                    next_token = i
                    break
            
            generated.append(next_token)
            
            # Check for end token (typically 3 for <EOS>)
            if next_token == 3:
                break
        
        return generated
    
    def get_num_parameters(self) -> int:
        """Get total number of parameters."""
        total = 0
        for param in self.parameters():
            total += len(param.data)
        return total


class ModelOptimizer:
    """Adam optimizer for model training."""
    
    def __init__(self, parameters: List[Tensor], lr: float = 0.001,
                 betas: Tuple[float, float] = (0.9, 0.999),
                 eps: float = 1e-8, weight_decay: float = 0.0):
        self.parameters = parameters
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        
        # Initialize momentum and velocity
        self.m = [zeros(*p.shape.dims) for p in parameters]
        self.v = [zeros(*p.shape.dims) for p in parameters]
        self.t = 0
    
    def step(self, gradients: List[Tensor]) -> None:
        """Update parameters using gradients."""
        self.t += 1
        
        for i, (param, grad) in enumerate(zip(self.parameters, gradients)):
            if grad is None:
                continue
            
            # Update momentum
            for j in range(len(param.data)):
                self.m[i].data[j] = self.beta1 * self.m[i].data[j] + (1 - self.beta1) * grad.data[j]
                self.v[i].data[j] = self.beta2 * self.v[i].data[j] + (1 - self.beta2) * grad.data[j] ** 2
            
            # Bias correction
            m_hat = [m / (1 - self.beta1 ** self.t) for m in self.m[i].data]
            v_hat = [v / (1 - self.beta2 ** self.t) for v in self.v[i].data]
            
            # Update parameters
            for j in range(len(param.data)):
                # Weight decay
                if self.weight_decay > 0:
                    param.data[j] -= self.lr * self.weight_decay * param.data[j]
                
                # Adam update
                param.data[j] -= self.lr * m_hat[j] / (math.sqrt(v_hat[j]) + self.eps)
    
    def zero_grad(self) -> None:
        """Reset gradients (placeholder - gradients handled externally)."""
        pass


class LossFunction:
    """Cross-entropy loss function."""
    
    @staticmethod
    def cross_entropy(logits: Tensor, targets: Tensor, 
                      ignore_index: int = -100) -> Tensor:
        """Compute cross-entropy loss."""
        seq_len = len(targets.data)
        vocab_size = len(logits.data) // seq_len
        
        total_loss = 0.0
        count = 0
        
        for i in range(seq_len):
            target = int(targets.data[i])
            if target == ignore_index:
                continue
            
            # Get logits for this position
            pos_logits = logits.data[i * vocab_size:(i + 1) * vocab_size]
            
            # Log-softmax
            max_logit = max(pos_logits)
            log_sum_exp = max_logit + math.log(sum(math.exp(l - max_logit) for l in pos_logits))
            log_prob = pos_logits[target] - log_sum_exp
            
            total_loss -= log_prob
            count += 1
        
        return Tensor(total_loss / max(count, 1))
    
    @staticmethod
    def mse(predictions: Tensor, targets: Tensor) -> Tensor:
        """Mean squared error loss."""
        total = 0.0
        for p, t in zip(predictions.data, targets.data):
            total += (p - t) ** 2
        return Tensor(total / len(predictions.data))


class LearningRateScheduler:
    """Learning rate scheduler with warmup."""
    
    def __init__(self, optimizer: ModelOptimizer, warmup_steps: int = 4000,
                 d_model: int = 512):
        self.optimizer = optimizer
        self.warmup_steps = warmup_steps
        self.d_model = d_model
        self.current_step = 0
        self.base_lr = optimizer.lr
    
    def step(self) -> float:
        """Update learning rate and return new value."""
        self.current_step += 1
        
        # Transformer warmup schedule
        lr = self.base_lr * min(
            self.current_step ** (-0.5),
            self.current_step * self.warmup_steps ** (-1.5)
        ) * (self.d_model ** (-0.5))
        
        self.optimizer.lr = lr
        return lr


class KVCache:
    """Key-value cache for efficient generation."""
    
    def __init__(self, num_layers: int, max_seq_len: int, d_model: int, num_heads: int):
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.keys: List[Optional[Tensor]] = [None] * num_layers
        self.values: List[Optional[Tensor]] = [None] * num_layers
        self.seq_len = 0
    
    def update(self, layer_idx: int, new_key: Tensor, new_value: Tensor) -> Tuple[Tensor, Tensor]:
        """Update cache and return combined keys/values."""
        if self.keys[layer_idx] is None:
            self.keys[layer_idx] = new_key
            self.values[layer_idx] = new_value
        else:
            # Concatenate new keys/values
            old_k = self.keys[layer_idx]
            old_v = self.values[layer_idx]
            
            new_k_data = old_k.data + new_key.data
            new_v_data = old_v.data + new_value.data
            
            old_seq = old_k.shape.dims[0]
            new_seq = old_seq + new_key.shape.dims[0]
            
            self.keys[layer_idx] = Tensor(new_k_data, Shape((new_seq, self.d_model)))
            self.values[layer_idx] = Tensor(new_v_data, Shape((new_seq, self.d_model)))
        
        self.seq_len = self.keys[layer_idx].shape.dims[0]
        return self.keys[layer_idx], self.values[layer_idx]
    
    def clear(self) -> None:
        """Clear the cache."""
        self.keys = [None] * self.num_layers
        self.values = [None] * self.num_layers
        self.seq_len = 0
