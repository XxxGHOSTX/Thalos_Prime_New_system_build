"""
THALOS Prime - Reasoning Module
Semantic Behavioral Integration (SBI) for intelligent response generation.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import math
from collections import defaultdict


class SemanticAnalyzer:
    """Analyze semantic content of input text."""
    
    def __init__(self):
        self.intent_keywords = {
            'question': ['what', 'why', 'how', 'when', 'where', 'who', 'which', '?'],
            'command': ['do', 'make', 'create', 'generate', 'write', 'build', 'show'],
            'statement': ['is', 'are', 'was', 'were', 'has', 'have', 'had'],
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening'],
            'farewell': ['bye', 'goodbye', 'farewell', 'see you', 'later'],
            'thanks': ['thank', 'thanks', 'appreciate', 'grateful'],
            'help': ['help', 'assist', 'support', 'guide', 'explain'],
        }
        
        self.category_keywords = {
            'technical': ['code', 'programming', 'software', 'algorithm', 'function', 'class'],
            'science': ['physics', 'chemistry', 'biology', 'math', 'science', 'research'],
            'general': ['life', 'world', 'people', 'nature', 'society'],
            'creative': ['story', 'poem', 'creative', 'imagine', 'fiction', 'art'],
            'business': ['business', 'company', 'market', 'sales', 'profit', 'strategy'],
        }
        
        self.entities = {
            'person': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}(:\d{2})?\s*(am|pm|AM|PM)?\b',
            'email': r'\b[\w.-]+@[\w.-]+\.\w+\b',
            'url': r'https?://[\w.-]+(/[\w.-]*)*',
            'number': r'\b\d+(\.\d+)?\b',
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Perform semantic analysis on text."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Detect intent
        intent = self._detect_intent(text_lower, words)
        
        # Detect category
        category = self._detect_category(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Compute sentiment
        sentiment = self._compute_sentiment(text_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(words)
        
        return {
            'intent': intent,
            'category': category,
            'entities': entities,
            'sentiment': sentiment,
            'keywords': keywords,
            'word_count': len(words),
            'char_count': len(text),
        }
    
    def _detect_intent(self, text: str, words: List[str]) -> str:
        """Detect the intent of the input."""
        scores = defaultdict(int)
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[intent] += 1
        
        if not scores:
            return 'statement'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _detect_category(self, text: str) -> str:
        """Detect the category of the input."""
        scores = defaultdict(int)
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        if not scores:
            return 'general'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {}
        
        for entity_type, pattern in self.entities.items():
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    matches = [m[0] if m[0] else m for m in matches]
                entities[entity_type] = matches
        
        return entities
    
    def _compute_sentiment(self, text: str) -> Dict[str, float]:
        """Compute basic sentiment scores."""
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 
                         'love', 'like', 'happy', 'joy', 'positive', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 
                         'sad', 'angry', 'negative', 'worst', 'horrible']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        total = pos_count + neg_count
        if total == 0:
            return {'positive': 0.5, 'negative': 0.5, 'neutral': True}
        
        return {
            'positive': pos_count / total,
            'negative': neg_count / total,
            'neutral': False
        }
    
    def _extract_keywords(self, words: List[str]) -> List[str]:
        """Extract important keywords."""
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'must', 'can',
                    'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                    'as', 'into', 'through', 'during', 'before', 'after',
                    'above', 'below', 'between', 'under', 'again', 'further',
                    'then', 'once', 'here', 'there', 'when', 'where', 'why',
                    'how', 'all', 'each', 'few', 'more', 'most', 'other',
                    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                    'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if',
                    'or', 'because', 'until', 'while', 'it', 'its', 'i', 'me',
                    'my', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
                    'we', 'us', 'our', 'they', 'them', 'their', 'this', 'that'}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Count frequency
        freq = defaultdict(int)
        for word in keywords:
            freq[word] += 1
        
        # Return top keywords
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, _ in sorted_keywords[:10]]


class BehaviorEngine:
    """Generate context-aware behavioral responses."""
    
    def __init__(self):
        self.response_templates = {
            'question': [
                "Based on my understanding, {answer}",
                "The answer to your question is: {answer}",
                "Let me explain: {answer}",
            ],
            'command': [
                "I'll help you with that. {action}",
                "Here's what I've done: {action}",
                "Done! {action}",
            ],
            'greeting': [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Greetings! I'm ready to help.",
            ],
            'farewell': [
                "Goodbye! Have a great day!",
                "Take care! Feel free to return anytime.",
                "Farewell! It was nice chatting with you.",
            ],
            'thanks': [
                "You're welcome! Is there anything else I can help with?",
                "Happy to help! Let me know if you need more assistance.",
                "My pleasure! Feel free to ask more questions.",
            ],
            'help': [
                "I'm here to help! What would you like to know?",
                "I can assist with various topics. What do you need help with?",
                "Let me guide you. What specific help do you need?",
            ],
        }
        
        self.knowledge_base = {
            'machine learning': "Machine learning is a subset of AI that enables systems to learn from data.",
            'programming': "Programming is the process of creating instructions for computers to execute.",
            'python': "Python is a versatile programming language known for readability and simplicity.",
            'ai': "Artificial Intelligence refers to machines that can perform tasks requiring human intelligence.",
        }
    
    def generate_response(self, analysis: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """Generate a response based on semantic analysis."""
        intent = analysis.get('intent', 'statement')
        keywords = analysis.get('keywords', [])
        category = analysis.get('category', 'general')
        
        # Handle simple intents
        if intent in ['greeting', 'farewell', 'thanks']:
            import random
            return random.choice(self.response_templates.get(intent, ["I understand."]))
        
        # Check knowledge base
        for keyword in keywords:
            if keyword in self.knowledge_base:
                template = self.response_templates.get(intent, ["Here's information: {answer}"])[0]
                return template.format(answer=self.knowledge_base[keyword], action="Provided information.")
        
        # Default response based on intent
        if intent == 'question':
            return f"That's an interesting question about {category}. Let me provide some insights based on my training."
        elif intent == 'command':
            return f"I'll do my best to help you with that {category} task."
        else:
            return f"I understand you're discussing {category}. How can I assist further?"


class ContextManager:
    """Manage conversation context and history."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.user_profile: Dict[str, Any] = {}
    
    def add_interaction(self, user_input: str, response: str, 
                        analysis: Dict[str, Any]) -> None:
        """Add an interaction to history."""
        interaction = {
            'input': user_input,
            'response': response,
            'analysis': analysis,
            'timestamp': None,  # Would use time.time() in real implementation
        }
        
        self.history.append(interaction)
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Update context
        self._update_context(analysis)
    
    def _update_context(self, analysis: Dict[str, Any]) -> None:
        """Update current context based on analysis."""
        # Track topics discussed
        if 'topics' not in self.current_context:
            self.current_context['topics'] = []
        
        self.current_context['topics'].extend(analysis.get('keywords', []))
        self.current_context['topics'] = self.current_context['topics'][-20:]  # Keep recent topics
        
        # Track intents
        if 'intents' not in self.current_context:
            self.current_context['intents'] = []
        
        self.current_context['intents'].append(analysis.get('intent', 'unknown'))
        self.current_context['intents'] = self.current_context['intents'][-10:]
        
        # Update category focus
        self.current_context['current_category'] = analysis.get('category', 'general')
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context."""
        return {
            'history_length': len(self.history),
            'topics': list(set(self.current_context.get('topics', []))),
            'current_category': self.current_context.get('current_category', 'general'),
            'conversation_flow': self.current_context.get('intents', []),
        }
    
    def clear(self) -> None:
        """Clear conversation context."""
        self.history = []
        self.current_context = {}


class SemanticBehavioralIntegration:
    """
    Main SBI system integrating semantic analysis with behavioral generation.
    """
    
    def __init__(self):
        self.analyzer = SemanticAnalyzer()
        self.behavior_engine = BehaviorEngine()
        self.context_manager = ContextManager()
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and generate response."""
        # Semantic analysis
        analysis = self.analyzer.analyze(user_input)
        
        # Get context
        context = self.context_manager.get_context_summary()
        
        # Generate response
        response = self.behavior_engine.generate_response(analysis, context)
        
        # Update context
        self.context_manager.add_interaction(user_input, response, analysis)
        
        # Compute confidence
        confidence = self._compute_confidence(analysis)
        
        return {
            'response': response,
            'analysis': analysis,
            'context': context,
            'confidence': confidence,
        }
    
    def _compute_confidence(self, analysis: Dict[str, Any]) -> float:
        """Compute confidence score for the response."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear intents
        if analysis.get('intent') in ['greeting', 'farewell', 'thanks']:
            confidence += 0.3
        
        # Increase confidence for recognized keywords
        if analysis.get('keywords'):
            confidence += min(0.2, len(analysis['keywords']) * 0.02)
        
        # Increase confidence for detected entities
        if analysis.get('entities'):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.context_manager.history
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        self.context_manager.clear()


# Export main classes
__all__ = [
    'SemanticAnalyzer',
    'BehaviorEngine',
    'ContextManager',
    'SemanticBehavioralIntegration',
]
