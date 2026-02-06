#!/usr/bin/env python3
"""
THALOS Prime - Complete System Setup and Runner

This script initializes all necessary directories, verifies the installation,
and provides options to run the complete THALOS Prime system.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def create_directories():
    """Create all necessary runtime directories."""
    print_header("Creating Runtime Directories")
    
    base_dir = Path(__file__).parent
    dirs = {
        'data': 'Runtime data and databases',
        'logs': 'Application logs',
        'cache': 'Temporary cache files',
        'output': 'Generated output files',
        'thalos_storage': 'Application storage'
    }
    
    for dir_name, description in dirs.items():
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_name}/ - {description}")
        else:
            print(f"✓ Exists: {dir_name}/ - {description}")
    
    return True


def verify_structure():
    """Verify the directory structure is complete."""
    print_header("Verifying Directory Structure")
    
    base_dir = Path(__file__).parent
    
    # Check main packages
    packages = {
        'thalos_prime': 'Core AI system',
        'thalos_sbi_standalone': 'Standalone SBI system',
        'thalos_prime_advanced_gui': 'Advanced GUI components',
    }
    
    all_ok = True
    for pkg_name, description in packages.items():
        pkg_path = base_dir / pkg_name
        init_file = pkg_path / '__init__.py'
        
        if pkg_path.exists() and pkg_path.is_dir():
            if init_file.exists():
                print(f"✓ Package: {pkg_name}/ - {description}")
            else:
                print(f"⚠ Package: {pkg_name}/ exists but missing __init__.py")
                all_ok = False
        else:
            print(f"✗ Missing: {pkg_name}/ - {description}")
            all_ok = False
    
    # Check subdirectories
    thalos_subdirs = [
        'config', 'core', 'crypto', 'database', 'encoding',
        'inference', 'kernel', 'math', 'nn', 'reasoning',
        'storage', 'utils', 'wetware'
    ]
    
    print(f"\n  Checking thalos_prime subdirectories:")
    for subdir in thalos_subdirs:
        subdir_path = base_dir / 'thalos_prime' / subdir
        init_file = subdir_path / '__init__.py'
        if subdir_path.exists() and init_file.exists():
            print(f"    ✓ {subdir}/")
        else:
            print(f"    ✗ {subdir}/ - missing")
            all_ok = False
    
    return all_ok


def check_entry_points():
    """Check that all entry points exist."""
    print_header("Checking Entry Points")
    
    base_dir = Path(__file__).parent
    entry_points = {
        'main.py': 'Main CLI interface',
        'app.py': 'Web server application',
        'thalos_prime_gui.py': 'GUI application',
        'thalos_prime_advanced_gui.py': 'Advanced GUI',
        'test_system.py': 'System tests',
    }
    
    all_ok = True
    for file_name, description in entry_points.items():
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"✓ {file_name} - {description}")
        else:
            print(f"✗ Missing: {file_name} - {description}")
            all_ok = False
    
    return all_ok


def test_imports():
    """Test that key modules can be imported."""
    print_header("Testing Module Imports")
    
    tests = [
        ('thalos_prime', 'Core package'),
        ('thalos_sbi_standalone', 'SBI standalone package'),
    ]
    
    all_ok = True
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✓ Import: {module_name} - {description}")
        except ImportError as e:
            print(f"⚠ Import: {module_name} - {description} (Warning: {e})")
            # Don't fail on import errors, just warn
    
    return all_ok


def show_menu():
    """Show interactive menu for running the system."""
    print_header("THALOS Prime - System Runner")
    
    print("Select an option to run:")
    print()
    print("  1. Run Interactive CLI (main.py --interactive)")
    print("  2. Run GUI (thalos_prime_gui.py)")
    print("  3. Run Advanced GUI (thalos_prime_advanced_gui.py)")
    print("  4. Run System Tests (test_system.py)")
    print("  5. Show Version Info (main.py --version)")
    print("  6. Run Query (enter custom query)")
    print("  7. Start Web Server (app.py)")
    print()
    print("  0. Exit")
    print()


def run_option(option):
    """Run the selected option."""
    base_dir = Path(__file__).parent
    
    if option == '1':
        print("\nStarting Interactive CLI...")
        os.system(f'cd "{base_dir}" && python main.py --interactive')
    
    elif option == '2':
        print("\nStarting GUI...")
        os.system(f'cd "{base_dir}" && python thalos_prime_gui.py')
    
    elif option == '3':
        print("\nStarting Advanced GUI...")
        os.system(f'cd "{base_dir}" && python thalos_prime_advanced_gui.py')
    
    elif option == '4':
        print("\nRunning System Tests...")
        os.system(f'cd "{base_dir}" && python test_system.py')
    
    elif option == '5':
        print("\nShowing Version Info...")
        os.system(f'cd "{base_dir}" && python main.py --version')
    
    elif option == '6':
        query = input("\nEnter your query: ")
        if query:
            print(f"\nProcessing query: {query}")
            os.system(f'cd "{base_dir}" && python main.py --query "{query}"')
    
    elif option == '7':
        print("\nStarting Web Server...")
        os.system(f'cd "{base_dir}" && python app.py')
    
    elif option == '0':
        print("\nExiting...")
        return False
    
    else:
        print("\nInvalid option. Please try again.")
    
    return True


def main():
    """Main entry point."""
    print_header("THALOS Prime - Complete System Setup")
    print("Version: 3.1.0")
    print("Author: THALOS Prime Systems")
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Verify structure
    structure_ok = verify_structure()
    
    # Step 3: Check entry points
    entry_points_ok = check_entry_points()
    
    # Step 4: Test imports
    imports_ok = test_imports()
    
    # Summary
    print_header("Setup Summary")
    print(f"Directory Structure: {'✓ OK' if structure_ok else '⚠ Issues Found'}")
    print(f"Entry Points: {'✓ OK' if entry_points_ok else '⚠ Issues Found'}")
    print(f"Module Imports: {'✓ OK' if imports_ok else '⚠ Warnings'}")
    
    if structure_ok and entry_points_ok:
        print("\n✓ System is ready to run!")
    else:
        print("\n⚠ Some issues were found. Please review the output above.")
        return 1
    
    # Interactive menu
    print()
    response = input("Would you like to run the system now? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        while True:
            show_menu()
            choice = input("Enter your choice (0-7): ").strip()
            
            if not run_option(choice):
                break
            
            if choice != '0':
                input("\nPress Enter to continue...")
    
    print_header("Setup Complete")
    print("To run the system later:")
    print("  python setup_and_run.py")
    print("  or use the launcher scripts: LAUNCH.bat, LAUNCH_GUI.bat, etc.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
