"""
THALOS Prime - Core Engine Module
Main orchestrator for the THALOS Prime system.
"""

from typing import Optional, Dict, Any, List
import time


class THALOSPrimeEngine:
    """Main orchestrator for THALOS Prime system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False
        self.start_time = None
        self.session_id = None
        self.components: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
    
    def initialize(self) -> bool:
        """Initialize the THALOS Prime system."""
        try:
            self.start_time = time.time()
            self.session_id = f"session_{int(self.start_time)}"
            
            # Initialize components
            from ..reasoning import SemanticBehavioralIntegration
            from ..config import Settings
            
            self.components['sbi'] = SemanticBehavioralIntegration()
            self.components['settings'] = Settings()
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a user query and generate response."""
        if not self.initialized:
            self.initialize()
        
        start = time.time()
        
        # Use SBI for processing
        sbi = self.components.get('sbi')
        if sbi:
            result = sbi.process_input(query)
        else:
            result = {
                'response': f"Processed: {query}",
                'analysis': {'intent': 'unknown'},
                'confidence': 0.5
            }
        
        # Add timing info
        result['processing_time'] = time.time() - start
        result['session_id'] = self.session_id
        
        # Add to history
        self._history.append({
            'query': query,
            'result': result,
            'timestamp': time.time()
        })
        
        return result
    
    def interactive_session(self) -> None:
        """Run interactive command-line session."""
        print("=" * 60)
        print("THALOS Prime Interactive Session")
        print("Type 'quit' or 'exit' to end the session")
        print("=" * 60)
        
        self.initialize()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! Thank you for using THALOS Prime.")
                    break
                
                if user_input.lower() == 'status':
                    self._print_status()
                    continue
                
                if user_input.lower() == 'history':
                    self._print_history()
                    continue
                
                result = self.process_query(user_input)
                print(f"\nTHALOS: {result['response']}")
                
                if self.config.get('show_confidence', False):
                    print(f"[Confidence: {result['confidence']:.2f}]")
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    def _print_status(self) -> None:
        """Print system status."""
        uptime = time.time() - self.start_time if self.start_time else 0
        print(f"\n--- System Status ---")
        print(f"Session ID: {self.session_id}")
        print(f"Uptime: {uptime:.1f} seconds")
        print(f"Queries processed: {len(self._history)}")
        print(f"Components: {list(self.components.keys())}")
    
    def _print_history(self) -> None:
        """Print conversation history."""
        print(f"\n--- Conversation History ({len(self._history)} entries) ---")
        for i, entry in enumerate(self._history[-10:], 1):
            print(f"{i}. You: {entry['query'][:50]}...")
            print(f"   THALOS: {entry['result']['response'][:50]}...")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            'initialized': self.initialized,
            'session_id': self.session_id,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'queries_processed': len(self._history),
            'components': list(self.components.keys())
        }
    
    def save_state(self, path: str) -> bool:
        """Save system state to file."""
        import json
        try:
            state = {
                'session_id': self.session_id,
                'config': self.config,
                'history': self._history,
            }
            with open(path, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, path: str) -> bool:
        """Load system state from file."""
        import json
        import os
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    state = json.load(f)
                self.session_id = state.get('session_id')
                self.config.update(state.get('config', {}))
                self._history = state.get('history', [])
                return True
            return False
        except Exception as e:
            print(f"Error loading state: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the system gracefully."""
        print("Shutting down THALOS Prime...")
        self.initialized = False
        self.components.clear()


class QueryProcessor:
    """Process and transform queries."""
    
    def __init__(self):
        self.preprocessors: List[callable] = []
        self.postprocessors: List[callable] = []
    
    def add_preprocessor(self, fn: callable) -> None:
        """Add a query preprocessor."""
        self.preprocessors.append(fn)
    
    def add_postprocessor(self, fn: callable) -> None:
        """Add a response postprocessor."""
        self.postprocessors.append(fn)
    
    def preprocess(self, query: str) -> str:
        """Apply all preprocessors to query."""
        for fn in self.preprocessors:
            query = fn(query)
        return query
    
    def postprocess(self, response: str) -> str:
        """Apply all postprocessors to response."""
        for fn in self.postprocessors:
            response = fn(response)
        return response


class SystemMonitor:
    """Monitor system performance and health."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict[str, Any]] = []
    
    def record_metric(self, name: str, value: float) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        
        # Keep only recent values
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        values = self.metrics.get(name, [])
        if not values:
            return {'count': 0, 'min': 0, 'max': 0, 'avg': 0}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
    
    def add_alert(self, level: str, message: str) -> None:
        """Add an alert."""
        self.alerts.append({
            'level': level,
            'message': message,
            'timestamp': time.time()
        })
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return self.alerts[-limit:]


# Export classes
__all__ = [
    'THALOSPrimeEngine',
    'QueryProcessor',
    'SystemMonitor',
]
