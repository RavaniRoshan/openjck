---
title: How It Works
description: Architecture and internals of OpenJCK.
---

# How It Works

## Architecture

<svg width="900" height="520" viewBox="0 0 900 520" xmlns="http://www.w3.org/2000/svg">
  <style>
    .label{fill:white;font-family:Arial, Helvetica, sans-serif;font-size:16px;text-anchor:middle;dominant-baseline:middle;}
    .small{font-size:13px;fill:#eef2ff}
    .arrow{stroke:#64748b;stroke-width:2.5;marker-end:url(#arrow)}
  </style>

  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
      <polygon points="0 0, 10 5, 0 10" fill="#64748b" />
    </marker>
    <linearGradient id="grad1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#4f46e5"/>
    </linearGradient>
  </defs>

  <rect x="300" y="20" width="300" height="65" rx="18" fill="url(#grad1)" />
  <text class="label" x="450" y="48">Your Agent Code</text>
  <text class="label small" x="450" y="68">@trace / @trace_llm / @trace_tool</text>

  <line class="arrow" x1="450" y1="85" x2="450" y2="120" />

  <rect x="260" y="120" width="380" height="70" rx="35" fill="#0ea5e9" />
  <text class="label" x="450" y="155">TraceCollector</text>
  <text class="label small" x="450" y="175">in-memory · per-thread (threading.local)</text>

  <line class="arrow" x1="450" y1="190" x2="450" y2="230" />

  <rect x="240" y="230" width="420" height="70" rx="10" fill="#10b981" stroke="#065f46" stroke-width="2" stroke-dasharray="8 6" />
  <text class="label" x="450" y="265">~/.openjck/traces/</text>
  <text class="label small" x="450" y="285">one JSON file per run · local only</text>

  <line class="arrow" x1="450" y1="300" x2="450" y2="340" />

  <g>
    <rect x="255" y="345" width="390" height="20" rx="6" fill="#f59e0b" />
    <rect x="250" y="360" width="400" height="50" rx="8" fill="#fbbf24" />
  </g>
  <text class="label" x="450" y="382">Express Server</text>
  <text class="label small" x="450" y="400">localhost:7823 · npx openjck</text>

  <line class="arrow" x1="450" y1="410" x2="450" y2="450" />

  <rect x="300" y="450" width="300" height="60" rx="14" fill="#ec4899" />
  <text class="label" x="450" y="480">Web UI</text>
  <text class="label small" x="450" y="500">timeline · step inspector · token counts</text>
</svg>

## The Agent Loop

OpenJCK instruments the classic agent loop: **think → tool → observe → think**. Each decorator fires at a specific point:

- `@trace`: Wraps the entire agent execution, capturing overall metrics and status
- `@trace_llm`: Fires before and after each LLM call to capture prompts, responses, and token usage
- `@trace_tool`: Wraps tool/function invocations to record arguments, return values, and execution time

In the think→tool→observe cycle:
1. **Think phase**: `@trace_llm` captures the LLM call that produces the next action
2. **Tool phase**: `@trace_tool` captures the execution of the selected tool
3. **Observe phase**: `@trace_llm` captures the LLM call that interprets the tool result

## Trace JSON Schema

Each trace is saved as a JSON file in `~/.openjck/traces/<trace_id>.json` with this structure:

```json
{
  "trace_id": "a3f9c1b2",
  "run_name": "research_agent",
  "started_at": "2026-03-12T10:00:00Z",
  "status": "completed",           // completed | failed | running
  "total_duration_ms": 4200,
  "total_tokens": 2840,
  "total_cost_usd": 0.0042,
  "error": null,
  "steps": [
    {
      "step_id": 1,
      "type": "llm_call",          // llm_call | tool_call | agent_step
      "name": "call_llm",
      "duration_ms": 1100,
      "input": { "messages": [{"role": "user", "content": "What is the capital of France?"}] },
      "output": { "content": "The capital of France is Paris." },
      "error": null,
      "tokens_in": 420,
      "tokens_out": 89,
      "model": "qwen2.5:7b",
      "cost_usd": 0.0012
    }
  ]
}
```

## Thread Safety

OpenJCK uses `threading.local()` to ensure each thread maintains its own independent trace collector. This makes it safe for concurrent agents running in the same process without interference between traces.

## Performance

The decorators add minimal overhead:
- `<1ms` per decorated function call
- Memory usage scales linearly with trace size (typically <1MB per run)
- JSON serialization happens asynchronously after trace completion
