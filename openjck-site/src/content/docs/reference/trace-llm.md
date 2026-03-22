---
title: "@trace_llm"
description: The @trace_llm decorator reference.
---

# @trace_llm

## Full Signature
```python
@trace_llm(model=None)
```

## Parameter Table
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | `None` | Overrides auto-detected model name |

## Usage Examples

### Bare decorator
```python
from openjck import trace_llm

@trace_llm
def call_llm(messages):
    # LLM logic here
    pass
```

### Explicit model name
```python
from openjck import trace_llm

@trace_llm(model="qwen2.5:7b")
def call_llm(messages):
    # LLM logic here
    pass
```

### Async function support
```python
from openjck import trace_llm
import asyncio

@trace_llm
async def call_llm(messages):
    # async LLM logic here
    pass
```

## Captured Fields Table
| Field | Type | Description |
|-------|------|-------------|
| `messages` | list | Input messages to the LLM |
| `model` | str | Model name used for the call |
| `content` | str | Response content from the LLM |
| `tokens_in` | int | Number of input tokens |
| `tokens_out` | int | Number of output tokens |
| `latency_ms` | int | Call duration in milliseconds |
| `cost_usd` | float | Estimated cost of the call |

## Auto-detection Mechanism
OpenJCK automatically extracts token usage from various LLM providers:

- **Ollama**: Reads `prompt_eval_count` and `eval_count` from response
- **OpenAI**: Uses `usage.prompt_tokens` and `usage.completion_tokens`
- **Anthropic**: Reads `usage.input_tokens` and `usage.output_tokens`

If token information isn't available, OpenJCK estimates based on character count (4 chars ≈ 1 token).

## Example JSON Snippet
Here's how an `llm_call` step appears in the trace JSON:

```json
{
  "step_id": 1,
  "type": "llm_call",
  "name": "call_llm",
  "duration_ms": 1100,
  "input": {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ]
  },
  "output": {
    "content": "The capital of France is Paris."
  },
  "error": null,
  "tokens_in": 420,
  "tokens_out": 89,
  "model": "qwen2.5:7b",
  "cost_usd": 0.0012
}
```