#!/usr/bin/env python3
"""
THALOS Prime - Integrated System Module
Full system integration with all components.
"""

from typing import Dict, Any


class IntegratedSystem:
    """Fully integrated THALOS Prime system."""
    
    def __init__(self):
        self.components = {}
        self.ready = False
    
    def setup(self) -> bool:
        """Setup all integrated components."""
        try:
            from thalos_prime.core import THALOSPrimeEngine
            from thalos_prime.reasoning import SemanticBehavioralIntegration
            
            self.components['engine'] = THALOSPrimeEngine()
            self.components['engine'].initialize()
            self.components['sbi'] = SemanticBehavioralIntegration()
            
            self.ready = True
            return True
        except Exception as e:
            print(f"Setup error: {e}")
            return False
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run a query through the integrated system."""
        if not self.ready:
            self.setup()
        
        return self.components['engine'].process_query(query)


def main():
    system = IntegratedSystem()
    system.setup()
    print("Integrated System ready")


if __name__ == '__main__':
    main()
