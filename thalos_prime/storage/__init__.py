"""
THALOS Prime - Storage Module

Provides persistent storage for models, experiences, and knowledge.

Components:
    - ModelManager: Checkpoint management
    - ExperienceDatabase: Interaction logging
    - KnowledgeBase: Knowledge graph storage

Author: THALOS Prime Development Team
License: MIT
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime


class ModelManager:
    """
    Manages model checkpoints with versioning and metadata.
    
    Features:
        - Automatic checkpoint versioning
        - Metadata tracking (loss, accuracy, etc.)
        - Best model selection
        - Checkpoint cleanup
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """
        Initialize model manager.
        
        Args:
            checkpoint_dir: Directory for storing checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.checkpoint_dir / "metadata.json"
        self.metadata: Dict[str, Any] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load checkpoint metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {'checkpoints': [], 'best_checkpoint': None}
    
    def _save_metadata(self):
        """Save checkpoint metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_checkpoint(self, name: str, state: Dict[str, Any], metrics: Optional[Dict[str, float]] = None) -> bool:
        """
        Save a model checkpoint.
        
        Args:
            name: Checkpoint name
            state: Model state dictionary
            metrics: Optional performance metrics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            checkpoint_path = self.checkpoint_dir / f"{name}.json"
            
            checkpoint_data = {
                'name': name,
                'state': state,
                'metrics': metrics or {},
                'timestamp': datetime.now().isoformat()
            }
            
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.metadata['checkpoints'].append({
                'name': name,
                'path': str(checkpoint_path),
                'metrics': metrics or {},
                'timestamp': checkpoint_data['timestamp']
            })
            
            if metrics and 'loss' in metrics:
                if not self.metadata['best_checkpoint'] or metrics['loss'] < self.metadata.get('best_loss', float('inf')):
                    self.metadata['best_checkpoint'] = name
                    self.metadata['best_loss'] = metrics['loss']
            
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"Failed to save checkpoint: {e}")
            return False
    
    def load_checkpoint(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a model checkpoint.
        
        Args:
            name: Checkpoint name
            
        Returns:
            Checkpoint data or None if not found
        """
        try:
            checkpoint_path = self.checkpoint_dir / f"{name}.json"
            
            if not checkpoint_path.exists():
                return None
            
            with open(checkpoint_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Failed to load checkpoint: {e}")
            return None
    
    def get_best_checkpoint(self) -> Optional[str]:
        """Get name of best checkpoint by metrics."""
        return self.metadata.get('best_checkpoint')
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        return self.metadata.get('checkpoints', [])


class ExperienceDatabase:
    """
    Logs and retrieves conversation interactions for learning.
    
    Features:
        - Query-response pair logging
        - Context tracking
        - Feedback recording
        - Experience replay
    """
    
    def __init__(self, db_path: str = "experience.db"):
        """
        Initialize experience database.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                confidence REAL,
                feedback INTEGER,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                experience_id INTEGER,
                sequence_num INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (experience_id) REFERENCES experiences(id)
            )
        """)
        
        self.conn.commit()
    
    def log_experience(self, query: str, response: str, context: Optional[List[str]] = None, 
                       confidence: float = 0.0) -> int:
        """
        Log a query-response interaction.
        
        Args:
            query: User query
            response: System response
            context: Conversation context
            confidence: Response confidence score
            
        Returns:
            Experience ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO experiences (query, response, context, confidence, feedback, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            query,
            response,
            json.dumps(context or []),
            confidence,
            0,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_feedback(self, experience_id: int, feedback: int):
        """
        Add user feedback to an experience.
        
        Args:
            experience_id: Experience ID
            feedback: Feedback score (-1, 0, 1)
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE experiences SET feedback = ? WHERE id = ?", (feedback, experience_id))
        self.conn.commit()
    
    def get_experiences(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent experiences.
        
        Args:
            limit: Maximum number of experiences to return
            
        Returns:
            List of experience dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, query, response, context, confidence, feedback, timestamp
            FROM experiences
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        experiences = []
        for row in cursor.fetchall():
            experiences.append({
                'id': row[0],
                'query': row[1],
                'response': row[2],
                'context': json.loads(row[3]) if row[3] else [],
                'confidence': row[4],
                'feedback': row[5],
                'timestamp': row[6]
            })
        
        return experiences
    
    def close(self):
        """Close database connection."""
        self.conn.close()


class KnowledgeBase:
    """
    Persistent knowledge storage with semantic organization.
    
    Features:
        - Fact storage and retrieval
        - Semantic indexing
        - Knowledge graph construction
        - Query-based search
    """
    
    def __init__(self, db_path: str = "knowledge.db"):
        """
        Initialize knowledge base.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT,
                properties TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def add_fact(self, subject: str, predicate: str, obj: str, confidence: float = 1.0, source: str = "system"):
        """
        Add a fact to the knowledge base.
        
        Args:
            subject: Fact subject
            predicate: Fact relation
            obj: Fact object
            confidence: Confidence score
            source: Fact source
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO facts (subject, predicate, object, confidence, source, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (subject, predicate, obj, confidence, source, datetime.now().isoformat()))
        self.conn.commit()
    
    def query_facts(self, subject: Optional[str] = None, predicate: Optional[str] = None, 
                    obj: Optional[str] = None) -> List[Tuple[str, str, str, float]]:
        """
        Query facts by subject, predicate, or object.
        
        Args:
            subject: Optional subject filter
            predicate: Optional predicate filter
            obj: Optional object filter
            
        Returns:
            List of (subject, predicate, object, confidence) tuples
        """
        cursor = self.conn.cursor()
        
        query = "SELECT subject, predicate, object, confidence FROM facts WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate)
        if obj:
            query += " AND object = ?"
            params.append(obj)
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Close database connection."""
        self.conn.close()


__all__ = ['ModelManager', 'ExperienceDatabase', 'KnowledgeBase']
__version__ = '1.0.0'
