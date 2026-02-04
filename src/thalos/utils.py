"""
Utility Functions for THALOS Prime
Common helper functions used across the application
"""
import os
import sys
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from a file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON data as dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2):
    """
    Save data to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
        indent: JSON indentation level
    """
    filepath = Path(filepath)
    ensure_directory(filepath.parent)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def calculate_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)
        
    Returns:
        Hex digest of file hash
    """
    hash_func = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_size(filepath: Union[str, Path]) -> int:
    """
    Get file size in bytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes
    """
    return Path(filepath).stat().st_size


def format_bytes(size: int) -> str:
    """
    Format byte size to human-readable string
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def find_files(directory: Union[str, Path], pattern: str = "*", 
               recursive: bool = True) -> List[Path]:
    """
    Find files matching a pattern
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def get_python_version() -> str:
    """Get Python version string"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_project_root() -> Path:
    """
    Get the project root directory
    
    Returns:
        Path to project root
    """
    # Assume this file is in src/thalos/utils.py or similar
    current = Path(__file__).parent
    
    # Look for key project files
    while current != current.parent:
        if (current / 'thalos_app.py').exists() or \
           (current / 'pyproject.toml').exists() or \
           (current / '.git').exists():
            return current
        current = current.parent
    
    return Path.cwd()


def merge_dicts(base: Dict, update: Dict) -> Dict:
    """
    Recursively merge two dictionaries
    
    Args:
        base: Base dictionary
        update: Dictionary with updates
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def chunks(lst: List, n: int):
    """
    Yield successive n-sized chunks from list
    
    Args:
        lst: List to chunk
        n: Chunk size
        
    Yields:
        List chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class Timer:
    """Simple timer context manager for performance measurement"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        print(f"{self.name} took {elapsed:.3f} seconds")
    
    @property
    def elapsed(self) -> Optional[float]:
        """Get elapsed time, returns None if timer hasn't finished"""
        if self.start_time is None:
            return None
        if self.end_time is not None:
            return self.end_time - self.start_time
        # Return current elapsed time if timer is still running
        import time
        return time.time() - self.start_time
