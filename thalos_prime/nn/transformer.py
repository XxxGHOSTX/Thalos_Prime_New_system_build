"""
THALOS Prime - Transformer Architecture Module
Multi-head attention, feed-forward networks, and transformer blocks.
"""

from typing import Optional, List
import math
import random
from .layer import Layer, Linear, Dropout, LayerNormLayer
from ..math.tensor import Tensor, Shape, zeros
from ..math.activations import Activations


class MultiHeadAttention(Layer):
    """Multi-head attention mechanism."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.0):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.dropout = dropout
        
        # Projection layers
        self.w_q = Linear(d_model, d_model, bias=False)
        self.w_k = Linear(d_model, d_model, bias=False)
        self.w_v = Linear(d_model, d_model, bias=False)
        self.w_o = Linear(d_model, d_model, bias=False)
        
        self._parameters.update(self.w_q._parameters)
        self._parameters.update(self.w_k._parameters)
        self._parameters.update(self.w_v._parameters)
        self._parameters.update(self.w_o._parameters)
    
    def _scaled_dot_product_attention(self, q: Tensor, k: Tensor, v: Tensor,
                                       mask: Optional[Tensor] = None) -> Tensor:
        """Scaled dot-product attention."""
        seq_q = q.shape.dims[0]
        seq_k = k.shape.dims[0]
        d_k = q.shape.dims[1]
        d_v = v.shape.dims[1]
        
        scale = 1.0 / math.sqrt(d_k)
        
        # Compute attention scores
        scores_data = []
        for i in range(seq_q):
            for j in range(seq_k):
                score = 0.0
                for k_idx in range(d_k):
                    score += q.data[i * d_k + k_idx] * k.data[j * d_k + k_idx]
                scores_data.append(score * scale)
        
        # Apply mask
        if mask is not None:
            for i in range(seq_q):
                for j in range(seq_k):
                    if mask.data[i * seq_k + j] == 0:
                        scores_data[i * seq_k + j] = -1e9
        
        # Softmax over keys
        attention_data = []
        for i in range(seq_q):
            row = scores_data[i * seq_k:(i + 1) * seq_k]
            max_val = max(row)
            exp_vals = [math.exp(s - max_val) for s in row]
            sum_exp = sum(exp_vals)
            attention_data.extend([e / sum_exp for e in exp_vals])
        
        # Apply dropout
        if self.training and self.dropout > 0:
            for i in range(len(attention_data)):
                if random.random() < self.dropout:
                    attention_data[i] = 0.0
        
        # Compute output
        output_data = []
        for i in range(seq_q):
            for k_idx in range(d_v):
                val = 0.0
                for j in range(seq_k):
                    val += attention_data[i * seq_k + j] * v.data[j * d_v + k_idx]
                output_data.append(val)
        
        return Tensor(output_data, Shape((seq_q, d_v)))
    
    def forward(self, query: Tensor, key: Tensor, value: Tensor,
                mask: Optional[Tensor] = None) -> Tensor:
        """Multi-head attention forward pass."""
        seq_q = query.shape.dims[0]
        seq_k = key.shape.dims[0]
        
        # Project Q, K, V
        q = self.w_q(query)
        k = self.w_k(key)
        v = self.w_v(value)
        
        # Split into heads and compute attention
        head_outputs = []
        for h in range(self.num_heads):
            start = h * self.d_k
            end = start + self.d_k
            
            # Extract head slice
            q_h_data = []
            k_h_data = []
            v_h_data = []
            
            for i in range(seq_q):
                for j in range(start, end):
                    q_h_data.append(q.data[i * self.d_model + j])
            
            for i in range(seq_k):
                for j in range(start, end):
                    k_h_data.append(k.data[i * self.d_model + j])
                    v_h_data.append(v.data[i * self.d_model + j])
            
            q_h = Tensor(q_h_data, Shape((seq_q, self.d_k)))
            k_h = Tensor(k_h_data, Shape((seq_k, self.d_k)))
            v_h = Tensor(v_h_data, Shape((seq_k, self.d_k)))
            
            attn_out = self._scaled_dot_product_attention(q_h, k_h, v_h, mask)
            head_outputs.append(attn_out)
        
        # Concatenate heads
        concat_data = []
        for i in range(seq_q):
            for h in range(self.num_heads):
                for j in range(self.d_k):
                    concat_data.append(head_outputs[h].data[i * self.d_k + j])
        
        concat = Tensor(concat_data, Shape((seq_q, self.d_model)))
        
        # Final projection
        return self.w_o(concat)


class FeedForwardNetwork(Layer):
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        self.linear1 = Linear(d_model, d_ff)
        self.linear2 = Linear(d_ff, d_model)
        self.dropout_layer = Dropout(dropout)
        
        self._parameters.update(self.linear1._parameters)
        self._parameters.update(self.linear2._parameters)
    
    def forward(self, x: Tensor) -> Tensor:
        """FFN forward pass: Linear -> GELU -> Dropout -> Linear."""
        x = self.linear1(x)
        x = Activations.gelu(x)
        x = self.dropout_layer(x)
        x = self.linear2(x)
        return x


class TransformerBlock(Layer):
    """Single transformer block with attention and FFN."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.ffn = FeedForwardNetwork(d_model, d_ff, dropout)
        self.norm1 = LayerNormLayer(d_model)
        self.norm2 = LayerNormLayer(d_model)
        self.dropout1 = Dropout(dropout)
        self.dropout2 = Dropout(dropout)
        
        self._parameters.update(self.attention._parameters)
        self._parameters.update(self.ffn._parameters)
        self._parameters.update(self.norm1._parameters)
        self._parameters.update(self.norm2._parameters)
    
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        """Transformer block forward pass with residual connections."""
        # Self-attention with residual
        attn_out = self.attention(x, x, x, mask)
        attn_out = self.dropout1(attn_out)
        
        # Add residual and normalize
        residual1_data = [x.data[i] + attn_out.data[i] for i in range(len(x.data))]
        x = self.norm1(Tensor(residual1_data, x.shape))
        
        # FFN with residual
        ffn_out = self.ffn(x)
        ffn_out = self.dropout2(ffn_out)
        
        # Add residual and normalize
        residual2_data = [x.data[i] + ffn_out.data[i] for i in range(len(x.data))]
        x = self.norm2(Tensor(residual2_data, x.shape))
        
        return x


class TransformerEncoder(Layer):
    """Stack of transformer encoder blocks."""
    
    def __init__(self, num_layers: int, d_model: int, num_heads: int, 
                 d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.layers = [TransformerBlock(d_model, num_heads, d_ff, dropout) 
                       for _ in range(num_layers)]
        
        for i, layer in enumerate(self.layers):
            for name, param in layer._parameters.items():
                self._parameters[f'layer{i}_{name}'] = param
    
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        """Forward through all encoder layers."""
        for layer in self.layers:
            x = layer(x, mask)
        return x


class TransformerDecoder(Layer):
    """Stack of transformer decoder blocks with causal masking."""
    
    def __init__(self, num_layers: int, d_model: int, num_heads: int, 
                 d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.layers = [TransformerBlock(d_model, num_heads, d_ff, dropout) 
                       for _ in range(num_layers)]
        
        for i, layer in enumerate(self.layers):
            for name, param in layer._parameters.items():
                self._parameters[f'layer{i}_{name}'] = param
    
    def _create_causal_mask(self, seq_len: int) -> Tensor:
        """Create causal attention mask."""
        mask_data = []
        for i in range(seq_len):
            for j in range(seq_len):
                mask_data.append(1.0 if j <= i else 0.0)
        return Tensor(mask_data, Shape((seq_len, seq_len)))
    
    def forward(self, x: Tensor, encoder_output: Optional[Tensor] = None) -> Tensor:
        """Forward through all decoder layers with causal masking."""
        seq_len = x.shape.dims[0]
        causal_mask = self._create_causal_mask(seq_len)
        
        for layer in self.layers:
            x = layer(x, causal_mask)
        
        return x


class CrossAttentionBlock(Layer):
    """Cross-attention block for encoder-decoder architectures."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.cross_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm = LayerNormLayer(d_model)
        self.dropout_layer = Dropout(dropout)
        
        self._parameters.update(self.cross_attention._parameters)
        self._parameters.update(self.norm._parameters)
    
    def forward(self, query: Tensor, encoder_output: Tensor) -> Tensor:
        """Cross-attention with encoder output."""
        attn_out = self.cross_attention(query, encoder_output, encoder_output)
        attn_out = self.dropout_layer(attn_out)
        
        # Residual connection
        residual_data = [query.data[i] + attn_out.data[i] for i in range(len(query.data))]
        return self.norm(Tensor(residual_data, query.shape))
