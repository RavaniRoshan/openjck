---
title: EventCapture
description: Manual instrumentation with EventCapture.
---

# EventCapture

## Full Signature
```python
EventCapture(event_type, name, input=None, model=None, metadata=None)
```

## Parameter Table
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `event_type` | `str` | (required) | Type of event: `"llm_call"`, `"tool_call"`, or `"agent_step"` |
| `name` | `str` | (required) | Display name for the event in the UI timeline |
| `input` | `any` | `None` | Input data to the function being traced |
| `model` | `str` | `None` | Model name (only relevant for llm_call events) |
| `metadata` | `dict` | `None` | Arbitrary data attached to the trace |

## Usage as Context Manager

```python
from openjck import EventCapture

# Manual instrumentation of a function
def my_function(arg1, arg2):
    with EventCapture("tool_call", "my_function", input={"arg1": arg1, "arg2": arg2}) as ctx:
        # Your function logic here
        result = some_operation(arg1, arg2)
        
        # Optionally set output fields
        ctx.output = result
        ctx.latency_ms = 150  # if you want to override auto-calculated latency
        
        return result
```

## Settable Fields Inside the Block
Inside the `with` block, you can set these attributes on the context object:

| Field | Type | Description |
|-------|------|-------------|
| `output` | any | The result/output of the function |
| `tokens_in` | int | Number of input tokens (for llm_call events) |
| `tokens_out` | int | Number of output tokens (for llm_call events) |
| `latency_ms` | int | Execution time in milliseconds |
| `cost_usd` | float | Estimated cost of the operation |
| `error` | str/null | Exception traceback if the function failed |

## Full Example with Database Query

```python
from openjck import EventCapture
import sqlite3

def get_user_data(user_id):
    with EventCapture("tool_call", "database_query", 
                     input={"user_id": user_id, "query": "SELECT * FROM users WHERE id = ?"}) as ctx:
        try:
            conn = sqlite3.connect('example.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            ctx.output = result
            # Optionally set latency if known
            # ctx.latency_ms = 45
            
            return result
        except Exception as e:
            ctx.error = str(e)
            raise  # Re-raise so normal error handling works
```

## When to Use Over Decorators
Use `EventCapture` instead of decorators when:

1. **Dynamic naming**: You need to determine the trace name at runtime
2. **Partial tracing**: You only want to trace specific sections within a function
3. **Async contexts**: When working with complex async flows that don't fit decorator patterns
4. **Library code**: When you can't modify function signatures but want to trace specific calls
5. **Hybrid approaches**: Combining automatic decorator tracing with manual instrumentation for specific cases

Example of dynamic naming:
```python
def process_items(items):
    results = []
    for i, item in enumerate(items):
        # Dynamic name based on loop iteration
        with EventCapture("tool_call", f"process_item_{i}", input={"item": item}) as ctx:
            result = process_single_item(item)
            ctx.output = result
            results.append(result)
    return results
```