"""
THALOS Prime - Kernel Module

This module provides OS-like infrastructure components for the THALOS Prime system:
- Memory management with best-fit allocation
- Virtual file system with inode management
- Process context management
- I/O buffering and management
- Unified kernel interface

All implementations are from scratch using only Python standard library.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading
import time
import io


# ============================================================================
# Memory Management System
# ============================================================================

@dataclass
class MemoryBlock:
    """Represents a block of memory with start address and size."""
    start: int
    size: int
    is_free: bool = True
    
    @property
    def end(self) -> int:
        """Get the end address of this memory block."""
        return self.start + self.size


class MemoryAllocator:
    """
    Memory allocator with best-fit strategy.
    
    This allocator manages a contiguous memory space and uses the best-fit
    algorithm to allocate memory blocks, minimizing fragmentation.
    
    Attributes:
        total_size: Total size of managed memory
        blocks: List of memory blocks (free and allocated)
        allocated_blocks: Mapping from start address to block info
    
    Example:
        >>> mem = MemoryAllocator(1024)
        >>> addr = mem.allocate(256)
        >>> mem.deallocate(addr)
    """
    
    def __init__(self, size: int):
        """
        Initialize memory allocator with specified size.
        
        Args:
            size: Total size of memory to manage in bytes
            
        Raises:
            ValueError: If size is not positive
        """
        if size <= 0:
            raise ValueError("Memory size must be positive")
            
        self.total_size = size
        self.blocks: List[MemoryBlock] = [MemoryBlock(start=0, size=size, is_free=True)]
        self.allocated_blocks: Dict[int, MemoryBlock] = {}
        self._lock = threading.Lock()
        
        # Statistics
        self.total_allocated = 0
        self.total_freed = 0
        self.allocation_count = 0
        self.deallocation_count = 0
        self.fragmentation_events = 0
        
    def allocate(self, size: int) -> Optional[int]:
        """
        Allocate a memory block using best-fit strategy.
        
        The best-fit strategy finds the smallest free block that can
        accommodate the requested size, minimizing wasted space.
        
        Args:
            size: Size of memory to allocate in bytes
            
        Returns:
            Starting address of allocated block, or None if allocation fails
            
        Raises:
            ValueError: If size is not positive
        """
        if size <= 0:
            raise ValueError("Allocation size must be positive")
            
        with self._lock:
            # Find best-fit free block (smallest block that fits)
            best_block_idx = None
            best_block_size = float('inf')
            
            for idx, block in enumerate(self.blocks):
                if block.is_free and block.size >= size:
                    if block.size < best_block_size:
                        best_block_idx = idx
                        best_block_size = block.size
                        
            if best_block_idx is None:
                # Try to coalesce free blocks first
                self._coalesce_free_blocks()
                
                # Try again after coalescing
                for idx, block in enumerate(self.blocks):
                    if block.is_free and block.size >= size:
                        if block.size < best_block_size:
                            best_block_idx = idx
                            best_block_size = block.size
                            
                if best_block_idx is None:
                    return None  # Out of memory
                    
            # Allocate from the best-fit block
            block = self.blocks[best_block_idx]
            allocated_block = MemoryBlock(start=block.start, size=size, is_free=False)
            
            # Update blocks list
            if block.size == size:
                # Exact fit - replace the block
                self.blocks[best_block_idx] = allocated_block
            else:
                # Split the block
                remaining_block = MemoryBlock(
                    start=block.start + size,
                    size=block.size - size,
                    is_free=True
                )
                self.blocks[best_block_idx] = allocated_block
                self.blocks.insert(best_block_idx + 1, remaining_block)
                
            # Track allocation
            self.allocated_blocks[allocated_block.start] = allocated_block
            self.total_allocated += size
            self.allocation_count += 1
            
            return allocated_block.start
            
    def deallocate(self, address: int) -> bool:
        """
        Deallocate a previously allocated memory block.
        
        Args:
            address: Starting address of block to deallocate
            
        Returns:
            True if deallocation successful, False otherwise
        """
        with self._lock:
            if address not in self.allocated_blocks:
                return False
                
            # Find the block in the blocks list
            block_idx = None
            for idx, block in enumerate(self.blocks):
                if block.start == address and not block.is_free:
                    block_idx = idx
                    break
                    
            if block_idx is None:
                return False
                
            # Mark block as free
            block = self.blocks[block_idx]
            block.is_free = True
            
            # Remove from allocated tracking
            del self.allocated_blocks[address]
            self.total_freed += block.size
            self.deallocation_count += 1
            
            # Coalesce adjacent free blocks
            self._coalesce_at_index(block_idx)
            
            return True
            
    def _coalesce_at_index(self, idx: int):
        """Coalesce free blocks starting at given index."""
        if idx >= len(self.blocks):
            return
            
        # Coalesce with next block if free
        while idx < len(self.blocks) - 1:
            current = self.blocks[idx]
            next_block = self.blocks[idx + 1]
            
            if current.is_free and next_block.is_free:
                # Merge blocks
                current.size += next_block.size
                self.blocks.pop(idx + 1)
                self.fragmentation_events += 1
            else:
                break
                
        # Coalesce with previous block if free
        while idx > 0:
            current = self.blocks[idx]
            prev_block = self.blocks[idx - 1]
            
            if current.is_free and prev_block.is_free:
                # Merge blocks
                prev_block.size += current.size
                self.blocks.pop(idx)
                idx -= 1
                self.fragmentation_events += 1
            else:
                break
                
    def _coalesce_free_blocks(self):
        """Coalesce all adjacent free blocks to reduce fragmentation."""
        idx = 0
        while idx < len(self.blocks) - 1:
            current = self.blocks[idx]
            next_block = self.blocks[idx + 1]
            
            if current.is_free and next_block.is_free:
                current.size += next_block.size
                self.blocks.pop(idx + 1)
                self.fragmentation_events += 1
            else:
                idx += 1
                
    def get_free_memory(self) -> int:
        """Get total free memory available."""
        with self._lock:
            return sum(block.size for block in self.blocks if block.is_free)
            
    def get_used_memory(self) -> int:
        """Get total used memory."""
        with self._lock:
            return sum(block.size for block in self.blocks if not block.is_free)
            
    def get_fragmentation_ratio(self) -> float:
        """
        Calculate memory fragmentation ratio.
        
        Returns:
            Ratio of free blocks to total blocks (0.0 to 1.0)
        """
        with self._lock:
            if len(self.blocks) == 0:
                return 0.0
            free_blocks = sum(1 for block in self.blocks if block.is_free)
            return free_blocks / len(self.blocks)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory allocation statistics."""
        with self._lock:
            used_memory = sum(block.size for block in self.blocks if not block.is_free)
            free_memory = sum(block.size for block in self.blocks if block.is_free)
            free_blocks_count = sum(1 for b in self.blocks if b.is_free)
            frag_ratio = free_blocks_count / len(self.blocks) if len(self.blocks) > 0 else 0.0
            
            return {
                'total_size': self.total_size,
                'used_memory': used_memory,
                'free_memory': free_memory,
                'total_blocks': len(self.blocks),
                'free_blocks': free_blocks_count,
                'allocated_blocks': len(self.allocated_blocks),
                'fragmentation_ratio': frag_ratio,
                'total_allocated': self.total_allocated,
                'total_freed': self.total_freed,
                'allocation_count': self.allocation_count,
                'deallocation_count': self.deallocation_count,
                'fragmentation_events': self.fragmentation_events
            }


# ============================================================================
# Virtual File System
# ============================================================================

class InodeType(Enum):
    """Types of inodes in the virtual file system."""
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class Inode:
    """
    Represents an inode in the virtual file system.
    
    An inode contains metadata about a file or directory.
    
    Attributes:
        inode_id: Unique inode identifier
        type: Type of inode (file or directory)
        size: Size in bytes (for files)
        created: Creation timestamp
        modified: Last modification timestamp
        accessed: Last access timestamp
        permissions: Access permissions (simplified)
        content: File content (for files) or None (for directories)
        children: Set of child inode IDs (for directories)
    """
    inode_id: int
    type: InodeType
    size: int = 0
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)
    accessed: float = field(default_factory=time.time)
    permissions: int = 0o644  # Read/write for owner, read for others
    content: Optional[str] = None
    children: Set[int] = field(default_factory=set)
    
    def update_modified(self):
        """Update modification timestamp."""
        self.modified = time.time()
        
    def update_accessed(self):
        """Update access timestamp."""
        self.accessed = time.time()


class VirtualFileSystem:
    """
    Virtual file system with inode management.
    
    This VFS provides a Unix-like hierarchical file system with inodes,
    supporting files and directories with paths.
    
    Features:
        - Inode-based architecture
        - Path-based file access
        - Directory hierarchies
        - Metadata tracking (timestamps, permissions)
        - Thread-safe operations
    
    Example:
        >>> vfs = VirtualFileSystem()
        >>> vfs.create_file("test.txt", "Hello")
        >>> content = vfs.read_file("test.txt")
        >>> vfs.delete_file("test.txt")
    """
    
    def __init__(self):
        """Initialize the virtual file system."""
        self.inodes: Dict[int, Inode] = {}
        self.next_inode_id = 1
        self.path_to_inode: Dict[str, int] = {}
        self._lock = threading.Lock()
        
        # Create root directory (inode 0)
        root_inode = Inode(
            inode_id=0,
            type=InodeType.DIRECTORY,
            permissions=0o755
        )
        self.inodes[0] = root_inode
        self.path_to_inode['/'] = 0
        
        # Statistics
        self.files_created = 0
        self.files_deleted = 0
        self.files_read = 0
        self.files_written = 0
        
    def _allocate_inode(self, type: InodeType) -> Inode:
        """Allocate a new inode."""
        inode_id = self.next_inode_id
        self.next_inode_id += 1
        
        inode = Inode(inode_id=inode_id, type=type)
        self.inodes[inode_id] = inode
        return inode
        
    def _normalize_path(self, path: str) -> str:
        """Normalize a file path."""
        if not path:
            return '/'
        if not path.startswith('/'):
            path = '/' + path
        # Remove duplicate slashes
        while '//' in path:
            path = path.replace('//', '/')
        # Remove trailing slash except for root
        if len(path) > 1 and path.endswith('/'):
            path = path[:-1]
        return path
        
    def _get_parent_path(self, path: str) -> str:
        """Get parent directory path."""
        path = self._normalize_path(path)
        if path == '/':
            return '/'
        parent = path.rsplit('/', 1)[0]
        return parent if parent else '/'
        
    def _get_name(self, path: str) -> str:
        """Get file/directory name from path."""
        path = self._normalize_path(path)
        if path == '/':
            return '/'
        return path.rsplit('/', 1)[1]
        
    def create_file(self, path: str, content: str = "") -> bool:
        """
        Create a new file with optional content.
        
        Args:
            path: Path to the file
            content: Initial file content
            
        Returns:
            True if file created successfully, False otherwise
        """
        with self._lock:
            path = self._normalize_path(path)
            
            # Check if file already exists
            if path in self.path_to_inode:
                return False
                
            # Ensure parent directory exists
            parent_path = self._get_parent_path(path)
            if parent_path not in self.path_to_inode:
                # Create parent directory if it doesn't exist
                self.create_directory(parent_path)
                
            # Create file inode
            inode = self._allocate_inode(InodeType.FILE)
            inode.content = content
            inode.size = len(content)
            
            # Add to path mapping
            self.path_to_inode[path] = inode.inode_id
            
            # Add to parent directory
            if parent_path in self.path_to_inode:
                parent_inode_id = self.path_to_inode[parent_path]
                parent_inode = self.inodes[parent_inode_id]
                if parent_inode.type == InodeType.DIRECTORY:
                    parent_inode.children.add(inode.inode_id)
                    parent_inode.update_modified()
                    
            self.files_created += 1
            return True
            
    def read_file(self, path: str) -> Optional[str]:
        """
        Read content from a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File content as string, or None if file doesn't exist
        """
        with self._lock:
            path = self._normalize_path(path)
            
            if path not in self.path_to_inode:
                return None
                
            inode_id = self.path_to_inode[path]
            inode = self.inodes[inode_id]
            
            if inode.type != InodeType.FILE:
                return None
                
            inode.update_accessed()
            self.files_read += 1
            return inode.content
            
    def write_file(self, path: str, content: str) -> bool:
        """
        Write content to an existing file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            True if write successful, False otherwise
        """
        with self._lock:
            path = self._normalize_path(path)
            
            if path not in self.path_to_inode:
                return False
                
            inode_id = self.path_to_inode[path]
            inode = self.inodes[inode_id]
            
            if inode.type != InodeType.FILE:
                return False
                
            inode.content = content
            inode.size = len(content)
            inode.update_modified()
            self.files_written += 1
            return True
            
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if deletion successful, False otherwise
        """
        with self._lock:
            path = self._normalize_path(path)
            
            if path not in self.path_to_inode:
                return False
                
            inode_id = self.path_to_inode[path]
            inode = self.inodes[inode_id]
            
            if inode.type != InodeType.FILE:
                return False
                
            # Remove from parent directory
            parent_path = self._get_parent_path(path)
            if parent_path in self.path_to_inode:
                parent_inode_id = self.path_to_inode[parent_path]
                parent_inode = self.inodes[parent_inode_id]
                if inode_id in parent_inode.children:
                    parent_inode.children.remove(inode_id)
                    parent_inode.update_modified()
                    
            # Remove inode and path mapping
            del self.inodes[inode_id]
            del self.path_to_inode[path]
            self.files_deleted += 1
            return True
            
    def create_directory(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if directory created successfully, False otherwise
        """
        with self._lock:
            path = self._normalize_path(path)
            
            if path in self.path_to_inode:
                return False
                
            # Create parent directories recursively
            parent_path = self._get_parent_path(path)
            if parent_path != path and parent_path not in self.path_to_inode:
                self.create_directory(parent_path)
                
            # Create directory inode
            inode = self._allocate_inode(InodeType.DIRECTORY)
            inode.permissions = 0o755
            
            # Add to path mapping
            self.path_to_inode[path] = inode.inode_id
            
            # Add to parent directory
            if parent_path in self.path_to_inode:
                parent_inode_id = self.path_to_inode[parent_path]
                parent_inode = self.inodes[parent_inode_id]
                if parent_inode.type == InodeType.DIRECTORY:
                    parent_inode.children.add(inode.inode_id)
                    parent_inode.update_modified()
                    
            return True
            
    def list_files(self, path: str = "/") -> List[str]:
        """
        List files in a directory.
        
        Args:
            path: Directory path (default is root)
            
        Returns:
            List of file paths in the directory
        """
        with self._lock:
            path = self._normalize_path(path)
            
            if path not in self.path_to_inode:
                return []
                
            inode_id = self.path_to_inode[path]
            inode = self.inodes[inode_id]
            
            if inode.type != InodeType.DIRECTORY:
                return []
                
            # Get all paths that start with this directory path
            result = []
            prefix = path if path == '/' else path + '/'
            
            for file_path in self.path_to_inode.keys():
                if file_path.startswith(prefix) and file_path != path:
                    # Only include direct children (no subdirectories)
                    relative = file_path[len(prefix):]
                    if '/' not in relative:
                        result.append(file_path)
                        
            return sorted(result)
            
    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        with self._lock:
            path = self._normalize_path(path)
            return path in self.path_to_inode
            
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        with self._lock:
            path = self._normalize_path(path)
            if path not in self.path_to_inode:
                return False
            inode_id = self.path_to_inode[path]
            return self.inodes[inode_id].type == InodeType.FILE
            
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory."""
        with self._lock:
            path = self._normalize_path(path)
            if path not in self.path_to_inode:
                return False
            inode_id = self.path_to_inode[path]
            return self.inodes[inode_id].type == InodeType.DIRECTORY
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get file system statistics."""
        with self._lock:
            return {
                'total_inodes': len(self.inodes),
                'files': sum(1 for i in self.inodes.values() if i.type == InodeType.FILE),
                'directories': sum(1 for i in self.inodes.values() if i.type == InodeType.DIRECTORY),
                'total_size': sum(i.size for i in self.inodes.values() if i.type == InodeType.FILE),
                'files_created': self.files_created,
                'files_deleted': self.files_deleted,
                'files_read': self.files_read,
                'files_written': self.files_written
            }


# ============================================================================
# Process Management
# ============================================================================

class ProcessState(Enum):
    """States of a process."""
    CREATED = 'created'
    READY = 'ready'
    RUNNING = 'running'
    BLOCKED = 'blocked'
    TERMINATED = 'terminated'


class ProcessContext:
    """
    Process context for task simulation.
    
    Represents a lightweight process with state management, resembling
    operating system process contexts.
    
    Attributes:
        name: Process name
        pid: Process ID
        state: Current process state
        priority: Process priority (0-10, higher is more important)
        cpu_time: Accumulated CPU time in seconds
        memory_usage: Memory usage in bytes
        created_at: Creation timestamp
        
    Example:
        >>> proc = ProcessContext("test_proc")
        >>> assert proc.state == 'created'
        >>> proc.transition_to('running')
        >>> assert proc.state == 'running'
    """
    
    _next_pid = 1
    _pid_lock = threading.Lock()
    
    def __init__(self, name: str, priority: int = 5):
        """
        Initialize a process context.
        
        Args:
            name: Name of the process
            priority: Process priority (0-10, default 5)
        """
        with ProcessContext._pid_lock:
            self.pid = ProcessContext._next_pid
            ProcessContext._next_pid += 1
            
        self.name = name
        self._state = ProcessState.CREATED
        self.priority = max(0, min(10, priority))
        self.cpu_time = 0.0
        self.memory_usage = 0
        self.created_at = time.time()
        self.parent_pid: Optional[int] = None
        self.children: Set[int] = set()
        self._lock = threading.Lock()
        
    @property
    def state(self) -> str:
        """Get current process state as string."""
        return self._state.value
        
    def transition_to(self, new_state: str) -> bool:
        """
        Transition process to a new state.
        
        Args:
            new_state: Target state name
            
        Returns:
            True if transition successful, False otherwise
        """
        with self._lock:
            try:
                target = ProcessState(new_state)
                
                # Validate state transitions
                valid_transitions = {
                    ProcessState.CREATED: [ProcessState.READY],
                    ProcessState.READY: [ProcessState.RUNNING, ProcessState.TERMINATED],
                    ProcessState.RUNNING: [ProcessState.READY, ProcessState.BLOCKED, ProcessState.TERMINATED],
                    ProcessState.BLOCKED: [ProcessState.READY, ProcessState.TERMINATED],
                    ProcessState.TERMINATED: []
                }
                
                if target in valid_transitions.get(self._state, []):
                    self._state = target
                    return True
                return False
            except ValueError:
                return False
                
    def accumulate_cpu_time(self, seconds: float):
        """Add CPU time to process."""
        with self._lock:
            self.cpu_time += seconds
            
    def set_memory_usage(self, bytes_used: int):
        """Set process memory usage."""
        with self._lock:
            self.memory_usage = bytes_used
            
    def get_info(self) -> Dict[str, Any]:
        """Get process information."""
        with self._lock:
            return {
                'pid': self.pid,
                'name': self.name,
                'state': self.state,
                'priority': self.priority,
                'cpu_time': self.cpu_time,
                'memory_usage': self.memory_usage,
                'created_at': self.created_at,
                'age': time.time() - self.created_at,
                'parent_pid': self.parent_pid,
                'children_count': len(self.children)
            }


# ============================================================================
# I/O Management
# ============================================================================

class IOBuffer:
    """
    Buffered I/O manager for efficient read/write operations.
    
    Provides buffered input/output similar to file I/O, with
    configurable buffer sizes and flush policies.
    """
    
    def __init__(self, buffer_size: int = 4096):
        """
        Initialize I/O buffer.
        
        Args:
            buffer_size: Size of buffer in bytes
        """
        self.buffer_size = buffer_size
        self.read_buffer = io.StringIO()
        self.write_buffer = io.StringIO()
        self._lock = threading.Lock()
        
        # Statistics
        self.bytes_read = 0
        self.bytes_written = 0
        self.flush_count = 0
        
    def write(self, data: str) -> int:
        """
        Write data to buffer.
        
        Args:
            data: Data to write
            
        Returns:
            Number of bytes written
        """
        with self._lock:
            bytes_written = self.write_buffer.write(data)
            self.bytes_written += bytes_written
            
            # Auto-flush if buffer exceeds size
            if self.write_buffer.tell() >= self.buffer_size:
                self.flush()
                
            return bytes_written
            
    def read(self, size: int = -1) -> str:
        """
        Read data from buffer.
        
        Args:
            size: Number of bytes to read (-1 for all)
            
        Returns:
            Data read from buffer
        """
        with self._lock:
            data = self.read_buffer.read(size)
            self.bytes_read += len(data)
            return data
            
    def flush(self) -> str:
        """
        Flush write buffer and return contents.
        
        Returns:
            Contents of write buffer
        """
        with self._lock:
            content = self.write_buffer.getvalue()
            self.write_buffer = io.StringIO()
            self.flush_count += 1
            return content
            
    def get_write_buffer_size(self) -> int:
        """Get current write buffer size."""
        with self._lock:
            return self.write_buffer.tell()
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get I/O statistics."""
        with self._lock:
            return {
                'buffer_size': self.buffer_size,
                'bytes_read': self.bytes_read,
                'bytes_written': self.bytes_written,
                'flush_count': self.flush_count,
                'current_write_buffer_size': self.get_write_buffer_size()
            }


class IOManager:
    """
    I/O Manager with buffered operations.
    
    Manages multiple I/O streams with buffering, providing efficient
    input/output operations across the system.
    
    Features:
        - Multiple named streams
        - Configurable buffer sizes
        - Automatic flushing
        - Thread-safe operations
        - Statistics tracking
    
    Example:
        >>> io_mgr = IOManager()
        >>> io_mgr.write("stdout", "Hello, World!")
        >>> io_mgr.flush("stdout")
    """
    
    def __init__(self, default_buffer_size: int = 4096):
        """
        Initialize I/O manager.
        
        Args:
            default_buffer_size: Default buffer size for new streams
        """
        self.default_buffer_size = default_buffer_size
        self.streams: Dict[str, IOBuffer] = {}
        self._lock = threading.Lock()
        
        # Create standard streams
        self.create_stream("stdin")
        self.create_stream("stdout")
        self.create_stream("stderr")
        
    def create_stream(self, name: str, buffer_size: Optional[int] = None) -> bool:
        """
        Create a new I/O stream.
        
        Args:
            name: Stream name
            buffer_size: Buffer size (uses default if None)
            
        Returns:
            True if stream created, False if already exists
        """
        with self._lock:
            if name in self.streams:
                return False
                
            size = buffer_size if buffer_size is not None else self.default_buffer_size
            self.streams[name] = IOBuffer(size)
            return True
            
    def write(self, stream_name: str, data: str) -> int:
        """
        Write data to a stream.
        
        Args:
            stream_name: Name of stream
            data: Data to write
            
        Returns:
            Number of bytes written
        """
        with self._lock:
            if stream_name not in self.streams:
                self.create_stream(stream_name)
            return self.streams[stream_name].write(data)
            
    def read(self, stream_name: str, size: int = -1) -> Optional[str]:
        """
        Read data from a stream.
        
        Args:
            stream_name: Name of stream
            size: Number of bytes to read
            
        Returns:
            Data read, or None if stream doesn't exist
        """
        with self._lock:
            if stream_name not in self.streams:
                return None
            return self.streams[stream_name].read(size)
            
    def flush(self, stream_name: str) -> Optional[str]:
        """
        Flush a stream.
        
        Args:
            stream_name: Name of stream
            
        Returns:
            Flushed content, or None if stream doesn't exist
        """
        with self._lock:
            if stream_name not in self.streams:
                return None
            return self.streams[stream_name].flush()
            
    def flush_all(self) -> Dict[str, str]:
        """
        Flush all streams.
        
        Returns:
            Dictionary mapping stream names to flushed content
        """
        with self._lock:
            result = {}
            for name, stream in self.streams.items():
                result[name] = stream.flush()
            return result
            
    def close_stream(self, name: str) -> bool:
        """
        Close and remove a stream.
        
        Args:
            name: Stream name
            
        Returns:
            True if stream closed, False if not found
        """
        with self._lock:
            if name in self.streams:
                del self.streams[name]
                return True
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get I/O manager statistics."""
        with self._lock:
            return {
                'total_streams': len(self.streams),
                'streams': {
                    name: stream.get_statistics()
                    for name, stream in self.streams.items()
                }
            }


# ============================================================================
# Kernel Interface
# ============================================================================

class KernelInterface:
    """
    Unified kernel interface for system-wide access.
    
    Provides a centralized interface to all kernel subsystems:
    - Memory management
    - File system
    - Process management
    - I/O operations
    
    This acts as the main entry point for kernel services.
    
    Example:
        >>> kernel = KernelInterface()
        >>> kernel.memory.allocate(256)
        >>> kernel.filesystem.create_file("test.txt", "Hello")
        >>> kernel.io.write("stdout", "Output")
    """
    
    def __init__(
        self,
        memory_size: int = 1024 * 1024,  # 1 MB default
        io_buffer_size: int = 4096
    ):
        """
        Initialize kernel interface.
        
        Args:
            memory_size: Total memory size to manage
            io_buffer_size: Default I/O buffer size
        """
        self.memory = MemoryAllocator(memory_size)
        self.filesystem = VirtualFileSystem()
        self.io = IOManager(io_buffer_size)
        self.processes: Dict[int, ProcessContext] = {}
        self._lock = threading.Lock()
        
        # Kernel statistics
        self.boot_time = time.time()
        self.syscall_count = 0
        
    def create_process(self, name: str, priority: int = 5) -> ProcessContext:
        """
        Create a new process.
        
        Args:
            name: Process name
            priority: Process priority
            
        Returns:
            New ProcessContext instance
        """
        with self._lock:
            proc = ProcessContext(name, priority)
            self.processes[proc.pid] = proc
            self.syscall_count += 1
            return proc
            
    def get_process(self, pid: int) -> Optional[ProcessContext]:
        """
        Get process by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessContext or None if not found
        """
        with self._lock:
            return self.processes.get(pid)
            
    def terminate_process(self, pid: int) -> bool:
        """
        Terminate a process.
        
        Args:
            pid: Process ID
            
        Returns:
            True if terminated, False if not found
        """
        with self._lock:
            if pid in self.processes:
                proc = self.processes[pid]
                proc.transition_to('terminated')
                del self.processes[pid]
                self.syscall_count += 1
                return True
            return False
            
    def list_processes(self) -> List[Dict[str, Any]]:
        """
        List all active processes.
        
        Returns:
            List of process information dictionaries
        """
        with self._lock:
            return [proc.get_info() for proc in self.processes.values()]
            
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary with system statistics
        """
        with self._lock:
            return {
                'uptime': time.time() - self.boot_time,
                'syscall_count': self.syscall_count,
                'memory': self.memory.get_statistics(),
                'filesystem': self.filesystem.get_statistics(),
                'io': self.io.get_statistics(),
                'processes': {
                    'active': len(self.processes),
                    'list': self.list_processes()
                }
            }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Memory Management
    'MemoryAllocator',
    'MemoryBlock',
    
    # File System
    'VirtualFileSystem',
    'Inode',
    'InodeType',
    
    # Process Management
    'ProcessContext',
    'ProcessState',
    
    # I/O Management
    'IOManager',
    'IOBuffer',
    
    # Kernel Interface
    'KernelInterface'
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
