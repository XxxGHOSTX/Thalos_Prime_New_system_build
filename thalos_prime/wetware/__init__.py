"""
THALOS Prime - Wetware Module
Biological-inspired computing and neural interface simulations.
"""

from typing import Dict, Any, Optional, List, Callable
import math
import random


class NeuralPattern:
    """Represents a neural activation pattern."""
    
    def __init__(self, size: int = 100):
        self.size = size
        self.activations = [0.0] * size
        self.connections: Dict[int, List[tuple]] = {}  # neuron -> [(target, weight)]
    
    def activate(self, neuron_id: int, strength: float = 1.0) -> None:
        """Activate a neuron."""
        if 0 <= neuron_id < self.size:
            self.activations[neuron_id] = min(1.0, self.activations[neuron_id] + strength)
    
    def propagate(self) -> None:
        """Propagate activations through connections."""
        new_activations = self.activations.copy()
        
        for source, targets in self.connections.items():
            if self.activations[source] > 0.1:  # Threshold
                for target, weight in targets:
                    if 0 <= target < self.size:
                        new_activations[target] += self.activations[source] * weight
        
        # Apply activation function (tanh) and decay
        self.activations = [math.tanh(a) * 0.9 for a in new_activations]
    
    def add_connection(self, source: int, target: int, weight: float = 0.5) -> None:
        """Add a connection between neurons."""
        if source not in self.connections:
            self.connections[source] = []
        self.connections[source].append((target, weight))
    
    def get_active_neurons(self, threshold: float = 0.5) -> List[int]:
        """Get list of active neurons above threshold."""
        return [i for i, a in enumerate(self.activations) if a > threshold]
    
    def reset(self) -> None:
        """Reset all activations."""
        self.activations = [0.0] * self.size


class MemoryCell:
    """Simulates a biological memory cell."""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.memories: Dict[str, Dict] = {}
        self.access_counts: Dict[str, int] = {}
        self.creation_times: Dict[str, float] = {}
    
    def store(self, key: str, value: Any, importance: float = 0.5) -> bool:
        """Store a memory."""
        import time
        
        if len(self.memories) >= self.capacity:
            self._consolidate()
        
        self.memories[key] = {
            'value': value,
            'importance': importance,
            'strength': 1.0
        }
        self.access_counts[key] = 0
        self.creation_times[key] = time.time()
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory."""
        if key in self.memories:
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
            # Strengthen memory on access
            self.memories[key]['strength'] = min(
                1.0, self.memories[key]['strength'] + 0.1
            )
            return self.memories[key]['value']
        return None
    
    def forget(self, key: str) -> bool:
        """Forget a memory."""
        if key in self.memories:
            del self.memories[key]
            del self.access_counts[key]
            del self.creation_times[key]
            return True
        return False
    
    def _consolidate(self) -> None:
        """Consolidate memories, forgetting weak ones."""
        # Calculate memory scores
        scores = {}
        for key in self.memories:
            mem = self.memories[key]
            access = self.access_counts.get(key, 0)
            scores[key] = mem['importance'] * mem['strength'] * (1 + access * 0.1)
        
        # Remove lowest scoring memories
        to_remove = sorted(scores.keys(), key=lambda k: scores[k])[:len(self.memories) // 4]
        for key in to_remove:
            self.forget(key)
    
    def decay(self, rate: float = 0.01) -> None:
        """Apply memory decay."""
        for key in list(self.memories.keys()):
            self.memories[key]['strength'] -= rate
            if self.memories[key]['strength'] <= 0:
                self.forget(key)


class SynapticNetwork:
    """Simulates a network of synaptic connections."""
    
    def __init__(self, num_neurons: int = 1000):
        self.num_neurons = num_neurons
        self.synapses: Dict[tuple, float] = {}  # (pre, post) -> weight
        self.neurotransmitters = {
            'dopamine': 0.5,
            'serotonin': 0.5,
            'acetylcholine': 0.5,
            'gaba': 0.5
        }
    
    def create_synapse(self, pre: int, post: int, weight: float = 0.5) -> None:
        """Create a synapse between neurons."""
        self.synapses[(pre, post)] = weight
    
    def fire(self, neuron: int, strength: float = 1.0) -> Dict[int, float]:
        """Fire a neuron and return downstream activations."""
        activations = {}
        
        for (pre, post), weight in self.synapses.items():
            if pre == neuron:
                # Modulate by neurotransmitters
                modulation = (
                    self.neurotransmitters['dopamine'] * 0.3 +
                    self.neurotransmitters['acetylcholine'] * 0.3 +
                    (1 - self.neurotransmitters['gaba']) * 0.4
                )
                activations[post] = strength * weight * modulation
        
        return activations
    
    def long_term_potentiation(self, pre: int, post: int, amount: float = 0.1) -> None:
        """Strengthen a synapse (learning)."""
        if (pre, post) in self.synapses:
            self.synapses[(pre, post)] = min(1.0, self.synapses[(pre, post)] + amount)
    
    def long_term_depression(self, pre: int, post: int, amount: float = 0.1) -> None:
        """Weaken a synapse (forgetting)."""
        if (pre, post) in self.synapses:
            self.synapses[(pre, post)] = max(0.0, self.synapses[(pre, post)] - amount)
    
    def release_neurotransmitter(self, nt: str, amount: float) -> None:
        """Release a neurotransmitter."""
        if nt in self.neurotransmitters:
            self.neurotransmitters[nt] = min(1.0, max(0.0, 
                self.neurotransmitters[nt] + amount))
    
    def reuptake(self, rate: float = 0.1) -> None:
        """Simulate neurotransmitter reuptake (return to baseline)."""
        for nt in self.neurotransmitters:
            diff = 0.5 - self.neurotransmitters[nt]
            self.neurotransmitters[nt] += diff * rate


class ConsciousnessSimulator:
    """Simulate aspects of conscious awareness."""
    
    def __init__(self):
        self.attention_focus: Optional[str] = None
        self.awareness_level = 0.5
        self.emotional_state = 'neutral'
        self.thoughts: List[str] = []
        self.working_memory: List[Any] = []
        self.max_working_memory = 7
    
    def focus_attention(self, target: str) -> None:
        """Focus attention on a target."""
        self.attention_focus = target
        self.awareness_level = min(1.0, self.awareness_level + 0.2)
    
    def process_stimulus(self, stimulus: Any) -> Dict[str, Any]:
        """Process an incoming stimulus."""
        response = {
            'perceived': True,
            'attention_captured': False,
            'emotional_impact': 'neutral'
        }
        
        # Add to working memory
        if len(self.working_memory) >= self.max_working_memory:
            self.working_memory.pop(0)
        self.working_memory.append(stimulus)
        
        # Determine if attention is captured
        if random.random() < self.awareness_level:
            response['attention_captured'] = True
            self.attention_focus = str(stimulus)
        
        return response
    
    def generate_thought(self) -> str:
        """Generate a thought based on current state."""
        templates = [
            f"Currently focused on {self.attention_focus}",
            f"Feeling {self.emotional_state}",
            f"Awareness level: {self.awareness_level:.2f}",
            f"Working memory contains {len(self.working_memory)} items"
        ]
        
        thought = random.choice(templates)
        self.thoughts.append(thought)
        return thought
    
    def set_emotional_state(self, state: str) -> None:
        """Set emotional state."""
        valid_states = ['happy', 'sad', 'angry', 'fearful', 'surprised', 'neutral']
        if state in valid_states:
            self.emotional_state = state
    
    def get_state(self) -> Dict[str, Any]:
        """Get current consciousness state."""
        return {
            'attention_focus': self.attention_focus,
            'awareness_level': self.awareness_level,
            'emotional_state': self.emotional_state,
            'working_memory_usage': f"{len(self.working_memory)}/{self.max_working_memory}",
            'recent_thoughts': self.thoughts[-5:]
        }


class BiofeedbackSystem:
    """Simulate biofeedback mechanisms."""
    
    def __init__(self):
        self.heart_rate = 70.0
        self.stress_level = 0.3
        self.energy_level = 0.7
        self.alertness = 0.6
        
        self.baseline = {
            'heart_rate': 70.0,
            'stress_level': 0.3,
            'energy_level': 0.7,
            'alertness': 0.6
        }
    
    def update(self, stimulus_intensity: float = 0.0) -> Dict[str, float]:
        """Update biofeedback based on stimulus."""
        # Respond to stimulus
        if stimulus_intensity > 0.5:
            self.heart_rate += stimulus_intensity * 10
            self.stress_level += stimulus_intensity * 0.1
            self.alertness += stimulus_intensity * 0.1
        
        # Natural regulation (return to baseline)
        for attr in ['heart_rate', 'stress_level', 'energy_level', 'alertness']:
            current = getattr(self, attr)
            baseline = self.baseline[attr]
            setattr(self, attr, current + (baseline - current) * 0.1)
        
        # Clamp values
        self.heart_rate = max(50, min(180, self.heart_rate))
        self.stress_level = max(0, min(1, self.stress_level))
        self.energy_level = max(0, min(1, self.energy_level))
        self.alertness = max(0, min(1, self.alertness))
        
        return self.get_state()
    
    def get_state(self) -> Dict[str, float]:
        """Get current biofeedback state."""
        return {
            'heart_rate': round(self.heart_rate, 1),
            'stress_level': round(self.stress_level, 2),
            'energy_level': round(self.energy_level, 2),
            'alertness': round(self.alertness, 2)
        }


# Export classes
__all__ = [
    'NeuralPattern',
    'MemoryCell',
    'SynapticNetwork',
    'ConsciousnessSimulator',
    'BiofeedbackSystem',
]
