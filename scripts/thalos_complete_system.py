#!/usr/bin/env python3
"""
THALOS Prime - Complete System Module
Integrates all THALOS Prime subsystems.
"""

from typing import Dict, Any, Optional, List


class CompleteSystem:
    """Complete integrated THALOS Prime system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.subsystems: Dict[str, Any] = {}
        self.initialized = False
    
    def initialize_all(self) -> bool:
        """Initialize all subsystems."""
        try:
            # Core engine
            from thalos_prime.core import THALOSPrimeEngine
            self.subsystems['core'] = THALOSPrimeEngine()
            self.subsystems['core'].initialize()
            
            # Reasoning
            from thalos_prime.reasoning import SemanticBehavioralIntegration
            self.subsystems['reasoning'] = SemanticBehavioralIntegration()
            
            # Storage
            from thalos_prime.storage import ModelManager, KnowledgeBase
            self.subsystems['model_manager'] = ModelManager()
            self.subsystems['knowledge'] = KnowledgeBase()
            
            # Config
            from thalos_prime.config import Settings
            self.subsystems['settings'] = Settings()
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the complete system."""
        if not self.initialized:
            self.initialize_all()
        
        query = input_data.get('query', '')
        
        # Process through core
        result = self.subsystems['core'].process_query(query)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all subsystems."""
        return {
            'initialized': self.initialized,
            'subsystems': list(self.subsystems.keys()),
            'core_status': self.subsystems.get('core', {}).get_status() if 'core' in self.subsystems else None
        }
    
    def shutdown(self):
        """Shutdown all subsystems."""
        if 'core' in self.subsystems:
            self.subsystems['core'].shutdown()
        self.initialized = False


def main():
    """Main entry point."""
    system = CompleteSystem()
    system.initialize_all()
    
    print("THALOS Complete System initialized")
    print("Status:", system.get_status())
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() in ['quit', 'exit']:
                break
            
            result = system.process({'query': query})
            print(f"Response: {result.get('response', 'No response')}")
        except KeyboardInterrupt:
            break
    
    system.shutdown()


if __name__ == '__main__':
    main()
