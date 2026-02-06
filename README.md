# THALOS Prime - Single File Deployment

**Version 3.1.0** - Complete Consolidated System

## Overview

This repository contains the complete THALOS Prime AI system in a single, self-contained Python file: `thalos_prime_complete.py`

## Features

- ✅ **Zero Dependencies** - Uses only Python standard library
- ✅ **Single File** - Everything in one file for easy deployment
- ✅ **Auto-Deploy** - GitHub Actions automatically deploys on push to master
- ✅ **Complete System** - Full transformer-based AI with 260K+ parameters
- ✅ **Multiple Modes** - Interactive, query, and server modes

## Quick Start

```bash
# Show version information
python thalos_prime_complete.py --version

# Interactive mode
python thalos_prime_complete.py --interactive

# Process a single query
python thalos_prime_complete.py --query "Hello THALOS"

# Run as web server
python thalos_prime_complete.py --server
```

## Requirements

- Python 3.6 or higher
- No external dependencies required!

## Components Included

- **Tensor Operations** - N-dimensional arrays with broadcasting
- **Neural Networks** - Transformer architecture with multi-head attention
- **Tokenization** - Character and word-level tokenizers
- **Text Generation** - Temperature, top-k, top-p sampling
- **Web Application** - REST API for query processing

## Auto-Deployment

Every push to the master branch automatically:
1. ✅ Verifies the single file exists
2. ✅ Tests the system functionality
3. ✅ Confirms deployment readiness

See `.github/workflows/deploy-thalos.yml` for deployment configuration.

## Architecture

The system implements a complete transformer-based language model with:
- Multi-head self-attention
- Feed-forward networks
- Layer normalization
- Positional encoding
- Text generation with sampling

Total: ~260,840 trainable parameters

## License

Proprietary - THALOS Prime Systems

---

**THALOS Prime** - *Intelligent AI System with Semantic Behavioral Integration*
