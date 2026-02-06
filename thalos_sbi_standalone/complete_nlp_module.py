"""
THALOS SBI Standalone - Complete NLP Module
Natural Language Processing utilities.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter


class TextPreprocessor:
    """Text preprocessing utilities."""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words."""
        return text.lower().split()
    
    @staticmethod
    def sentence_split(text: str) -> List[str]:
        """Split text into sentences."""
        return re.split(r'(?<=[.!?])\s+', text)
    
    @staticmethod
    def remove_stopwords(tokens: List[str], stopwords: Optional[List[str]] = None) -> List[str]:
        """Remove stopwords from tokens."""
        if stopwords is None:
            stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 
                        'been', 'being', 'have', 'has', 'had', 'do', 'does', 
                        'did', 'will', 'would', 'could', 'should', 'may', 
                        'might', 'must', 'can', 'to', 'of', 'in', 'for', 'on', 
                        'with', 'at', 'by', 'from', 'as', 'into', 'through', 
                        'and', 'or', 'but', 'if', 'it', 'its', 'this', 'that'}
        return [t for t in tokens if t.lower() not in stopwords]
    
    @staticmethod
    def stem(word: str) -> str:
        """Simple Porter-like stemming."""
        if word.endswith('ing'):
            return word[:-3]
        if word.endswith('ed'):
            return word[:-2]
        if word.endswith('ly'):
            return word[:-2]
        if word.endswith('ness'):
            return word[:-4]
        if word.endswith('ment'):
            return word[:-4]
        return word


class POSTagger:
    """Part-of-speech tagging."""
    
    def __init__(self):
        self.tag_patterns = {
            r'.*ing$': 'VBG',  # Gerund
            r'.*ed$': 'VBD',   # Past tense
            r'.*ly$': 'RB',    # Adverb
            r'.*ness$': 'NN',  # Noun
            r'.*tion$': 'NN',  # Noun
            r'.*ment$': 'NN',  # Noun
            r'^[A-Z].*': 'NNP', # Proper noun
            r'^\d+$': 'CD',    # Number
        }
        
        self.word_tags = {
            'the': 'DT', 'a': 'DT', 'an': 'DT',
            'is': 'VBZ', 'are': 'VBP', 'was': 'VBD', 'were': 'VBD',
            'and': 'CC', 'or': 'CC', 'but': 'CC',
            'in': 'IN', 'on': 'IN', 'at': 'IN', 'to': 'TO',
            'he': 'PRP', 'she': 'PRP', 'it': 'PRP', 'they': 'PRP',
            'i': 'PRP', 'you': 'PRP', 'we': 'PRP',
        }
    
    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Tag tokens with POS."""
        tagged = []
        for token in tokens:
            tag = self._get_tag(token)
            tagged.append((token, tag))
        return tagged
    
    def _get_tag(self, word: str) -> str:
        """Get tag for a word."""
        lower = word.lower()
        
        if lower in self.word_tags:
            return self.word_tags[lower]
        
        for pattern, tag in self.tag_patterns.items():
            if re.match(pattern, word):
                return tag
        
        return 'NN'  # Default to noun


class NamedEntityRecognizer:
    """Named entity recognition."""
    
    def __init__(self):
        self.entity_patterns = {
            'PERSON': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'TIME': r'\b\d{1,2}:\d{2}(:\d{2})?\s*(am|pm|AM|PM)?\b',
            'EMAIL': r'\b[\w.-]+@[\w.-]+\.\w+\b',
            'URL': r'https?://[\w.-]+(/[\w.-]*)*',
            'MONEY': r'\$\d+(\.\d{2})?',
            'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        }
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'type': entity_type,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return entities


class SentimentAnalyzer:
    """Sentiment analysis."""
    
    def __init__(self):
        self.positive_words = {
            'good', 'great', 'excellent', 'wonderful', 'amazing', 
            'love', 'like', 'happy', 'joy', 'positive', 'best',
            'beautiful', 'fantastic', 'perfect', 'brilliant'
        }
        self.negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 
            'sad', 'angry', 'negative', 'worst', 'horrible',
            'ugly', 'poor', 'fail', 'wrong', 'broken'
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        words = text.lower().split()
        
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        total = pos_count + neg_count
        
        if total == 0:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.5}
        
        score = (pos_count - neg_count) / total
        
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': min(1.0, total / len(words) if words else 0),
            'positive_words': pos_count,
            'negative_words': neg_count
        }


class TextSimilarity:
    """Text similarity metrics."""
    
    @staticmethod
    def jaccard(text1: str, text2: str) -> float:
        """Jaccard similarity coefficient."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    @staticmethod
    def cosine(text1: str, text2: str) -> float:
        """Cosine similarity."""
        words1 = Counter(text1.lower().split())
        words2 = Counter(text2.lower().split())
        
        all_words = set(words1.keys()) | set(words2.keys())
        
        dot_product = sum(words1.get(w, 0) * words2.get(w, 0) for w in all_words)
        
        mag1 = sum(v ** 2 for v in words1.values()) ** 0.5
        mag2 = sum(v ** 2 for v in words2.values()) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    @staticmethod
    def levenshtein(s1: str, s2: str) -> int:
        """Levenshtein edit distance."""
        if len(s1) < len(s2):
            return TextSimilarity.levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            prev_row = current_row
        
        return prev_row[-1]


# Export classes
__all__ = [
    'TextPreprocessor',
    'POSTagger',
    'NamedEntityRecognizer',
    'SentimentAnalyzer',
    'TextSimilarity'
]
