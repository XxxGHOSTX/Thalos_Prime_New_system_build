#!/usr/bin/env python3
"""
THALOS Prime - GUI Application
Graphical user interface for THALOS Prime.
"""

from typing import Optional, Dict, Any
import sys


class THALOSPrimeGUI:
    """Main GUI application class."""
    
    def __init__(self):
        self.engine = None
        self.window = None
        self.history = []
        self.config = {}
    
    def initialize(self):
        """Initialize the GUI and engine."""
        try:
            from thalos_prime.core import THALOSPrimeEngine
            self.engine = THALOSPrimeEngine()
            self.engine.initialize()
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def run_console_ui(self):
        """Run console-based UI when no GUI is available."""
        print("=" * 60)
        print("THALOS Prime Console UI")
        print("=" * 60)
        print("GUI dependencies not available. Running in console mode.")
        print()
        
        if not self.initialize():
            print("Failed to initialize engine")
            return
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                result = self.engine.process_query(user_input)
                print(f"\nTHALOS: {result['response']}")
                
                self.history.append({
                    'input': user_input,
                    'output': result['response']
                })
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
    
    def run(self):
        """Run the GUI application."""
        # Try to use tkinter if available
        try:
            import tkinter as tk
            from tkinter import ttk, scrolledtext
            
            self.run_tkinter_ui()
        except ImportError:
            # Fall back to console UI
            self.run_console_ui()
    
    def run_tkinter_ui(self):
        """Run tkinter-based GUI."""
        import tkinter as tk
        from tkinter import ttk, scrolledtext
        
        if not self.initialize():
            print("Failed to initialize engine")
            return
        
        # Create main window
        self.window = tk.Tk()
        self.window.title("THALOS Prime")
        self.window.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, height=25, width=80,
            state='disabled'
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, pady=5, sticky="nsew")
        
        # Input field
        self.input_field = ttk.Entry(main_frame, width=70)
        self.input_field.grid(row=1, column=0, pady=5, sticky="ew")
        self.input_field.bind('<Return>', self.send_message)
        
        # Send button
        send_btn = ttk.Button(main_frame, text="Send", command=self.send_message)
        send_btn.grid(row=1, column=1, pady=5, padx=5)
        
        # Welcome message
        self.display_message("THALOS", "Welcome to THALOS Prime! How can I help you today?")
        
        # Run main loop
        self.window.mainloop()
    
    def display_message(self, sender: str, message: str):
        """Display a message in the chat."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send a message and get response."""
        user_input = self.input_field.get().strip()
        
        if not user_input:
            return
        
        # Display user message
        self.display_message("You", user_input)
        self.input_field.delete(0, tk.END)
        
        # Get response
        result = self.engine.process_query(user_input)
        self.display_message("THALOS", result['response'])
        
        # Save to history
        self.history.append({
            'input': user_input,
            'output': result['response']
        })


def main():
    """Main entry point."""
    gui = THALOSPrimeGUI()
    gui.run()


if __name__ == '__main__':
    main()
