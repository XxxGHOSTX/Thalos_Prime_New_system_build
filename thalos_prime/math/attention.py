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
