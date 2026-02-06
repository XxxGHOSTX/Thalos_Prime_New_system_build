# THALOS Prime Complete - Quick Reference

## File Location
```
/home/runner/work/Thalos_Prime_New_system_build/Thalos_Prime_New_system_build/thalos_prime_complete.py
```

## Basic Commands

```bash
# Version info
python thalos_prime_complete.py --version

# Interactive mode
python thalos_prime_complete.py --interactive

# Single query
python thalos_prime_complete.py --query "your question here"

# Web server
python thalos_prime_complete.py --server

# With custom port
python thalos_prime_complete.py --server --port 8080
```

## Quick Python API Examples

### Basic Usage
```python
import thalos_prime_complete as tpc

# Initialize engine
engine = tpc.THALOSPrimeEngine()
engine.initialize()

# Process query
result = engine.process_query("Hello")
print(result['response'])
```

### Tensor Operations
```python
import thalos_prime_complete as tpc

# Create tensors
t1 = tpc.Tensor([1, 2, 3])
t2 = tpc.Tensor([4, 5, 6])

# Operations
t3 = t1 + t2      # [5, 7, 9]
t4 = t1 * 2       # [2, 4, 6]
t5 = tpc.zeros(3) # [0, 0, 0]

# 2D tensors
matrix = tpc.Tensor([[1, 2], [3, 4]])
transposed = matrix.T
```

### Tokenization
```python
import thalos_prime_complete as tpc

# Create tokenizer
tokenizer = tpc.WordTokenizer()

# Build vocabulary
texts = ['hello world', 'machine learning']
tokenizer.build_vocab(texts)

# Encode/decode
ids = tokenizer.encode('hello world')
text = tokenizer.decode(ids)
```

### Model Creation
```python
import thalos_prime_complete as tpc

# Create model
model = tpc.THALOSPrimeModel(
    vocab_size=1000,
    d_model=128,
    num_heads=4,
    num_layers=2
)

# Generate text
input_ids = tpc.Tensor([1.0, 2.0, 3.0])
output_ids = model.generate(input_ids, max_length=20)
```

## File Structure (Line Numbers)

| Section | Lines | Content |
|---------|-------|---------|
| Header | 1-80 | Documentation & imports |
| Tensor Ops | 80-450 | Shape, Tensor, factories |
| Activations | 455-520 | ReLU, GELU, Softmax |
| Tokenizers | 525-710 | Character & Word tokenizers |
| NN Layers | 715-990 | Linear, Embedding, etc. |
| Transformers | 995-1160 | Attention, FFN, blocks |
| Model | 1165-1290 | Main model & generation |
| Engine | 1295-1420 | Orchestration |
| Web App | 1425-1480 | REST API |
| CLI | 1485-1506 | Main entry point |

## Key Classes

- `Shape` - Dimension management
- `Tensor` - N-dimensional arrays
- `Activations` - Activation functions (static methods)
- `CharacterTokenizer` - Character-level tokenization
- `WordTokenizer` - Word-level tokenization
- `Layer` - Abstract base for layers
- `Linear` - Fully connected layer
- `Embedding` - Token embeddings
- `PositionalEncoding` - Position embeddings
- `MultiHeadAttention` - Multi-head attention
- `TransformerBlock` - Transformer layer
- `TransformerDecoder` - Decoder stack
- `THALOSPrimeModel` - Complete model
- `THALOSPrimeEngine` - Main engine
- `THALOSApp` - Web application

## Configuration Options

```python
config = {
    'vocab_size': 1000,    # Vocabulary size
    'd_model': 128,        # Model dimension
    'num_heads': 4,        # Attention heads
    'num_layers': 2,       # Transformer layers
    'd_ff': 512,           # FFN dimension
    'max_seq_len': 512,    # Max sequence length
    'dropout': 0.1         # Dropout rate
}

engine = tpc.THALOSPrimeEngine(config)
```

## Common Patterns

### Query Processing
```python
engine = tpc.THALOSPrimeEngine()
engine.initialize()
result = engine.process_query("What is AI?")
print(f"{result['response']} (confidence: {result['confidence']:.2%})")
```

### Batch Tensor Operations
```python
# Create batch of tensors
batch = [tpc.Tensor([i, i+1, i+2]) for i in range(5)]

# Process each
results = [t.mean() for t in batch]
```

### Model Inference
```python
model = tpc.THALOSPrimeModel(vocab_size=1000, d_model=128)
model.eval()  # Set to evaluation mode

input_ids = tpc.Tensor([1.0, 2.0, 3.0])
logits = model.forward(input_ids)
```

## Performance Tips

1. **Smaller models**: Reduce `d_model` and `num_layers`
2. **Shorter sequences**: Keep inputs < 50 tokens
3. **Reuse engine**: Don't reinitialize for each query
4. **PyPy**: Use PyPy for 2-5x speedup

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow init | Reduce vocab_size, d_model |
| Out of memory | Decrease num_layers, max_seq_len |
| Import errors | Use Python 3.6+ |
| Poor quality | This is demo; train for production |

## File Info

- **Size**: 51 KB
- **Lines**: 1,506
- **Executable**: Yes
- **Dependencies**: None (stdlib only)
- **Python**: 3.6+

## Documentation Files

- `thalos_prime_complete.py` - Main file
- `THALOS_PRIME_COMPLETE_README.md` - Full documentation
- `CONSOLIDATION_SUMMARY.txt` - Implementation details
- `QUICK_REFERENCE.md` - This file
