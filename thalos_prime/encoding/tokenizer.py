"""
THALOS Prime - Tokenization Module

Implements multiple tokenization strategies from scratch:
- Character-level tokenizer
- Byte-Pair Encoding (BPE) tokenizer
- SentencePiece-style tokenizer
- Special token handling
- Vocabulary management
- Encoding/decoding operations
"""

from typing import List, Dict, Tuple, Optional, Set
import json
import re
from collections import Counter, defaultdict


class BaseTokenizer:
    """Base class for all tokenizers with common functionality."""
    
    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.special_tokens = {
            '[PAD]': 0,
            '[UNK]': 1,
            '[BOS]': 2,
            '[EOS]': 3,
        }
        self._vocab_built = False
    
    @property
    def vocab_size(self) -> int:
        """Return the size of the vocabulary."""
        return len(self.vocab)
    
    def _add_special_tokens(self):
        """Add special tokens to vocabulary."""
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.inverse_vocab[idx] = token
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement encode()")
    
    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs back to text. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement decode()")
    
    def build_vocab(self, texts: List[str]):
        """Build vocabulary from texts. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement build_vocab()")
    
    def save(self, path: str):
        """Save vocabulary to file."""
        data = {
            'vocab': self.vocab,
            'special_tokens': self.special_tokens,
            'type': self.__class__.__name__
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """Load vocabulary from file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocab = data['vocab']
        self.special_tokens = data['special_tokens']
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
        self._vocab_built = True


class CharacterTokenizer(BaseTokenizer):
    """
    Character-level tokenizer that splits text into individual characters.
    
    Features:
    - Character-level vocabulary
    - Special token support ([PAD], [UNK], [BOS], [EOS])
    - Case-sensitive by default
    - Handles Unicode characters
    
    Example:
        >>> tokenizer = CharacterTokenizer()
        >>> tokenizer.build_vocab(["hello world", "thalos prime"])
        >>> encoded = tokenizer.encode("hello")
        >>> decoded = tokenizer.decode(encoded)
        >>> print(decoded)  # "hello"
    """
    
    def __init__(self, lowercase: bool = False):
        """
        Initialize character tokenizer.
        
        Args:
            lowercase: If True, convert all text to lowercase before tokenization
        """
        super().__init__()
        self.lowercase = lowercase
    
    def build_vocab(self, texts: List[str]):
        """
        Build vocabulary from list of texts.
        
        Args:
            texts: List of text strings to build vocabulary from
        """
        # Start with special tokens
        self._add_special_tokens()
        current_idx = len(self.special_tokens)
        
        # Collect all unique characters
        char_set = set()
        for text in texts:
            if self.lowercase:
                text = text.lower()
            char_set.update(text)
        
        # Sort characters for deterministic ordering
        sorted_chars = sorted(char_set)
        
        # Add characters to vocabulary
        for char in sorted_chars:
            if char not in self.vocab:
                self.vocab[char] = current_idx
                self.inverse_vocab[current_idx] = char
                current_idx += 1
        
        self._vocab_built = True
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text to encode
            add_special_tokens: If True, add [BOS] and [EOS] tokens
            
        Returns:
            List of token IDs
        """
        if not self._vocab_built:
            raise ValueError("Vocabulary not built. Call build_vocab() first.")
        
        if self.lowercase:
            text = text.lower()
        
        token_ids = []
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[BOS]'])
        
        for char in text:
            token_id = self.vocab.get(char, self.special_tokens['[UNK]'])
            token_ids.append(token_id)
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[EOS]'])
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs to decode
            skip_special_tokens: If True, skip special tokens in output
            
        Returns:
            Decoded text string
        """
        chars = []
        special_ids = set(self.special_tokens.values())
        
        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            
            char = self.inverse_vocab.get(token_id, '[UNK]')
            chars.append(char)
        
        return ''.join(chars)


class BPETokenizer(BaseTokenizer):
    """
    Byte-Pair Encoding (BPE) tokenizer.
    
    BPE is a data compression technique that iteratively replaces the most
    frequent pair of bytes/characters with a new token. It's widely used
    in NLP for subword tokenization.
    
    Features:
    - Subword tokenization
    - Configurable vocabulary size
    - Handles out-of-vocabulary words through character fallback
    - Special token support
    
    Example:
        >>> tokenizer = BPETokenizer(vocab_size=1000)
        >>> tokenizer.build_vocab(["hello world", "thalos prime system"])
        >>> encoded = tokenizer.encode("hello")
        >>> decoded = tokenizer.decode(encoded)
    """
    
    def __init__(self, vocab_size: int = 5000):
        """
        Initialize BPE tokenizer.
        
        Args:
            vocab_size: Target vocabulary size (approximate)
        """
        super().__init__()
        self.target_vocab_size = vocab_size
        self.merges: List[Tuple[str, str]] = []
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
    
    def _get_char_vocab(self, texts: List[str]) -> Set[str]:
        """Get all unique characters from texts."""
        char_set = set()
        for text in texts:
            char_set.update(text)
        return char_set
    
    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize a word into characters with end-of-word marker."""
        if not word:
            return []
        return list(word[:-1]) + [word[-1] + '</w>']
    
    def _get_word_tokens(self, texts: List[str]) -> Dict[Tuple[str, ...], int]:
        """Get word tokens and their frequencies."""
        word_freqs = Counter()
        for text in texts:
            words = text.split()
            word_freqs.update(words)
        
        word_tokens = {}
        for word, freq in word_freqs.items():
            tokens = tuple(self._tokenize_word(word))
            word_tokens[tokens] = freq
        
        return word_tokens
    
    def _get_pair_freqs(self, word_tokens: Dict[Tuple[str, ...], int]) -> Counter:
        """Get frequencies of adjacent token pairs."""
        pair_freqs = Counter()
        for tokens, freq in word_tokens.items():
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                pair_freqs[pair] += freq
        return pair_freqs
    
    def _merge_pair(self, 
                    word_tokens: Dict[Tuple[str, ...], int],
                    pair: Tuple[str, str]) -> Dict[Tuple[str, ...], int]:
        """Merge a pair in all word tokens."""
        new_word_tokens = {}
        merged_token = pair[0] + pair[1]
        
        for tokens, freq in word_tokens.items():
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                    new_tokens.append(merged_token)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            new_word_tokens[tuple(new_tokens)] = freq
        
        return new_word_tokens
    
    def build_vocab(self, texts: List[str], num_merges: Optional[int] = None):
        """
        Build BPE vocabulary from texts.
        
        Args:
            texts: List of text strings
            num_merges: Number of merge operations (if None, uses target_vocab_size)
        """
        # Add special tokens
        self._add_special_tokens()
        current_idx = len(self.special_tokens)
        
        # Get character vocabulary
        char_vocab = self._get_char_vocab(' '.join(texts))
        
        # Initialize token vocabulary with characters
        for char in sorted(char_vocab):
            if char not in self.vocab:
                self.vocab[char] = current_idx
                self.inverse_vocab[current_idx] = char
                current_idx += 1
        
        # Add end-of-word marker variations
        for char in sorted(char_vocab):
            token = char + '</w>'
            if token not in self.vocab:
                self.vocab[token] = current_idx
                self.inverse_vocab[current_idx] = token
                current_idx += 1
        
        # Get word tokens
        word_tokens = self._get_word_tokens(texts)
        
        # Perform BPE merges
        if num_merges is None:
            num_merges = self.target_vocab_size - len(self.vocab)
        
        for _ in range(num_merges):
            pair_freqs = self._get_pair_freqs(word_tokens)
            if not pair_freqs:
                break
            
            # Get most frequent pair
            best_pair = pair_freqs.most_common(1)[0][0]
            self.merges.append(best_pair)
            
            # Add merged token to vocabulary
            merged_token = best_pair[0] + best_pair[1]
            if merged_token not in self.vocab:
                self.vocab[merged_token] = current_idx
                self.inverse_vocab[current_idx] = merged_token
                current_idx += 1
            
            # Merge in all word tokens
            word_tokens = self._merge_pair(word_tokens, best_pair)
            
            # Stop if we've reached target vocab size
            if len(self.vocab) >= self.target_vocab_size:
                break
        
        self._vocab_built = True
    
    def _apply_merges(self, tokens: List[str]) -> List[str]:
        """Apply learned merges to token list."""
        for pair in self.merges:
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                    new_tokens.append(pair[0] + pair[1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        return tokens
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """
        Encode text to token IDs using BPE.
        
        Args:
            text: Input text to encode
            add_special_tokens: If True, add [BOS] and [EOS] tokens
            
        Returns:
            List of token IDs
        """
        if not self._vocab_built:
            raise ValueError("Vocabulary not built. Call build_vocab() first.")
        
        token_ids = []
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[BOS]'])
        
        words = text.split()
        for word in words:
            # Tokenize word
            tokens = self._tokenize_word(word)
            # Apply merges
            tokens = self._apply_merges(tokens)
            # Convert to IDs
            for token in tokens:
                token_id = self.vocab.get(token, self.special_tokens['[UNK]'])
                token_ids.append(token_id)
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[EOS]'])
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs to decode
            skip_special_tokens: If True, skip special tokens in output
            
        Returns:
            Decoded text string
        """
        tokens = []
        special_ids = set(self.special_tokens.values())
        
        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            
            token = self.inverse_vocab.get(token_id, '[UNK]')
            tokens.append(token)
        
        # Join tokens and handle end-of-word markers
        text = ''.join(tokens)
        text = text.replace('</w>', ' ')
        return text.strip()
    
    def save(self, path: str):
        """Save tokenizer with merges."""
        data = {
            'vocab': self.vocab,
            'special_tokens': self.special_tokens,
            'merges': self.merges,
            'target_vocab_size': self.target_vocab_size,
            'type': self.__class__.__name__
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """Load tokenizer with merges."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocab = data['vocab']
        self.special_tokens = data['special_tokens']
        self.merges = [tuple(pair) for pair in data['merges']]
        self.target_vocab_size = data['target_vocab_size']
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
        self._vocab_built = True


class SentencePieceTokenizer(BaseTokenizer):
    """
    SentencePiece-style tokenizer with unigram language model.
    
    This implementation uses a simplified unigram approach where tokens
    are selected based on frequency and coverage. It handles subword
    tokenization similar to SentencePiece but without the full unigram
    language model complexity.
    
    Features:
    - Subword tokenization
    - Frequency-based vocabulary building
    - Character fallback for unknown sequences
    - Special token support
    
    Example:
        >>> tokenizer = SentencePieceTokenizer(vocab_size=2000)
        >>> tokenizer.build_vocab(["hello world", "thalos prime"])
        >>> encoded = tokenizer.encode("hello")
    """
    
    def __init__(self, vocab_size: int = 8000, character_coverage: float = 0.9995):
        """
        Initialize SentencePiece-style tokenizer.
        
        Args:
            vocab_size: Target vocabulary size
            character_coverage: Fraction of characters to cover (0.0 to 1.0)
        """
        super().__init__()
        self.target_vocab_size = vocab_size
        self.character_coverage = character_coverage
        self.pieces: List[str] = []
    
    def _get_char_freq(self, texts: List[str]) -> Counter:
        """Get character frequencies across all texts."""
        char_freq = Counter()
        for text in texts:
            char_freq.update(text)
        return char_freq
    
    def _get_substring_freq(self, texts: List[str], min_len: int = 2, max_len: int = 8) -> Counter:
        """Get substring frequencies."""
        substr_freq = Counter()
        for text in texts:
            for i in range(len(text)):
                for length in range(min_len, min(max_len + 1, len(text) - i + 1)):
                    substr = text[i:i + length]
                    # Only count substrings with reasonable characters
                    if substr.strip():
                        substr_freq[substr] += 1
        return substr_freq
    
    def build_vocab(self, texts: List[str]):
        """
        Build vocabulary using frequency-based selection.
        
        Args:
            texts: List of text strings to build vocabulary from
        """
        # Add special tokens
        self._add_special_tokens()
        current_idx = len(self.special_tokens)
        
        # Get character frequencies
        char_freq = self._get_char_freq(' '.join(texts))
        total_chars = sum(char_freq.values())
        
        # Add most common characters (coverage)
        sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)
        cumulative_freq = 0
        char_vocab = set()
        
        for char, freq in sorted_chars:
            if cumulative_freq / total_chars >= self.character_coverage:
                break
            char_vocab.add(char)
            cumulative_freq += freq
        
        # Add characters to vocabulary
        for char in sorted(char_vocab):
            if char not in self.vocab:
                self.vocab[char] = current_idx
                self.inverse_vocab[current_idx] = char
                self.pieces.append(char)
                current_idx += 1
        
        # Get substring frequencies
        substr_freq = self._get_substring_freq(texts)
        
        # Add most frequent substrings to vocabulary
        sorted_substrs = sorted(substr_freq.items(), key=lambda x: x[1], reverse=True)
        
        for substr, freq in sorted_substrs:
            if len(self.vocab) >= self.target_vocab_size:
                break
            
            # Only add if not already in vocab
            if substr not in self.vocab and freq > 1:
                self.vocab[substr] = current_idx
                self.inverse_vocab[current_idx] = substr
                self.pieces.append(substr)
                current_idx += 1
        
        # Sort pieces by length (longer first) for greedy matching
        self.pieces.sort(key=len, reverse=True)
        
        self._vocab_built = True
    
    def _greedy_tokenize(self, text: str) -> List[str]:
        """Tokenize text using greedy longest-match."""
        tokens = []
        i = 0
        
        while i < len(text):
            matched = False
            # Try to match longest piece
            for piece in self.pieces:
                if text[i:i + len(piece)] == piece:
                    tokens.append(piece)
                    i += len(piece)
                    matched = True
                    break
            
            if not matched:
                # Fallback to single character
                char = text[i]
                if char in self.vocab:
                    tokens.append(char)
                else:
                    tokens.append('[UNK]')
                i += 1
        
        return tokens
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text to encode
            add_special_tokens: If True, add [BOS] and [EOS] tokens
            
        Returns:
            List of token IDs
        """
        if not self._vocab_built:
            raise ValueError("Vocabulary not built. Call build_vocab() first.")
        
        token_ids = []
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[BOS]'])
        
        tokens = self._greedy_tokenize(text)
        
        for token in tokens:
            token_id = self.vocab.get(token, self.special_tokens['[UNK]'])
            token_ids.append(token_id)
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['[EOS]'])
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs to decode
            skip_special_tokens: If True, skip special tokens in output
            
        Returns:
            Decoded text string
        """
        tokens = []
        special_ids = set(self.special_tokens.values())
        
        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            
            token = self.inverse_vocab.get(token_id, '[UNK]')
            tokens.append(token)
        
        return ''.join(tokens)
    
    def save(self, path: str):
        """Save tokenizer with pieces."""
        data = {
            'vocab': self.vocab,
            'special_tokens': self.special_tokens,
            'pieces': self.pieces,
            'target_vocab_size': self.target_vocab_size,
            'character_coverage': self.character_coverage,
            'type': self.__class__.__name__
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """Load tokenizer with pieces."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.vocab = data['vocab']
        self.special_tokens = data['special_tokens']
        self.pieces = data['pieces']
        self.target_vocab_size = data['target_vocab_size']
        self.character_coverage = data['character_coverage']
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
        self._vocab_built = True


# Convenience function for creating tokenizers
def create_tokenizer(tokenizer_type: str = 'character', **kwargs) -> BaseTokenizer:
    """
    Create a tokenizer of the specified type.
    
    Args:
        tokenizer_type: Type of tokenizer ('character', 'bpe', 'sentencepiece')
        **kwargs: Additional arguments passed to tokenizer constructor
        
    Returns:
        Tokenizer instance
        
    Example:
        >>> tokenizer = create_tokenizer('character', lowercase=True)
        >>> tokenizer = create_tokenizer('bpe', vocab_size=5000)
        >>> tokenizer = create_tokenizer('sentencepiece', vocab_size=8000)
    """
    tokenizer_map = {
        'character': CharacterTokenizer,
        'char': CharacterTokenizer,
        'bpe': BPETokenizer,
        'sentencepiece': SentencePieceTokenizer,
        'sp': SentencePieceTokenizer,
    }
    
    tokenizer_type = tokenizer_type.lower()
    if tokenizer_type not in tokenizer_map:
        raise ValueError(
            f"Unknown tokenizer type: {tokenizer_type}. "
            f"Available types: {list(tokenizer_map.keys())}"
        )
    
    return tokenizer_map[tokenizer_type](**kwargs)
