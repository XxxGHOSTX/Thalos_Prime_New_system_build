# THALOS Prime

**Intelligent AI System with Semantic Behavioral Integration**

Version: 3.1.0

## Overview

THALOS Prime is a comprehensive AI system built from the ground up with custom implementations of:

- Tensor operations and linear algebra
- Neural network layers and transformer architectures
- Text tokenization (BPE, character-level, word-level)
- Cryptographic functions (AES-256, SHA-256)
- Operating system primitives (memory management, virtual filesystem)
- Semantic Behavioral Integration (SBI) reasoning

## Features

- **Custom Math Engine**: Full tensor operations without external dependencies
- **Transformer Architecture**: Multi-head attention, feed-forward networks
- **Tokenization**: Multiple tokenization strategies
- **Security**: Built-in encryption and hashing
- **Reasoning**: Semantic analysis with behavioral modeling

## Quick Start (Windows)

### Option 1: Use Launcher Scripts (Easiest)
Double-click any of these Windows batch files:
- `LAUNCH.bat` - Start THALOS Prime in interactive mode
- `LAUNCH_GUI.bat` - Start the GUI interface
- `LAUNCH_ADVANCED_GUI.bat` - Start the advanced GUI

### Option 2: Command Line
```bash
# Run interactive session
python main.py --interactive

# Process a single query
python main.py --query "What is machine learning?"

# Run GUI
python thalos_prime_gui.py

# Run system tests
python test_system.py
```

## Installation (Windows)

1. **Install Python 3.11 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Clone or Download this repository**
   - Extract all files to a folder (e.g., `C:\ThalosApp`)

3. **Run the application**
   - Double-click `LAUNCH.bat` to start

No additional dependencies are required for core functionality!

## Project Structure

```
ThalosApp/
├── LAUNCH.bat              # Windows launcher (interactive mode)
├── LAUNCH_GUI.bat          # GUI launcher
├── LAUNCH_ADVANCED_GUI.bat # Advanced GUI launcher
├── main.py                 # Main entry point
├── app.py                  # Web application
├── requirements.txt        # Optional dependencies
├── pyproject.toml         # Project configuration
│
├── thalos_prime/          # Core AI system modules
│   ├── math/              # Tensor operations, linear algebra
│   ├── nn/                # Neural network layers, transformers
│   ├── encoding/          # Text tokenization
│   ├── crypto/            # Encryption and hashing
│   ├── kernel/            # Memory management, filesystem
│   ├── reasoning/         # SBI reasoning engine
│   ├── core/              # Main orchestrator
│   ├── config/            # Configuration management
│   ├── storage/           # Data persistence
│   ├── inference/         # Text generation
│   ├── utils/             # Utilities
│   ├── database/          # Database operations
│   └── wetware/           # Bio-inspired computing
│
├── thalos_sbi_standalone/ # Standalone SBI system
│   ├── core_engine.py
│   ├── code_generator.py
│   ├── nlp_module.py
│   └── ...
│
├── docs/                  # All documentation
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   └── ...
│
├── scripts/               # Utility and helper scripts
│   ├── master_builder.py
│   ├── system_validator.py
│   └── ...
│
├── tests/                 # Test files
│   └── test_gui_import.py
│
├── data/                  # Database files (auto-created)
│   └── (database files stored here)
│
└── thalos_storage/        # Application data storage
```

## Requirements

- **Python 3.11+** (required)
- **Windows 7 or higher** (recommended: Windows 10/11)
- No external dependencies for core functionality
- Optional dependencies available in `requirements.txt` for enhanced features

## License

Proprietary - THALOS Prime Systems

## Documentation

All documentation is located in the `docs/` folder:
- `docs/QUICKSTART.md` - Quick start guide
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/FILE_INDEX.md` - Complete file listing
- `docs/GUI_README.md` - GUI usage guide
- `docs/QUICK_REFERENCE.md` - Quick reference guide

## Support

For issues or questions, please refer to the documentation in the `docs/` folder.
