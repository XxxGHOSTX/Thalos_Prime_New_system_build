"""
Crypto module for THALOS Prime
Provides hashing, encryption, and secure random generation
"""
import hashlib
import secrets
import os


class SecureHash:
    """Secure hash functions"""
    
    @staticmethod
    def sha256(data):
        """SHA-256 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha512(data):
        """SHA-512 hash"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()


class AES256:
    """Simple XOR-based encryption (not actual AES-256, simplified for minimal implementation)
    
    Note: This is a basic XOR cipher for demonstration purposes.
    For production use, use a proper cryptography library like cryptography or pycryptodome.
    """
    
    def __init__(self, password):
        self.password = password
        # Generate a key from password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def encrypt_simple(self, plaintext):
        """Simple XOR-based encryption (simplified)"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Simple XOR encryption for minimal implementation
        key_bytes = self.key
        encrypted = bytearray()
        for i, byte in enumerate(plaintext):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return encrypted.hex()
    
    def decrypt_simple(self, ciphertext):
        """Simple XOR-based decryption"""
        # Convert hex back to bytes
        encrypted = bytes.fromhex(ciphertext)
        
        # XOR decryption (same as encryption for XOR)
        key_bytes = self.key
        decrypted = bytearray()
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode('utf-8')


class SecureRandom:
    """Cryptographically secure random number generation"""
    
    @staticmethod
    def random_bytes(n):
        """Generate n random bytes"""
        return secrets.token_bytes(n)
    
    @staticmethod
    def random_int(a, b):
        """Generate random integer in [a, b]"""
        return secrets.randbelow(b - a + 1) + a


__all__ = ['SecureHash', 'AES256', 'SecureRandom']
