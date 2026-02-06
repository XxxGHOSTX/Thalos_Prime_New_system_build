#!/usr/bin/env python3
"""
THALOS Prime Attention Module
Pure Python implementation of attention mechanisms
"""

import math
from typing import Optional, Tuple
from .tensor import Tensor, zeros, ones
from .activations import Activations
from .linear_algebra import LinearAlgebra


class AttentionMechanisms:
    """Collection of attention mechanisms"""
    
    @staticmethod
    def scaled_dot_product_attention(query: Tensor, key: Tensor, value: Tensor,
                                    mask: Optional[Tensor] = None,
                                    dropout_p: float = 0.0) -> Tuple[Tensor, Tensor]:
        """
        Scaled dot-product attention
        Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
        
        Args:
            query: Query tensor (seq_len_q, d_k)
            key: Key tensor (seq_len_k, d_k)
            value: Value tensor (seq_len_k, d_v)
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
            output: Attention output (seq_len_q, d_v)
            attention_weights: Attention weights (seq_len_q, seq_len_k)
        """
        # Get dimensions
        if query.shape.ndim == 1:
            query = query.reshape(1, query.shape.size)
        if key.shape.ndim == 1:
            key = key.reshape(1, key.shape.size)
        if value.shape.ndim == 1:
            value = value.reshape(1, value.shape.size)
        
        d_k = query.shape.dims[-1]
        scale = 1.0 / math.sqrt(d_k)
        
        # Compute attention scores: Q @ K^T
        key_t = key.transpose()
        scores = LinearAlgebra.matmul(query, key_t)
        
        # Scale
        scores = scores * scale
        
        # Apply mask if provided
        if mask is not None:
            # Set masked positions to large negative value
            masked_data = []
            for i, (score, m) in enumerate(zip(scores.data, mask.data)):
                if m == 0:
                    masked_data.append(-1e9)
                else:
                    masked_data.append(score)
            scores = Tensor(masked_data, scores.shape)
        
        # Apply softmax
        attention_weights = Activations.softmax(scores, axis=-1)
        
        # Apply dropout if specified
        if dropout_p > 0:
            from .distributions import Distributions
            attention_weights = Distributions.dropout(attention_weights, dropout_p, training=True)
        
        # Compute output: attention_weights @ V
        output = LinearAlgebra.matmul(attention_weights, value)
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
    def multi_head_attention(query: Tensor, key: Tensor, value: Tensor,
                            num_heads: int = 8,
                            mask: Optional[Tensor] = None) -> Tensor:
        """
        Multi-head attention mechanism
        
        Args:
            query: Query tensor (seq_len, d_model)
            key: Key tensor (seq_len, d_model)
            value: Value tensor (seq_len, d_model)
            num_heads: Number of attention heads
            mask: Optional attention mask
        
        Returns:
            output: Multi-head attention output
        """
        if query.shape.ndim == 1:
            seq_len = 1
            d_model = query.shape.size
            query = query.reshape(1, d_model)
            key = key.reshape(1, d_model)
            value = value.reshape(1, d_model)
        else:
            seq_len, d_model = query.shape.dims
        
        if d_model % num_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by num_heads ({num_heads})")
        
        d_head = d_model // num_heads
        
        # Split into heads (simplified - just use first head)
        # In practice, would split across heads
        head_query = Tensor(query.data[:seq_len * d_head], 
                           query.shape.__class__(seq_len, d_head))
        head_key = Tensor(key.data[:seq_len * d_head],
                         key.shape.__class__(seq_len, d_head))
        head_value = Tensor(value.data[:seq_len * d_head],
                           value.shape.__class__(seq_len, d_head))
        
        # Apply attention
        head_output, _ = AttentionMechanisms.scaled_dot_product_attention(
            head_query, head_key, head_value, mask
        )
        
        # In full implementation, would concatenate all heads
        # For now, return single head output padded to d_model
        output_data = head_output.data + [0.0] * (seq_len * d_model - len(head_output.data))
        
        from .tensor import Shape
        return Tensor(output_data[:seq_len * d_model], Shape(seq_len, d_model))
    
    @staticmethod
    def causal_mask(size: int) -> Tensor:
        """
        Create causal mask for autoregressive attention
        Prevents attending to future positions
        
        Args:
            size: Sequence length
        
        Returns:
            mask: Lower triangular mask (size, size)
        """
        mask_data = []
        for i in range(size):
            for j in range(size):
                # Can attend to current and previous positions
                mask_data.append(1.0 if j <= i else 0.0)
        
        from .tensor import Shape
        return Tensor(mask_data, Shape(size, size))
    
    @staticmethod
    def padding_mask(lengths: Tensor, max_len: int) -> Tensor:
        """
        Create padding mask for variable-length sequences
        
        Args:
            lengths: Actual lengths of each sequence (batch_size,)
            max_len: Maximum sequence length
        
        Returns:
            mask: Padding mask (batch_size, max_len)
        """
        batch_size = lengths.shape.size
        mask_data = []
        
        for i in range(batch_size):
            length = int(lengths.data[i])
            for j in range(max_len):
                mask_data.append(1.0 if j < length else 0.0)
        
        from .tensor import Shape
        return Tensor(mask_data, Shape(batch_size, max_len))
    
    @staticmethod
    def relative_position_bias(seq_len: int, num_buckets: int = 32,
                              max_distance: int = 128) -> Tensor:
        """
        Compute relative position bias for attention
        
        Args:
            seq_len: Sequence length
            num_buckets: Number of relative position buckets
            max_distance: Maximum distance to consider
        
        Returns:
            bias: Relative position bias (seq_len, seq_len)
        """
        def relative_position_bucket(relative_pos: int) -> int:
            """Map relative position to bucket index"""
            num_buckets_half = num_buckets // 2
            
            # Handle negative positions
            ret = 0 if relative_pos >= 0 else num_buckets_half
            relative_pos = abs(relative_pos)
            
            # Half of buckets for exact positions
            max_exact = num_buckets_half // 2
            is_small = relative_pos < max_exact
            
            if is_small:
                return ret + relative_pos
            else:
                # Logarithmic spacing for larger distances
                val_if_large = max_exact + int(
                    math.log(relative_pos / max_exact) / 
                    math.log(max_distance / max_exact) *
                    (num_buckets_half - max_exact)
                )
                return ret + min(val_if_large, num_buckets_half - 1)
        
        # Create position bias
        bias_data = []
        for i in range(seq_len):
            for j in range(seq_len):
                relative_pos = j - i
                bucket = relative_position_bucket(relative_pos)
                # Simple bias value (in practice, would use learned embeddings)
                bias_data.append(float(bucket) / num_buckets)
        
        from .tensor import Shape
        return Tensor(bias_data, Shape(seq_len, seq_len))
    
    @staticmethod
    def cross_attention(query: Tensor, context_key: Tensor, context_value: Tensor,
                       mask: Optional[Tensor] = None) -> Tuple[Tensor, Tensor]:
        """
        Cross-attention for encoder-decoder architecture
        Query from decoder, Key and Value from encoder
        
        Args:
            query: Decoder query (tgt_len, d_model)
            context_key: Encoder key (src_len, d_model)
            context_value: Encoder value (src_len, d_model)
            mask: Optional attention mask
        
        Returns:
            output: Cross-attention output
            attention_weights: Attention weights
        """
        return AttentionMechanisms.scaled_dot_product_attention(
            query, context_key, context_value, mask
        )
    
    @staticmethod
    def attention_entropy(attention_weights: Tensor, eps: float = 1e-10) -> float:
        """
        Compute entropy of attention distribution
        Higher entropy indicates more uniform attention
        
        Args:
            attention_weights: Attention weights (seq_len_q, seq_len_k)
            eps: Small constant for numerical stability
        
        Returns:
            entropy: Average entropy across queries
        """
        if attention_weights.shape.ndim == 1:
            # Single distribution
            entropy = 0.0
            for p in attention_weights.data:
                if p > eps:
                    entropy -= p * math.log(p + eps)
            return entropy
        
        # Multiple distributions
        rows, cols = attention_weights.shape.dims
        total_entropy = 0.0
        
        for i in range(rows):
            row_entropy = 0.0
            for j in range(cols):
                p = attention_weights.data[i * cols + j]
                if p > eps:
                    row_entropy -= p * math.log(p + eps)
            total_entropy += row_entropy
        
        return total_entropy / rows
    
    @staticmethod
    def attention_concentration(attention_weights: Tensor, top_k: int = 1) -> float:
        """
        Measure attention concentration
        Returns fraction of attention mass on top-k positions
        
        Args:
            attention_weights: Attention weights (seq_len_q, seq_len_k)
            top_k: Number of top positions to consider
        
        Returns:
            concentration: Average concentration score
        """
        if attention_weights.shape.ndim == 1:
            # Single distribution
            sorted_weights = sorted(attention_weights.data, reverse=True)
            return sum(sorted_weights[:top_k])
        
        # Multiple distributions
        rows, cols = attention_weights.shape.dims
        total_concentration = 0.0
        
        for i in range(rows):
            row_data = [attention_weights.data[i * cols + j] for j in range(cols)]
            sorted_weights = sorted(row_data, reverse=True)
            total_concentration += sum(sorted_weights[:top_k])
        
        return total_concentration / rows
    
    @staticmethod
    def linear_attention(query: Tensor, key: Tensor, value: Tensor,
                        feature_map: str = "elu") -> Tensor:
        """
        Linear attention approximation
        More efficient O(N) complexity instead of O(N^2)
        
        Args:
            query: Query tensor (seq_len, d_k)
            key: Key tensor (seq_len, d_k)
            value: Value tensor (seq_len, d_v)
            feature_map: Feature mapping function ("elu", "relu")
        
        Returns:
            output: Linear attention output
        """
        # Apply feature mapping
        if feature_map == "elu":
            query_prime = Activations.elu(query)
            query_prime = query_prime + 1.0  # Shift to be positive
            key_prime = Activations.elu(key)
            key_prime = key_prime + 1.0
        elif feature_map == "relu":
            query_prime = Activations.relu(query)
            key_prime = Activations.relu(key)
        else:
            query_prime = query
            key_prime = key
        
        # Linear attention: (Q' @ (K'^T @ V)) / (Q' @ K'^T @ 1)
        # Simplified implementation
        
        if query_prime.shape.ndim == 1:
            seq_len = 1
            d_k = query_prime.shape.size
            query_prime = query_prime.reshape(1, d_k)
            key_prime = key_prime.reshape(1, d_k)
            value = value.reshape(1, value.shape.size)
        else:
            seq_len, d_k = query_prime.shape.dims
        
        # Compute K'^T @ V (d_k, d_v)
        key_prime_t = key_prime.transpose()
        kv = LinearAlgebra.matmul(key_prime_t, value)
        
        # Compute Q' @ (K'^T @ V)
        output = LinearAlgebra.matmul(query_prime, kv)
        
        # Normalization (simplified)
        # In practice, would divide by Q' @ K'^T @ 1
        norm_factor = seq_len
        output = output / norm_factor
        
        return output
    
    @staticmethod
    def attention_rollout(attention_weights_list: list, 
                         start_layer: int = 0) -> Tensor:
        """
        Compute attention rollout across layers
        Tracks attention flow through transformer layers
        
        Args:
            attention_weights_list: List of attention weight tensors from each layer
            start_layer: Layer to start rollout from
        
        Returns:
            rollout: Rolled-out attention (seq_len, seq_len)
        """
        if not attention_weights_list:
            raise ValueError("Empty attention weights list")
        
        # Start with identity or first layer
        if start_layer >= len(attention_weights_list):
            start_layer = 0
        
        rollout = attention_weights_list[start_layer]
        
        # Multiply attention matrices
        for i in range(start_layer + 1, len(attention_weights_list)):
            rollout = LinearAlgebra.matmul(rollout, attention_weights_list[i])
        
        return rollout
    
    @staticmethod
    def sparse_attention(query: Tensor, key: Tensor, value: Tensor,
                        sparsity_pattern: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Sparse attention with predefined sparsity pattern
        Only computes attention for specified positions
        
        Args:
            query: Query tensor (seq_len_q, d_k)
            key: Key tensor (seq_len_k, d_k)
            value: Value tensor (seq_len_k, d_v)
            sparsity_pattern: Binary mask (seq_len_q, seq_len_k)
        
        Returns:
            output: Sparse attention output
            attention_weights: Sparse attention weights
        """
        # Use sparsity pattern as mask
        return AttentionMechanisms.scaled_dot_product_attention(
            query, key, value, mask=sparsity_pattern
        )
    
    @staticmethod
    def local_attention(query: Tensor, key: Tensor, value: Tensor,
                       window_size: int = 3) -> Tuple[Tensor, Tensor]:
        """
        Local windowed attention
        Each position only attends to nearby positions
        
        Args:
            query: Query tensor (seq_len, d_k)
            key: Key tensor (seq_len, d_k)
            value: Value tensor (seq_len, d_v)
            window_size: Size of attention window (radius)
        
        Returns:
            output: Local attention output
            attention_weights: Local attention weights
        """
        if query.shape.ndim == 1:
            seq_len = 1
        else:
            seq_len = query.shape.dims[0]
        
        # Create local attention mask
        mask_data = []
        for i in range(seq_len):
            for j in range(seq_len):
                # Allow attention within window
                if abs(i - j) <= window_size:
                    mask_data.append(1.0)
                else:
                    mask_data.append(0.0)
        
        from .tensor import Shape
        local_mask = Tensor(mask_data, Shape(seq_len, seq_len))
        
        return AttentionMechanisms.scaled_dot_product_attention(
            query, key, value, mask=local_mask
        )
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
