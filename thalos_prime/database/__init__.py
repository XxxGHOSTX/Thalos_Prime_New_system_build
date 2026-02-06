"""
THALOS Prime - Database Module
Database connections and operations.
"""

from typing import Dict, Any, Optional, List
import json
import os
import sqlite3


class DatabaseConnection:
    """SQLite database connection manager."""
    
    def __init__(self, db_path: str = ':memory:'):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: tuple = ()) -> Optional[List[Dict]]:
        """Execute a query and return results."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self.connection.commit()
                return [{'affected_rows': cursor.rowcount}]
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Execute query for multiple parameter sets."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Query error: {e}")
            return False


class ModelDatabase:
    """Database for model-related data."""
    
    def __init__(self, db_path: str = 'thalos_models.db'):
        self.db = DatabaseConnection(db_path)
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize database tables."""
        self.db.connect()
        
        # Models table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Training runs table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS training_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                epoch INTEGER,
                loss REAL,
                metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id)
            )
        """)
        
        # Checkpoints table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                path TEXT,
                epoch INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id)
            )
        """)
    
    def save_model(self, name: str, version: str, parameters: Dict) -> int:
        """Save model metadata."""
        result = self.db.execute(
            "INSERT INTO models (name, version, parameters) VALUES (?, ?, ?)",
            (name, version, json.dumps(parameters))
        )
        return result[0]['affected_rows'] if result else 0
    
    def get_model(self, model_id: int) -> Optional[Dict]:
        """Get model by ID."""
        result = self.db.execute(
            "SELECT * FROM models WHERE id = ?",
            (model_id,)
        )
        if result and len(result) > 0:
            model = result[0]
            model['parameters'] = json.loads(model['parameters'])
            return model
        return None
    
    def list_models(self) -> List[Dict]:
        """List all models."""
        result = self.db.execute("SELECT * FROM models ORDER BY created_at DESC")
        return result or []
    
    def save_training_run(self, model_id: int, epoch: int, loss: float, 
                          metrics: Dict) -> int:
        """Save training run data."""
        result = self.db.execute(
            "INSERT INTO training_runs (model_id, epoch, loss, metrics) VALUES (?, ?, ?, ?)",
            (model_id, epoch, loss, json.dumps(metrics))
        )
        return result[0]['affected_rows'] if result else 0
    
    def get_training_history(self, model_id: int) -> List[Dict]:
        """Get training history for a model."""
        result = self.db.execute(
            "SELECT * FROM training_runs WHERE model_id = ? ORDER BY epoch",
            (model_id,)
        )
        if result:
            for run in result:
                run['metrics'] = json.loads(run['metrics'])
        return result or []


class ConversationDatabase:
    """Database for conversation history."""
    
    def __init__(self, db_path: str = 'thalos_conversations.db'):
        self.db = DatabaseConnection(db_path)
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize database tables."""
        self.db.connect()
        
        # Sessions table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """Create a new session."""
        result = self.db.execute(
            "INSERT OR IGNORE INTO sessions (session_id, user_id) VALUES (?, ?)",
            (session_id, user_id)
        )
        return result is not None
    
    def add_message(self, session_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None) -> bool:
        """Add a message to a session."""
        result = self.db.execute(
            "INSERT INTO messages (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, role, content, json.dumps(metadata or {}))
        )
        return result is not None
    
    def get_messages(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get messages for a session."""
        result = self.db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at LIMIT ?",
            (session_id, limit)
        )
        if result:
            for msg in result:
                msg['metadata'] = json.loads(msg['metadata'])
        return result or []
    
    def search_messages(self, query: str, limit: int = 50) -> List[Dict]:
        """Search messages by content."""
        result = self.db.execute(
            "SELECT * FROM messages WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f'%{query}%', limit)
        )
        return result or []


# Export classes
__all__ = [
    'DatabaseConnection',
    'ModelDatabase',
    'ConversationDatabase',
]
