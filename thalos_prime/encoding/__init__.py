"""
THALOS Prime - Encoding Module

Provides tokenization functionality for text processing.

Public API:
    - CharacterTokenizer: Character-level tokenizer
    - BPETokenizer: Byte-Pair Encoding tokenizer
    - SentencePieceTokenizer: SentencePiece-style tokenizer
    - BaseTokenizer: Base class for custom tokenizers
    - create_tokenizer: Factory function for creating tokenizers

Example:
    >>> from thalos_prime.encoding import CharacterTokenizer
    >>> tokenizer = CharacterTokenizer()
    >>> tokenizer.build_vocab(["hello world", "thalos prime"])
    >>> encoded = tokenizer.encode("hello")
    >>> decoded = tokenizer.decode(encoded)
    >>> print(f"Encoded: {encoded}")
    >>> print(f"Decoded: {decoded}")
"""

from .tokenizer import (
    BaseTokenizer,
    CharacterTokenizer,
    BPETokenizer,
    SentencePieceTokenizer,
    create_tokenizer
)

__all__ = [
    'BaseTokenizer',
    'CharacterTokenizer',
    'BPETokenizer',
    'SentencePieceTokenizer',
    'create_tokenizer'
]

__version__ = '1.0.0'
