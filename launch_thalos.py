#!/usr/bin/env python3
"""
THALOS Prime - Launch Script
Launches the THALOS Prime system.
"""

import sys
from pathlib import Path


def main():
    """Launch THALOS Prime."""
    print("=" * 60)
    print("THALOS Prime Launcher")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("Warning: Python 3.11+ recommended")
    
    # Import and run
    try:
        from main import main as run_main
        run_main()
    except ImportError:
        # Run directly
        from thalos_prime.core import THALOSPrimeEngine
        
        engine = THALOSPrimeEngine()
        engine.interactive_session()


if __name__ == '__main__':
    main()
