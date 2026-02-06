#!/usr/bin/env python3
"""
THALOS Prime Neural Network Models
Pure Python implementation of complete models and training utilities
"""

import math
import random
from typing import Optional, List, Tuple

from ..math import Tensor, Shape, zeros, ones
from ..math.activations import Activations
from ..math.linear_algebra import LinearAlgebra
from .layer import Layer, Linear, Embedding, PositionalEncoding, Dropout
from .transformer import TransformerEncoder, TransformerDecoder, TransformerBlock


class THALOSPrimeModel(Layer):
    """
    THALOS Prime main language model
    Transformer-based architecture for text generation
    """
    
    def __init__(self, vocab_size: int, d_model: int = 512, num_layers: int = 6,
                 num_heads: int = 8, d_ff: int = 2048, max_seq_len: int = 512,
                 dropout: float = 0.1):
        """
        Initialize THALOS Prime model
        
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
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_layers = num_layers
        self.num_heads = num_heads
        
        # Embedding layers
        self.token_embedding = Embedding(vocab_size, d_model)
        self.position_encoding = PositionalEncoding(d_model, max_seq_len)
        
        # Transformer decoder stack
        self.decoder = TransformerDecoder(num_layers, d_model, num_heads, d_ff, dropout)
        
        # Output projection to vocabulary
        self.output_projection = Linear(d_model, vocab_size)
        
        # Dropout
        self.dropout = Dropout(dropout)
    
    def forward(self, input_ids: Tensor) -> Tensor:
        """
        Forward pass through model
        
        Args:
            input_ids: Input token IDs (batch_size, seq_len) or (seq_len,)
            
        Returns:
            Logits over vocabulary (batch_size, seq_len, vocab_size) or (seq_len, vocab_size)
        """
        # Get embeddings
        embeddings = self.token_embedding.forward(input_ids)
        
        # Add positional encoding
        embeddings = self.position_encoding.forward(embeddings)
        
        # Apply dropout
        embeddings = self.dropout.forward(embeddings)
        
        # Pass through decoder
        hidden_states = self.decoder.forward(embeddings)
        
        # Project to vocabulary
        original_shape = hidden_states.shape.dims
        if hidden_states.shape.ndim == 3:
            batch_size, seq_len, d_model = original_shape
            hidden_flat = hidden_states.reshape(batch_size * seq_len, d_model)
            logits = self.output_projection.forward(hidden_flat)
            logits = logits.reshape(batch_size, seq_len, self.vocab_size)
        else:
            seq_len, d_model = original_shape
            hidden_flat = hidden_states.reshape(seq_len, d_model)
            logits = self.output_projection.forward(hidden_flat)
            logits = logits.reshape(seq_len, self.vocab_size)
        
        return logits
    
    def generate(self, prompt_ids: List[int], max_length: int = 100,
                 temperature: float = 1.0, top_k: int = 50, top_p: float = 0.95) -> List[int]:
        """
        Generate text autoregressively
        
        Args:
            prompt_ids: Initial prompt token IDs
            max_length: Maximum generation length
            temperature: Sampling temperature (higher = more random)
            top_k: Top-K filtering (0 = disabled)
            top_p: Top-P (nucleus) filtering (1.0 = disabled)
            
        Returns:
            Generated token IDs
            
        Note:
            If the generated sequence exceeds the model's max_seq_len from initialization,
            the model will raise a ValueError. Consider implementing sliding window or
            truncation strategies for longer sequences.
        """
        self.eval()
        generated = list(prompt_ids)
        
        for _ in range(max_length):
            # Get logits for current sequence
            input_tensor = Tensor(generated, Shape(len(generated),))
            logits = self.forward(input_tensor)
            
            # Get logits for last position
            last_logits_data = logits.data[-self.vocab_size:]
            last_logits = Tensor(last_logits_data, Shape(self.vocab_size,))
            
            # Apply temperature
            if temperature != 1.0:
                scaled_logits = last_logits * (1.0 / temperature)
            else:
                scaled_logits = last_logits
            
            # Apply top-k filtering
            if top_k > 0:
                scaled_logits = self._top_k_filtering(scaled_logits, top_k)
            
            # Apply top-p filtering
            if top_p < 1.0:
                scaled_logits = self._top_p_filtering(scaled_logits, top_p)
            
            # Convert to probabilities
            probs = Activations.softmax(scaled_logits)
            
            # Sample from distribution
            next_token = self._sample(probs)
            generated.append(next_token)
            
            # Check for end-of-sequence token (assuming 0 is EOS)
            if next_token == 0:
                break
        
        return generated
    
    def _top_k_filtering(self, logits: Tensor, k: int) -> Tensor:
        """
        Filter logits to keep only top K values
        
        Args:
            logits: Input logits
            k: Number of top values to keep
            
        Returns:
            Filtered logits
        """
        # Get indices sorted by value
        indexed_logits = [(i, val) for i, val in enumerate(logits.data)]
        indexed_logits.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top k
        top_k_indices = set(idx for idx, _ in indexed_logits[:k])
        
        # Set others to -inf
        filtered_data = []
        for i, val in enumerate(logits.data):
            if i in top_k_indices:
                filtered_data.append(val)
            else:
                filtered_data.append(-1e9)
        
        return Tensor(filtered_data, logits.shape)
    
    def _top_p_filtering(self, logits: Tensor, p: float) -> Tensor:
        """
        Filter logits using nucleus (top-p) sampling
        
        Args:
            logits: Input logits
            p: Cumulative probability threshold
            
        Returns:
            Filtered logits
        """
        # Convert to probabilities
        probs = Activations.softmax(logits)
        
        # Sort by probability
        indexed_probs = [(i, val) for i, val in enumerate(probs.data)]
        indexed_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Find cutoff point
        cumsum = 0.0
        cutoff_idx = len(indexed_probs)
        for i, (idx, prob) in enumerate(indexed_probs):
            cumsum += prob
            if cumsum >= p:
                cutoff_idx = i + 1
                break
        
        # Keep top-p tokens
        top_p_indices = set(idx for idx, _ in indexed_probs[:cutoff_idx])
        
        # Filter logits
        filtered_data = []
        for i, val in enumerate(logits.data):
            if i in top_p_indices:
                filtered_data.append(val)
            else:
                filtered_data.append(-1e9)
        
        return Tensor(filtered_data, logits.shape)
    
    def _sample(self, probs: Tensor) -> int:
        """
        Sample from probability distribution
        
        Args:
            probs: Probability distribution
            
        Returns:
            Sampled index
        """
        # Multinomial sampling
        r = random.random()
        cumsum = 0.0
        
        for i, p in enumerate(probs.data):
            cumsum += p
            if cumsum >= r:
                return i
        
        # Fallback to last index
        return len(probs.data) - 1


class ModelOptimizer:
    """
    Adam optimizer for model training
    """
    
    def __init__(self, learning_rate: float = 0.001, beta1: float = 0.9,
                 beta2: float = 0.999, epsilon: float = 1e-8):
        """
        Initialize Adam optimizer
        
        Args:
            learning_rate: Learning rate
            beta1: Exponential decay rate for first moment
            beta2: Exponential decay rate for second moment
            epsilon: Small constant for numerical stability
        """
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        
        # State
        self.t = 0
        self.m = {}  # First moment estimates
        self.v = {}  # Second moment estimates
    
    def step(self, parameters: List[Tuple[str, Tensor]], gradients: List[Tensor]):
        """
        Perform optimization step
        
        Args:
            parameters: List of (name, parameter) tuples
            gradients: List of gradients corresponding to parameters
        """
        self.t += 1
        
        for (name, param), grad in zip(parameters, gradients):
            # Initialize moments if needed
            if name not in self.m:
                self.m[name] = zeros(*param.shape.dims)
                self.v[name] = zeros(*param.shape.dims)
            
            # Update biased first moment estimate
            m_data = []
            for i in range(len(param.data)):
                m_val = self.beta1 * self.m[name].data[i] + (1 - self.beta1) * grad.data[i]
                m_data.append(m_val)
            self.m[name] = Tensor(m_data, param.shape)
            
            # Update biased second moment estimate
            v_data = []
            for i in range(len(param.data)):
                v_val = self.beta2 * self.v[name].data[i] + (1 - self.beta2) * (grad.data[i] ** 2)
                v_data.append(v_val)
            self.v[name] = Tensor(v_data, param.shape)
            
            # Compute bias-corrected moment estimates
            m_hat_data = [m / (1 - self.beta1 ** self.t) for m in self.m[name].data]
            v_hat_data = [v / (1 - self.beta2 ** self.t) for v in self.v[name].data]
            
            # Update parameters
            param_data = []
            for i in range(len(param.data)):
                update = self.learning_rate * m_hat_data[i] / (math.sqrt(v_hat_data[i]) + self.epsilon)
                param_data.append(param.data[i] - update)
            
            # Update parameter in place
            param.data = param_data
    
    def zero_grad(self):
        """Reset optimizer state"""
        pass


class LossFunction:
    """
    Loss functions for training
    """
    
    @staticmethod
    def cross_entropy(logits: Tensor, targets: Tensor, reduction: str = 'mean') -> float:
        """
        Cross-entropy loss for classification
        
        Args:
            logits: Model predictions (batch_size, num_classes) or (num_classes,)
            targets: Target labels (batch_size,) or scalar
            reduction: How to reduce loss ('mean', 'sum', 'none')
            
        Returns:
            Loss value
        """
        # Handle different input shapes
        if logits.shape.ndim == 1:
            # Single prediction
            num_classes = logits.shape.dims[0]
            target_idx = int(targets.data[0] if isinstance(targets, Tensor) else targets)
            
            # Apply softmax to get probabilities
            probs = Activations.softmax(logits)
            
            # Cross-entropy: -log(p[target])
            target_prob = probs.data[target_idx]
            loss = -math.log(max(target_prob, 1e-10))
            
            return loss
        
        elif logits.shape.ndim == 2:
            # Batch of predictions
            batch_size, num_classes = logits.shape.dims
            
            losses = []
            for i in range(batch_size):
                # Get logits for this sample
                sample_logits_data = logits.data[i * num_classes:(i + 1) * num_classes]
                sample_logits = Tensor(sample_logits_data, Shape(num_classes,))
                
                # Get target for this sample
                target_idx = int(targets.data[i])
                
                # Apply softmax
                probs = Activations.softmax(sample_logits)
                
                # Cross-entropy
                target_prob = probs.data[target_idx]
                loss = -math.log(max(target_prob, 1e-10))
                losses.append(loss)
            
            if reduction == 'mean':
                return sum(losses) / len(losses)
            elif reduction == 'sum':
                return sum(losses)
            else:
                return losses
        
        else:
            raise ValueError(f"Unsupported logits shape: {logits.shape}")
    
    @staticmethod
    def mse_loss(predictions: Tensor, targets: Tensor, reduction: str = 'mean') -> float:
        """
        Mean squared error loss
        
        Args:
            predictions: Model predictions
            targets: Target values
            reduction: How to reduce loss ('mean', 'sum', 'none')
            
        Returns:
            Loss value
        """
        # Compute squared differences
        squared_diffs = []
        for pred, target in zip(predictions.data, targets.data):
            squared_diffs.append((pred - target) ** 2)
        
        if reduction == 'mean':
            return sum(squared_diffs) / len(squared_diffs)
        elif reduction == 'sum':
            return sum(squared_diffs)
        else:
            return squared_diffs
    
    @staticmethod
    def binary_cross_entropy(predictions: Tensor, targets: Tensor, 
                            reduction: str = 'mean') -> float:
        """
        Binary cross-entropy loss
        
        Args:
            predictions: Model predictions (probabilities between 0 and 1)
            targets: Target binary labels (0 or 1)
            reduction: How to reduce loss ('mean', 'sum', 'none')
            
        Returns:
            Loss value
        """
        losses = []
        for pred, target in zip(predictions.data, targets.data):
            # Clip predictions to avoid log(0)
            pred = max(min(pred, 1 - 1e-7), 1e-7)
            
            # Binary cross-entropy: -[y*log(p) + (1-y)*log(1-p)]
            loss = -(target * math.log(pred) + (1 - target) * math.log(1 - pred))
            losses.append(loss)
        
        if reduction == 'mean':
            return sum(losses) / len(losses)
        elif reduction == 'sum':
            return sum(losses)
        else:
            return losses


class SimpleClassifier(Layer):
    """
    Simple feedforward classifier
    """
    
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int, dropout: float = 0.1):
        """
        Initialize classifier
        
        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden layer dimension
            num_classes: Number of output classes
            dropout: Dropout probability
        """
        super().__init__()
        
        self.fc1 = Linear(input_dim, hidden_dim)
        self.fc2 = Linear(hidden_dim, num_classes)
        self.dropout = Dropout(dropout)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass through classifier
        
        Args:
            x: Input tensor (batch_size, input_dim) or (input_dim,)
            
        Returns:
            Logits (batch_size, num_classes) or (num_classes,)
        """
        # First layer + activation + dropout
        hidden = self.fc1.forward(x)
        hidden = Activations.relu(hidden)
        hidden = self.dropout.forward(hidden)
        
        # Output layer
        logits = self.fc2.forward(hidden)
        
        return logits


class Seq2SeqModel(Layer):
    """
    Sequence-to-sequence model with encoder-decoder architecture
    """
    
    def __init__(self, vocab_size: int, d_model: int = 512, num_layers: int = 6,
                 num_heads: int = 8, d_ff: int = 2048, dropout: float = 0.1):
        """
        Initialize seq2seq model
        
        Args:
            vocab_size: Size of vocabulary
            d_model: Dimension of model embeddings
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            d_ff: Dimension of feed-forward hidden layer
            dropout: Dropout probability
        """
        super().__init__()
        
        # Embeddings
        self.encoder_embedding = Embedding(vocab_size, d_model)
        self.decoder_embedding = Embedding(vocab_size, d_model)
        self.position_encoding = PositionalEncoding(d_model)
        
        # Encoder and decoder
        self.encoder = TransformerEncoder(num_layers, d_model, num_heads, d_ff, dropout)
        self.decoder = TransformerDecoder(num_layers, d_model, num_heads, d_ff, dropout)
        
        # Output projection
        self.output_projection = Linear(d_model, vocab_size)
    
    def forward(self, encoder_input: Tensor, decoder_input: Tensor) -> Tensor:
        """
        Forward pass through seq2seq model
        
        Args:
            encoder_input: Encoder input token IDs
            decoder_input: Decoder input token IDs
            
        Returns:
            Output logits
        """
        # Encode
        encoder_embeddings = self.encoder_embedding.forward(encoder_input)
        encoder_embeddings = self.position_encoding.forward(encoder_embeddings)
        encoder_output = self.encoder.forward(encoder_embeddings)
        
        # Decode
        decoder_embeddings = self.decoder_embedding.forward(decoder_input)
        decoder_embeddings = self.position_encoding.forward(decoder_embeddings)
        decoder_output = self.decoder.forward(decoder_embeddings)
        
        # Project to vocabulary
        logits = self.output_projection.forward(decoder_output)
        
        return logits


class ModelUtils:
    """
    Utility functions for model operations
    """
    
    @staticmethod
    def count_parameters(model: Layer) -> int:
        """
        Count total number of parameters in a model
        
        Args:
            model: Model instance
            
        Returns:
            Total parameter count
        """
        total = 0
        
        # Count parameters in all layer attributes
        for attr_name in dir(model):
            attr = getattr(model, attr_name)
            
            # Check if it's a layer
            if isinstance(attr, Layer):
                # Recursively count parameters
                total += ModelUtils.count_parameters(attr)
            
            # Check if it's a tensor (parameter)
            elif isinstance(attr, Tensor):
                total += attr.shape.size
        
        return total
    
    @staticmethod
    def model_summary(model: Layer) -> str:
        """
        Generate a summary of model architecture
        
        Args:
            model: Model instance
            
        Returns:
            Summary string
        """
        summary = []
        summary.append("="*60)
        summary.append(f"Model: {model.__class__.__name__}")
        summary.append("="*60)
        
        total_params = ModelUtils.count_parameters(model)
        summary.append(f"Total Parameters: {total_params:,}")
        
        return "\n".join(summary)


__all__ = [
    'THALOSPrimeModel',
    'ModelOptimizer',
    'LossFunction',
    'SimpleClassifier',
    'Seq2SeqModel',
    'ModelUtils',
]
