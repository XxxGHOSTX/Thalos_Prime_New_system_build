# THALOS Prime Application

## Overview

The THALOS Prime application provides a web API for the THALOS Prime system.

## Endpoints

- `/` - Index/status
- `/api/query` - Process queries
- `/api/status` - System status
- `/api/health` - Health check

## Running

```bash
python app.py --host 127.0.0.1 --port 5000
```

## Example

```python
from app import create_app

app = create_app()
result = app.handle_request('/api/query', {'query': 'Hello'})
```
