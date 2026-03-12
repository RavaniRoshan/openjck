---
title: "@trace_tool"
description: The @trace_tool decorator reference.
---

# @trace_tool

## Full Signature
```python
@trace_tool(name=None)
```

## Parameter Table
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Display name for the tool in the UI timeline |

## Usage Examples

### Bare decorator
```python
from agentrace import trace_tool

@trace_tool
def web_search(query: str) -> str:
    # tool logic here
    return results
```

### With custom name
```python
from agentrace import trace_tool

@trace_tool(name="Google Search")
def web_search(query: str) -> str:
    # tool logic here
    return results
```

### Async function support
```python
from agentrace import trace_tool
import asyncio

@trace_tool
async def fetch_url(url: str) -> str:
    # async tool logic here
    return content
```

## Captured Fields
| Field | Type | Description |
|-------|------|-------------|
| `arguments` | dict | Parameters passed to the function |
| `return_value` | any | Value returned by the function |
| `duration_ms` | int | Execution time in milliseconds |
| `error` | str/null | Exception traceback if function failed |

## Error Handling
When a decorated tool function raises an exception:
- The exception is captured and stored in the `error` field
- The original exception is re-raised so your error handling still works
- The entire trace run is marked as "failed" in status
- Failed steps are highlighted in red in the UI timeline

## Example JSON Snippet
Here's how a `tool_call` step appears in the trace JSON:

```json
{
  "step_id": 2,
  "type": "tool_call",
  "name": "web_search",
  "duration_ms": 850,
  "input": {
    "arguments": {
      "query": "capital of France"
    }
  },
  "output": {
    "return_value": "Paris is the capital and most populous city of France."
  },
  "error": null
}
```