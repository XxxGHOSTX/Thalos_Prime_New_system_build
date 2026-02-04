#!/usr/bin/env python
"""
Setup script for THALOS Prime
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="thalos-prime",
    version="3.2.0",
    description="THALOS Prime - Advanced AI System with Matrix Codex and Neural Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="THALOS Prime Systems",
    python_requires=">=3.11",
    packages=find_packages(include=["thalos_prime", "thalos_prime.*"]) + find_packages(where="src"),
    package_dir={"": ".", "thalos": "src/thalos"},
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "thalos-prime=thalos_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai neural-networks matrix visualization",
)
