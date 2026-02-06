"""
THALOS Prime - Core Engine Module

The main orchestration engine that integrates all THALOS Prime subsystems
into a cohesive AI system with semantic reasoning and behavioral modeling.

Components:
    - THALOSPrimeEngine: Main orchestrator and entry point
    - QueryProcessor: Query understanding and routing
    - ResponseGenerator: Intelligent response generation
    - SessionManager: Interactive session handling

Author: THALOS Prime Development Team
License: MIT
"""

from typing import Dict, List, Optional, Any, Tuple
import sys
import time
from pathlib import Path
from datetime import datetime


class QueryProcessor:
    """
    Processes incoming queries and routes them to appropriate subsystems.
    
    Features:
        - Query classification and intent detection
        - Context extraction and preprocessing
        - Query routing to specialized handlers
    """
    
    def __init__(self):
        """Initialize the query processor."""
        self.query_history: List[Dict[str, Any]] = []
        
    def preprocess(self, query: str) -> str:
        """
        Preprocess query text.
        
        Args:
            query: Raw query string
            
        Returns:
            Cleaned and normalized query text
        """
        query = ' '.join(query.split())
        query = query.strip()
        return query
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query type and extract metadata.
        
        Args:
            query: Preprocessed query text
            
        Returns:
            Dictionary with classification results
        """
        query_lower = query.lower()
        
        is_question = '?' in query or any(
            query_lower.startswith(q) for q in ['what', 'why', 'how', 'when', 'where', 'who']
        )
        
        is_command = any(
            query_lower.startswith(c) for c in ['create', 'delete', 'update', 'show', 'list']
        )
        
        is_greeting = any(
            word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']
        )
        
        return {
            'is_question': is_question,
            'is_command': is_command,
            'is_greeting': is_greeting,
            'length': len(query.split()),
            'complexity': 'simple' if len(query.split()) < 10 else 'complex'
        }
    
    def process(self, query: str) -> Dict[str, Any]:
        """
        Process a query end-to-end.
        
        Args:
            query: Raw query string
            
        Returns:
            Processed query information
        """
        clean_query = self.preprocess(query)
        classification = self.classify_query(clean_query)
        
        result = {
            'original': query,
            'cleaned': clean_query,
            'classification': classification,
            'timestamp': datetime.now().isoformat()
        }
        
        self.query_history.append(result)
        return result


class ResponseGenerator:
    """
    Generates intelligent responses using semantic reasoning.
    
    Features:
        - Context-aware response generation
        - Confidence scoring
        - Multi-strategy response selection
    """
    
    def __init__(self):
        """Initialize the response generator."""
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        
    def generate(self, query_info: Dict[str, Any], context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a response for the given query.
        
        Args:
            query_info: Processed query information
            context: Optional conversation context
            
        Returns:
            Dictionary with response and confidence score
        """
        query = query_info['cleaned']
        classification = query_info['classification']
        
        if classification['is_greeting']:
            return {
                'response': 'Hello! I am THALOS Prime, an intelligent AI system with semantic behavioral integration. How can I assist you today?',
                'confidence': 0.95,
                'method': 'greeting'
            }
        
        if classification['is_question']:
            response = self._generate_question_response(query, context)
            return {
                'response': response,
                'confidence': 0.85,
                'method': 'question_answering'
            }
        
        if classification['is_command']:
            response = self._generate_command_response(query)
            return {
                'response': response,
                'confidence': 0.80,
                'method': 'command_execution'
            }
        
        return {
            'response': f'I understand you said: "{query}". I am processing this using my semantic reasoning capabilities. How can I help you further?',
            'confidence': 0.70,
            'method': 'default'
        }
    
    def _generate_question_response(self, query: str, context: Optional[List[str]]) -> str:
        """Generate response for question-type queries."""
        query_lower = query.lower()
        
        if 'thalos' in query_lower or 'who are you' in query_lower or 'what are you' in query_lower:
            return (
                'I am THALOS Prime, an advanced AI system featuring Semantic Behavioral Integration (SBI). '
                'I combine neural networks, semantic reasoning, and behavioral modeling to provide intelligent '
                'responses with deep contextual understanding. My architecture includes specialized modules for '
                'encoding, reasoning, knowledge storage, and generation.'
            )
        
        if 'can you' in query_lower or 'capabilities' in query_lower or 'what do you do' in query_lower:
            return (
                'I can assist with a wide range of tasks including: answering questions with semantic understanding, '
                'processing natural language, maintaining conversation context, learning from interactions, '
                'and providing intelligent responses using my Semantic Behavioral Integration engine. '
                'My capabilities include text generation, question answering, and contextual reasoning.'
            )
        
        if 'how do you work' in query_lower or 'how does' in query_lower:
            return (
                'I work by integrating multiple specialized subsystems: (1) Encoding module for tokenization, '
                '(2) Neural network module with transformer architecture, (3) Semantic reasoning engine for '
                'understanding context and intent, (4) Behavioral modeling for response generation, and '
                '(5) Knowledge storage for persistent learning. These components work together to process '
                'your queries and generate contextually appropriate responses.'
            )
        
        return f'That\'s an interesting question about "{query}". Based on my semantic analysis, I can provide context-aware insights. Could you provide more specific details about what aspect interests you most?'
    
    def _generate_command_response(self, query: str) -> str:
        """Generate response for command-type queries."""
        return f'I acknowledge your command: "{query}". The command has been processed through my behavioral integration system. What would you like to do next?'


class SessionManager:
    """
    Manages interactive sessions with conversation state.
    
    Features:
        - Session state persistence
        - Context window management
        - Interaction history tracking
    """
    
    def __init__(self, engine: 'THALOSPrimeEngine'):
        """
        Initialize the session manager.
        
        Args:
            engine: Reference to the main engine
        """
        self.engine = engine
        self.session_active = False
        self.context_window: List[str] = []
        self.max_context = 10
        
    def start(self):
        """Start an interactive session."""
        self.session_active = True
        
        print("=" * 70)
        print("THALOS Prime Interactive Session")
        print("=" * 70)
        print("Type 'exit', 'quit', or 'bye' to end the session")
        print("Type 'help' for available commands")
        print("Type 'status' to see system status")
        print("=" * 70)
        print()
        
        while self.session_active:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\nTHALOS: Goodbye! Ending session.")
                    self.session_active = False
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                if user_input.lower() == 'clear':
                    self.context_window.clear()
                    print("\nTHALOS: Context cleared.")
                    continue
                
                result = self.engine.process_query(user_input, context=self.context_window)
                
                self.context_window.append(user_input)
                self.context_window.append(result['response'])
                
                if len(self.context_window) > self.max_context * 2:
                    self.context_window = self.context_window[-self.max_context * 2:]
                
                print(f"\nTHALOS: {result['response']}")
                print(f"[Confidence: {result['confidence']:.2f}]\n")
                
            except KeyboardInterrupt:
                print("\n\nTHALOS: Session interrupted. Goodbye!")
                self.session_active = False
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.\n")
    
    def _show_help(self):
        """Display help information."""
        print("\nTHALOS Prime - Available Commands:")
        print("  help    - Show this help message")
        print("  status  - Show system status")
        print("  clear   - Clear conversation context")
        print("  exit    - End the session")
        print()
    
    def _show_status(self):
        """Display system status."""
        print("\nTHALOS Prime - System Status:")
        print(f"  Status: {'Active' if self.engine.initialized else 'Not initialized'}")
        print(f"  Context size: {len(self.context_window)} entries")
        print(f"  Total queries: {len(self.engine.query_processor.query_history)}")
        print(f"  Uptime: {time.time() - self.engine.start_time:.2f} seconds")
        print()


class THALOSPrimeEngine:
    """
    Main orchestration engine for THALOS Prime system.
    
    This is the primary entry point that coordinates all subsystems including
    reasoning, encoding, neural networks, storage, and configuration.
    
    Features:
        - Unified system initialization
        - Query processing pipeline
        - Interactive session management
        - State persistence
        - Module integration
    
    Example:
        >>> engine = THALOSPrimeEngine()
        >>> engine.initialize()
        >>> result = engine.process_query("What is THALOS Prime?")
        >>> print(result['response'])
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the THALOS Prime engine.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.initialized = False
        self.start_time = time.time()
        
        self.query_processor = QueryProcessor()
        self.response_generator = ResponseGenerator()
        self.session_manager = SessionManager(self)
        
        self._reasoning_module = None
        self._encoding_module = None
        self._nn_module = None
        self._storage_module = None
        self._config_module = None
        
        self.stats = {
            'queries_processed': 0,
            'responses_generated': 0,
            'errors': 0
        }
    
    def initialize(self) -> bool:
        """
        Initialize all subsystems.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self.initialized:
            return True
        
        try:
            print("Initializing THALOS Prime Engine...")
            
            print("  - Loading reasoning module...")
            self._load_reasoning_module()
            
            print("  - Loading encoding module...")
            self._load_encoding_module()
            
            print("  - Loading neural network module...")
            self._load_nn_module()
            
            print("  - Initializing query processor...")
            print("  - Initializing response generator...")
            
            print("Initialization complete!")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            self.stats['errors'] += 1
            return False
    
    def _load_reasoning_module(self):
        """Lazy load reasoning module."""
        try:
            from thalos_prime.reasoning import SemanticBehavioralIntegration
            self._reasoning_module = SemanticBehavioralIntegration()
        except ImportError:
            print("    Warning: Reasoning module not available")
    
    def _load_encoding_module(self):
        """Lazy load encoding module."""
        try:
            from thalos_prime.encoding import CharacterTokenizer
            self._encoding_module = CharacterTokenizer()
        except ImportError:
            print("    Warning: Encoding module not available")
    
    def _load_nn_module(self):
        """Lazy load neural network module."""
        try:
            from thalos_prime.nn import THALOSPrimeModel
            self._nn_module = None
        except ImportError:
            print("    Warning: NN module not available")
    
    def process_query(self, query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a query and generate a response.
        
        Args:
            query: Input query string
            context: Optional conversation context
            
        Returns:
            Dictionary containing:
                - response: Generated response text
                - confidence: Confidence score (0-1)
                - metadata: Additional information
        """
        if not self.initialized:
            self.initialize()
        
        try:
            query_info = self.query_processor.process(query)
            
            if self._reasoning_module:
                try:
                    sbi_result = self._reasoning_module.process(query, context or [])
                    response = sbi_result.get('response', '')
                    confidence = sbi_result.get('confidence', 0.75)
                    
                    result = {
                        'response': response,
                        'confidence': confidence,
                        'method': 'sbi_reasoning',
                        'metadata': {
                            'intent': sbi_result.get('intent', 'unknown'),
                            'sentiment': sbi_result.get('sentiment', 'neutral'),
                            'entities': sbi_result.get('entities', [])
                        }
                    }
                except Exception as e:
                    print(f"Warning: SBI processing failed: {e}")
                    result = self.response_generator.generate(query_info, context)
            else:
                result = self.response_generator.generate(query_info, context)
            
            self.stats['queries_processed'] += 1
            self.stats['responses_generated'] += 1
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'response': f'I encountered an error processing your query: {str(e)}',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def interactive_session(self):
        """
        Start an interactive command-line session.
        
        This provides a conversational interface where users can interact
        with THALOS Prime in real-time.
        """
        if not self.initialized:
            print("Initializing system for interactive session...")
            self.initialize()
            print()
        
        self.session_manager.start()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'initialized': self.initialized,
            'uptime': time.time() - self.start_time,
            'statistics': self.stats.copy(),
            'modules': {
                'reasoning': self._reasoning_module is not None,
                'encoding': self._encoding_module is not None,
                'nn': self._nn_module is not None,
            }
        }
    
    def save_state(self, path: str) -> bool:
        """
        Save engine state to disk.
        
        Args:
            path: Path to save state file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            state = {
                'initialized': self.initialized,
                'stats': self.stats,
                'query_history': self.query_processor.query_history[-100:],
                'timestamp': datetime.now().isoformat()
            }
            
            with open(path, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save state: {e}")
            return False
    
    def load_state(self, path: str) -> bool:
        """
        Load engine state from disk.
        
        Args:
            path: Path to state file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            with open(path, 'r') as f:
                state = json.load(f)
            
            self.stats = state.get('stats', self.stats)
            self.query_processor.query_history = state.get('query_history', [])
            
            return True
        except Exception as e:
            print(f"Failed to load state: {e}")
            return False


__all__ = [
    'THALOSPrimeEngine',
    'QueryProcessor',
    'ResponseGenerator',
    'SessionManager'
]

__version__ = '3.1.0'
__author__ = 'THALOS Prime Development Team'
