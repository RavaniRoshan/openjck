---
title: Ollama
description: Using AgentTrace with Ollama.
---

# Ollama Integration

## @trace_llm wrapping ollama.chat()
The primary integration point with Ollama is tracing LLM calls using the `@trace_llm` decorator:

```python
from agentrace import trace_llm
import ollama

@trace_llm
def call_llm(messages):
    return ollama.chat(model="qwen2.5:7b", messages=messages)
```

## Available Models
AgentTrace works with all Ollama models. Popular choices include:
- `qwen2.5-coder:7b` - Excellent for code generation and debugging
- `llama3.1:8b` - Strong general-purpose model
- `gemma3:4b` - Efficient and capable smaller model
- `mistral:7b` - Good balance of performance and quality
- `phi3:medium` - Microsoft's capable medium-sized model

## Full Example

```python
from agentrace import trace, trace_llm, trace_tool
import ollama

@trace(name="ollama_agent")
def run_agent(task: str):
    messages = [{"role": "user", "content": task}]
    response = call_llm(messages)
    result = process_response(response.message.content)
    return result

@trace_llm
def call_llm(messages):
    # You can specify any Ollama model here
    return ollama.chat(
        model="qwen2.5:7b",  # Change this to use different models
        messages=messages,
        options={"temperature": 0.7}  # Optional: adjust generation parameters
    )

@trace_tool
def process_response(text: str) -> str:
    # Example tool that processes the LLM response
    return text.strip()

if __name__ == "__main__":
    result = run_agent("Explain quantum computing in simple terms")
    print(result)
```

## Note on ollama.AsyncClient for async usage
For asynchronous applications, use the `ollama.AsyncClient` with async tracing:

```python
from agentrace import trace_llm
import ollama

# Initialize async client
async_client = ollama.AsyncClient()

@trace_llm
async def call_llm_async(messages):
    return await async_client.chat(
        model="qwen2.5:7b",
        messages=messages
    )

# Usage in async function
import asyncio

@trace(name="async_ollama_agent")
async def run_async_agent(task: str):
    messages = [{"role": "user", "content": task}]
    response = await call_llm_async(messages)
    return response.message.content

# Run the async agent
async def main():
    result = await run_async_agent("What is machine learning?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## How Token Extraction Works
When tracing Ollama calls, AgentTrace automatically extracts token usage from the response:

- **Input tokens**: `prompt_eval_count` from Ollama response
- **Output tokens**: `eval_count` from Ollama response
- **Model name**: Extracted from the model parameter or auto-detected
- **Latency**: Measured from the duration of the ollama.chat() call

Example of captured data in trace JSON:
```json
{
  "step_id": 1,
  "type": "llm_call",
  "name": "call_llm",
  "duration_ms": 1250,
  "input": {
    "messages": [{"role": "user", "content": "Explain quantum computing"}]
  },
  "output": {
    "content": "Quantum computing uses quantum bits..."
  },
  "error": null,
  "tokens_in": 145,
  "tokens_out": 320,
  "model": "qwen2.5:7b",
  "cost_usd": 0.0  // Ollama is free/local, so cost is 0
}
```

## Ollama Server Configuration
AgentTrace works with both local and remote Ollama instances:

### Local (default)
```python
ollama.chat(model="qwen2.5:7b", messages=messages)  # Uses localhost:11434
```

### Remote Server
```python
import os
os.environ["OLLAMA_HOST"] = "http://your-ollama-server:11434"
# or
client = ollama.Client(host="http://your-ollama-server:11434")
```

## Performance Tips
1. **Model warming**: Keep frequently used models loaded in Ollama memory
2. **Batch processing**: When possible, batch multiple prompts into fewer calls
3. **Temperature settings**: Lower temperatures (0.1-0.3) for faster, more deterministic responses
4. **Context management**: Be mindful of context window limits for your chosen model