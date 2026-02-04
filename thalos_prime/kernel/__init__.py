"""
THALOS Prime - Kernel Module
Memory management, virtual filesystem, and process context.
"""

from typing import Dict, List, Optional, Any, Callable
import time
import threading


class MemoryBlock:
    """Represents a block of memory."""
    
    def __init__(self, address: int, size: int, allocated: bool = False):
        self.address = address
        self.size = size
        self.allocated = allocated
        self.data = bytearray(size) if allocated else None


class MemoryAllocator:
    """Memory allocator with best-fit strategy."""
    
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size, False)]
        self.allocated_blocks: Dict[int, MemoryBlock] = {}
    
    def allocate(self, size: int) -> Optional[int]:
        """Allocate memory block using best-fit strategy."""
        # Find best fitting free block
        best_block = None
        best_idx = -1
        
        for i, block in enumerate(self.blocks):
            if not block.allocated and block.size >= size:
                if best_block is None or block.size < best_block.size:
                    best_block = block
                    best_idx = i
        
        if best_block is None:
            return None  # Out of memory
        
        address = best_block.address
        
        # Split block if necessary
        if best_block.size > size:
            new_block = MemoryBlock(
                address + size,
                best_block.size - size,
                False
            )
            self.blocks.insert(best_idx + 1, new_block)
        
        # Mark as allocated
        best_block.size = size
        best_block.allocated = True
        best_block.data = bytearray(size)
        self.allocated_blocks[address] = best_block
        
        return address
    
    def deallocate(self, address: int) -> bool:
        """Free allocated memory block."""
        if address not in self.allocated_blocks:
            return False
        
        block = self.allocated_blocks[address]
        block.allocated = False
        block.data = None
        del self.allocated_blocks[address]
        
        # Coalesce adjacent free blocks
        self._coalesce()
        
        return True
    
    def _coalesce(self):
        """Merge adjacent free blocks."""
        i = 0
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            next_block = self.blocks[i + 1]
            
            if not current.allocated and not next_block.allocated:
                current.size += next_block.size
                self.blocks.pop(i + 1)
            else:
                i += 1
    
    def read(self, address: int, size: int) -> Optional[bytes]:
        """Read data from memory."""
        if address not in self.allocated_blocks:
            return None
        block = self.allocated_blocks[address]
        return bytes(block.data[:size])
    
    def write(self, address: int, data: bytes) -> bool:
        """Write data to memory."""
        if address not in self.allocated_blocks:
            return False
        block = self.allocated_blocks[address]
        if len(data) > block.size:
            return False
        block.data[:len(data)] = data
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics."""
        allocated = sum(b.size for b in self.blocks if b.allocated)
        free = sum(b.size for b in self.blocks if not b.allocated)
        return {
            'total': self.total_size,
            'allocated': allocated,
            'free': free,
            'blocks': len(self.blocks),
            'fragmentation': len([b for b in self.blocks if not b.allocated])
        }


class INode:
    """Represents a file or directory in the virtual filesystem."""
    
    def __init__(self, name: str, is_dir: bool = False):
        self.name = name
        self.is_dir = is_dir
        self.content = b'' if not is_dir else None
        self.children: Dict[str, 'INode'] = {} if is_dir else None
        self.created_at = time.time()
        self.modified_at = time.time()
        self.size = 0
        self.permissions = 0o755 if is_dir else 0o644


class VirtualFileSystem:
    """Virtual filesystem with inode management."""
    
    def __init__(self):
        self.root = INode('/', is_dir=True)
        self.cwd = '/'
    
    def _resolve_path(self, path: str) -> List[str]:
        """Resolve path to components."""
        if not path.startswith('/'):
            path = self.cwd + '/' + path
        
        parts = []
        for part in path.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        
        return parts
    
    def _get_inode(self, path: str) -> Optional[INode]:
        """Get inode for path."""
        parts = self._resolve_path(path)
        node = self.root
        
        for part in parts:
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        
        return node
    
    def _get_parent(self, path: str) -> Optional[INode]:
        """Get parent inode for path."""
        parts = self._resolve_path(path)
        if not parts:
            return self.root
        
        node = self.root
        for part in parts[:-1]:
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        
        return node
    
    def create_file(self, path: str, content: str = '') -> bool:
        """Create a file."""
        parts = self._resolve_path(path)
        if not parts:
            return False
        
        parent = self._get_parent(path)
        if parent is None or not parent.is_dir:
            return False
        
        name = parts[-1]
        if name in parent.children:
            return False
        
        inode = INode(name, is_dir=False)
        inode.content = content.encode('utf-8')
        inode.size = len(inode.content)
        parent.children[name] = inode
        
        return True
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content."""
        node = self._get_inode(path)
        if node is None or node.is_dir:
            return None
        return node.content.decode('utf-8')
    
    def write_file(self, path: str, content: str) -> bool:
        """Write to file (overwrite)."""
        node = self._get_inode(path)
        if node is None:
            return self.create_file(path, content)
        
        if node.is_dir:
            return False
        
        node.content = content.encode('utf-8')
        node.size = len(node.content)
        node.modified_at = time.time()
        return True
    
    def append_file(self, path: str, content: str) -> bool:
        """Append to file."""
        node = self._get_inode(path)
        if node is None or node.is_dir:
            return False
        
        node.content += content.encode('utf-8')
        node.size = len(node.content)
        node.modified_at = time.time()
        return True
    
    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        parts = self._resolve_path(path)
        if not parts:
            return False
        
        parent = self._get_parent(path)
        if parent is None:
            return False
        
        name = parts[-1]
        if name not in parent.children:
            return False
        
        node = parent.children[name]
        if node.is_dir and node.children:
            return False  # Directory not empty
        
        del parent.children[name]
        return True
    
    def create_directory(self, path: str) -> bool:
        """Create a directory."""
        parts = self._resolve_path(path)
        if not parts:
            return False
        
        parent = self._get_parent(path)
        if parent is None or not parent.is_dir:
            return False
        
        name = parts[-1]
        if name in parent.children:
            return False
        
        parent.children[name] = INode(name, is_dir=True)
        return True
    
    def list_directory(self, path: str = '.') -> Optional[List[str]]:
        """List directory contents."""
        node = self._get_inode(path)
        if node is None or not node.is_dir:
            return None
        return list(node.children.keys())
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self._get_inode(path) is not None
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        node = self._get_inode(path)
        return node is not None and not node.is_dir
    
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        node = self._get_inode(path)
        return node is not None and node.is_dir
    
    def get_size(self, path: str) -> int:
        """Get file size."""
        node = self._get_inode(path)
        if node is None or node.is_dir:
            return 0
        return node.size


class IOBuffer:
    """Buffered I/O operations."""
    
    def __init__(self, buffer_size: int = 4096):
        self.buffer_size = buffer_size
        self.read_buffer = bytearray()
        self.write_buffer = bytearray()
    
    def buffer_read(self, data: bytes) -> bytes:
        """Buffer read operation."""
        self.read_buffer.extend(data)
        if len(self.read_buffer) >= self.buffer_size:
            result = bytes(self.read_buffer)
            self.read_buffer.clear()
            return result
        return b''
    
    def buffer_write(self, data: bytes) -> Optional[bytes]:
        """Buffer write operation."""
        self.write_buffer.extend(data)
        if len(self.write_buffer) >= self.buffer_size:
            result = bytes(self.write_buffer)
            self.write_buffer.clear()
            return result
        return None
    
    def flush_read(self) -> bytes:
        """Flush read buffer."""
        result = bytes(self.read_buffer)
        self.read_buffer.clear()
        return result
    
    def flush_write(self) -> bytes:
        """Flush write buffer."""
        result = bytes(self.write_buffer)
        self.write_buffer.clear()
        return result


class IOManager:
    """Manage I/O operations."""
    
    def __init__(self, fs: VirtualFileSystem):
        self.fs = fs
        self.buffers: Dict[str, IOBuffer] = {}
        self.open_files: Dict[str, str] = {}  # handle -> path
    
    def open(self, path: str, mode: str = 'r') -> Optional[str]:
        """Open a file."""
        if mode in ('r', 'r+') and not self.fs.exists(path):
            return None
        
        if mode in ('w', 'w+', 'a', 'a+') and not self.fs.exists(path):
            self.fs.create_file(path)
        
        import uuid
        handle = str(uuid.uuid4())[:8]
        self.open_files[handle] = path
        self.buffers[handle] = IOBuffer()
        
        return handle
    
    def close(self, handle: str) -> bool:
        """Close a file."""
        if handle not in self.open_files:
            return False
        
        # Flush buffers
        if handle in self.buffers:
            remaining = self.buffers[handle].flush_write()
            if remaining:
                path = self.open_files[handle]
                self.fs.append_file(path, remaining.decode('utf-8', errors='replace'))
            del self.buffers[handle]
        
        del self.open_files[handle]
        return True
    
    def read(self, handle: str) -> Optional[str]:
        """Read from file."""
        if handle not in self.open_files:
            return None
        return self.fs.read_file(self.open_files[handle])
    
    def write(self, handle: str, content: str) -> bool:
        """Write to file."""
        if handle not in self.open_files:
            return False
        return self.fs.write_file(self.open_files[handle], content)


class ProcessContext:
    """Process context for task simulation."""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.pid = id(self)
        self.priority = priority
        self.state = 'created'
        self.created_at = time.time()
        self.started_at = None
        self.ended_at = None
        self.result = None
        self.error = None
        self._thread = None
        self._task = None
    
    def start(self, task: Callable) -> None:
        """Start the process."""
        self._task = task
        self.state = 'running'
        self.started_at = time.time()
        
        def wrapper():
            try:
                self.result = self._task()
                self.state = 'completed'
            except Exception as e:
                self.error = str(e)
                self.state = 'failed'
            finally:
                self.ended_at = time.time()
        
        self._thread = threading.Thread(target=wrapper)
        self._thread.start()
    
    def wait(self, timeout: float = None) -> bool:
        """Wait for process to complete."""
        if self._thread is None:
            return False
        self._thread.join(timeout)
        return not self._thread.is_alive()
    
    def terminate(self) -> None:
        """Terminate the process."""
        self.state = 'terminated'
        self.ended_at = time.time()
    
    def get_info(self) -> Dict[str, Any]:
        """Get process information."""
        return {
            'name': self.name,
            'pid': self.pid,
            'priority': self.priority,
            'state': self.state,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'duration': (self.ended_at - self.started_at) if self.ended_at and self.started_at else None,
            'result': self.result,
            'error': self.error
        }


class Scheduler:
    """Simple priority-based scheduler."""
    
    def __init__(self):
        self.ready_queue: List[ProcessContext] = []
        self.running: Optional[ProcessContext] = None
        self.completed: List[ProcessContext] = []
    
    def add_process(self, process: ProcessContext) -> None:
        """Add process to ready queue."""
        self.ready_queue.append(process)
        self.ready_queue.sort(key=lambda p: -p.priority)
    
    def schedule(self) -> Optional[ProcessContext]:
        """Get next process to run."""
        if not self.ready_queue:
            return None
        return self.ready_queue.pop(0)
    
    def run_all(self, tasks: Dict[str, Callable]) -> List[ProcessContext]:
        """Run all scheduled tasks."""
        for name, task in tasks.items():
            proc = ProcessContext(name)
            proc.start(task)
            self.completed.append(proc)
        
        # Wait for all to complete
        for proc in self.completed:
            proc.wait()
        
        return self.completed


class KernelInterface:
    """Unified kernel interface."""
    
    def __init__(self, memory_size: int = 1024 * 1024):
        self.memory = MemoryAllocator(memory_size)
        self.fs = VirtualFileSystem()
        self.io = IOManager(self.fs)
        self.scheduler = Scheduler()
        self.processes: Dict[int, ProcessContext] = {}
    
    def malloc(self, size: int) -> Optional[int]:
        """Allocate memory."""
        return self.memory.allocate(size)
    
    def free(self, address: int) -> bool:
        """Free memory."""
        return self.memory.deallocate(address)
    
    def create_process(self, name: str, task: Callable) -> ProcessContext:
        """Create and start a new process."""
        proc = ProcessContext(name)
        proc.start(task)
        self.processes[proc.pid] = proc
        return proc
    
    def get_status(self) -> Dict[str, Any]:
        """Get kernel status."""
        return {
            'memory': self.memory.get_stats(),
            'processes': len(self.processes),
            'open_files': len(self.io.open_files)
        }


# Export all classes
__all__ = [
    'MemoryBlock',
    'MemoryAllocator',
    'INode',
    'VirtualFileSystem',
    'IOBuffer',
    'IOManager',
    'ProcessContext',
    'Scheduler',
    'KernelInterface',
]
