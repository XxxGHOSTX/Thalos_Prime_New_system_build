"""
Kernel module for THALOS Prime
Provides memory management, virtual filesystem, and process context
"""
from typing import Dict, Optional


class MemoryAllocator:
    """Simple memory allocator"""
    
    def __init__(self, total_size):
        self.total_size = total_size
        self.allocated = {}
        self.next_addr = 0
    
    def allocate(self, size):
        """Allocate memory block"""
        if self.next_addr + size > self.total_size:
            raise MemoryError("Out of memory")
        
        addr = self.next_addr
        self.allocated[addr] = size
        self.next_addr += size
        return addr
    
    def deallocate(self, addr):
        """Deallocate memory block"""
        if addr in self.allocated:
            del self.allocated[addr]


class VirtualFileSystem:
    """Simple virtual filesystem"""
    
    def __init__(self):
        self.files = {}
    
    def create_file(self, filename, content=""):
        """Create a new file"""
        self.files[filename] = content
    
    def read_file(self, filename):
        """Read file content"""
        return self.files.get(filename, None)
    
    def write_file(self, filename, content):
        """Write content to file"""
        self.files[filename] = content
    
    def delete_file(self, filename):
        """Delete a file"""
        if filename in self.files:
            del self.files[filename]
    
    def list_files(self):
        """List all files"""
        return list(self.files.keys())


class IOManager:
    """Simple IO manager"""
    
    def __init__(self):
        self.buffer = []
    
    def read(self, source):
        """Read from source"""
        return source
    
    def write(self, destination, data):
        """Write to destination"""
        self.buffer.append((destination, data))


class ProcessContext:
    """Simple process context"""
    
    def __init__(self, name):
        self.name = name
        self.state = 'created'
        self.pid = id(self)
    
    def start(self):
        """Start process"""
        self.state = 'running'
    
    def stop(self):
        """Stop process"""
        self.state = 'stopped'
    
    def get_state(self):
        """Get process state"""
        return self.state


class KernelInterface:
    """Unified kernel interface"""
    
    def __init__(self):
        self.memory = MemoryAllocator(1024 * 1024)  # 1MB
        self.vfs = VirtualFileSystem()
        self.io = IOManager()
        self.processes = {}
    
    def create_process(self, name):
        """Create a new process"""
        proc = ProcessContext(name)
        self.processes[proc.pid] = proc
        return proc


__all__ = [
    'MemoryAllocator', 'VirtualFileSystem', 'IOManager',
    'ProcessContext', 'KernelInterface'
]
