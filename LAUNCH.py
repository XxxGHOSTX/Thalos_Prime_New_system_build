#!/usr/bin/env python3
"""
THALOS Prime - Launch Script
Quick launch script for THALOS Prime.
"""

import sys


def main():
    """Launch THALOS Prime."""
    print("Launching THALOS Prime...")
    
    try:
        from main import main as run_main
        run_main()
    except ImportError:
        from thalos_prime.core import THALOSPrimeEngine
        engine = THALOSPrimeEngine()
        engine.interactive_session()


if __name__ == '__main__':
    main()
