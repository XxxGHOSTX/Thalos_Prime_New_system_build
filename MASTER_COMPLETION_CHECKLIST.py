#!/usr/bin/env python3
"""
THALOS Prime - Master Completion Checklist
Checks all required components are present and functional.
"""

import os
import sys
from pathlib import Path


def check_component(name: str, check_fn) -> bool:
    """Check a component."""
    try:
        result = check_fn()
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
        return result
    except Exception as e:
        print(f"  ✗ {name} - {e}")
        return False


def run_checklist():
    """Run the completion checklist."""
    print("=" * 60)
    print("THALOS Prime Master Completion Checklist")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Core modules
    print("\n[Core Modules]")
    
    checks = [
        ("Math module", lambda: __import__('thalos_prime.math')),
        ("Encoding module", lambda: __import__('thalos_prime.encoding')),
        ("Crypto module", lambda: __import__('thalos_prime.crypto')),
        ("Kernel module", lambda: __import__('thalos_prime.kernel')),
        ("NN module", lambda: __import__('thalos_prime.nn')),
        ("Reasoning module", lambda: __import__('thalos_prime.reasoning')),
        ("Config module", lambda: __import__('thalos_prime.config')),
        ("Storage module", lambda: __import__('thalos_prime.storage')),
        ("Inference module", lambda: __import__('thalos_prime.inference')),
        ("Core module", lambda: __import__('thalos_prime.core')),
        ("Utils module", lambda: __import__('thalos_prime.utils')),
        ("Database module", lambda: __import__('thalos_prime.database')),
        ("Wetware module", lambda: __import__('thalos_prime.wetware')),
    ]
    
    for name, check in checks:
        if check_component(name, check):
            passed += 1
        else:
            failed += 1
    
    # Standalone modules
    print("\n[SBI Standalone]")
    standalone_checks = [
        ("Core engine", lambda: os.path.exists('thalos_sbi_standalone/core_engine.py')),
        ("Code generator", lambda: os.path.exists('thalos_sbi_standalone/code_generator.py')),
        ("Math module", lambda: os.path.exists('thalos_sbi_standalone/complete_math_module.py')),
        ("NLP module", lambda: os.path.exists('thalos_sbi_standalone/complete_nlp_module.py')),
    ]
    
    for name, check in standalone_checks:
        if check_component(name, check):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_checklist()
    sys.exit(0 if success else 1)
