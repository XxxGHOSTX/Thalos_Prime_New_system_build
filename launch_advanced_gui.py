#!/usr/bin/env python3
"""
THALOS Prime - Advanced GUI Launcher
Launches the advanced GUI interface.
"""

import sys


def main():
    """Launch advanced GUI."""
    from thalos_prime_advanced_gui import AdvancedGUI
    
    gui = AdvancedGUI()
    gui.run()


if __name__ == '__main__':
    main()
