#!/usr/bin/env python3
"""
THALOS Prime Transformer Components
Pure Python implementation of transformer architecture
"""

import math
from typing import Optional

from ..math import Tensor, Shape, zeros, ones
from ..math.linear_algebra import LinearAlgebra
from ..math.activations import Activations
from ..math.attention import AttentionMechanisms
from .layer import Layer, Linear, Dropout, LayerNorm


class MultiHeadAttention(Layer):
    """
    Multi-head attention mechanism
    Allows the model to jointly attend to information from different representation subspaces
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """
        Initialize multi-head attention
        
        Args:
            d_model: Dimension of model embeddings
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        
        if d_model % num_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by num_heads ({num_heads})")
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V
        self.q_linear = Linear(d_model, d_model)
        self.k_linear = Linear(d_model, d_model)
        self.v_linear = Linear(d_model, d_model)
        
        # Output projection
        self.out_linear = Linear(d_model, d_model)
        
        # Dropout
        self.dropout = Dropout(dropout)
    
    def _split_heads(self, x: Tensor, batch_size: int, seq_len: int) -> Tensor:
        """
        Split tensor into multiple heads
        
        Args:
            x: Input tensor (batch_size * seq_len, d_model)
            batch_size: Batch size
            seq_len: Sequence length
            
        Returns:
            Reshaped tensor (batch_size, num_heads, seq_len, d_k)
        """
        # Reshape to (batch_size, seq_len, num_heads, d_k)
        data = []
        for b in range(batch_size):
            for h in range(self.num_heads):
                for s in range(seq_len):
                    for d in range(self.d_k):
                        idx = b * seq_len * self.d_model + s * self.d_model + h * self.d_k + d
                        data.append(x.data[idx])
        
        return Tensor(data, Shape(batch_size, self.num_heads, seq_len, self.d_k))
    
    def _merge_heads(self, x: Tensor, batch_size: int, seq_len: int) -> Tensor:
        """
        Merge multiple heads back together
        
        Args:
            x: Input tensor (batch_size, num_heads, seq_len, d_k)
            batch_size: Batch size
            seq_len: Sequence length
            
        Returns:
            Merged tensor (batch_size, seq_len, d_model)
        """
        # Reshape from (batch_size, num_heads, seq_len, d_k) to (batch_size, seq_len, d_model)
        data = []
        for b in range(batch_size):
            for s in range(seq_len):
                for h in range(self.num_heads):
                    for d in range(self.d_k):
                        idx = b * self.num_heads * seq_len * self.d_k + h * seq_len * self.d_k + s * self.d_k + d
                        data.append(x.data[idx])
        
        return Tensor(data, Shape(batch_size, seq_len, self.d_model))
    
    def forward(self, query: Tensor, key: Tensor, value: Tensor, 
                mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through multi-head attention
        
        Args:
            query: Query tensor (batch_size, seq_len, d_model) or (seq_len, d_model)
            key: Key tensor
            value: Value tensor
            mask: Optional attention mask
            
        Returns:
            Output tensor
        """
        # Handle 2D input (seq_len, d_model) by adding batch dimension
        if query.shape.ndim == 2:
            seq_len, d_model = query.shape.dims
            batch_size = 1
            query = query.reshape(1, seq_len, d_model)
            key = key.reshape(1, seq_len, d_model)
            value = value.reshape(1, seq_len, d_model)
            squeeze_output = True
        else:
            batch_size, seq_len, d_model = query.shape.dims
            squeeze_output = False
        
        # Linear projections
        q = self.q_linear.forward(query.reshape(batch_size * seq_len, d_model))
        k = self.k_linear.forward(key.reshape(batch_size * seq_len, d_model))
        v = self.v_linear.forward(value.reshape(batch_size * seq_len, d_model))
        
        # Reshape for multi-head attention: (batch_size, num_heads, seq_len, d_k)
        q = self._split_heads(q, batch_size, seq_len)
        k = self._split_heads(k, batch_size, seq_len)
        v = self._split_heads(v, batch_size, seq_len)
        
        # Compute attention for each head (simplified - process all heads together)
        # For simplicity, we'll process each head separately
        attention_outputs = []
        
        for h in range(self.num_heads):
            # Extract head h: (batch_size, seq_len, d_k)
            q_h_data = []
            k_h_data = []
            v_h_data = []
            
            for b in range(batch_size):
                for s in range(seq_len):
                    for d in range(self.d_k):
                        idx = b * self.num_heads * seq_len * self.d_k + h * seq_len * self.d_k + s * self.d_k + d
                        q_h_data.append(q.data[idx])
                        k_h_data.append(k.data[idx])
                        v_h_data.append(v.data[idx])
            
            q_h = Tensor(q_h_data, Shape(batch_size, seq_len, self.d_k))
            k_h = Tensor(k_h_data, Shape(batch_size, seq_len, self.d_k))
            v_h = Tensor(v_h_data, Shape(batch_size, seq_len, self.d_k))
            
            # Apply scaled dot-product attention for this head
            # For each batch item
            head_outputs = []
            for b in range(batch_size):
                # Extract batch b
                q_b_data = q_h.data[b * seq_len * self.d_k:(b + 1) * seq_len * self.d_k]
                k_b_data = k_h.data[b * seq_len * self.d_k:(b + 1) * seq_len * self.d_k]
                v_b_data = v_h.data[b * seq_len * self.d_k:(b + 1) * seq_len * self.d_k]
                
                q_b = Tensor(q_b_data, Shape(seq_len, self.d_k))
                k_b = Tensor(k_b_data, Shape(seq_len, self.d_k))
                v_b = Tensor(v_b_data, Shape(seq_len, self.d_k))
                
                attn_output, _ = AttentionMechanisms.scaled_dot_product_attention(
                    q_b, k_b, v_b, mask=mask, dropout_p=0.0
                )
                head_outputs.append(attn_output)
            
            attention_outputs.append(head_outputs)
        
        # Concatenate heads
        concat_data = []
        for b in range(batch_size):
            for s in range(seq_len):
                for h in range(self.num_heads):
                    for d in range(self.d_k):
                        idx = s * self.d_k + d
                        concat_data.append(attention_outputs[h][b].data[idx])
        
        concat_output = Tensor(concat_data, Shape(batch_size, seq_len, self.d_model))
        
        # Final linear projection
        output = self.out_linear.forward(concat_output.reshape(batch_size * seq_len, self.d_model))
        output = output.reshape(batch_size, seq_len, self.d_model)
        
        # Apply dropout
        output = self.dropout.forward(output)
        
        # Remove batch dimension if input was 2D
        if squeeze_output:
            output = output.reshape(seq_len, self.d_model)
        
        return output


class FeedForwardNetwork(Layer):
    """
    Position-wise feed-forward network
    Two-layer MLP with activation in between
    """
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        """
        Initialize feed-forward network
        
        Args:
            d_model: Dimension of model embeddings
            d_ff: Dimension of feed-forward hidden layer
            dropout: Dropout probability
        """
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        
        # Two linear layers
        self.linear1 = Linear(d_model, d_ff)
        self.linear2 = Linear(d_ff, d_model)
        
        # Dropout
        self.dropout = Dropout(dropout)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass through FFN
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model) or (seq_len, d_model)
            
        Returns:
            Output tensor
        """
        original_shape = x.shape.dims
        
        # Reshape to 2D for linear layers
        if x.shape.ndim == 3:
            batch_size, seq_len, d_model = original_shape
            x_flat = x.reshape(batch_size * seq_len, d_model)
        elif x.shape.ndim == 2:
            seq_len, d_model = original_shape
            x_flat = x
        else:
            x_flat = x
        
        # First linear + GELU activation
        hidden = self.linear1.forward(x_flat)
        hidden = Activations.gelu(hidden)
        hidden = self.dropout.forward(hidden)
        
        # Second linear
        output = self.linear2.forward(hidden)
        output = self.dropout.forward(output)
        
        # Reshape back to original
        if x.shape.ndim == 3:
            output = output.reshape(*original_shape)
        
        return output


class TransformerBlock(Layer):
    """
    Transformer block with self-attention and feed-forward network
    Includes residual connections and layer normalization
    """
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        """
        Initialize transformer block
        
        Args:
            d_model: Dimension of model embeddings
            num_heads: Number of attention heads
            d_ff: Dimension of feed-forward hidden layer
            dropout: Dropout probability
        """
        super().__init__()
        self.d_model = d_model
        
        # Multi-head attention
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        
        # Feed-forward network
        self.ffn = FeedForwardNetwork(d_model, d_ff, dropout)
        
        # Layer normalization
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        
        # Dropout
        self.dropout = Dropout(dropout)
    
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through transformer block
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model) or (seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Output tensor
        """
        # Self-attention with residual connection and layer norm
        attn_output = self.attention.forward(x, x, x, mask)
        x = x + attn_output  # Residual connection
        x = self.norm1.forward(x)
        
        # Feed-forward with residual connection and layer norm
        ffn_output = self.ffn.forward(x)
        x = x + ffn_output  # Residual connection
        x = self.norm2.forward(x)
        
        return x


class TransformerEncoder(Layer):
    """
    Stack of transformer encoder blocks
    """
    
    def __init__(self, num_layers: int, d_model: int, num_heads: int, 
                 d_ff: int, dropout: float = 0.1):
        """
        Initialize transformer encoder
        
        Args:
            num_layers: Number of transformer blocks
            d_model: Dimension of model embeddings
            num_heads: Number of attention heads
            d_ff: Dimension of feed-forward hidden layer
            dropout: Dropout probability
        """
        super().__init__()
        self.num_layers = num_layers
        
        # Stack of transformer blocks
        self.blocks = [
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ]
        
        # Final layer norm
        self.norm = LayerNorm(d_model)
    
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through encoder stack
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model) or (seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Encoded tensor
        """
        for block in self.blocks:
            x = block.forward(x, mask)
        
        x = self.norm.forward(x)
        return x


class TransformerDecoder(Layer):
    """
    Stack of transformer decoder blocks with causal masking
    """
    
    def __init__(self, num_layers: int, d_model: int, num_heads: int,
                 d_ff: int, dropout: float = 0.1):
        """
        Initialize transformer decoder
        
        Args:
            num_layers: Number of transformer blocks
            d_model: Dimension of model embeddings
            num_heads: Number of attention heads
            d_ff: Dimension of feed-forward hidden layer
            dropout: Dropout probability
        """
        super().__init__()
        self.num_layers = num_layers
        
        # Stack of decoder blocks
        self.blocks = [
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ]
        
        # Final layer norm
        self.norm = LayerNorm(d_model)
    
    def _create_causal_mask(self, seq_len: int) -> Tensor:
        """
        Create causal mask for autoregressive generation
        
        Args:
            seq_len: Sequence length
            
        Returns:
            Causal mask tensor
        """
        mask_data = []
        for i in range(seq_len):
            for j in range(seq_len):
                # Can attend to positions <= current position
                mask_data.append(1.0 if j <= i else 0.0)
        
        return Tensor(mask_data, Shape(seq_len, seq_len))
    
    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through decoder stack with causal masking
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model) or (seq_len, d_model)
            mask: Optional additional mask
            
        Returns:
            Decoded tensor
        """
        # Get sequence length
        if x.shape.ndim == 3:
            seq_len = x.shape.dims[1]
        else:
            seq_len = x.shape.dims[0]
        
        # Create causal mask
        causal_mask = self._create_causal_mask(seq_len)
        
        # Combine with provided mask if any
        if mask is not None:
            # Element-wise multiplication
            combined_mask_data = [
                causal_mask.data[i] * mask.data[i]
                for i in range(len(causal_mask.data))
            ]
            final_mask = Tensor(combined_mask_data, causal_mask.shape)
        else:
            final_mask = causal_mask
        
        # Pass through decoder blocks
        for block in self.blocks:
            x = block.forward(x, final_mask)
        
        x = self.norm.forward(x)
        return x


class CrossAttentionBlock(Layer):
    """
    Cross-attention block for encoder-decoder architecture
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """
        Initialize cross-attention block
        
        Args:
            d_model: Dimension of model embeddings
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        
        # Self-attention on decoder
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        
        # Cross-attention with encoder output
        self.cross_attention = MultiHeadAttention(d_model, num_heads, dropout)
        
        # Feed-forward network
        self.ffn = FeedForwardNetwork(d_model, d_model * 4, dropout)
        
        # Layer normalization
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.norm3 = LayerNorm(d_model)
    
    def forward(self, decoder_input: Tensor, encoder_output: Tensor,
                decoder_mask: Optional[Tensor] = None,
                encoder_mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through cross-attention block
        
        Args:
            decoder_input: Decoder input tensor
            encoder_output: Encoder output tensor
            decoder_mask: Optional decoder mask
            encoder_mask: Optional encoder mask
            
        Returns:
            Output tensor
        """
        # Self-attention on decoder
        attn_output = self.self_attention.forward(
            decoder_input, decoder_input, decoder_input, decoder_mask
        )
        decoder_input = decoder_input + attn_output
        decoder_input = self.norm1.forward(decoder_input)
        
        # Cross-attention with encoder
        cross_attn_output = self.cross_attention.forward(
            decoder_input, encoder_output, encoder_output, encoder_mask
        )
        decoder_input = decoder_input + cross_attn_output
        decoder_input = self.norm2.forward(decoder_input)
        
        # Feed-forward
        ffn_output = self.ffn.forward(decoder_input)
        output = decoder_input + ffn_output
        output = self.norm3.forward(output)
        
        return output


class EncoderDecoderModel(Layer):
    """
    Complete encoder-decoder transformer model
    Used for sequence-to-sequence tasks like translation
    """
    
    def __init__(self, vocab_size: int, d_model: int = 512, num_layers: int = 6,
                 num_heads: int = 8, d_ff: int = 2048, max_seq_len: int = 512,
                 dropout: float = 0.1):
        """
        Initialize encoder-decoder model
        
        Args:
            vocab_size: Size of vocabulary
            d_model: Dimension of model embeddings
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            d_ff: Dimension of feed-forward hidden layer
            max_seq_len: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()
        
        # Encoder
        self.encoder = TransformerEncoder(num_layers, d_model, num_heads, d_ff, dropout)
        
        # Decoder with cross-attention blocks
        self.decoder_blocks = [
            CrossAttentionBlock(d_model, num_heads, dropout)
            for _ in range(num_layers)
        ]
        
        self.final_norm = LayerNorm(d_model)
    
    def forward(self, encoder_input: Tensor, decoder_input: Tensor,
                encoder_mask: Optional[Tensor] = None,
                decoder_mask: Optional[Tensor] = None) -> Tensor:
        """
        Forward pass through encoder-decoder
        
        Args:
            encoder_input: Encoder input tensor
            decoder_input: Decoder input tensor
            encoder_mask: Optional encoder mask
            decoder_mask: Optional decoder mask
            
        Returns:
            Decoder output tensor
        """
        # Encode
        encoder_output = self.encoder.forward(encoder_input, encoder_mask)
        
        # Decode with cross-attention to encoder output
        decoder_output = decoder_input
        for block in self.decoder_blocks:
            decoder_output = block.forward(
                decoder_output, encoder_output,
                decoder_mask, encoder_mask
            )
        
        decoder_output = self.final_norm.forward(decoder_output)
        
        return decoder_output


class PositionWiseFeedForward(Layer):
    """
    Alternative implementation of position-wise feed-forward network
    with configurable activation function
    """
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1,
                 activation: str = 'relu'):
        """
        Initialize position-wise FFN
        
        Args:
            d_model: Model dimension
            d_ff: Feed-forward dimension
            dropout: Dropout probability
            activation: Activation function ('relu', 'gelu', 'swish')
        """
        super().__init__()
        
        self.fc1 = Linear(d_model, d_ff)
        self.fc2 = Linear(d_ff, d_model)
        self.dropout = Dropout(dropout)
        self.activation = activation
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor
        """
        original_shape = x.shape.dims
        
        # Flatten if needed
        if x.shape.ndim > 2:
            batch_size = 1
            for dim in original_shape[:-1]:
                batch_size *= dim
            x_flat = x.reshape(batch_size, original_shape[-1])
        else:
            x_flat = x
        
        # First linear
        hidden = self.fc1.forward(x_flat)
        
        # Activation
        if self.activation == 'relu':
            hidden = Activations.relu(hidden)
        elif self.activation == 'gelu':
            hidden = Activations.gelu(hidden)
        elif self.activation == 'swish':
            hidden = Activations.swish(hidden)
        else:
            raise ValueError(f"Unknown activation: {self.activation}")
        
        hidden = self.dropout.forward(hidden)
        
        # Second linear
        output = self.fc2.forward(hidden)
        output = self.dropout.forward(output)
        
        # Reshape back
        if x.shape.ndim > 2:
            output = output.reshape(*original_shape)
        
        return output


__all__ = [
    'MultiHeadAttention',
    'FeedForwardNetwork',
    'TransformerBlock',
    'TransformerEncoder',
    'TransformerDecoder',
    'CrossAttentionBlock',
    'EncoderDecoderModel',
    'PositionWiseFeedForward',
]
