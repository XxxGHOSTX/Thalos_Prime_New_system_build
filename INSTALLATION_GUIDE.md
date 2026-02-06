# THALOS Prime - Installation and Setup Guide

Complete guide for installing and setting up THALOS Prime on your system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Install](#quick-install)
3. [Detailed Installation](#detailed-installation)
4. [Verification](#verification)
5. [Running the System](#running-the-system)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Python 3.11 or higher** (Python 3.12 also supported)
- **Windows 7 or higher** (Windows 10/11 recommended)
- **50 MB free disk space** (plus space for data/logs)

### Optional
- Git (for cloning the repository)
- Virtual environment tool (venv, conda)

---

## Quick Install

### Option 1: For Windows Users (Easiest)

1. **Download the repository**
   - Download and extract all files to a folder (e.g., `C:\ThalosApp`)

2. **Install Python**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, **CHECK "Add Python to PATH"**
   - Click "Install Now"

3. **Run Setup**
   - Double-click `SETUP_AND_RUN.bat`
   - Follow the on-screen prompts

That's it! The system will be ready to use.

### Option 2: Command Line (For Developers)

```bash
# Clone or download repository
cd C:\ThalosApp

# Run setup
python setup_and_run.py
```

---

## Detailed Installation

### Step 1: Install Python

1. **Download Python**
   - Visit [python.org/downloads](https://www.python.org/downloads/)
   - Download Python 3.11 or 3.12

2. **Run Installer**
   - Check "Add Python to PATH" ✓
   - Check "Install pip" ✓
   - Click "Install Now"

3. **Verify Installation**
   ```bash
   python --version
   # Should show: Python 3.11.x or Python 3.12.x
   ```

### Step 2: Get THALOS Prime

#### Option A: Download ZIP
1. Download the repository as ZIP
2. Extract to your chosen location (e.g., `C:\ThalosApp`)

#### Option B: Clone with Git
```bash
git clone https://github.com/XxxGHOSTX/Thalos_Prime_New_system_build.git
cd Thalos_Prime_New_system_build
```

### Step 3: Setup the System

#### Automatic Setup (Recommended)
```bash
python setup_and_run.py
```

This will:
- ✓ Create necessary directories (data, logs, cache, output)
- ✓ Verify all packages are present
- ✓ Check entry points
- ✓ Test module imports
- ✓ Provide interactive menu to run the system

#### Manual Setup
If you prefer manual setup:

1. **Create Runtime Directories**
   ```bash
   mkdir data logs cache output
   ```

2. **Install Dependencies (Optional)**
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: Core functionality works without additional dependencies!

3. **Verify Structure**
   ```bash
   python -c "import thalos_prime; print('OK')"
   ```

### Step 4: (Optional) Install as Package

To install THALOS Prime as a Python package:

```bash
# Install in development mode
pip install -e .

# Or install normally
pip install .
```

After installation, you can use:
```bash
thalos --version
thalos --interactive
thalos-gui
thalos-test
```

---

## Verification

### Verify Installation

Run the setup script to verify everything:
```bash
python setup_and_run.py
```

You should see:
- ✓ Directory Structure: OK
- ✓ Entry Points: OK
- ✓ Module Imports: OK
- ✓ System is ready to run!

### Run System Tests

```bash
python test_system.py
```

Expected output:
```
======================================================================
THALOS Prime System Test Suite
======================================================================

[1/6] Testing Math Module...
✓ Math module working correctly

[2/6] Testing Encoding Module...
✓ Encoding module working correctly

... (all tests should pass)

======================================================================
All Tests Passed! ✓
======================================================================
```

### Check Version

```bash
python main.py --version
```

Expected output:
```
============================================================
THALOS Prime v3.1.0
============================================================
Intelligent AI System with Semantic Behavioral Integration
...
```

---

## Running the System

### Windows Users (Easiest)

Simply double-click one of these launcher files:
- `LAUNCH.bat` - Interactive CLI mode
- `LAUNCH_GUI.bat` - GUI interface
- `LAUNCH_ADVANCED_GUI.bat` - Advanced GUI
- `SETUP_AND_RUN.bat` - Setup wizard and menu

### Command Line

#### Interactive Mode
```bash
python main.py --interactive
```

#### Single Query
```bash
python main.py --query "What is machine learning?"
```

#### GUI Mode
```bash
python thalos_prime_gui.py
```

#### Advanced GUI
```bash
python thalos_prime_advanced_gui.py
```

#### Web Server
```bash
python app.py
```

#### Run Tests
```bash
python test_system.py
```

### Using the Setup Wizard

The interactive setup wizard provides a menu:
```bash
python setup_and_run.py
```

Menu options:
1. Run Interactive CLI
2. Run GUI
3. Run Advanced GUI
4. Run System Tests
5. Show Version Info
6. Run Query (custom)
7. Start Web Server

---

## Troubleshooting

### "Python is not recognized"

**Problem**: Command prompt doesn't recognize Python.

**Solution**:
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Or add Python manually to PATH

### "Module not found" Error

**Problem**: Python can't find THALOS modules.

**Solution**:
1. Make sure you're in the correct directory
2. Run `python setup_and_run.py` to verify structure
3. Check that all folders exist (thalos_prime/, thalos_sbi_standalone/)

### Missing Directories

**Problem**: data/, logs/, cache/, or output/ folders missing.

**Solution**:
Run the setup script:
```bash
python setup_and_run.py
```

Or create manually:
```bash
mkdir data logs cache output
```

### Import Errors

**Problem**: Getting import errors when running scripts.

**Solution**:
1. Verify Python version: `python --version` (must be 3.11+)
2. Verify packages exist:
   ```bash
   python -c "import thalos_prime; print('OK')"
   ```
3. Run setup to check structure:
   ```bash
   python setup_and_run.py
   ```

### Permission Errors

**Problem**: Can't create files or directories.

**Solution**:
1. Run as Administrator (Windows)
2. Or extract to a location where you have write permissions (e.g., Documents)

### Tests Failing

**Problem**: System tests fail.

**Solution**:
1. Check Python version (must be 3.11+)
2. Verify all files are present
3. Run setup: `python setup_and_run.py`
4. Check for error messages in the test output

---

## Directory Structure After Installation

```
ThalosApp/
├── thalos_prime/              # Core AI system
├── thalos_sbi_standalone/     # SBI system
├── thalos_prime_advanced_gui/ # GUI components
├── data/                      # Runtime data (created)
├── logs/                      # Application logs (created)
├── cache/                     # Cache files (created)
├── output/                    # Output files (created)
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── tests/                     # Test files
├── LAUNCH.bat                 # Launchers
├── main.py                    # Entry points
└── README.md                  # Documentation
```

---

## Next Steps

After installation:

1. **Read Documentation**
   - `README.md` - Overview and features
   - `WINDOWS_DEPLOYMENT.md` - Windows deployment details
   - `DIRECTORY_STRUCTURE.md` - Complete directory reference
   - `FINAL_USER_GUIDE.txt` - Quick reference

2. **Try the System**
   - Run interactive mode: `python main.py --interactive`
   - Run GUI: `LAUNCH_GUI.bat` or `python thalos_prime_gui.py`
   - Run tests: `python test_system.py`

3. **Explore Examples**
   - Check `docs/` folder for detailed documentation
   - Look at test files for usage examples

---

## Getting Help

If you encounter issues:

1. Run the verification:
   ```bash
   python setup_and_run.py
   ```

2. Check the troubleshooting section above

3. Review the documentation in `docs/` folder

4. Run system tests to identify problems:
   ```bash
   python test_system.py
   ```

---

## Uninstallation

To remove THALOS Prime:

1. Delete the application folder
2. If installed as package:
   ```bash
   pip uninstall thalos-prime
   ```

---

**Version**: 3.1.0  
**Last Updated**: February 2026  
**Author**: THALOS Prime Systems

For more information, see `README.md` and `WINDOWS_DEPLOYMENT.md`.
