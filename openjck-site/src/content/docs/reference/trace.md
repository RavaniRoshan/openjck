---
title: "@trace"
description: The @trace decorator reference.
---

# @trace

## Full Signature
```python
@trace(name=None, metadata=None, auto_open=True)
```

## Parameter Table
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Run name displayed in the UI timeline |
| `metadata` | `dict` | `None` | Arbitrary data attached to the trace JSON |
| `auto_open` | `bool` | `True` | Whether to automatically start the UI server on trace completion |

## Usage Examples

### Bare decorator
```python
from openjck import trace

@trace
def my_agent():
    # agent logic here
    pass
```

### With custom name
```python
from openjck import trace

@trace(name="research_agent")
def research_agent(task):
    # agent logic here
    pass
```

### With metadata
```python
from openjck import trace

@trace(
    name="customer_support_bot",
    metadata={"version": "1.2.0", "user_id": "user_123"}
)
def support_agent(query):
    # agent logic here
    pass
```

### Async function support
```python
from openjck import trace
import asyncio

@trace(name="async_agent")
async def async_agent(task):
    # async agent logic here
    pass
```

## What Gets Captured
The `@trace` decorator captures:
- Run name (from `name` parameter or function name)
- All steps executed within the decorated function
- Total token count and estimated cost
- Overall duration and status (completed/failed)
- Any uncaught exceptions that occur during execution

## Output File
Traces are saved as JSON files in `~/.openjck/traces/<trace_id>.json` where `<trace_id>` is a unique identifier for each run.

## Terminal Output Format
When a traced function completes, OpenJCK prints a summary to the terminal:
```
[OpenJCK] Run complete → COMPLETED
[OpenJCK] 3 steps  |  180 tokens  |  1.2s
[OpenJCK] View trace → http://localhost:7823/trace/a3f9c1b2
```