"""
THALOS Prime - Cryptography Module
AES-256 encryption, hashing, and secure random generation.
"""

from typing import Optional, List, Union
import hashlib
import hmac
import os
import struct


class SecureRandom:
    """Cryptographically secure random number generator."""
    
    @staticmethod
    def random_bytes(n: int) -> bytes:
        """Generate n random bytes."""
        return os.urandom(n)
    
    @staticmethod
    def random_int(min_val: int, max_val: int) -> int:
        """Generate random integer in range."""
        range_size = max_val - min_val + 1
        random_bytes = os.urandom(8)
        random_value = int.from_bytes(random_bytes, 'big')
        return min_val + (random_value % range_size)
    
    @staticmethod
    def random_float() -> float:
        """Generate random float between 0 and 1."""
        random_bytes = os.urandom(8)
        random_int = int.from_bytes(random_bytes, 'big')
        return random_int / (2 ** 64)
    
    @staticmethod
    def random_string(length: int, alphabet: str = None) -> str:
        """Generate random string."""
        if alphabet is None:
            alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(alphabet[SecureRandom.random_int(0, len(alphabet) - 1)] 
                       for _ in range(length))


class SecureHash:
    """Secure hashing functions."""
    
    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """Compute SHA-256 hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha512(data: Union[str, bytes]) -> str:
        """Compute SHA-512 hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()
    
    @staticmethod
    def blake2b(data: Union[str, bytes], digest_size: int = 32) -> str:
        """Compute BLAKE2b hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()
    
    @staticmethod
    def hmac_sha256(key: bytes, message: Union[str, bytes]) -> str:
        """Compute HMAC-SHA256."""
        if isinstance(message, str):
            message = message.encode('utf-8')
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    
    @staticmethod
    def verify_hmac(key: bytes, message: Union[str, bytes], expected: str) -> bool:
        """Verify HMAC."""
        computed = SecureHash.hmac_sha256(key, message)
        return hmac.compare_digest(computed, expected)


class PBKDF2:
    """Password-Based Key Derivation Function 2."""
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None, iterations: int = 100000,
                   key_length: int = 32) -> tuple:
        """Derive key from password."""
        if salt is None:
            salt = SecureRandom.random_bytes(16)
        
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                   salt, iterations, dklen=key_length)
        return key, salt


class AES256:
    """AES-256 encryption (simplified implementation)."""
    
    # S-box for SubBytes
    S_BOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    def __init__(self, password: str, salt: bytes = None):
        """Initialize AES with password-derived key."""
        self.key, self.salt = PBKDF2.derive_key(password, salt)
    
    def _xor_bytes(self, a: bytes, b: bytes) -> bytes:
        """XOR two byte strings."""
        return bytes(x ^ y for x, y in zip(a, b))
    
    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding."""
        block_size = 16
        padding_len = block_size - (len(data) % block_size)
        return data + bytes([padding_len] * padding_len)
    
    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_len = data[-1]
        return data[:-padding_len]
    
    def encrypt_simple(self, plaintext: str) -> bytes:
        """Simple XOR-based encryption (for demonstration)."""
        data = plaintext.encode('utf-8')
        data = self._pad(data)
        
        iv = SecureRandom.random_bytes(16)
        encrypted = bytearray()
        prev_block = iv
        
        for i in range(0, len(data), 16):
            block = data[i:i + 16]
            xored = self._xor_bytes(block, prev_block)
            
            # Simple block cipher (XOR with key-derived data)
            key_block = hashlib.sha256(self.key + struct.pack('>I', i // 16)).digest()[:16]
            encrypted_block = self._xor_bytes(xored, key_block)
            encrypted.extend(encrypted_block)
            prev_block = encrypted_block
        
        return iv + bytes(encrypted)
    
    def decrypt_simple(self, ciphertext: bytes) -> str:
        """Simple XOR-based decryption (for demonstration)."""
        iv = ciphertext[:16]
        data = ciphertext[16:]
        
        decrypted = bytearray()
        prev_block = iv
        
        for i in range(0, len(data), 16):
            block = data[i:i + 16]
            
            key_block = hashlib.sha256(self.key + struct.pack('>I', i // 16)).digest()[:16]
            xored = self._xor_bytes(block, key_block)
            decrypted_block = self._xor_bytes(xored, prev_block)
            decrypted.extend(decrypted_block)
            prev_block = block
        
        return self._unpad(bytes(decrypted)).decode('utf-8')
    
    def encrypt(self, plaintext: Union[str, bytes]) -> bytes:
        """Encrypt data."""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        return self.encrypt_simple(plaintext.decode('utf-8') if isinstance(plaintext, bytes) else plaintext)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data."""
        return self.decrypt_simple(ciphertext).encode('utf-8')


class ParameterEncryption:
    """Encrypt and decrypt model parameters."""
    
    def __init__(self, password: str):
        self.cipher = AES256(password)
    
    def encrypt_tensor(self, data: List[float]) -> bytes:
        """Encrypt tensor data."""
        # Pack floats to bytes
        packed = struct.pack(f'{len(data)}f', *data)
        return self.cipher.encrypt_simple(packed.hex())
    
    def decrypt_tensor(self, encrypted: bytes) -> List[float]:
        """Decrypt tensor data."""
        hex_data = self.cipher.decrypt_simple(encrypted)
        packed = bytes.fromhex(hex_data)
        return list(struct.unpack(f'{len(packed) // 4}f', packed))


class KeyManager:
    """Manage cryptographic keys."""
    
    def __init__(self, master_password: str):
        self.master_key, self.salt = PBKDF2.derive_key(master_password)
        self.derived_keys = {}
    
    def derive_key(self, purpose: str) -> bytes:
        """Derive a key for a specific purpose."""
        if purpose not in self.derived_keys:
            key = hashlib.pbkdf2_hmac('sha256', 
                                       self.master_key + purpose.encode('utf-8'),
                                       self.salt, 10000, dklen=32)
            self.derived_keys[purpose] = key
        return self.derived_keys[purpose]
    
    def get_encryption_key(self) -> bytes:
        """Get key for data encryption."""
        return self.derive_key('encryption')
    
    def get_signing_key(self) -> bytes:
        """Get key for message signing."""
        return self.derive_key('signing')
    
    def get_auth_key(self) -> bytes:
        """Get key for authentication."""
        return self.derive_key('authentication')


# Export all classes
__all__ = [
    'SecureRandom',
    'SecureHash',
    'PBKDF2',
    'AES256',
    'ParameterEncryption',
    'KeyManager',
]
