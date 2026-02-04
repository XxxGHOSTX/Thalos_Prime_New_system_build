"""
Character tokenizer for THALOS Prime
"""


class CharacterTokenizer:
    """Simple character-level tokenizer"""
    
    def __init__(self):
        self.vocab = {}
        self.reverse_vocab = {}
        self.vocab_size = 0
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<SOS>': 2,
            '<EOS>': 3
        }
        # Initialize with special tokens
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.reverse_vocab[idx] = token
        self.vocab_size = len(self.special_tokens)
    
    def build_vocab(self, texts):
        """Build vocabulary from texts"""
        chars = set()
        for text in texts:
            chars.update(text)
        
        for char in sorted(chars):
            if char not in self.vocab:
                idx = self.vocab_size
                self.vocab[char] = idx
                self.reverse_vocab[idx] = char
                self.vocab_size += 1
    
    def encode(self, text):
        """Encode text to token ids"""
        return [self.vocab.get(char, self.special_tokens['<UNK>']) for char in text]
    
    def decode(self, token_ids):
        """Decode token ids to text"""
        return ''.join(self.reverse_vocab.get(idx, '<UNK>') for idx in token_ids)
