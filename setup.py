#!/usr/bin/env python3
"""
THALOS Prime - Setup Script

This script allows THALOS Prime to be installed as a Python package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "THALOS Prime - Intelligent AI System with Semantic Behavioral Integration"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.strip().startswith('#')
        ]

setup(
    name="thalos-prime",
    version="3.1.0",
    author="THALOS Prime Systems",
    description="Intelligent AI System with Semantic Behavioral Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XxxGHOSTX/Thalos_Prime_New_system_build",
    packages=find_packages(exclude=["tests", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'thalos=main:main',
            'thalos-gui=thalos_prime_gui:main',
            'thalos-test=test_system:main',
        ],
    },
    include_package_data=True,
    package_data={
        'thalos_prime': ['**/*.py'],
        'thalos_sbi_standalone': ['**/*.py', '**/*.json'],
        'thalos_prime_advanced_gui': ['**/*.py'],
    },
)
