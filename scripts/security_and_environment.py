#!/usr/bin/env python3
"""
THALOS Prime - Security and Environment
Security utilities and environment management.
"""

from typing import Dict, Any, Optional
import os
import hashlib


class SecurityManager:
    """Security management utilities."""
    
    def __init__(self):
        self.permissions: Dict[str, list] = {}
        self.audit_log: list = []
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash a password."""
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key.hex(), salt.hex()
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify a password."""
        key, _ = self.hash_password(password, bytes.fromhex(salt))
        return key == hashed
    
    def add_permission(self, user: str, permission: str) -> None:
        """Add permission for user."""
        if user not in self.permissions:
            self.permissions[user] = []
        self.permissions[user].append(permission)
        self.audit_log.append(f"Added {permission} to {user}")
    
    def check_permission(self, user: str, permission: str) -> bool:
        """Check if user has permission."""
        return permission in self.permissions.get(user, [])


class EnvironmentManager:
    """Environment management utilities."""
    
    def __init__(self):
        self.env_vars: Dict[str, str] = {}
        self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default environment variables."""
        self.env_vars = {
            'THALOS_ENV': os.environ.get('THALOS_ENV', 'development'),
            'THALOS_DEBUG': os.environ.get('THALOS_DEBUG', 'false'),
            'THALOS_LOG_LEVEL': os.environ.get('THALOS_LOG_LEVEL', 'INFO'),
        }
    
    def get(self, key: str, default: str = '') -> str:
        """Get environment variable."""
        return self.env_vars.get(key, os.environ.get(key, default))
    
    def set(self, key: str, value: str) -> None:
        """Set environment variable."""
        self.env_vars[key] = value
        os.environ[key] = value
    
    def is_production(self) -> bool:
        """Check if in production mode."""
        return self.get('THALOS_ENV') == 'production'


def main():
    security = SecurityManager()
    hashed, salt = security.hash_password('test123')
    print(f"Verified: {security.verify_password('test123', hashed, salt)}")
    
    env = EnvironmentManager()
    print(f"Environment: {env.get('THALOS_ENV')}")


if __name__ == '__main__':
    main()
