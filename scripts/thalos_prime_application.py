#!/usr/bin/env python3
"""
THALOS Prime - Application Module
Main application orchestration.
"""

from typing import Dict, Any, Optional


class THALOSApplication:
    """Main THALOS Prime application."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.engine = None
        self.running = False
    
    def start(self) -> bool:
        """Start the application."""
        try:
            from thalos_prime.core import THALOSPrimeEngine
            self.engine = THALOSPrimeEngine(self.config)
            self.engine.initialize()
            self.running = True
            return True
        except Exception as e:
            print(f"Start error: {e}")
            return False
    
    def stop(self):
        """Stop the application."""
        if self.engine:
            self.engine.shutdown()
        self.running = False
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process a query."""
        if not self.running:
            self.start()
        return self.engine.process_query(query)


def main():
    """Main entry point."""
    app = THALOSApplication()
    app.start()
    
    print("THALOS Application running. Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break
            result = app.process(user_input)
            print(f"Response: {result['response']}")
        except KeyboardInterrupt:
            break
    
    app.stop()
    print("Application stopped.")


if __name__ == '__main__':
    main()
