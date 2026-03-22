---
title: Quick Start
description: Get OpenJCK running in 5 minutes.
---

# Quick Start

## Prerequisites
- Python 3.10+
- Node.js 18+ (for the viewer)
- An agent to debug (or use the example below)

## Install
```bash
pip install openjck
```

## Instrument your agent — show full working Ollama example:
```python
from openjck import trace, trace_llm, trace_tool
import ollama

@trace(name="my_first_agent")
def run_agent(task: str):
    messages = [{"role": "user", "content": task}]
    response = call_llm(messages)
    result = process_result(response.message.content)
    return result

@trace_llm
def call_llm(messages):
    return ollama.chat(model="qwen2.5:7b", messages=messages)

@trace_tool
def process_result(text: str) -> str:
    return text.strip().upper()

if __name__ == "__main__":
    run_agent("What is the capital of France?")
```

## What you see in the terminal after running:
```
[OpenJCK] Run complete → COMPLETED
[OpenJCK] 3 steps  |  180 tokens  |  1.2s
[OpenJCK] View trace → http://localhost:7823/trace/a3f9c1b2
```

## Open the viewer:
```bash
npx openjck
```

## What the UI shows:
The OpenJCK UI displays:
- **Timeline**: Clickable visualization of each step your agent took
- **Step Inspector**: Click any step to see detailed information including inputs, outputs, and timing
- **Token Counts**: Exact token usage per LLM call with cost calculations
- **Error Highlighting**: Failed steps are highlighted in red with clickable tracebacks

## Next steps links:
- [How It Works](/guides/how-it-works/) - Deep dive into OpenJCK architecture
- [LangChain Integration](/integrations/langchain/) - Using OpenJCK with LangChain
- [CLI Reference](/reference/cli/) - All OpenJCK CLI commands