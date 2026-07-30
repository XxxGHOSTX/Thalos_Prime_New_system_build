"""
THALOS Prime - Semantic & Behavioral Integration (SBI) Module

This module provides advanced semantic analysis, behavioral modeling,
and context-aware reasoning capabilities for the THALOS Prime system.

Components:
    - SemanticAnalyzer: Natural language understanding and intent detection
    - BehaviorEngine: Context-aware response generation
    - ContextManager: Conversation state and history tracking
    - SemanticBehavioralIntegration: Main SBI orchestration system

Author: THALOS Prime Development Team
License: MIT
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import re
import math
from collections import defaultdict, deque
from datetime import datetime


# ============================================================================
# SEMANTIC ANALYZER - Natural Language Understanding
# ============================================================================

class SemanticAnalyzer:
    """
    Analyzes text input to extract semantic meaning, intent, and entities.
    
    Features:
        - Intent detection using pattern matching and keyword analysis
        - Entity extraction (names, dates, numbers, locations)
        - Sentiment analysis
        - Topic categorization
        - Question type classification
    """
    
    # Intent patterns and keywords
    INTENT_PATTERNS = {
        'question': {
            'patterns': [
                r'\bwhat\s+(is|are|was|were|does|do|did)',
                r'\bwhy\s+(is|are|was|were|does|do|did)',
                r'\bhow\s+(is|are|was|were|does|do|did|can|could|to)',
                r'\bwhen\s+(is|are|was|were|does|do|did)',
                r'\bwhere\s+(is|are|was|were|does|do|did)',
                r'\bwho\s+(is|are|was|were|does|do|did)',
                r'\bwhich\s+(is|are|was|were)',
                r'\bcan\s+you',
                r'\bcould\s+you',
                r'\bwould\s+you',
                r'\?$'
            ],
            'keywords': ['what', 'why', 'how', 'when', 'where', 'who', 'which', 'can', 'could', 'would']
        },
        'definition': {
            'patterns': [
                r'\bwhat\s+is\s+(?:a|an|the)\s+',
                r'\bdefine\s+',
                r'\bdefinition\s+of\s+',
                r'\bexplain\s+(?:what|the)\s+',
                r'\bmean(?:ing)?\s+of\s+'
            ],
            'keywords': ['define', 'definition', 'meaning', 'explain', 'what is']
        },
        'instruction': {
            'patterns': [
                r'\bhow\s+to\s+',
                r'\bhow\s+do\s+(?:i|you|we)\s+',
                r'\bshow\s+me\s+',
                r'\btell\s+me\s+how\s+',
                r'\bstep(?:s)?\s+to\s+'
            ],
            'keywords': ['how to', 'show me', 'tell me', 'steps', 'guide']
        },
        'comparison': {
            'patterns': [
                r'\bdifference\s+between\s+',
                r'\bcompare\s+',
                r'\bversus\s+',
                r'\bvs\s+',
                r'\brather\s+than\s+',
                r'\binstead\s+of\s+'
            ],
            'keywords': ['difference', 'compare', 'versus', 'vs', 'rather than', 'instead']
        },
        'greeting': {
            'patterns': [
                r'^hello\b',
                r'^hi\b',
                r'^hey\b',
                r'^greetings\b',
                r'^good\s+(?:morning|afternoon|evening)\b'
            ],
            'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning']
        },
        'farewell': {
            'patterns': [
                r'\bgoodbye\b',
                r'\bbye\b',
                r'\bsee\s+you\b',
                r'\btake\s+care\b',
                r'\bthanks?\b'
            ],
            'keywords': ['goodbye', 'bye', 'see you', 'take care', 'thanks']
        }
    }
    
    # Topic categories with associated keywords
    TOPIC_CATEGORIES = {
        'machine_learning': [
            'machine learning', 'ml', 'neural network', 'deep learning', 'ai',
            'artificial intelligence', 'training', 'model', 'algorithm', 'supervised',
            'unsupervised', 'reinforcement', 'classification', 'regression', 'clustering',
            'gradient', 'backpropagation', 'optimizer', 'loss function', 'accuracy',
            'overfitting', 'underfitting', 'dataset', 'feature', 'label', 'prediction'
        ],
        'programming': [
            'code', 'coding', 'programming', 'software', 'developer', 'function',
            'variable', 'class', 'object', 'method', 'python', 'java', 'javascript',
            'compiler', 'interpreter', 'debug', 'algorithm', 'data structure', 'array',
            'list', 'dictionary', 'loop', 'recursion', 'api', 'library', 'framework'
        ],
        'mathematics': [
            'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'statistics',
            'probability', 'equation', 'theorem', 'proof', 'derivative', 'integral',
            'matrix', 'vector', 'linear', 'exponential', 'logarithm', 'prime',
            'factorial', 'polynomial', 'trigonometry', 'sine', 'cosine', 'tangent'
        ],
        'science': [
            'science', 'physics', 'chemistry', 'biology', 'astronomy', 'experiment',
            'theory', 'hypothesis', 'observation', 'atom', 'molecule', 'energy',
            'force', 'gravity', 'electron', 'proton', 'neutron', 'cell', 'dna',
            'evolution', 'ecosystem', 'quantum', 'relativity', 'universe', 'planet'
        ],
        'technology': [
            'technology', 'computer', 'internet', 'network', 'server', 'database',
            'cloud', 'security', 'encryption', 'hardware', 'software', 'processor',
            'memory', 'storage', 'bandwidth', 'protocol', 'ip', 'tcp', 'http',
            'web', 'mobile', 'app', 'device', 'sensor', 'iot', 'blockchain'
        ],
        'general': [
            'general', 'information', 'knowledge', 'question', 'answer', 'help',
            'explain', 'understand', 'learn', 'teach', 'know', 'tell', 'show'
        ]
    }
    
    def __init__(self):
        """Initialize the semantic analyzer with compiled regex patterns."""
        self.compiled_patterns = {}
        for intent, data in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in data['patterns']
            ]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis on input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
                - intent: Detected intent type
                - category: Topic category
                - entities: Extracted entities
                - sentiment: Sentiment score (-1 to 1)
                - complexity: Text complexity score
                - keywords: Important keywords
                - question_type: Type of question (if applicable)
        """
        text_lower = text.lower().strip()
        
        # Detect intent
        intent, intent_confidence = self._detect_intent(text_lower)
        
        # Categorize topic
        category, category_confidence = self._categorize_topic(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text_lower)
        
        # Calculate complexity
        complexity = self._calculate_complexity(text)
        
        # Extract keywords
        keywords = self._extract_keywords(text_lower)
        
        # Detect question type
        question_type = self._detect_question_type(text_lower) if intent == 'question' else None
        
        return {
            'intent': intent,
            'intent_confidence': intent_confidence,
            'category': category,
            'category_confidence': category_confidence,
            'entities': entities,
            'sentiment': sentiment,
            'complexity': complexity,
            'keywords': keywords,
            'question_type': question_type,
            'length': len(text.split()),
            'has_question_mark': '?' in text
        }
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect the primary intent of the input text."""
        scores = defaultdict(float)
        
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    scores[intent] += 1.0
            
            # Check keywords
            keywords = self.INTENT_PATTERNS[intent]['keywords']
            for keyword in keywords:
                if keyword in text:
                    scores[intent] += 0.5
        
        if scores:
            best_intent = max(scores, key=scores.get)
            max_score = scores[best_intent]
            confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
            return best_intent, confidence
        
        return 'statement', 0.5
    
    def _categorize_topic(self, text: str) -> Tuple[str, float]:
        """Categorize the topic of the input text."""
        scores = defaultdict(float)
        
        # Tokenize text
        tokens = set(text.split())
        
        for category, keywords in self.TOPIC_CATEGORIES.items():
            for keyword in keywords:
                if ' ' in keyword:
                    if keyword in text:
                        scores[category] += 2.0
                else:
                    if keyword in tokens:
                        scores[category] += 1.0
        
        if scores:
            best_category = max(scores, key=scores.get)
            max_score = scores[best_category]
            total_score = sum(scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.5
            return best_category, confidence
        
        return 'general', 0.5
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {
            'numbers': [],
            'dates': [],
            'capitalized': [],
            'acronyms': []
        }
        
        # Extract numbers
        number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        entities['numbers'] = number_pattern.findall(text)
        
        # Extract dates (simple patterns)
        date_pattern = re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b')
        entities['dates'] = date_pattern.findall(text)
        
        # Extract capitalized words (potential proper nouns)
        cap_pattern = re.compile(r'\b[A-Z][a-z]+\b')
        entities['capitalized'] = cap_pattern.findall(text)
        
        # Extract acronyms
        acronym_pattern = re.compile(r'\b[A-Z]{2,}\b')
        entities['acronyms'] = acronym_pattern.findall(text)
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text.
        
        Returns:
            Score from -1 (negative) to 1 (positive)
        """
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'best', 'awesome', 'perfect', 'happy', 'joy',
            'beautiful', 'brilliant', 'superb', 'outstanding', 'impressive'
        }
        
        negative_words = {
            'bad', 'terrible', 'horrible', 'awful', 'worst', 'hate', 'dislike',
            'poor', 'sad', 'angry', 'upset', 'disappointed', 'frustrating',
            'annoying', 'useless', 'broken', 'fail', 'failure', 'wrong', 'error'
        }
        
        words = set(text.split())
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _calculate_complexity(self, text: str) -> float:
        """
        Calculate text complexity based on various metrics.
        
        Returns:
            Complexity score from 0 (simple) to 1 (complex)
        """
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence count (approximate)
        sentence_count = text.count('.') + text.count('!') + text.count('?') + 1
        
        # Words per sentence
        words_per_sentence = len(words) / sentence_count
        
        # Long word ratio (words > 7 characters)
        long_words = sum(1 for word in words if len(word) > 7)
        long_word_ratio = long_words / len(words)
        
        # Combine metrics
        complexity = (
            (avg_word_length - 4) / 6 * 0.3 +  # Normalize avg word length
            min(words_per_sentence / 20, 1.0) * 0.4 +  # Normalize words/sentence
            long_word_ratio * 0.3
        )
        
        return max(0.0, min(complexity, 1.0))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        freq = defaultdict(int)
        for word in keywords:
            freq[word] += 1
        
        # Return top keywords
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:10]]
    
    def _detect_question_type(self, text: str) -> Optional[str]:
        """Detect the type of question being asked."""
        question_types = {
            'what': r'\bwhat\b',
            'why': r'\bwhy\b',
            'how': r'\bhow\b',
            'when': r'\bwhen\b',
            'where': r'\bwhere\b',
            'who': r'\bwho\b',
            'which': r'\bwhich\b',
            'yes_no': r'\b(can|could|would|will|should|is|are|do|does|did)\b'
        }
        
        for q_type, pattern in question_types.items():
            if re.search(pattern, text):
                return q_type
        
        return 'unknown'


# ============================================================================
# BEHAVIOR ENGINE - Context-Aware Response Generation
# ============================================================================

class BehaviorEngine:
    """
    Generates context-aware behavioral responses based on semantic analysis.
    
    Features:
        - Response strategy selection
        - Tone and style adaptation
        - Context-aware behavior modeling
        - Response confidence estimation
    """
    
    def __init__(self):
        """Initialize the behavior engine."""
        self.response_strategies = {
            'question': self._question_strategy,
            'definition': self._definition_strategy,
            'instruction': self._instruction_strategy,
            'comparison': self._comparison_strategy,
            'greeting': self._greeting_strategy,
            'farewell': self._farewell_strategy,
            'statement': self._statement_strategy
        }
        
        self.category_behaviors = {
            'machine_learning': {
                'tone': 'technical',
                'detail_level': 'high',
                'examples': True
            },
            'programming': {
                'tone': 'practical',
                'detail_level': 'high',
                'examples': True
            },
            'mathematics': {
                'tone': 'formal',
                'detail_level': 'high',
                'examples': True
            },
            'science': {
                'tone': 'explanatory',
                'detail_level': 'medium',
                'examples': True
            },
            'technology': {
                'tone': 'informative',
                'detail_level': 'medium',
                'examples': True
            },
            'general': {
                'tone': 'conversational',
                'detail_level': 'medium',
                'examples': False
            }
        }
    
    def generate_behavior(
        self,
        semantic_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate behavioral response based on semantic analysis and context.
        
        Args:
            semantic_analysis: Results from semantic analyzer
            context: Optional conversation context
            
        Returns:
            Dictionary containing:
                - strategy: Selected response strategy
                - tone: Recommended tone
                - detail_level: Recommended detail level
                - confidence: Confidence in behavior selection
                - metadata: Additional behavioral metadata
        """
        intent = semantic_analysis['intent']
        category = semantic_analysis['category']
        
        # Select response strategy
        strategy = self.response_strategies.get(intent, self._statement_strategy)
        strategy_result = strategy(semantic_analysis)
        
        # Get category-specific behavior
        category_behavior = self.category_behaviors.get(
            category,
            self.category_behaviors['general']
        )
        
        # Adjust based on context
        if context:
            category_behavior = self._adjust_for_context(category_behavior, context)
        
        # Calculate overall confidence
        confidence = (
            semantic_analysis['intent_confidence'] * 0.5 +
            semantic_analysis['category_confidence'] * 0.3 +
            strategy_result.get('confidence', 0.5) * 0.2
        )
        
        return {
            'strategy': intent,
            'tone': category_behavior['tone'],
            'detail_level': category_behavior['detail_level'],
            'include_examples': category_behavior['examples'],
            'confidence': confidence,
            'metadata': {
                'question_type': semantic_analysis.get('question_type'),
                'complexity': semantic_analysis['complexity'],
                'sentiment': semantic_analysis['sentiment']
            }
        }
    
    def _question_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling questions."""
        return {
            'approach': 'answer_directly',
            'structure': 'definition_then_details',
            'confidence': 0.8
        }
    
    def _definition_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling definition requests."""
        return {
            'approach': 'provide_definition',
            'structure': 'definition_examples_context',
            'confidence': 0.9
        }
    
    def _instruction_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling instruction requests."""
        return {
            'approach': 'step_by_step',
            'structure': 'overview_steps_details',
            'confidence': 0.85
        }
    
    def _comparison_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling comparison requests."""
        return {
            'approach': 'compare_contrast',
            'structure': 'similarities_differences_conclusion',
            'confidence': 0.75
        }
    
    def _greeting_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling greetings."""
        return {
            'approach': 'acknowledge_offer_help',
            'structure': 'greeting_availability',
            'confidence': 0.95
        }
    
    def _farewell_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling farewells."""
        return {
            'approach': 'acknowledge_close',
            'structure': 'farewell_invitation',
            'confidence': 0.95
        }
    
    def _statement_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for handling general statements."""
        return {
            'approach': 'acknowledge_expand',
            'structure': 'acknowledgment_information',
            'confidence': 0.6
        }
    
    def _adjust_for_context(
        self,
        behavior: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust behavior based on conversation context."""
        adjusted = behavior.copy()
        
        # Adjust detail level based on previous interactions
        if context.get('previous_complexity', 0) > 0.7:
            adjusted['detail_level'] = 'high'
        elif context.get('previous_complexity', 0) < 0.3:
            adjusted['detail_level'] = 'low'
        
        # Adjust tone based on sentiment history
        if context.get('sentiment_history'):
            avg_sentiment = sum(context['sentiment_history']) / len(context['sentiment_history'])
            if avg_sentiment < -0.3:
                adjusted['tone'] = 'supportive'
            elif avg_sentiment > 0.3:
                adjusted['tone'] = 'enthusiastic'
        
        return adjusted


# ============================================================================
# CONTEXT MANAGER - Conversation State Tracking
# ============================================================================

class ContextManager:
    """
    Manages conversation context and history.
    
    Features:
        - Conversation history tracking
        - Context state management
        - Topic continuity detection
        - User preference learning
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the context manager.
        
        Args:
            max_history: Maximum number of interactions to keep in history
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.current_topic = None
        self.topic_continuity_count = 0
        self.user_preferences = {
            'preferred_detail_level': 'medium',
            'preferred_tone': 'conversational',
            'topics_of_interest': []
        }
        self.session_start = datetime.now()
        self.interaction_count = 0
    
    def add_interaction(
        self,
        user_input: str,
        semantic_analysis: Dict[str, Any],
        behavior: Dict[str, Any],
        response: Optional[str] = None
    ) -> None:
        """
        Add an interaction to the conversation history.
        
        Args:
            user_input: User's input text
            semantic_analysis: Semantic analysis results
            behavior: Behavioral response information
            response: System's response (if available)
        """
        interaction = {
            'timestamp': datetime.now(),
            'input': user_input,
            'analysis': semantic_analysis,
            'behavior': behavior,
            'response': response
        }
        
        self.history.append(interaction)
        self.interaction_count += 1
        
        # Update topic tracking
        current_category = semantic_analysis['category']
        if current_category == self.current_topic:
            self.topic_continuity_count += 1
        else:
            self.current_topic = current_category
            self.topic_continuity_count = 1
        
        # Update user preferences
        self._update_preferences(semantic_analysis, behavior)
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context.
        
        Returns:
            Dictionary containing:
                - current_topic: Current topic being discussed
                - topic_continuity: Number of consecutive interactions on same topic
                - recent_intents: List of recent intents
                - recent_categories: List of recent categories
                - sentiment_history: Recent sentiment scores
                - complexity_history: Recent complexity scores
                - interaction_count: Total number of interactions
                - session_duration: Time since session start
        """
        if not self.history:
            return {
                'current_topic': None,
                'topic_continuity': 0,
                'recent_intents': [],
                'recent_categories': [],
                'sentiment_history': [],
                'complexity_history': [],
                'interaction_count': 0,
                'session_duration': 0.0
            }
        
        # Get recent history (last 5 interactions)
        recent = list(self.history)[-5:]
        
        return {
            'current_topic': self.current_topic,
            'topic_continuity': self.topic_continuity_count,
            'recent_intents': [i['analysis']['intent'] for i in recent],
            'recent_categories': [i['analysis']['category'] for i in recent],
            'sentiment_history': [i['analysis']['sentiment'] for i in recent],
            'complexity_history': [i['analysis']['complexity'] for i in recent],
            'interaction_count': self.interaction_count,
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'previous_complexity': recent[-1]['analysis']['complexity'] if recent else 0.5
        }
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            n: Number of recent interactions to retrieve (None for all)
            
        Returns:
            List of interaction dictionaries
        """
        if n is None:
            return list(self.history)
        return list(self.history)[-n:]
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history.clear()
        self.current_topic = None
        self.topic_continuity_count = 0
        self.interaction_count = 0
        self.session_start = datetime.now()
    
    def _update_preferences(
        self,
        semantic_analysis: Dict[str, Any],
        behavior: Dict[str, Any]
    ) -> None:
        """Update user preferences based on interactions."""
        # Track topics of interest
        category = semantic_analysis['category']
        if category not in self.user_preferences['topics_of_interest']:
            self.user_preferences['topics_of_interest'].append(category)
        
        # Update preferred detail level (based on complexity)
        complexity = semantic_analysis['complexity']
        if complexity > 0.7:
            self.user_preferences['preferred_detail_level'] = 'high'
        elif complexity < 0.3:
            self.user_preferences['preferred_detail_level'] = 'low'
    
    def get_topic_statistics(self) -> Dict[str, int]:
        """Get statistics about discussed topics."""
        topic_counts = defaultdict(int)
        for interaction in self.history:
            category = interaction['analysis']['category']
            topic_counts[category] += 1
        return dict(topic_counts)
    
    def get_intent_statistics(self) -> Dict[str, int]:
        """Get statistics about user intents."""
        intent_counts = defaultdict(int)
        for interaction in self.history:
            intent = interaction['analysis']['intent']
            intent_counts[intent] += 1
        return dict(intent_counts)


# ============================================================================
# SEMANTIC BEHAVIORAL INTEGRATION (SBI) - Main System
# ============================================================================

class SemanticBehavioralIntegration:
    """
    Main SBI system that orchestrates semantic analysis, behavioral modeling,
    and context management for intelligent, context-aware interactions.
    
    This is the primary interface for the THALOS Prime reasoning module.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the SBI system.
        
        Args:
            max_history: Maximum number of interactions to keep in history
        """
        self.semantic_analyzer = SemanticAnalyzer()
        self.behavior_engine = BehaviorEngine()
        self.context_manager = ContextManager(max_history=max_history)
        self.version = "1.0.0"
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Process user input through the complete SBI pipeline.
        
        This is the main entry point for the SBI system. It performs:
        1. Semantic analysis of the input
        2. Context retrieval from conversation history
        3. Behavioral response generation
        4. Context update with new interaction
        
        Args:
            text: User input text to process
            
        Returns:
            Dictionary containing:
                - analysis: Semantic analysis results (intent, category, etc.)
                - behavior: Behavioral response information
                - context: Current conversation context
                - confidence: Overall system confidence
                - metadata: Additional processing information
        """
        if not text or not text.strip():
            return {
                'analysis': {
                    'intent': 'unknown',
                    'category': 'general'
                },
                'confidence': 0.0,
                'error': 'Empty input'
            }
        
        # Step 1: Perform semantic analysis
        semantic_analysis = self.semantic_analyzer.analyze(text)
        
        # Step 2: Get current context
        context = self.context_manager.get_context()
        
        # Step 3: Generate behavioral response
        behavior = self.behavior_engine.generate_behavior(
            semantic_analysis,
            context
        )
        
        # Step 4: Update context with new interaction
        self.context_manager.add_interaction(
            text,
            semantic_analysis,
            behavior
        )
        
        # Step 5: Compile results
        result = {
            'analysis': {
                'intent': semantic_analysis['intent'],
                'category': semantic_analysis['category'],
                'entities': semantic_analysis['entities'],
                'keywords': semantic_analysis['keywords'],
                'sentiment': semantic_analysis['sentiment'],
                'complexity': semantic_analysis['complexity'],
                'question_type': semantic_analysis.get('question_type')
            },
            'behavior': {
                'strategy': behavior['strategy'],
                'tone': behavior['tone'],
                'detail_level': behavior['detail_level'],
                'include_examples': behavior['include_examples']
            },
            'context': {
                'current_topic': context['current_topic'],
                'topic_continuity': context['topic_continuity'],
                'interaction_count': context['interaction_count']
            },
            'confidence': behavior['confidence'],
            'metadata': {
                'processing_timestamp': datetime.now().isoformat(),
                'sbi_version': self.version,
                'input_length': len(text.split())
            }
        }
        
        return result
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context.
        
        Returns:
            Dictionary containing context information
        """
        return self.context_manager.get_context()
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            n: Number of recent interactions to retrieve (None for all)
            
        Returns:
            List of interaction dictionaries
        """
        return self.context_manager.get_history(n)
    
    def clear_context(self) -> None:
        """Clear conversation context and history."""
        self.context_manager.clear_history()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the conversation session.
        
        Returns:
            Dictionary containing:
                - topic_statistics: Topic distribution
                - intent_statistics: Intent distribution
                - interaction_count: Total interactions
                - session_duration: Session duration in seconds
        """
        context = self.context_manager.get_context()
        
        return {
            'topic_statistics': self.context_manager.get_topic_statistics(),
            'intent_statistics': self.context_manager.get_intent_statistics(),
            'interaction_count': context['interaction_count'],
            'session_duration': context['session_duration']
        }
    
    def analyze_sentiment_trend(self) -> Dict[str, Any]:
        """
        Analyze sentiment trends across the conversation.
        
        Returns:
            Dictionary containing sentiment trend analysis
        """
        context = self.context_manager.get_context()
        sentiment_history = context['sentiment_history']
        
        if not sentiment_history:
            return {
                'average': 0.0,
                'trend': 'neutral',
                'volatility': 0.0
            }
        
        avg_sentiment = sum(sentiment_history) / len(sentiment_history)
        
        # Calculate trend
        if len(sentiment_history) >= 2:
            recent_avg = sum(sentiment_history[-3:]) / len(sentiment_history[-3:])
            if recent_avg > avg_sentiment + 0.1:
                trend = 'improving'
            elif recent_avg < avg_sentiment - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'neutral'
        
        # Calculate volatility (standard deviation)
        if len(sentiment_history) >= 2:
            variance = sum((s - avg_sentiment) ** 2 for s in sentiment_history) / len(sentiment_history)
            volatility = math.sqrt(variance)
        else:
            volatility = 0.0
        
        return {
            'average': avg_sentiment,
            'trend': trend,
            'volatility': volatility,
            'sample_size': len(sentiment_history)
        }
    
    def process(self, text: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process input text and generate response (alias for process_input).
        
        This method provides compatibility with the core engine.
        
        Args:
            text: Input text to process
            context: Optional conversation context (for compatibility)
            
        Returns:
            Dictionary with 'response', 'confidence', and other metadata
        """
        result = self.process_input(text)
        
        # Generate response text based on analysis
        intent = result['analysis']['intent']
        category = result['analysis']['category']
        
        # Build response
        if intent == 'greeting':
            response = "Hello! I'm THALOS Prime. How can I assist you today?"
        elif intent == 'question':
            response = f"I understand you're asking about {category}. Based on my semantic analysis, I can provide detailed information on this topic."
        elif intent == 'farewell':
            response = "Goodbye! Feel free to return if you need assistance."
        else:
            response = f"I've analyzed your {intent} regarding {category}. Let me provide you with a thoughtful response."
        
        # Return in expected format
        return {
            'response': response,
            'confidence': result['confidence'],
            'intent': intent,
            'sentiment': result['analysis']['sentiment'],
            'entities': result['analysis']['entities']
        }
    
    def __repr__(self) -> str:
        """String representation of the SBI system."""
        context = self.context_manager.get_context()
        return (
            f"SemanticBehavioralIntegration(version={self.version}, "
            f"interactions={context['interaction_count']}, "
            f"current_topic={context['current_topic']})"
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SemanticAnalyzer',
    'BehaviorEngine',
    'ContextManager',
    'SemanticBehavioralIntegration'
]
