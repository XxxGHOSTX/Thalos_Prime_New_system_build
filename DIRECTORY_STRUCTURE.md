# THALOS Prime - Complete Directory Structure

This document describes the complete directory structure of THALOS Prime and explains the purpose of each folder and key file.

## Root Directory Structure

```
ThalosApp/
├── 📁 Main Packages
│   ├── thalos_prime/              # Core AI system package
│   ├── thalos_sbi_standalone/     # Standalone SBI system
│   └── thalos_prime_advanced_gui/ # Advanced GUI components
│
├── 📁 Runtime Directories
│   ├── data/                      # Database files, training data
│   ├── logs/                      # Application logs
│   ├── cache/                     # Temporary cache files
│   ├── output/                    # Generated outputs
│   └── thalos_storage/            # Application storage
│
├── 📁 Organization Folders
│   ├── docs/                      # All documentation (47 files)
│   ├── scripts/                   # Utility scripts (21 files)
│   └── tests/                     # Test files
│
├── 🚀 Launcher Scripts
│   ├── LAUNCH.bat                 # Main launcher (Windows)
│   ├── LAUNCH_GUI.bat             # GUI launcher
│   ├── LAUNCH_ADVANCED_GUI.bat    # Advanced GUI launcher
│   └── SETUP_AND_RUN.bat          # Setup and run wizard
│
├── 🐍 Python Entry Points
│   ├── main.py                    # CLI interface
│   ├── app.py                     # Web server
│   ├── thalos_prime_gui.py        # GUI application
│   ├── thalos_prime_advanced_gui.py # Advanced GUI
│   ├── launch_thalos.py           # Launcher helper
│   ├── launch_advanced_gui.py     # GUI launcher helper
│   ├── LAUNCH.py                  # Generic launcher
│   └── setup_and_run.py           # Setup and run wizard
│
├── 🧪 Testing
│   ├── test_system.py             # Main system tests
│   └── test_system_v2.py          # Additional tests
│
├── ⚙️ Configuration
│   ├── requirements.txt           # Python dependencies
│   ├── pyproject.toml             # Project metadata
│   ├── setup.py                   # Package installation
│   ├── azure-pipelines.yml        # Azure CI/CD
│   └── .gitignore                 # Git ignore rules
│
└── 📄 Documentation
    ├── README.md                  # Main documentation
    ├── WINDOWS_DEPLOYMENT.md      # Windows deployment guide
    ├── DIRECTORY_STRUCTURE.md     # This file
    ├── REORGANIZATION_SUMMARY.md  # Changes documentation
    ├── SECURITY_SUMMARY.md        # Security review
    └── FINAL_USER_GUIDE.txt       # Quick start guide
```

## Package Details

### 1. thalos_prime/ - Core AI System

The main AI system package with the following modules:

```
thalos_prime/
├── __init__.py           # Package initialization
├── config/               # Configuration management
├── core/                 # Main orchestration engine
├── crypto/               # Encryption (AES-256, SHA-256)
├── database/             # Database operations
├── encoding/             # Text tokenization (BPE, character, word)
├── inference/            # Text generation
├── kernel/               # Memory management, virtual filesystem
├── math/                 # Tensor operations, linear algebra
│   ├── activations.py    # Activation functions
│   ├── attention.py      # Attention mechanisms
│   ├── distributions.py  # Statistical distributions
│   ├── linear_algebra.py # Matrix operations
│   └── tensor.py         # Tensor implementation
├── nn/                   # Neural network layers
│   ├── layer.py          # Layer implementations
│   ├── model.py          # Model definitions
│   └── transformer.py    # Transformer architecture
├── reasoning/            # Semantic Behavioral Integration
├── storage/              # Data persistence
├── utils/                # Utility functions
└── wetware/              # Bio-inspired computing
```

Each subdirectory contains:
- `__init__.py` - Makes it a Python package
- Module-specific Python files with implementations

### 2. thalos_sbi_standalone/ - Standalone SBI System

Independent Semantic Behavioral Integration system:

```
thalos_sbi_standalone/
├── __init__.py              # Package initialization
├── MODULE_INDEX.json        # Module registry
├── core_engine.py           # Main SBI engine
├── semantic_engine.py       # Semantic analysis
├── behavioral_engine.py     # Behavioral modeling
├── nlp_module.py            # Natural language processing
├── complete_nlp_module.py   # Extended NLP features
├── reasoning_engines.py     # Advanced reasoning
├── code_generator.py        # Code generation
├── run_generator.py         # Run configurations
├── knowledge_system.py      # Knowledge management
├── multiagent_system.py     # Multi-agent coordination
├── planning_module.py       # Planning and scheduling
├── learning_systems.py      # Machine learning integration
├── complete_math_module.py  # Mathematical operations
├── analytics_module.py      # Analytics and insights
├── api_layer.py             # API interface
├── web_interface.py         # Web-based interface
└── testing_suite.py         # Testing utilities
```

### 3. thalos_prime_advanced_gui/

Advanced GUI components package:

```
thalos_prime_advanced_gui/
└── __init__.py              # Package initialization
```

### 4. Runtime Directories

#### data/
- Database files (*.db, *.sqlite)
- Training data
- Model files
- Persistent storage
- **Gitignored** (except README.md)

#### logs/
- Application logs (*.log)
- Debug information
- Error traces
- **Gitignored** (except README.md)

#### cache/
- Temporary cache files
- Processed data
- Session data
- **Gitignored** (except README.md)

#### output/
- Generated output files
- Reports
- Results
- Exported data
- **Gitignored** (except README.md)

#### thalos_storage/
- Application-specific storage
- User data
- Configuration backups

### 5. Organization Folders

#### docs/
Contains all documentation (47 files):
- Architecture documents
- API documentation
- User guides
- Technical specifications
- Completion reports
- System status files

#### scripts/
Contains utility scripts (21 files):
- System builders
- Integration tools
- Database configuration
- Validators
- Helper scripts

#### tests/
Contains test files:
- Unit tests
- Integration tests
- GUI import tests

### 6. GitHub Workflows

```
.github/
└── workflows/
    ├── python-app.yml       # CI/CD pipeline for tests
    └── deploy-thalos.yml    # Deployment automation
```

## How to Use This Structure

### For End Users (Windows)

1. **Quick Start**:
   ```
   Double-click LAUNCH.bat
   ```

2. **Setup and Choose**:
   ```
   Double-click SETUP_AND_RUN.bat
   ```

3. **GUI Mode**:
   ```
   Double-click LAUNCH_GUI.bat
   ```

### For Developers

1. **Install as Package**:
   ```bash
   pip install -e .
   ```

2. **Run from Command Line**:
   ```bash
   python main.py --interactive
   python app.py
   python thalos_prime_gui.py
   ```

3. **Run Tests**:
   ```bash
   python test_system.py
   ```

4. **Setup and Run**:
   ```bash
   python setup_and_run.py
   ```

### For System Administrators

1. **Initialize System**:
   ```bash
   python setup_and_run.py
   ```
   This will:
   - Create all necessary directories
   - Verify the installation
   - Test module imports
   - Provide interactive menu

2. **Check Structure**:
   ```bash
   python -c "from pathlib import Path; import thalos_prime; print('OK')"
   ```

## Directory Creation

The following directories are created automatically when needed:
- `data/` - Created on first run or by setup_and_run.py
- `logs/` - Created on first run or by setup_and_run.py
- `cache/` - Created on first run or by setup_and_run.py
- `output/` - Created on first run or by setup_and_run.py

These directories are gitignored but their README.md files are tracked.

## Important Files

### Configuration Files
- `.gitignore` - Excludes runtime data, IDE files, temp files
- `requirements.txt` - Python package dependencies
- `pyproject.toml` - Project metadata and build configuration
- `setup.py` - Package installation script

### Entry Points
- `main.py` - Main CLI entry point with argument parsing
- `app.py` - Web application server
- `thalos_prime_gui.py` - GUI application
- `setup_and_run.py` - Complete system setup and runner

### Documentation
- `README.md` - Main project documentation
- `WINDOWS_DEPLOYMENT.md` - Windows deployment guide
- `DIRECTORY_STRUCTURE.md` - This file
- `FINAL_USER_GUIDE.txt` - Quick reference guide

## File Counts

- **Total Files**: ~140 files
- **Python Modules**: 
  - thalos_prime: 22 files
  - thalos_sbi_standalone: 17 files
  - Root level: 13 entry points and scripts
- **Documentation**: 47 files in docs/
- **Utility Scripts**: 21 files in scripts/
- **Test Files**: 4 files
- **Configuration**: 5 files

## Package Import Structure

```python
# Import core package
import thalos_prime
from thalos_prime.core import THALOSPrimeEngine

# Import SBI package
import thalos_sbi_standalone
from thalos_sbi_standalone import core_engine

# Import GUI package
import thalos_prime_advanced_gui
```

## Version Information

- **THALOS Prime**: Version 3.1.0
- **SBI Standalone**: Version 2.0.0
- **GUI**: Version 1.0.0

## Support

For issues or questions:
1. Check `WINDOWS_DEPLOYMENT.md` for setup help
2. Check `FINAL_USER_GUIDE.txt` for quick start
3. Run `python setup_and_run.py` to verify installation
4. Read documentation in `docs/` folder

---

**Last Updated**: February 2026  
**Maintained By**: THALOS Prime Systems
