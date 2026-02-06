"""
THALOS SBI Standalone - Core Engine
Main orchestration and engine for SBI processing.
"""

from typing import Dict, Any, Optional, List
import time


class SBICoreEngine:
    """Core engine for SBI standalone system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.initialized = False
        self.start_time = None
        self.processors: List = []
        self.stats = {'queries': 0, 'errors': 0}
    
    def initialize(self) -> bool:
        """Initialize the core engine."""
        try:
            self.start_time = time.time()
            self.initialized = True
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the SBI pipeline."""
        if not self.initialized:
            self.initialize()
        
        self.stats['queries'] += 1
        start = time.time()
        
        result = {
            'status': 'success',
            'input': input_data,
            'output': {},
            'processing_time': 0.0
        }
        
        try:
            # Process through all registered processors
            data = input_data
            for processor in self.processors:
                data = processor.process(data)
            
            result['output'] = data
            result['processing_time'] = time.time() - start
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.stats['errors'] += 1
        
        return result
    
    def add_processor(self, processor) -> None:
        """Add a processor to the pipeline."""
        self.processors.append(processor)
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            'initialized': self.initialized,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'processors': len(self.processors),
            'stats': self.stats
        }
    
    def shutdown(self) -> None:
        """Shutdown the engine."""
        self.initialized = False
        self.processors.clear()


class ProcessorBase:
    """Base class for SBI processors."""
    
    def __init__(self, name: str = 'processor'):
        self.name = name
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data - override in subclass."""
        return data


class SemanticProcessor(ProcessorBase):
    """Semantic analysis processor."""
    
    def __init__(self):
        super().__init__('semantic')
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        text = data.get('text', '')
        data['semantic'] = {
            'word_count': len(text.split()),
            'char_count': len(text),
            'has_question': '?' in text
        }
        return data


class BehavioralProcessor(ProcessorBase):
    """Behavioral modeling processor."""
    
    def __init__(self):
        super().__init__('behavioral')
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data['behavioral'] = {
            'confidence': 0.8,
            'category': 'general'
        }
        return data


class IntegrationProcessor(ProcessorBase):
    """Integration processor combining semantic and behavioral."""
    
    def __init__(self):
        super().__init__('integration')
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        semantic = data.get('semantic', {})
        behavioral = data.get('behavioral', {})
        
        data['integrated'] = {
            'combined_confidence': behavioral.get('confidence', 0.5),
            'analysis_complete': True
        }
        return data


# Export classes
__all__ = [
    'SBICoreEngine',
    'ProcessorBase',
    'SemanticProcessor',
    'BehavioralProcessor',
    'IntegrationProcessor'
]
