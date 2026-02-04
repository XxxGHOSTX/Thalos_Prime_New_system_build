"""
THALOS Prime - Attention Mechanisms Module
Scaled dot-product attention and multi-head attention.
"""

from typing import Optional, Tuple
import math
from .tensor import Tensor, Shape, zeros
from .linear_algebra import LinearAlgebra
from .activations import Activations


class AttentionMechanisms:
    """Collection of attention mechanisms."""
    
    @staticmethod
    def scaled_dot_product_attention(
        query: Tensor,
        key: Tensor,
        value: Tensor,
        mask: Optional[Tensor] = None,
        dropout_p: float = 0.0
    ) -> Tuple[Tensor, Tensor]:
        """
        Scaled dot-product attention.
        
        Args:
            query: [batch, seq_q, d_k] or [seq_q, d_k]
            key: [batch, seq_k, d_k] or [seq_k, d_k]
            value: [batch, seq_k, d_v] or [seq_k, d_v]
            mask: Optional attention mask
            dropout_p: Dropout probability
        
        Returns:
            output: Attention output
            attention_weights: Attention weights
        """
        # Get dimensions
        if query.shape.ndim == 2:
            seq_q, d_k = query.shape.dims
            seq_k = key.shape.dims[0]
            d_v = value.shape.dims[1]
        else:
            seq_q, d_k = query.shape.dims[-2], query.shape.dims[-1]
            seq_k = key.shape.dims[-2]
            d_v = value.shape.dims[-1]
        
        scale = 1.0 / math.sqrt(d_k)
        
        # Compute Q @ K^T
        key_t = key.T
        scores_data = []
        for i in range(seq_q):
            for j in range(seq_k):
                score = 0.0
                for k in range(d_k):
                    score += query.data[i * d_k + k] * key.data[j * d_k + k]
                scores_data.append(score * scale)
        
        scores = Tensor(scores_data, Shape((seq_q, seq_k)))
        
        # Apply mask
        if mask is not None:
            for i in range(len(scores.data)):
                if mask.data[i % len(mask.data)] == 0:
                    scores.data[i] = -1e9
        
        # Softmax
        attention_weights = Activations.softmax(scores, dim=-1)
        
        # Apply dropout (simplified - skip in inference)
        if dropout_p > 0:
            import random
            for i in range(len(attention_weights.data)):
                if random.random() < dropout_p:
                    attention_weights.data[i] = 0.0
        
        # Compute attention @ value
        output_data = []
        for i in range(seq_q):
            for k in range(d_v):
                val = 0.0
                for j in range(seq_k):
                    val += attention_weights.data[i * seq_k + j] * value.data[j * d_v + k]
                output_data.append(val)
        
        output = Tensor(output_data, Shape((seq_q, d_v)))
        
        return output, attention_weights
    
    @staticmethod
    def causal_mask(size: int) -> Tensor:
        """Create causal (lower triangular) mask."""
        data = []
        for i in range(size):
            for j in range(size):
                data.append(1.0 if j <= i else 0.0)
        return Tensor(data, Shape((size, size)))
    
    @staticmethod
    def padding_mask(lengths: Tensor, max_len: int) -> Tensor:
        """Create padding mask from sequence lengths."""
        batch_size = len(lengths.data)
        data = []
        for b in range(batch_size):
            seq_len = int(lengths.data[b])
            for i in range(max_len):
                data.append(1.0 if i < seq_len else 0.0)
        return Tensor(data, Shape((batch_size, max_len)))
    
    @staticmethod
    def relative_position_bias(seq_len: int, num_heads: int = 8, 
                               max_distance: int = 128) -> Tensor:
        """Compute relative position bias."""
        data = []
        for h in range(num_heads):
            for i in range(seq_len):
                for j in range(seq_len):
                    distance = min(abs(i - j), max_distance)
                    # Simple learned bias approximation
                    bias = math.log(distance + 1) / math.log(max_distance + 1)
                    data.append(bias * 0.1)
        return Tensor(data, Shape((num_heads, seq_len, seq_len)))


class MultiHeadAttention:
    """Multi-head attention mechanism."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.0):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.dropout = dropout
        
        # Initialize projection weights
        self.w_q = self._init_weights(d_model, d_model)
        self.w_k = self._init_weights(d_model, d_model)
        self.w_v = self._init_weights(d_model, d_model)
        self.w_o = self._init_weights(d_model, d_model)
        
        # Biases
        self.b_q = zeros(d_model)
        self.b_k = zeros(d_model)
        self.b_v = zeros(d_model)
        self.b_o = zeros(d_model)
    
    def _init_weights(self, in_features: int, out_features: int) -> Tensor:
        """Initialize weights with Xavier initialization."""
        std = math.sqrt(2.0 / (in_features + out_features))
        data = []
        for _ in range(in_features * out_features):
            u1 = max(1e-10, __import__('random').random())
            u2 = __import__('random').random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            data.append(std * z)
        return Tensor(data, Shape((in_features, out_features)))
    
    def forward(self, query: Tensor, key: Tensor, value: Tensor,
                mask: Optional[Tensor] = None) -> Tensor:
        """
        Multi-head attention forward pass.
        
        Args:
            query: [seq_q, d_model]
            key: [seq_k, d_model]
            value: [seq_k, d_model]
            mask: Optional attention mask
        
        Returns:
            output: [seq_q, d_model]
        """
        seq_q = query.shape.dims[0]
        seq_k = key.shape.dims[0]
        
        # Project to Q, K, V
        q = self._linear(query, self.w_q, self.b_q)
        k = self._linear(key, self.w_k, self.b_k)
        v = self._linear(value, self.w_v, self.b_v)
        
        # Split into heads and compute attention
        head_outputs = []
        for h in range(self.num_heads):
            start = h * self.d_k
            end = start + self.d_k
            
            # Extract head slice
            q_h = self._slice_head(q, start, end)
            k_h = self._slice_head(k, start, end)
            v_h = self._slice_head(v, start, end)
            
            # Compute attention for this head
            attn_out, _ = AttentionMechanisms.scaled_dot_product_attention(
                q_h, k_h, v_h, mask, self.dropout
            )
            head_outputs.append(attn_out)
        
        # Concatenate heads
        concat = self._concat_heads(head_outputs)
        
        # Final projection
        output = self._linear(concat, self.w_o, self.b_o)
        
        return output
    
    def _linear(self, x: Tensor, w: Tensor, b: Tensor) -> Tensor:
        """Linear transformation: x @ w + b."""
        seq_len = x.shape.dims[0]
        in_features = x.shape.dims[1]
        out_features = w.shape.dims[1]
        
        result = []
        for i in range(seq_len):
            for j in range(out_features):
                val = b.data[j]
                for k in range(in_features):
                    val += x.data[i * in_features + k] * w.data[k * out_features + j]
                result.append(val)
        
        return Tensor(result, Shape((seq_len, out_features)))
    
    def _slice_head(self, x: Tensor, start: int, end: int) -> Tensor:
        """Extract a slice for one attention head."""
        seq_len = x.shape.dims[0]
        d_k = end - start
        
        result = []
        for i in range(seq_len):
            for j in range(start, end):
                result.append(x.data[i * x.shape.dims[1] + j])
        
        return Tensor(result, Shape((seq_len, d_k)))
    
    def _concat_heads(self, heads: list) -> Tensor:
        """Concatenate attention head outputs."""
        seq_len = heads[0].shape.dims[0]
        d_k = heads[0].shape.dims[1]
        d_model = d_k * len(heads)
        
        result = []
        for i in range(seq_len):
            for h, head in enumerate(heads):
                for j in range(d_k):
                    result.append(head.data[i * d_k + j])
        
        return Tensor(result, Shape((seq_len, d_model)))
    
    def __call__(self, query: Tensor, key: Tensor, value: Tensor,
                 mask: Optional[Tensor] = None) -> Tensor:
        return self.forward(query, key, value, mask)


class CrossAttention(MultiHeadAttention):
    """Cross-attention for encoder-decoder architectures."""
    
    def forward(self, query: Tensor, encoder_output: Tensor,
                mask: Optional[Tensor] = None) -> Tensor:
        """Cross-attention with encoder output as key and value."""
        return super().forward(query, encoder_output, encoder_output, mask)


class LinearAttention:
    """Linear attention approximation for efficiency."""
    
    def __init__(self, d_model: int, eps: float = 1e-6):
        self.d_model = d_model
        self.eps = eps
    
    @staticmethod
    def feature_map(x: Tensor) -> Tensor:
        """Feature map for linear attention (ELU + 1)."""
        data = [max(0, v) + 1.0 for v in x.data]
        return Tensor(data, x.shape)
    
    def forward(self, query: Tensor, key: Tensor, value: Tensor) -> Tensor:
        """Linear attention forward pass."""
        # Apply feature map
        q = self.feature_map(query)
        k = self.feature_map(key)
        
        seq_q, d_k = q.shape.dims
        seq_k = k.shape.dims[0]
        d_v = value.shape.dims[1]
        
        # Compute K^T @ V
        kv = zeros(d_k, d_v)
        for i in range(seq_k):
            for j in range(d_k):
                for l in range(d_v):
                    kv.data[j * d_v + l] += k.data[i * d_k + j] * value.data[i * d_v + l]
        
        # Compute Q @ (K^T @ V)
        output_data = []
        for i in range(seq_q):
            normalizer = 0.0
            for j in range(d_k):
                for l in range(seq_k):
                    normalizer += q.data[i * d_k + j] * k.data[l * d_k + j]
            normalizer = max(normalizer, self.eps)
            
            for l in range(d_v):
                val = 0.0
                for j in range(d_k):
                    val += q.data[i * d_k + j] * kv.data[j * d_v + l]
                output_data.append(val / normalizer)
        
        return Tensor(output_data, Shape((seq_q, d_v)))
    
    def __call__(self, query: Tensor, key: Tensor, value: Tensor) -> Tensor:
        return self.forward(query, key, value)


class AttentionMetrics:
    """Metrics for analyzing attention patterns."""
    
    @staticmethod
    def attention_entropy(weights: Tensor) -> float:
        """Compute entropy of attention weights."""
        entropy = 0.0
        for w in weights.data:
            if w > 0:
                entropy -= w * math.log(w + 1e-10)
        return entropy
    
    @staticmethod
    def attention_concentration(weights: Tensor) -> float:
        """Measure concentration (inverse of entropy normalized)."""
        entropy = AttentionMetrics.attention_entropy(weights)
        max_entropy = math.log(len(weights.data) + 1e-10)
        return 1.0 - (entropy / max_entropy) if max_entropy > 0 else 1.0
    
    @staticmethod
    def head_importance(attention_weights: list) -> list:
        """Estimate importance of each attention head."""
        importances = []
        for head_weights in attention_weights:
            # Use variance of attention as proxy for importance
            mean = sum(head_weights.data) / len(head_weights.data)
            variance = sum((w - mean) ** 2 for w in head_weights.data) / len(head_weights.data)
            importances.append(variance)
        return importances
