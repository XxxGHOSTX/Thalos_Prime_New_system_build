"""
THALOS Prime - Tokenization Module
BPE, Character-level, and SentencePiece-style tokenizers.
"""

from typing import List, Dict, Tuple, Optional
import json
import re


class CharacterTokenizer:
    """Character-level tokenizer."""
    
    def __init__(self):
        self.char_to_id: Dict[str, int] = {}
        self.id_to_char: Dict[int, str] = {}
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
        }
        self.vocab_size = len(self.special_tokens)
    
    def build_vocab(self, texts: List[str]) -> None:
        """Build vocabulary from texts."""
        chars = set()
        for text in texts:
            chars.update(text)
        
        # Initialize with special tokens
        self.char_to_id = dict(self.special_tokens)
        self.id_to_char = {v: k for k, v in self.special_tokens.items()}
        
        # Add characters
        for char in sorted(chars):
            if char not in self.char_to_id:
                idx = len(self.char_to_id)
                self.char_to_id[char] = idx
                self.id_to_char[idx] = char
        
        self.vocab_size = len(self.char_to_id)
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Encode text to token IDs."""
        ids = []
        if add_special_tokens:
            ids.append(self.special_tokens['<BOS>'])
        
        for char in text:
            ids.append(self.char_to_id.get(char, self.special_tokens['<UNK>']))
        
        if add_special_tokens:
            ids.append(self.special_tokens['<EOS>'])
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text."""
        chars = []
        for id_ in ids:
            char = self.id_to_char.get(id_, '<UNK>')
            if skip_special_tokens and char in self.special_tokens:
                continue
            chars.append(char)
        return ''.join(chars)
    
    def save(self, path: str) -> None:
        """Save tokenizer to file."""
        with open(path, 'w') as f:
            json.dump({
                'char_to_id': self.char_to_id,
                'special_tokens': self.special_tokens
            }, f)
    
    def load(self, path: str) -> None:
        """Load tokenizer from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.char_to_id = data['char_to_id']
        self.id_to_char = {int(v): k for k, v in self.char_to_id.items()}
        self.special_tokens = data['special_tokens']
        self.vocab_size = len(self.char_to_id)


class BPETokenizer:
    """Byte-Pair Encoding tokenizer."""
    
    def __init__(self, vocab_size: int = 1000):
        self.target_vocab_size = vocab_size
        self.vocab: Dict[str, int] = {}
        self.merges: List[Tuple[str, str]] = []
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
        }
    
    @property
    def vocab_size(self) -> int:
        return len(self.vocab)
    
    def _get_pairs(self, word: List[str]) -> Dict[Tuple[str, str], int]:
        """Get adjacent symbol pairs and their counts."""
        pairs = {}
        for i in range(len(word) - 1):
            pair = (word[i], word[i + 1])
            pairs[pair] = pairs.get(pair, 0) + 1
        return pairs
    
    def build_vocab(self, texts: List[str], min_frequency: int = 2) -> None:
        """Build BPE vocabulary from texts."""
        # Initialize with special tokens
        self.vocab = dict(self.special_tokens)
        
        # Count character-level tokens
        word_freqs: Dict[str, int] = {}
        for text in texts:
            words = text.split()
            for word in words:
                word = ' '.join(list(word)) + ' </w>'
                word_freqs[word] = word_freqs.get(word, 0) + 1
        
        # Add all characters to vocab
        for word in word_freqs:
            for char in word.split():
                if char not in self.vocab:
                    self.vocab[char] = len(self.vocab)
        
        # Iteratively merge most frequent pairs
        while len(self.vocab) < self.target_vocab_size:
            # Count pairs across all words
            pair_counts: Dict[Tuple[str, str], int] = {}
            for word, freq in word_freqs.items():
                symbols = word.split()
                for i in range(len(symbols) - 1):
                    pair = (symbols[i], symbols[i + 1])
                    pair_counts[pair] = pair_counts.get(pair, 0) + freq
            
            if not pair_counts:
                break
            
            # Find most frequent pair
            best_pair = max(pair_counts.items(), key=lambda x: x[1])
            if best_pair[1] < min_frequency:
                break
            
            pair = best_pair[0]
            new_token = pair[0] + pair[1]
            
            # Add merge
            self.merges.append(pair)
            self.vocab[new_token] = len(self.vocab)
            
            # Update words
            new_word_freqs = {}
            for word, freq in word_freqs.items():
                new_word = word.replace(f'{pair[0]} {pair[1]}', new_token)
                new_word_freqs[new_word] = freq
            word_freqs = new_word_freqs
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Encode text to token IDs."""
        ids = []
        if add_special_tokens:
            ids.append(self.special_tokens['<BOS>'])
        
        words = text.split()
        for word in words:
            # Convert to initial tokens
            tokens = list(word) + ['</w>']
            
            # Apply merges
            for pair in self.merges:
                i = 0
                while i < len(tokens) - 1:
                    if tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
                        tokens = tokens[:i] + [pair[0] + pair[1]] + tokens[i + 2:]
                    else:
                        i += 1
            
            # Convert to IDs
            for token in tokens:
                if token in self.vocab:
                    ids.append(self.vocab[token])
                else:
                    ids.append(self.special_tokens['<UNK>'])
        
        if add_special_tokens:
            ids.append(self.special_tokens['<EOS>'])
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text."""
        id_to_token = {v: k for k, v in self.vocab.items()}
        tokens = []
        for id_ in ids:
            token = id_to_token.get(id_, '<UNK>')
            if skip_special_tokens and token in self.special_tokens:
                continue
            tokens.append(token)
        
        text = ''.join(tokens)
        text = text.replace('</w>', ' ').strip()
        return text
    
    def save(self, path: str) -> None:
        """Save tokenizer to file."""
        with open(path, 'w') as f:
            json.dump({
                'vocab': self.vocab,
                'merges': self.merges,
                'special_tokens': self.special_tokens
            }, f)
    
    def load(self, path: str) -> None:
        """Load tokenizer from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.vocab = data['vocab']
        self.merges = [tuple(m) for m in data['merges']]
        self.special_tokens = data['special_tokens']


class SentencePieceTokenizer:
    """SentencePiece-style unigram tokenizer."""
    
    def __init__(self, vocab_size: int = 1000):
        self.target_vocab_size = vocab_size
        self.vocab: Dict[str, float] = {}  # token -> log probability
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
        }
    
    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)
    
    def build_vocab(self, texts: List[str]) -> None:
        """Build vocabulary from texts."""
        import math
        
        # Initialize with special tokens
        self.token_to_id = dict(self.special_tokens)
        
        # Count substrings
        substring_counts: Dict[str, int] = {}
        for text in texts:
            text = text.replace(' ', '▁')
            for length in range(1, min(len(text) + 1, 20)):
                for i in range(len(text) - length + 1):
                    substr = text[i:i + length]
                    substring_counts[substr] = substring_counts.get(substr, 0) + 1
        
        # Select top substrings by frequency
        sorted_substrings = sorted(substring_counts.items(), 
                                   key=lambda x: x[1], reverse=True)
        
        for substr, count in sorted_substrings[:self.target_vocab_size - len(self.special_tokens)]:
            if substr not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[substr] = idx
                self.vocab[substr] = -math.log(count + 1)
        
        self.id_to_token = {v: k for k, v in self.token_to_id.items()}
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Encode text using greedy longest-match."""
        ids = []
        if add_special_tokens:
            ids.append(self.special_tokens['<BOS>'])
        
        text = text.replace(' ', '▁')
        i = 0
        while i < len(text):
            # Find longest matching token
            best_length = 1
            for length in range(min(len(text) - i, 20), 0, -1):
                substr = text[i:i + length]
                if substr in self.token_to_id:
                    best_length = length
                    break
            
            token = text[i:i + best_length]
            ids.append(self.token_to_id.get(token, self.special_tokens['<UNK>']))
            i += best_length
        
        if add_special_tokens:
            ids.append(self.special_tokens['<EOS>'])
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text."""
        tokens = []
        for id_ in ids:
            token = self.id_to_token.get(id_, '<UNK>')
            if skip_special_tokens and token in ['<PAD>', '<UNK>', '<BOS>', '<EOS>']:
                continue
            tokens.append(token)
        
        text = ''.join(tokens)
        text = text.replace('▁', ' ').strip()
        return text
    
    def save(self, path: str) -> None:
        """Save tokenizer to file."""
        with open(path, 'w') as f:
            json.dump({
                'vocab': self.vocab,
                'token_to_id': self.token_to_id,
                'special_tokens': self.special_tokens
            }, f)
    
    def load(self, path: str) -> None:
        """Load tokenizer from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.vocab = data['vocab']
        self.token_to_id = data['token_to_id']
        self.id_to_token = {int(v): k for k, v in self.token_to_id.items()}
        self.special_tokens = data['special_tokens']


class WordTokenizer:
    """Simple word-level tokenizer."""
    
    def __init__(self):
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
        }
        self.vocab_size = len(self.special_tokens)
    
    def build_vocab(self, texts: List[str], min_freq: int = 1) -> None:
        """Build vocabulary from texts."""
        word_counts: Dict[str, int] = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                word = re.sub(r'[^\w\s]', '', word)
                if word:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        self.word_to_id = dict(self.special_tokens)
        self.id_to_word = {v: k for k, v in self.special_tokens.items()}
        
        for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= min_freq and word not in self.word_to_id:
                idx = len(self.word_to_id)
                self.word_to_id[word] = idx
                self.id_to_word[idx] = word
        
        self.vocab_size = len(self.word_to_id)
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Encode text to token IDs."""
        ids = []
        if add_special_tokens:
            ids.append(self.special_tokens['<BOS>'])
        
        words = text.lower().split()
        for word in words:
            word = re.sub(r'[^\w\s]', '', word)
            if word:
                ids.append(self.word_to_id.get(word, self.special_tokens['<UNK>']))
        
        if add_special_tokens:
            ids.append(self.special_tokens['<EOS>'])
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text."""
        words = []
        for id_ in ids:
            word = self.id_to_word.get(id_, '<UNK>')
            if skip_special_tokens and word in self.special_tokens:
                continue
            words.append(word)
        return ' '.join(words)
