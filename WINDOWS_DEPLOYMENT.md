# THALOS Prime - Windows Deployment Guide

## Overview

This guide explains how to deploy and use THALOS Prime as a standalone Windows application.

## Directory Structure

The application is organized for easy Windows deployment:

```
ThalosApp/
├── Launcher Scripts (Root Level)
│   ├── LAUNCH.bat              # Main launcher
│   ├── LAUNCH_GUI.bat          # GUI launcher
│   └── LAUNCH_ADVANCED_GUI.bat # Advanced GUI launcher
│
├── Application Entry Points
│   ├── main.py                 # CLI entry point
│   ├── app.py                  # Web server entry point
│   ├── thalos_prime_gui.py     # GUI entry point
│   └── thalos_prime_advanced_gui.py
│
├── Core System (thalos_prime/)
│   └── All core AI functionality modules
│
├── Additional Modules
│   ├── thalos_sbi_standalone/  # Standalone SBI system
│   └── thalos_prime_advanced_gui/
│
├── Supporting Files
│   ├── docs/                   # All documentation
│   ├── scripts/                # Utility scripts
│   ├── tests/                  # Test files
│   ├── data/                   # Runtime data (auto-created)
│   └── thalos_storage/         # Application storage
│
└── Configuration
    ├── requirements.txt        # Dependencies
    └── pyproject.toml         # Project metadata
```

## Installation Steps

### Step 1: Install Python

1. Download Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

### Step 2: Verify Python Installation

Open Command Prompt and run:
```cmd
python --version
```

You should see: `Python 3.11.x` or higher

### Step 3: Extract Application Files

1. Extract all files from the repository to your chosen location
   - Example: `C:\ThalosApp\` or `C:\Program Files\ThalosApp\`
2. Keep all files and folders in their current structure
3. **Do not** delete any folders or files - they are all required

### Step 4: Run the Application

Simply double-click one of the launcher scripts:
- **LAUNCH.bat** - Interactive CLI mode
- **LAUNCH_GUI.bat** - Basic GUI interface
- **LAUNCH_ADVANCED_GUI.bat** - Advanced GUI with more features

## File Organization Details

### Root Level Files
- **Essential launcher scripts** for quick access
- **Main Python entry points** (main.py, app.py, etc.)
- **Configuration files** (requirements.txt, pyproject.toml)
- **README.md** - Main documentation

### docs/ Folder
Contains all project documentation:
- Architecture documentation
- User guides
- Completion reports
- Technical specifications

### scripts/ Folder
Contains utility and helper scripts:
- System builders and validators
- Integration scripts
- Database configuration
- Internal tools

### thalos_prime/ Folder
Core AI system modules (DO NOT MODIFY):
- math/ - Mathematical operations
- nn/ - Neural networks
- reasoning/ - AI reasoning engine
- crypto/ - Security functions
- And more...

### thalos_sbi_standalone/ Folder
Standalone Semantic Behavioral Integration system

### data/ Folder
Auto-generated runtime data:
- Database files
- Training data
- Model files

### thalos_storage/ Folder
Application data storage

## Usage

### Interactive Mode
```cmd
LAUNCH.bat
```
or
```cmd
python main.py --interactive
```

### Query Mode
```cmd
python main.py --query "Your question here"
```

### GUI Mode
```cmd
LAUNCH_GUI.bat
```
or
```cmd
python thalos_prime_gui.py
```

### Running Tests
```cmd
python test_system.py
```

## Optional Dependencies

For enhanced features, install optional dependencies:
```cmd
python -m pip install -r requirements.txt
```

Note: Core functionality works without any additional dependencies!

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Or add Python to PATH manually

### "Module not found" errors
- Ensure you're running commands from the application root directory
- Verify all folders are intact (thalos_prime/, thalos_sbi_standalone/, etc.)

### Application won't start
- Check Python version: `python --version` (must be 3.11+)
- Try running from command line to see error messages:
  ```cmd
  python main.py --version
  ```

## Auto-Deployment

The repository includes GitHub Actions workflows for continuous integration:
- `.github/workflows/python-app.yml` - CI/CD pipeline
- `.github/workflows/deploy-thalos.yml` - Deployment automation

These automatically test and deploy the application when changes are pushed to the master branch.

## Security Notes

- Database files are stored in `data/` folder (excluded from git)
- Sensitive configuration should not be committed to the repository
- The `.gitignore` file prevents accidental commits of temporary files

## Support

For detailed documentation, see the `docs/` folder:
- `docs/QUICKSTART.md` - Quick start guide
- `docs/ARCHITECTURE.md` - System architecture
- `docs/QUICK_REFERENCE.md` - Command reference

## Version

Current Version: 3.1.0

---

© 2024 THALOS Prime Systems. All rights reserved.
