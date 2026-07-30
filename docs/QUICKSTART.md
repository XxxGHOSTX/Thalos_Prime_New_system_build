# THALOS Prime Quick Start Guide

## Installation

1. Clone the repository
2. Ensure Python 3.11+ is installed
3. No additional dependencies required

## Running THALOS Prime

### Interactive Mode
```bash
python main.py --interactive
```

### Single Query
```bash
python main.py --query "Hello, how are you?"
```

### GUI Mode
```bash
python thalos_prime_gui.py
```

### Run Tests
```bash
python test_system.py
```

## Basic Usage

```python
from thalos_prime.core import THALOSPrimeEngine

# Create engine
engine = THALOSPrimeEngine()
engine.initialize()

# Process query
result = engine.process_query("What is AI?")
print(result['response'])
```

## Math Operations

```python
from thalos_prime.math import Tensor, randn, zeros

# Create tensors
t = randn(3, 4)
z = zeros(3, 4)

# Operations
result = t + z
result = t * 2
result = t.sum()
```

## Tokenization

```python
from thalos_prime.encoding import CharacterTokenizer

tokenizer = CharacterTokenizer()
tokenizer.build_vocab(["hello world"])

encoded = tokenizer.encode("hello")
decoded = tokenizer.decode(encoded)
```

## Encryption

```python
from thalos_prime.crypto import AES256, SecureHash

# Hash
hash_val = SecureHash.sha256("my data")

# Encrypt/Decrypt
aes = AES256("password")
encrypted = aes.encrypt_simple("secret message")
decrypted = aes.decrypt_simple(encrypted)
```
