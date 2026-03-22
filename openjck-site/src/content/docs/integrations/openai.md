---
title: OpenAI
description: Using OpenJCK with OpenAI SDK.
---

# OpenAI Integration

## @trace_llm wrapping openai.chat.completions.create()
The primary integration point with OpenAI is tracing LLM calls using the `@trace_llm` decorator:

```python
from openjck import trace_llm
import openai

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key-here")

@trace_llm
def call_llm(messages):
    return client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
```

## Token Extraction from OpenAI Response
OpenJCK automatically extracts token usage from OpenAI's response.usage object:

- **Input tokens**: `response.usage.prompt_tokens`
- **Output tokens**: `response.usage.completion_tokens`
- **Model name**: Taken from the `model` parameter or response.model
- **Latency**: Measured from the duration of the API call
- **Cost**: Calculated based on OpenAI's pricing for the specific model

## Full Working Example with Cost Tracking

```python
from openjck import trace, trace_llm, trace_tool
import openai
import os

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Better: use environment variable
)

@trace(name="openai_agent")
def run_agent(task: str):
    messages = [{"role": "user", "content": task}]
    response = call_llm(messages)
    result = process_response(response.choices[0].message.content)
    return result

@trace_llm
def call_llm(messages):
    return client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

@trace_tool
def process_response(text: str) -> str:
    # Example tool that processes the LLM response
    return text.strip()

if __name__ == "__main__":
    # Make sure to set your OpenAI API key as an environment variable
    # export OPENAI_API_KEY="your-key-here"
    result = run_agent("What are the benefits of renewable energy?")
    print(result)
```

## Cost Tracking Example
OpenJCK calculates costs based on OpenAI's official pricing:

```python
# Example trace JSON showing cost calculation
{
  "step_id": 1,
  "type": "llm_call",
  "name": "call_llm",
  "duration_ms": 1450,
  "input": {
    "messages": [{"role": "user", "content": "What are the benefits of renewable energy?"}]
  },
  "output": {
    "content": "Renewable energy offers several key benefits..."
  },
  "error": null,
  "tokens_in": 25,
  "tokens_out": 128,
  "model": "gpt-3.5-turbo",
  "cost_usd": 0.0004  // Calculated: (25 * $0.0005 + 128 * $0.0015) / 1000
}
```

## Pricing Reference (as of 2026)
OpenJCK uses these rates for cost estimation:
- **gpt-3.5-turbo**: $0.0005 per 1K input tokens, $0.0015 per 1K output tokens
- **gpt-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **gpt-4-turbo**: $0.01 per 1K input tokens, $0.03 per 1K output tokens

## Note: Streaming Not Yet Supported
Currently, OpenJCK does not support tracing OpenAI streaming responses (`stream=True`). For streaming use cases:

1. **Collect full response first**: Disable streaming to get complete tracing
2. **Manual instrumentation**: Use `EventCapture` for custom tracing of streaming chunks
3. **Future support**: Streaming tracing is planned for a future release

Example workaround for streaming scenarios:
```python
from openjck import EventCapture
import openai

def call_llm_streaming(messages):
    # Collect streaming response into a single string for tracing
    full_response = ""
    
    with EventCapture("llm_call", "openai_stream", input={"messages": messages}) as ctx:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                # Optional: yield or process chunks in real-time
        
        # Set the collected output
        ctx.output = {"content": full_response}
        # Optionally set token counts if you have a way to estimate them
        # ctx.tokens_in = estimated_input_tokens
        # ctx.tokens_out = estimated_output_tokens
    
    # Return object that mimics OpenAI response structure
    class MockResponse:
        class MockChoice:
            class MockMessage:
                def __init__(self, content):
                    self.content = content
            def __init__(self, content):
                self.message = self.MockMessage(content)
        def __init__(self, content):
            self.choices = [self.MockChoice(content)]
    
    return MockResponse(full_response)
```

## Environment Setup
For secure API key management:

```bash
# Recommended: set environment variable
export OPENAI_APIKEY="your-actual-api-key-here"

# Or use a .env file with python-dotenv
# Create .env file:
# OPENAI_APIKEY="your-actual-api-key-here"
# Then in Python:
# from dotenv import load_dotenv
# load_dotenv()
# client = openai.OpenAI()
```

## Error Handling
When tracing OpenAI calls, OpenJCK captures:
- Authentication errors (invalid API key)
- Rate limit errors (HTTP 429)
- Invalid request errors (HTTP 400)
- Service unavailable errors (HTTP 503)

All captured errors appear in the trace JSON with full details, and failed steps are highlighted in red in the UI.