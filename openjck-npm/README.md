# OpenJCK

Visual debugger for AI agent loops. Step-by-step. Locally. Zero config.

## Quick Start
```bash
npx openjck
```

Opens the trace viewer at http://localhost:7823

## Full Setup

Install the Python tracer in your agent project:
```bash
pip install openjck
```

Add decorators to your agent:
```python
from openjck import trace, trace_llm, trace_tool

@trace(name="my_agent")
def run_agent(task: str):
    ...

@trace_llm
def call_llm(messages):
    return ollama.chat(model="qwen2.5:7b", messages=messages)

@trace_tool
def web_search(query: str) -> str:
    ...
```

View traces from any terminal:
```bash
npx openjck
```

## Commands
```bash
npx openjck              # start UI viewer (default)
npx openjck ui           # start UI viewer
npx openjck traces       # list all traces in terminal
npx openjck clear        # delete all traces
npx openjck --version    # show version
npx openjck --help       # show help
```

## Global Install
```bash
npm install -g openjck
openjck ui
```

## How It Works

The Python library saves trace files to ~/.openjck/traces/
The npm CLI reads those same files and serves the web viewer.
No configuration needed between the two.

## Requirements
- Node.js 18+
- Python agent instrumented with pip install openjck

## License
MIT
