#!/usr/bin/env python3
"""
THALOS Prime - Main Entry Point
The primary entry point for the THALOS Prime system.
"""

import sys
import argparse
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='THALOS Prime - Intelligent AI System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Process a single query'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run system tests'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version information'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    return parser.parse_args()


def show_version():
    """Show version information."""
    print("=" * 60)
    print("THALOS Prime v3.1.0")
    print("=" * 60)
    print("Intelligent AI System with Semantic Behavioral Integration")
    print()
    print("Components:")
    print("  - Math Module: Tensor operations, linear algebra, activations")
    print("  - Encoding Module: BPE, character, word tokenization")
    print("  - Crypto Module: AES-256, SHA-256, PBKDF2")
    print("  - Kernel Module: Memory management, virtual filesystem")
    print("  - NN Module: Transformers, attention mechanisms")
    print("  - Reasoning Module: Semantic Behavioral Integration")
    print("  - Core Module: Main orchestration engine")
    print()


def run_interactive():
    """Run interactive session."""
    from thalos_prime.core import THALOSPrimeEngine
    
    engine = THALOSPrimeEngine()
    engine.interactive_session()


def process_query(query: str):
    """Process a single query."""
    from thalos_prime.core import THALOSPrimeEngine
    
    engine = THALOSPrimeEngine()
    engine.initialize()
    
    result = engine.process_query(query)
    print(f"\nQuery: {query}")
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['confidence']:.2f}")


def run_tests():
    """Run system tests."""
    print("Running THALOS Prime system tests...")
    print()
    
    # Import and run test
    try:
        import test_system
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_args()
    
    if args.version:
        show_version()
        return 0
    
    if args.test:
        run_tests()
        return 0
    
    if args.query:
        process_query(args.query)
        return 0
    
    if args.interactive:
        run_interactive()
        return 0
    
    # Default: show help
    print("THALOS Prime - Intelligent AI System")
    print()
    print("Usage:")
    print("  python main.py --interactive   # Interactive mode")
    print("  python main.py --query 'text'  # Process single query")
    print("  python main.py --test          # Run tests")
    print("  python main.py --version       # Show version")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
