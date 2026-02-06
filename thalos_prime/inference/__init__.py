"""
THALOS Prime - Inference Module
Text generation pipeline and inference utilities.
"""

from typing import Optional, List, Dict, Any, Callable
import math
import random


class TextGenerator:
    """Text generation with various sampling strategies."""
    
    def __init__(self, vocab_size: int = 50000):
        self.vocab_size = vocab_size
    
    def sample_token(self, logits: List[float], temperature: float = 1.0,
                     top_k: int = 0, top_p: float = 1.0) -> int:
        """Sample a token from logits."""
        # Apply temperature
        if temperature != 1.0:
            logits = [l / temperature for l in logits]
        
        # Top-K filtering
        if top_k > 0:
            sorted_indices = sorted(range(len(logits)), 
                                    key=lambda i: logits[i], reverse=True)
            for i in sorted_indices[top_k:]:
                logits[i] = -float('inf')
        
        # Top-P (nucleus) filtering
        if top_p < 1.0:
            sorted_pairs = sorted(enumerate(logits), key=lambda x: x[1], reverse=True)
            
            # Compute softmax probabilities
            max_logit = max(l for l in logits if l != -float('inf'))
            exp_vals = [math.exp(l - max_logit) if l != -float('inf') else 0 
                        for l in logits]
            sum_exp = sum(exp_vals)
            probs = [e / sum_exp for e in exp_vals]
            
            cumsum = 0.0
            for idx, _ in sorted_pairs:
                cumsum += probs[idx]
                if cumsum > top_p:
                    # Mask remaining tokens
                    break
            
            for i, (idx, _) in enumerate(sorted_pairs):
                if cumsum > top_p and i > 0:
                    logits[idx] = -float('inf')
        
        # Convert to probabilities
        max_logit = max(l for l in logits if l != -float('inf'))
        exp_vals = [math.exp(l - max_logit) if l != -float('inf') else 0 
                    for l in logits]
        sum_exp = sum(exp_vals)
        probs = [e / sum_exp for e in exp_vals]
        
        # Sample from distribution
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i
        
        return len(probs) - 1
    
    def greedy_decode(self, logits: List[float]) -> int:
        """Greedy decoding - select most likely token."""
        return max(range(len(logits)), key=lambda i: logits[i])
    
    def beam_search(self, logits_fn: Callable[[List[int]], List[float]],
                    input_ids: List[int], beam_width: int = 5,
                    max_length: int = 100) -> List[int]:
        """Beam search decoding."""
        beams = [(input_ids.copy(), 0.0)]  # (sequence, log_prob)
        
        for _ in range(max_length):
            new_beams = []
            
            for seq, log_prob in beams:
                # Get logits for this sequence
                logits = logits_fn(seq)
                
                # Get top-k tokens
                top_indices = sorted(range(len(logits)), 
                                     key=lambda i: logits[i], reverse=True)[:beam_width]
                
                for idx in top_indices:
                    new_seq = seq + [idx]
                    # Compute log probability
                    max_l = max(logits)
                    log_sum_exp = max_l + math.log(sum(math.exp(l - max_l) for l in logits))
                    token_log_prob = logits[idx] - log_sum_exp
                    new_log_prob = log_prob + token_log_prob
                    
                    new_beams.append((new_seq, new_log_prob))
            
            # Keep top beams
            new_beams.sort(key=lambda x: x[1], reverse=True)
            beams = new_beams[:beam_width]
            
            # Check for end token
            if all(seq[-1] == 3 for seq, _ in beams):  # 3 = <EOS>
                break
        
        return beams[0][0]


class InferencePipeline:
    """End-to-end inference pipeline."""
    
    def __init__(self, model=None, tokenizer=None):
        self.model = model
        self.tokenizer = tokenizer
        self.generator = TextGenerator()
    
    def generate(self, prompt: str, max_length: int = 100,
                 temperature: float = 1.0, top_k: int = 50,
                 top_p: float = 0.9, **kwargs) -> str:
        """Generate text from prompt."""
        if self.model is None:
            return self._generate_dummy(prompt, max_length)
        
        # Tokenize input
        if self.tokenizer:
            input_ids = self.tokenizer.encode(prompt)
        else:
            input_ids = [ord(c) % 100 for c in prompt]
        
        # Generate tokens
        generated_ids = input_ids.copy()
        
        for _ in range(max_length):
            # Get model output
            from ..math.tensor import Tensor
            logits = self.model.forward(Tensor([float(x) for x in generated_ids]))
            
            # Get logits for last position
            last_pos = len(generated_ids) - 1
            vocab_size = self.model.vocab_size
            last_logits = logits.data[last_pos * vocab_size:(last_pos + 1) * vocab_size]
            
            # Sample next token
            next_token = self.generator.sample_token(
                last_logits, temperature, top_k, top_p
            )
            
            generated_ids.append(next_token)
            
            if next_token == 3:  # <EOS>
                break
        
        # Decode
        if self.tokenizer:
            return self.tokenizer.decode(generated_ids)
        else:
            return ''.join(chr(min(x, 127)) for x in generated_ids if 32 <= x <= 126)
    
    def _generate_dummy(self, prompt: str, max_length: int) -> str:
        """Generate dummy response when no model is available."""
        responses = [
            "This is a generated response based on your input.",
            "I understand your query and am processing it.",
            "Based on the prompt, here is my generated output.",
        ]
        import random
        return f"{prompt}\n\n{random.choice(responses)}"
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        if self.tokenizer:
            return self.tokenizer.encode(text)
        return [ord(c) % 100 for c in text]
    
    def decode(self, ids: List[int]) -> str:
        """Decode token IDs to text."""
        if self.tokenizer:
            return self.tokenizer.decode(ids)
        return ''.join(chr(min(x + 32, 126)) for x in ids)


class StreamingGenerator:
    """Stream tokens during generation."""
    
    def __init__(self, pipeline: InferencePipeline):
        self.pipeline = pipeline
    
    def generate_stream(self, prompt: str, max_length: int = 100,
                        **kwargs):
        """Yield tokens as they are generated."""
        # Simplified streaming - just yield chunks
        response = self.pipeline.generate(prompt, max_length, **kwargs)
        
        # Simulate streaming
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]


# Export classes
__all__ = [
    'TextGenerator',
    'InferencePipeline',
    'StreamingGenerator',
]
