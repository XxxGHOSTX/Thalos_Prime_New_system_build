# THALOS Prime Modules - Quick Start Guide

## Overview

THALOS Prime now includes 6 fully-implemented core modules for AI system orchestration.

## Module Summary

| Module | Lines | Purpose |
|--------|-------|---------|
| **core** | 553 | Main orchestration engine |
| **config** | 253 | Configuration management |
| **storage** | 369 | Persistent storage |
| **inference** | 302 | Text generation |
| **utils** | 348 | Logging & profiling |
| **reasoning** | 1014+ | Semantic analysis |

## Quick Examples

### 1. Basic Usage

```python
from thalos_prime.core import THALOSPrimeEngine

# Create engine
engine = THALOSPrimeEngine()

# Initialize system
engine.initialize()

# Process a query
result = engine.process_query("What is THALOS Prime?")
print(result['response'])
print(f"Confidence: {result['confidence']}")
```

### 2. Interactive Mode

```python
from thalos_prime.core import THALOSPrimeEngine

engine = THALOSPrimeEngine()
engine.interactive_session()  # Start CLI
```

### 3. Configuration

```python
from thalos_prime.config import Settings

settings = Settings()
print(settings.get('model.vocab_size'))  # 10000
settings.set('model.vocab_size', 20000)
settings.save()
```

### 4. Storage

```python
from thalos_prime.storage import ModelManager, ExperienceDatabase

# Checkpoints
mgr = ModelManager()
mgr.save_checkpoint('model_v1', state_dict, {'loss': 0.5})

# Experience logging
db = ExperienceDatabase()
db.log_experience("query", "response", confidence=0.8)
```

### 5. Inference

```python
from thalos_prime.inference import InferencePipeline

pipeline = InferencePipeline()
text = pipeline.generate("Hello", max_length=50, temperature=0.7)
```

### 6. Utilities

```python
from thalos_prime.utils import Logger, Profiler

# Logging
logger = Logger(level="INFO")
logger.info("System started")

# Profiling
profiler = Profiler()
with profiler.profile("operation"):
    # your code here
    pass
stats = profiler.get_stats("operation")
```

## Command Line Interface

```bash
# Single query
python main.py --query "What is THALOS Prime?"

# Interactive session
python main.py --interactive

# Show version
python main.py --version

# Run tests
python main.py --test
```

## Architecture

```
THALOSPrimeEngine (Core)
    ├── QueryProcessor (Query analysis)
    ├── ResponseGenerator (Response generation)
    ├── SessionManager (Interactive sessions)
    │
    ├── Reasoning Module (SBI)
    ├── Encoding Module (Tokenization)
    ├── NN Module (Neural networks)
    ├── Storage Module (Persistence)
    ├── Config Module (Settings)
    └── Utils Module (Logging, profiling)
```

## Key Features

### Core Engine
- Unified system initialization
- Query processing pipeline
- Interactive CLI sessions
- State persistence
- Module integration

### Config
- Hierarchical JSON configuration
- Dot-notation key access
- Default values for all subsystems
- Save/load functionality

### Storage
- Model checkpoint versioning
- Experience database for learning
- Knowledge graph storage
- Automatic metadata tracking

### Inference
- Multiple sampling strategies
- KV caching for efficiency
- Batch generation
- Temperature control

### Utils
- Multi-level logging
- Performance profiling
- Input validation
- String sanitization

## API Reference

### THALOSPrimeEngine

```python
engine = THALOSPrimeEngine(config_path=None)

# Initialize
engine.initialize() -> bool

# Process query
result = engine.process_query(
    query: str,
    context: Optional[List[str]] = None
) -> Dict[str, Any]
# Returns: {'response': str, 'confidence': float, ...}

# Interactive session
engine.interactive_session()

# Get status
status = engine.get_status() -> Dict[str, Any]

# State persistence
engine.save_state(path: str) -> bool
engine.load_state(path: str) -> bool
```

## Integration Points

All modules integrate seamlessly:

1. **Core** orchestrates all other modules
2. **Config** provides settings to all modules
3. **Storage** persists data from all modules
4. **Inference** uses Reasoning + Encoding
5. **Utils** provides services to all modules
6. **Reasoning** uses Encoding for analysis

## Testing

All modules include comprehensive tests:

```bash
# Run module import tests
python -c "from thalos_prime.core import THALOSPrimeEngine; print('✓')"

# Run integration tests
python main.py --test

# Run custom tests
python -m pytest tests/ -v
```

## Next Steps

1. **Customize Configuration**: Edit config values in Settings
2. **Add Training**: Implement model training loops
3. **Extend Storage**: Add custom storage backends
4. **Enhance Reasoning**: Add domain-specific logic
5. **Build Applications**: Use THALOSPrimeEngine in your apps

## Support

For issues or questions:
- See MODULES_IMPLEMENTATION_REPORT.md for detailed documentation
- Check main.py for usage examples
- Review individual module docstrings

---

**Status**: ✅ All modules fully implemented and tested
**Version**: THALOS Prime 3.1.0
**Lines of Code**: 2,839 production lines
