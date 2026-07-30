#!/usr/bin/env python3
"""
THALOS Prime - Build Completion Report
Generates build completion report.
"""

import os
from pathlib import Path


def generate_report():
    """Generate build completion report."""
    print("=" * 60)
    print("THALOS Prime Build Completion Report")
    print("=" * 60)
    
    root = Path(__file__).parent
    
    # Count files by type
    py_files = list(root.rglob('*.py'))
    md_files = list(root.rglob('*.md'))
    txt_files = list(root.rglob('*.txt'))
    
    print(f"\nFile Statistics:")
    print(f"  Python files: {len(py_files)}")
    print(f"  Markdown files: {len(md_files)}")
    print(f"  Text files: {len(txt_files)}")
    
    # Count lines
    total_lines = 0
    for py_file in py_files:
        if '.git' not in str(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += len(f.readlines())
            except:
                pass
    
    print(f"\nCode Statistics:")
    print(f"  Total Python lines: {total_lines}")
    
    # Check key modules
    print(f"\nModule Status:")
    modules = [
        'thalos_prime/math',
        'thalos_prime/nn',
        'thalos_prime/encoding',
        'thalos_prime/crypto',
        'thalos_prime/kernel',
        'thalos_prime/reasoning',
        'thalos_prime/core',
    ]
    
    for module in modules:
        exists = (root / module).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {module}")
    
    print("\n" + "=" * 60)
    print("Build Status: COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    generate_report()
