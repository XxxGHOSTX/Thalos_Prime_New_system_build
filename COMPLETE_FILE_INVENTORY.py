#!/usr/bin/env python3
"""
THALOS Prime - Complete File Inventory
Generates inventory of all project files.
"""

import os
from pathlib import Path


def generate_inventory():
    """Generate file inventory."""
    root = Path(__file__).parent
    
    print("=" * 60)
    print("THALOS Prime File Inventory")
    print("=" * 60)
    
    categories = {
        'Python Modules': [],
        'Documentation': [],
        'Configuration': [],
        'Tests': [],
    }
    
    for path in root.rglob('*'):
        if path.is_file() and not any(p.startswith('.') for p in path.parts):
            rel_path = path.relative_to(root)
            
            if path.suffix == '.py':
                categories['Python Modules'].append(str(rel_path))
            elif path.suffix in ['.md', '.txt']:
                categories['Documentation'].append(str(rel_path))
            elif path.suffix in ['.toml', '.yml', '.yaml', '.json']:
                categories['Configuration'].append(str(rel_path))
            elif 'test' in path.stem.lower():
                categories['Tests'].append(str(rel_path))
    
    for category, files in categories.items():
        print(f"\n{category} ({len(files)} files):")
        print("-" * 40)
        for f in sorted(files)[:20]:
            print(f"  {f}")
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more")
    
    total = sum(len(f) for f in categories.values())
    print(f"\nTotal: {total} files")


if __name__ == '__main__':
    generate_inventory()
