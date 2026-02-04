# THALOS SBI Standalone Architecture

## Overview

The SBI Standalone package provides independent modules for semantic behavioral integration.

## Components

### Core Engine
- Main processing pipeline
- Processor registration
- Result aggregation

### Code Generator
- Natural language to code
- Template-based generation
- Multiple language support

### Math Module
- Extended math operations
- Vector operations
- Statistical functions

### NLP Module
- Text preprocessing
- POS tagging
- Named entity recognition
- Sentiment analysis

## Usage

```python
from thalos_sbi_standalone.core_engine import SBICoreEngine

engine = SBICoreEngine()
result = engine.process({'text': 'Hello'})
```
