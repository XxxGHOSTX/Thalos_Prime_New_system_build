#!/usr/bin/env python3
"""
THALOS Prime - Advanced GUI Application
Advanced graphical interface with extended features.
"""

from typing import Optional, Dict, Any, List
import sys


class AdvancedGUI:
    """Advanced GUI with extended features."""
    
    def __init__(self):
        self.engine = None
        self.config = {
            'theme': 'dark',
            'font_size': 12,
            'show_metrics': True
        }
        self.history: List[Dict] = []
        self.bookmarks: List[Dict] = []
    
    def initialize(self) -> bool:
        """Initialize the GUI."""
        try:
            from thalos_prime.core import THALOSPrimeEngine
            self.engine = THALOSPrimeEngine()
            self.engine.initialize()
            return True
        except Exception as e:
            print(f"Error initializing: {e}")
            return False
    
    def run(self):
        """Run the advanced GUI."""
        print("=" * 60)
        print("THALOS Prime Advanced Interface")
        print("=" * 60)
        print()
        print("Commands:")
        print("  /help     - Show help")
        print("  /settings - Show settings")
        print("  /history  - Show history")
        print("  /clear    - Clear history")
        print("  /quit     - Exit")
        print()
        
        if not self.initialize():
            print("Failed to initialize. Exiting.")
            return
        
        while True:
            try:
                user_input = input("\n[THALOS] >>> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    self.handle_command(user_input[1:])
                    continue
                
                result = self.engine.process_query(user_input)
                
                print(f"\n[Response]")
                print(f"{result['response']}")
                
                if self.config['show_metrics']:
                    print(f"\n[Metrics] Confidence: {result['confidence']:.2f}")
                
                self.history.append({
                    'input': user_input,
                    'response': result['response'],
                    'confidence': result['confidence']
                })
                
            except KeyboardInterrupt:
                print("\n\nExiting THALOS Prime. Goodbye!")
                break
    
    def handle_command(self, command: str):
        """Handle a command."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == 'help':
            self.show_help()
        elif cmd == 'settings':
            self.show_settings()
        elif cmd == 'history':
            self.show_history()
        elif cmd == 'clear':
            self.clear_history()
        elif cmd == 'quit' or cmd == 'exit':
            print("Goodbye!")
            sys.exit(0)
        elif cmd == 'set':
            self.set_setting(args)
        elif cmd == 'bookmark':
            self.add_bookmark()
        else:
            print(f"Unknown command: {cmd}")
    
    def show_help(self):
        """Show help information."""
        print("\nTHALOS Prime Advanced Interface - Help")
        print("-" * 40)
        print("/help          - Show this help")
        print("/settings      - Show current settings")
        print("/set <k> <v>   - Set a setting")
        print("/history       - Show conversation history")
        print("/clear         - Clear history")
        print("/bookmark      - Bookmark last response")
        print("/quit          - Exit the application")
    
    def show_settings(self):
        """Show current settings."""
        print("\nCurrent Settings:")
        print("-" * 40)
        for key, value in self.config.items():
            print(f"  {key}: {value}")
    
    def set_setting(self, args: List[str]):
        """Set a configuration value."""
        if len(args) < 2:
            print("Usage: /set <key> <value>")
            return
        
        key, value = args[0], ' '.join(args[1:])
        
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        
        self.config[key] = value
        print(f"Set {key} = {value}")
    
    def show_history(self):
        """Show conversation history."""
        print(f"\nConversation History ({len(self.history)} entries):")
        print("-" * 40)
        
        for i, entry in enumerate(self.history[-10:], 1):
            print(f"\n{i}. You: {entry['input'][:50]}...")
            print(f"   THALOS: {entry['response'][:50]}...")
    
    def clear_history(self):
        """Clear conversation history."""
        self.history.clear()
        print("History cleared.")
    
    def add_bookmark(self):
        """Bookmark the last response."""
        if not self.history:
            print("No history to bookmark.")
            return
        
        self.bookmarks.append(self.history[-1])
        print("Last response bookmarked.")


def main():
    """Main entry point."""
    gui = AdvancedGUI()
    gui.run()


if __name__ == '__main__':
    main()
