#!/usr/bin/env python3
"""
Test GUI imports.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_gui_package_import():
    """Test that GUI package can be imported."""
    try:
        from thalos_prime_advanced_gui import Window, Button, TextInput
        assert Window is not None
        assert Button is not None
        assert TextInput is not None
        print("✓ GUI package import successful")
        return True
    except Exception as e:
        print(f"✗ GUI package import failed: {e}")
        return False


def test_gui_component_creation():
    """Test GUI component creation."""
    try:
        from thalos_prime_advanced_gui import Window, Button
        
        window = Window("Test Window")
        assert window.title == "Test Window"
        
        button = Button("Click Me")
        assert button.text == "Click Me"
        
        window.add_child(button)
        assert len(window.children) == 1
        
        print("✓ GUI component creation successful")
        return True
    except Exception as e:
        print(f"✗ GUI component creation failed: {e}")
        return False


if __name__ == '__main__':
    test_gui_package_import()
    test_gui_component_creation()
