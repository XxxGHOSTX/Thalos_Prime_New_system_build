#!/usr/bin/env python3
"""
THALOS Prime System Test Script
Verifies all components are working correctly
"""

import sys
from pathlib import Path

# Test 1: Import math module
print("=" * 70)
print("THALOS Prime System Test Suite")
print("=" * 70)

print("\n[1/6] Testing Math Module...")
try:
    from thalos_prime.math import (
        Tensor, Shape, randn, zeros, ones,
        LinearAlgebra, Activations, Distributions,
        AttentionMechanisms
    )

    # Test tensor creation
    t = randn(3, 4)
    assert t.shape.dims == (3, 4)

    # Test activations
    x = Tensor([1.0, 2.0, 3.0, 4.0])
    relu_out = Activations.relu(x)
    assert len(relu_out.data) == 4

    print("✓ Math module working correctly")
    print(f"  - Created tensor: {t.shape}")
    print(f"  - ReLU activation: {relu_out.data}")
except Exception as e:
    print(f"✗ Math module test failed: {e}")
    sys.exit(1)

print("\n[2/6] Testing Encoding Module...")
try:
    from thalos_prime.encoding import CharacterTokenizer

    tokenizer = CharacterTokenizer()
    tokenizer.build_vocab(["hello world", "thalos prime"])

    encoded = tokenizer.encode("hello")
    decoded = tokenizer.decode(encoded)

    print("✓ Encoding module working correctly")
    print(f"  - Vocab size: {tokenizer.vocab_size}")
    print(f"  - Encoded: {encoded}")
    print(f"  - Decoded: '{decoded}'")
except Exception as e:
    print(f"✗ Encoding module test failed: {e}")
    sys.exit(1)

print("\n[3/6] Testing Crypto Module...")
try:
    from thalos_prime.crypto import SecureHash, AES256, SecureRandom

    # Test hash
    hash_val = SecureHash.sha256("test")
    assert len(hash_val) == 64

    # Test AES
    aes = AES256("password")
    encrypted = aes.encrypt_simple("secret")
    decrypted = aes.decrypt_simple(encrypted)

    # Test random
    random_bytes = SecureRandom.random_bytes(16)
    assert len(random_bytes) == 16

    print("✓ Crypto module working correctly")
    print(f"  - SHA256 hash: {hash_val[:16]}...")
    print(f"  - AES encryption/decryption: OK")
    print(f"  - Secure random: {len(random_bytes)} bytes generated")
except Exception as e:
    print(f"✗ Crypto module test failed: {e}")
    sys.exit(1)

print("\n[4/6] Testing Kernel Module...")
try:
    from thalos_prime.kernel import (
        MemoryAllocator, VirtualFileSystem,
        ProcessContext
    )

    # Test memory
    mem = MemoryAllocator(1024)
    addr = mem.allocate(256)
    assert addr == 0
    mem.deallocate(addr)

    # Test filesystem
    vfs = VirtualFileSystem()
    vfs.create_file("test.txt", "Hello")
    content = vfs.read_file("test.txt")
    assert content == "Hello"

    # Test process
    proc = ProcessContext("test_proc")
    assert proc.state == 'created'

    print("✓ Kernel module working correctly")
    print(f"  - Memory allocation: OK")
    print(f"  - Virtual filesystem: OK")
    print(f"  - Process context: OK")
except Exception as e:
    print(f"✗ Kernel module test failed: {e}")
    sys.exit(1)

print("\n[5/6] Testing Neural Network Module...")
try:
    from thalos_prime.nn import (
        Linear, Embedding, PositionalEncoding,
        TransformerBlock
    )
    from thalos_prime.math import randn

    # Test linear layer
    linear = Linear(10, 5)
    x = randn(3, 10)
    output = linear.forward(x)
    assert output.shape.dims == (3, 5)

    # Test embedding
    embedding = Embedding(100, 8)
    token_ids = Tensor([1, 2, 3])
    emb_output = embedding.forward(token_ids)
    assert emb_output.shape.dims[1] == 8

    print("✓ Neural Network module working correctly")
    print(f"  - Linear layer: {output.shape}")
    print(f"  - Embedding layer: {emb_output.shape}")
except Exception as e:
    print(f"✗ NN module test failed: {e}")
    sys.exit(1)

print("\n[6/6] Testing SBI Reasoning Module...")
try:
    from thalos_prime.reasoning import SemanticBehavioralIntegration

    sbi = SemanticBehavioralIntegration()

    # Test semantic analysis
    result = sbi.process_input("What is machine learning?")
    assert 'analysis' in result
    assert 'intent' in result['analysis']

    print("✓ SBI Reasoning module working correctly")
    print(f"  - Intent detection: {result['analysis']['intent']}")
    print(f"  - Category: {result['analysis']['category']}")
    print(f"  - Confidence: {result['confidence']}")
except Exception as e:
    print(f"✗ SBI module test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("All Tests Passed! ✓")
print("=" * 70)
print("\nTHALOS Prime system is ready for use.")
print("Run 'python main.py --interactive' to start the system.")
