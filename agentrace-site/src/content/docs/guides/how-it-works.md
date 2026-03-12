---
title: How It Works
description: Architecture and internals of AgentTrace.
---

# How It Works

## Architecture

```text
Your Agent Code
       │
       │  @trace / @trace_llm / @trace_tool
       ▼
TraceCollector        in-memory, per-thread (threading.local)
       │
       ▼
~/.agentrace/traces/  one JSON file per run, local only
       │
       ▼
Express server        localhost:7823  (npx @ravaniroshan/agentrace)
       │
       ▼
Web UI                timeline · step inspector · token counts
```

## The Agent Loop

AgentTrace instruments the classic agent loop: **think → tool → observe → think**. Each decorator fires at a specific point:

- `@trace`: Wraps the entire agent execution, capturing overall metrics and status
- `@trace_llm`: Fires before and after each LLM call to capture prompts, responses, and token usage
- `@trace_tool`: Wraps tool/function invocations to record arguments, return values, and execution time

In the think→tool→observe cycle:
1. **Think phase**: `@trace_llm` captures the LLM call that produces the next action
2. **Tool phase**: `@trace_tool` captures the execution of the selected tool
3. **Observe phase**: `@trace_llm` captures the LLM call that interprets the tool result

## Trace JSON Schema

Each trace is saved as a JSON file in `~/.agentrace/traces/<trace_id>.json` with this structure:

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

AgentTrace uses `threading.local()` to ensure each thread maintains its own independent trace collector. This makes it safe for concurrent agents running in the same process without interference between traces.

## Performance

The decorators add minimal overhead:
- `<1ms` per decorated function call
- Memory usage scales linearly with trace size (typically <1MB per run)
- JSON serialization happens asynchronously after trace completion