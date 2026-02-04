"""
Database Integration Layer for THALOS Prime
"""
import sqlite3
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "data/thalos_prime.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    input_text TEXT,
                    output_text TEXT,
                    intent TEXT,
                    confidence REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL
                )
            ''')
            
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        with self._lock:
            if self.connection:
                self.connection.close()
                self.connection = None
    
    def create_session(self, session_id: str) -> Optional[int]:
        """Create a new session, returns None if session already exists"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO sessions (session_id) VALUES (?)', (session_id,))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Session already exists, return None
                return None
    
    def log_interaction(self, session_id: str, input_text: str, output_text: str, 
                       intent: str = None, confidence: float = None):
        """Log an interaction"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (session_id, input_text, output_text, intent, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, input_text, output_text, intent, confidence))
            conn.commit()
    
    def log_metric(self, metric_name: str, metric_value: float):
        """Log a metric"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO metrics (metric_name, metric_value)
                VALUES (?, ?)
            ''', (metric_name, metric_value))
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            cursor.execute('SELECT COUNT(*) FROM sessions')
            stats['total_sessions'] = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM interactions')
            stats['total_interactions'] = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM metrics')
            stats['total_metrics'] = cursor.fetchone()[0]
            
            return stats


_db_manager: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
