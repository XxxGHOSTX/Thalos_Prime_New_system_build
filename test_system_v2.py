#!/usr/bin/env python3
"""
THALOS Prime - Test System v2
Extended test suite for THALOS Prime.
"""

import sys


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("THALOS Prime Test Suite v2")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import core modules
    print("\n[1/5] Testing core module imports...")
    try:
        from thalos_prime.math import Tensor, Shape, randn, zeros
        from thalos_prime.encoding import CharacterTokenizer
        from thalos_prime.crypto import SecureHash, AES256
        print("✓ Core imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Core imports failed: {e}")
        tests_failed += 1
    
    # Test 2: Tensor operations
    print("\n[2/5] Testing tensor operations...")
    try:
        from thalos_prime.math import Tensor, randn
        t = randn(3, 4)
        assert t.shape.dims == (3, 4)
        t2 = t + 1
        assert len(t2.data) == 12
        print("✓ Tensor operations successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Tensor operations failed: {e}")
        tests_failed += 1
    
    # Test 3: Tokenization
    print("\n[3/5] Testing tokenization...")
    try:
        from thalos_prime.encoding import CharacterTokenizer
        tokenizer = CharacterTokenizer()
        tokenizer.build_vocab(["hello world"])
        encoded = tokenizer.encode("hello")
        decoded = tokenizer.decode(encoded)
        print("✓ Tokenization successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Tokenization failed: {e}")
        tests_failed += 1
    
    # Test 4: Cryptography
    print("\n[4/5] Testing cryptography...")
    try:
        from thalos_prime.crypto import SecureHash, AES256
        hash_val = SecureHash.sha256("test")
        assert len(hash_val) == 64
        print("✓ Cryptography successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Cryptography failed: {e}")
        tests_failed += 1
    
    # Test 5: Reasoning
    print("\n[5/5] Testing reasoning...")
    try:
        from thalos_prime.reasoning import SemanticBehavioralIntegration
        sbi = SemanticBehavioralIntegration()
        result = sbi.process_input("Hello world")
        assert 'response' in result
        print("✓ Reasoning successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Reasoning failed: {e}")
        tests_failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests: {tests_passed + tests_failed}, Passed: {tests_passed}, Failed: {tests_failed}")
    print("=" * 60)
    
    return tests_failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
