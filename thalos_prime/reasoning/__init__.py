"""
Semantic Behavioral Integration (SBI) reasoning module for THALOS Prime
"""
from typing import Dict, Any


class SemanticAnalyzer:
    """Analyzes semantic content of text"""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text semantically"""
        # Simple keyword-based analysis
        text_lower = text.lower()
        
        # Detect intent
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            intent = 'question'
        elif any(word in text_lower for word in ['do', 'can you', 'please', 'help']):
            intent = 'request'
        else:
            intent = 'statement'
        
        # Detect category
        if any(word in text_lower for word in ['learn', 'machine', 'ai', 'model', 'training']):
            category = 'machine_learning'
        elif any(word in text_lower for word in ['data', 'analyze', 'statistics']):
            category = 'data_science'
        elif any(word in text_lower for word in ['code', 'program', 'software']):
            category = 'programming'
        else:
            category = 'general'
        
        # Extract entities (simple noun detection)
        words = text.split()
        entities = [w for w in words if len(w) > 3 and w[0].isupper()]
        
        return {
            'intent': intent,
            'category': category,
            'entities': entities,
            'word_count': len(words),
            'sentiment': 'neutral'
        }


class BehaviorEngine:
    """Manages behavioral responses"""
    
    def __init__(self):
        self.context = []
    
    def generate_response(self, analysis: Dict[str, Any]) -> str:
        """Generate response based on analysis"""
        intent = analysis.get('intent', 'statement')
        category = analysis.get('category', 'general')
        
        if intent == 'question':
            if category == 'machine_learning':
                return "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
            elif category == 'data_science':
                return "Data science involves extracting insights from structured and unstructured data."
            else:
                return "I understand your question. Let me help you with that."
        elif intent == 'request':
            return "I'll do my best to help you with your request."
        else:
            return "I acknowledge your statement."


class ContextManager:
    """Manages conversation context"""
    
    def __init__(self):
        self.history = []
        self.max_history = 10
    
    def add_interaction(self, user_input: str, response: str):
        """Add interaction to history"""
        self.history.append({
            'user': user_input,
            'response': response
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self):
        """Get current context"""
        return self.history


class SemanticBehavioralIntegration:
    """Main SBI system integrating semantic analysis and behavioral response"""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.behavior_engine = BehaviorEngine()
        self.context_manager = ContextManager()
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and generate response"""
        # Semantic analysis
        analysis = self.semantic_analyzer.analyze(user_input)
        
        # Generate response
        response = self.behavior_engine.generate_response(analysis)
        
        # Update context
        self.context_manager.add_interaction(user_input, response)
        
        # Calculate confidence (simple heuristic)
        confidence = 0.8 if analysis['intent'] in ['question', 'request'] else 0.6
        
        return {
            'analysis': analysis,
            'response': response,
            'confidence': confidence,
            'context': self.context_manager.get_context()
        }


__all__ = [
    'SemanticAnalyzer', 'BehaviorEngine', 'ContextManager',
    'SemanticBehavioralIntegration'
]
