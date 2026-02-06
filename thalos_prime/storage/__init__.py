"""
THALOS Prime - Storage Module
Model checkpoints, experience database, and knowledge persistence.
"""

from typing import Dict, Any, Optional, List
import json
import os
import time


class ModelManager:
    """Manage model checkpoints and states."""
    
    def __init__(self, checkpoint_dir: str = './checkpoints'):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(self, model_state: Dict[str, Any], 
                        optimizer_state: Optional[Dict] = None,
                        epoch: int = 0, step: int = 0,
                        metadata: Optional[Dict] = None) -> str:
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'step': step,
            'model_state': model_state,
            'optimizer_state': optimizer_state,
            'metadata': metadata or {},
            'timestamp': time.time(),
        }
        
        filename = f"checkpoint_epoch{epoch}_step{step}.json"
        path = os.path.join(self.checkpoint_dir, filename)
        
        # Convert tensors to lists for JSON serialization
        serializable = self._make_serializable(checkpoint)
        
        with open(path, 'w') as f:
            json.dump(serializable, f)
        
        return path
    
    def load_checkpoint(self, path: str) -> Dict[str, Any]:
        """Load model checkpoint."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def list_checkpoints(self) -> List[str]:
        """List available checkpoints."""
        if not os.path.exists(self.checkpoint_dir):
            return []
        return [f for f in os.listdir(self.checkpoint_dir) 
                if f.startswith('checkpoint_')]
    
    def get_latest_checkpoint(self) -> Optional[str]:
        """Get path to latest checkpoint."""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            return None
        
        # Sort by modification time
        paths = [os.path.join(self.checkpoint_dir, f) for f in checkpoints]
        paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return paths[0]
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if hasattr(obj, 'data'):  # Tensor-like
            return {'_type': 'tensor', 'data': obj.data, 'shape': obj.shape.dims}
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(v) for v in obj]
        return obj


class ExperienceDatabase:
    """Store and retrieve interaction experiences."""
    
    def __init__(self, db_path: str = './experience.json'):
        self.db_path = db_path
        self.experiences: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self) -> None:
        """Load experiences from file."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.experiences = json.load(f)
    
    def _save(self) -> None:
        """Save experiences to file."""
        with open(self.db_path, 'w') as f:
            json.dump(self.experiences, f, indent=2)
    
    def add_experience(self, input_text: str, response: str,
                       feedback: Optional[float] = None,
                       metadata: Optional[Dict] = None) -> None:
        """Add a new experience."""
        experience = {
            'id': len(self.experiences),
            'input': input_text,
            'response': response,
            'feedback': feedback,
            'metadata': metadata or {},
            'timestamp': time.time(),
        }
        self.experiences.append(experience)
        self._save()
    
    def get_experience(self, experience_id: int) -> Optional[Dict[str, Any]]:
        """Get experience by ID."""
        for exp in self.experiences:
            if exp.get('id') == experience_id:
                return exp
        return None
    
    def search_experiences(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search experiences by input text."""
        query_lower = query.lower()
        matching = []
        
        for exp in self.experiences:
            if query_lower in exp['input'].lower():
                matching.append(exp)
        
        # Sort by relevance (simple matching for now)
        matching.sort(key=lambda x: -x.get('feedback', 0) if x.get('feedback') else 0)
        return matching[:limit]
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent experiences."""
        return self.experiences[-limit:]
    
    def update_feedback(self, experience_id: int, feedback: float) -> bool:
        """Update feedback for an experience."""
        for exp in self.experiences:
            if exp.get('id') == experience_id:
                exp['feedback'] = feedback
                self._save()
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        feedbacks = [e.get('feedback', 0) for e in self.experiences if e.get('feedback')]
        return {
            'total_experiences': len(self.experiences),
            'with_feedback': len(feedbacks),
            'avg_feedback': sum(feedbacks) / len(feedbacks) if feedbacks else 0,
        }


class KnowledgeBase:
    """Persistent knowledge storage."""
    
    def __init__(self, kb_path: str = './knowledge.json'):
        self.kb_path = kb_path
        self.knowledge: Dict[str, Any] = {
            'facts': {},
            'concepts': {},
            'relations': [],
        }
        self._load()
    
    def _load(self) -> None:
        """Load knowledge from file."""
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r') as f:
                self.knowledge = json.load(f)
    
    def _save(self) -> None:
        """Save knowledge to file."""
        with open(self.kb_path, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def add_fact(self, key: str, value: Any, source: Optional[str] = None) -> None:
        """Add a fact to knowledge base."""
        self.knowledge['facts'][key] = {
            'value': value,
            'source': source,
            'added': time.time(),
        }
        self._save()
    
    def get_fact(self, key: str) -> Optional[Any]:
        """Get a fact from knowledge base."""
        fact = self.knowledge['facts'].get(key)
        return fact['value'] if fact else None
    
    def add_concept(self, name: str, definition: str, 
                    related: Optional[List[str]] = None) -> None:
        """Add a concept to knowledge base."""
        self.knowledge['concepts'][name] = {
            'definition': definition,
            'related': related or [],
            'added': time.time(),
        }
        self._save()
    
    def get_concept(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a concept from knowledge base."""
        return self.knowledge['concepts'].get(name)
    
    def add_relation(self, subject: str, relation: str, object_: str) -> None:
        """Add a relation between concepts."""
        self.knowledge['relations'].append({
            'subject': subject,
            'relation': relation,
            'object': object_,
            'added': time.time(),
        })
        self._save()
    
    def query_relations(self, subject: Optional[str] = None,
                        relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query relations."""
        results = []
        for rel in self.knowledge['relations']:
            if subject and rel['subject'] != subject:
                continue
            if relation and rel['relation'] != relation:
                continue
            results.append(rel)
        return results
    
    def search(self, query: str) -> Dict[str, Any]:
        """Search knowledge base."""
        query_lower = query.lower()
        
        matching_facts = {k: v for k, v in self.knowledge['facts'].items()
                         if query_lower in k.lower()}
        matching_concepts = {k: v for k, v in self.knowledge['concepts'].items()
                            if query_lower in k.lower() or 
                            query_lower in v.get('definition', '').lower()}
        
        return {
            'facts': matching_facts,
            'concepts': matching_concepts,
        }


# Export classes
__all__ = [
    'ModelManager',
    'ExperienceDatabase',
    'KnowledgeBase',
]
