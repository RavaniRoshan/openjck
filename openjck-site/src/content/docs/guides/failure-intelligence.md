---
title: Failure Intelligence
description: Automatic root cause analysis for failed agent runs.
---

When an agent run fails, OpenJCK automatically analyzes the trace to identify the root cause. No configuration required — it fires on every failed run.

## How It Works

The intelligence engine analyzes four aspects of every failure:

### 1. Root Cause Step

Identifies the earliest step whose output fed into the failure chain. This is the step that, if fixed, would prevent the failure.

**Example:**
- Step 1: LLM returns "Use file data/report_2026.csv"
- Step 2: Tool tries to read that file
- Step 3: FileNotFoundError

**Root cause:** Step 1 (the LLM generated a path to a non-existent file)

### 2. Root Cause Reason

Explains why the root cause step led to the failure:

```
Output from step 1 (call_llm) contained "data/report_2026.csv"
which was referenced by the failing step 3 (read_file).
Error: FileNotFoundError: data/report_2026.csv not found
```

### 3. Recovery Point

The last step with valid output before the failure chain began. This is where you could resume the run if implementing retry logic.

**Example:**
- Step 1: ✓ Valid output
- Step 2: ✓ Valid output  
- Step 3: ✗ Failed

**Recovery point:** Step 2

### 4. Dependency Chain

Lists all values passed between steps that appear in the failure context:

```
Step 1 → Step 3: "data/report_2026.csv"
Step 1 → Step 3: "2026"
```

This shows exactly which data flowed from the root cause to the failure.

## Viewing Intelligence

### In the Dashboard

Failed runs show an inline preview:

```
🔍 Root cause: Step 3 — File not found
[View Step 3 →]
```

Click "View Step N" to open the trace detail with the root cause step highlighted.

### In Trace Detail

Open any failed trace to see the full intelligence panel:

- **Root Cause**: Which step and why
- **Recovery Point**: Where to resume
- **Dependency Chain**: Full list of connected values

The root cause step is highlighted with an amber border and "Root Cause" badge in the step detail panel.

## Pattern Detection

The dashboard tracks recurring failures across multiple runs of the same agent:

- **Most common failure**: "Step X fails in N/M runs (P%)"
- **Most expensive step**: Which step costs the most on average

These patterns appear in the agent drill-down view.

## How It Detects Dependencies

The engine extracts values from each step's output that could be referenced later:

- File paths (e.g., `data/report.csv`)
- URLs (e.g., `https://api.example.com`)
- UUIDs
- Constant names (e.g., `MAX_RETRIES`)

It then checks if these values appear in the failing step's input or error message.

## Limitations

- Intelligence is computed **after** the run completes (not in real-time)
- Dependency detection works best with explicit file paths and IDs
- Complex data transformations between steps may not be captured
- Pattern detection requires at least 2 failed runs of the same agent

## Disabling Intelligence

Intelligence computation is automatic and lightweight. To skip it for a specific run:

```python
from openjck import trace

@trace(name="my_agent", compute_intelligence=False)
def run():
    pass
```

## Best Practices

1. **Name your steps clearly** — "fetch_user_data" is better than "step_3"
2. **Return explicit values** — return file paths as strings, not objects
3. **Check the intelligence panel first** when debugging failures
4. **Look for patterns** — recurring failures indicate systemic issues

## Example: Debugging a Failed Run

```python
from openjck import trace, trace_tool

@trace(name="research_agent")
def run():
    query = generate_query("AI safety")
    results = search_web(query)  # fails here
    return summarize(results)

@trace_tool
def generate_query(topic):
    return f"latest {topic} research 2026"

@trace_tool  
def search_web(query):
    # This fails because the query has no results
    return api.search(query)
```

**Intelligence output:**

```
Root cause: Step 1 (generate_query)
Reason: Output "latest AI safety research 2026" contained "2026"
which was used in the failing search query
Recovery point: Step 1
```

**Fix:** Update `generate_query` to use current year, not hardcoded 2026.

## Technical Details

The intelligence engine is pure Python with zero dependencies. It:

- Parses trace JSON files
- Uses regex to extract referenceable values
- Performs string matching to find dependencies
- Computes patterns across historical runs

Computation takes <100ms per trace and runs in a background thread.
