<div align="center">

<img width="4190" height="919" alt="image" src="https://github.com/user-attachments/assets/b68531aa-03d8-489c-931c-e9aeee35dad0" />


<br />
<br />

[![npm](https://img.shields.io/npm/v/openjck?color=7c6af7&labelColor=1a1a1f&style=flat-square&label=npm)](https://www.npmjs.com/package/openjck)
[![PyPI](https://img.shields.io/pypi/v/openjck?color=3ecf8e&labelColor=1a1a1f&style=flat-square&label=pip)](https://pypi.org/project/openjck/)
[![Python](https://img.shields.io/pypi/pyversions/openjck?color=4da6ff&labelColor=1a1a1f&style=flat-square)](https://pypi.org/project/openjck/)
[![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-f5a623?labelColor=1a1a1f&style=flat-square)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-white?labelColor=1a1a1f&style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/RavaniRoshan/openjck?color=7c6af7&labelColor=1a1a1f&style=flat-square)](https://github.com/RavaniRoshan/openjck)

<br />

[**Quick Start**](#quick-start) · [**How It Works**](#how-it-works) · [**CLI Commands**](#cli-commands) · [**API Reference**](#api-reference) · [**Frameworks**](#framework-support) · [**Roadmap**](#roadmap)

<br />




</div>

---

## The Problem

You built an AI agent. It runs 15 steps. Something breaks at step 9.

You have no idea why.

The LLM got a bad prompt? A tool returned garbage? A file permission failed silently? You add `print()` everywhere. You re-run it. You grep through 300 lines of logs. Forty minutes later, you find the bug.

**This is the debugging dark age for AI agents.** No step-by-step visibility. No tool call inspector. No way to see what the LLM was actually thinking at each decision point.

OpenJCK fixes this.

---

## Quick Start

**Two packages. One shared purpose.**

```
pip install openjck              ← instruments your Python agent
npx openjck                      ← opens the visual trace viewer
```

**Step 1 — Instrument your agent** (add 3 decorators, nothing else changes):

```python
from openjck import trace, trace_llm, trace_tool
import ollama

@trace(name="research_agent")
def run_agent(task: str):
    response = call_llm([{"role": "user", "content": task}])
    results  = web_search(response.message.content)
    write_file("output.md", results)

@trace_llm
def call_llm(messages: list):
    return ollama.chat(model="qwen2.5:7b", messages=messages)

@trace_tool
def web_search(query: str) -> str:
    ...
```

**Step 2 — Run your agent normally:**

```
[OpenJCK] Run complete → COMPLETED
[OpenJCK] 8 steps  |  2840 tokens  |  4.2s
[OpenJCK] View trace → http://localhost:7823/trace/a3f9c1b2
```

**Step 3 — Open the viewer:**

```bash
npx openjck
```

You see this:

```
● ──── ● ──── ● ──── ● ──── ● ──── ● ──── ● ──── ✕
1      2      3      4      5      6      7      8
                                               ERROR ↑

  STEP 8   write_file   [FAILED]   12ms
  ─────────────────────────────────────────────────
  INPUT
    path:    "output.md"
    content: "# Research Summary..."

  ERROR
    PermissionError: cannot write to output.md
    File is open in another process

  ← Step 7: LLM decided to write the summary
  → Step 9:  never reached
```

Bug found. Fixed in 30 seconds.

## Dashboard

```bash
npx openjck
```

Open http://localhost:7823 to see:
- All agent runs — live as they happen
- Costs, success rate, avg duration at a glance
- Automatic root cause analysis on every failure
- Time filters: last 24h / 7 days / all time

### Failure Intelligence

When an agent run fails, OpenJCK automatically identifies the root cause:

- Which step made the run unrecoverable
- Why that step's output caused the downstream failure
- The last recovery point before the failure chain began
- Recurring failure patterns across multiple runs

No configuration. No API keys. Fires automatically on every failed run.

---

## How It Works

```
Your Agent Code
    │
    │  @trace / @trace_llm / @trace_tool  (3 decorators)
    ▼
TraceCollector              captures every event in-memory, per-thread
    │
    ▼
~/.openjck/traces/        one JSON file per run — never leaves your machine
    │
    ▼
Express server              localhost:7823  (Node.js · npx openjck)
    │
    ▼
Visual UI                   timeline + step inspector + token counts
```

**Everything is local.** No cloud. No accounts. No API keys. No data leaves your machine.

Both the Python library and the npm CLI read from the **same folder** — `~/.openjck/traces/`. Run your agent from Python, view traces from any terminal with `npx`. Zero config between them.

---

## CLI Commands

```bash
npx openjck              # start UI viewer (default)
npx openjck ui           # start UI viewer
npx openjck traces       # list all traces in terminal
npx openjck clear        # delete all traces
npx openjck --version    # show version
npx openjck --help       # show help
```

**Global install** (optional — skip `npx` every time):

```bash
npm install -g openjck
openjck ui
openjck traces
```

**What `openjck traces` looks like:**

```
  OpenJCK — Recorded Runs

  ID          Name                  Status      Steps   Duration    Tokens
  ────────────────────────────────────────────────────────────────────────
  a3f9c1b2    research_agent        completed   8       4.20s       2840
  9c4b1e3f    failing_agent         failed      6       2.41s       1345
              ✕ FileNotFoundError: File not found: config.txt

  2 runs total  ·  npx openjck ui to view in browser
```

---

## What Gets Captured

### For every `@trace_llm` call

| Field | Description |
|---|---|
| Full message history | Every message sent to the model |
| Model name | Which model + version was called |
| Response content | What the model replied |
| Tokens in / out | Prompt + completion token counts |
| Cost (USD) | Per-step cost based on model pricing |
| Latency | Execution time in ms |
| Error | Full traceback if the call failed |

### For every `@trace_tool` call

| Field | Description |
|---|---|
| Function arguments | Exact values passed in |
| Return value | What the tool returned |
| Latency | Execution time in ms |
| Error | Full traceback including line number |

---

## API Reference

### `@trace`

Marks the agent entry point. Starts a new trace for the entire run.

```python
@trace                               # uses function name
@trace(name="my_agent")             # explicit run name
@trace(name="agent", metadata={})   # attach custom metadata
@trace(auto_open=False)             # don't auto-start UI server
```

Supports `def` and `async def`.

---

### `@trace_llm`

Wraps an LLM call. Captures prompt, response, tokens, model, latency, cost.

```python
@trace_llm                           # auto-detects model from arguments
@trace_llm(model="gpt-4o")          # explicit model label
```

Auto-detects token counts from **Ollama**, **OpenAI**, and **Anthropic** response formats.

---

### `@trace_tool`

Wraps a tool call. Captures input arguments, return value, and any exception.

```python
@trace_tool                              # uses function name
@trace_tool(name="filesystem.write")     # explicit name in the UI
```

---

### `EventCapture` — manual instrumentation

For wrapping third-party code or dynamic dispatch:

```python
from openjck import EventCapture

with EventCapture("tool_call", "database.query", input={"sql": query}) as cap:
    result = db.execute(query)
    cap.output   = result.fetchall()
    cap.metadata = {"rows": len(result)}
```

---

### `TraceStorage` — programmatic access

```python
from openjck import TraceStorage

traces = TraceStorage.list_all()           # all trace summaries
trace  = TraceStorage.load("a3f9c1b2")    # full trace with all steps
TraceStorage.delete("a3f9c1b2")           # remove one trace
TraceStorage.search(q="research", status="failed")  # filter traces
```

---

## Framework Support

OpenJCK is **framework-agnostic**. Wrap the functions. That's it.

```python
# ✅ Raw Python agents
# ✅ LangChain
# ✅ LlamaIndex
# ✅ CrewAI
# ✅ AutoGen
# ✅ Smolagents
# ✅ Async agents (asyncio / anyio)
# ✅ Any custom agent loop
```

### LangChain — zero decorators via auto-patch

```python
import openjck
openjck.patch_langchain()    # instruments all LangChain LLM + tool calls

@trace(name="my_chain")
def run():
    chain.invoke({"question": "..."})   # automatically traced
```

### CrewAI

```python
@trace(name="crewai_research")
def run_crew(topic: str):
    crew = Crew(agents=[researcher, writer], tasks=[...])
    return crew.kickoff(inputs={"topic": topic})

@trace_tool(name="search.web")
def search_tool(query: str) -> str:
    return SerperDevTool().run(query)
```

### Ollama

```python
@trace_llm
def call_llm(messages):
    return ollama.chat(model="qwen2.5-coder:7b", messages=messages)
```

---

## Async Support

All decorators work on `async def` with zero changes:

```python
@trace(name="async_agent")
async def run_agent(task: str):
    response = await call_llm(...)
    result   = await fetch_data(...)

@trace_llm
async def call_llm(messages):
    return await async_client.chat(model="qwen2.5:7b", messages=messages)
```

---

## Trace Storage

All traces are plain JSON at `~/.openjck/traces/<trace_id>.json`.

```
~/.openjck/
└── traces/
    ├── a3f9c1b2.json   # completed — 8 steps, 2840 tokens
    ├── 9c4b1e3f.json   # failed — error at step 6
    └── ...
```

Both the Python library and the npm CLI read and write to this same location. No sync needed.

---

## Installation

### Python library (required — for agent instrumentation)

```bash
pip install openjck              # core library only
pip install "openjck[server]"   # includes FastAPI UI server (alternative to npx)
```

Requires: **Python 3.10+**

### npm CLI (recommended — for the visual UI viewer)

```bash
# No install — always runs latest:
npx openjck

# Or install once globally:
npm install -g openjck
```

Requires: **Node.js 18+**

---

## Why Not Just Use...

| | OpenJCK | LangSmith | Helicone | Print statements |
|---|---|---|---|---|
| Step-by-step visibility | ✅ | ✅ | ❌ | ❌ |
| Works with any framework | ✅ | ❌ | ✅ | ✅ |
| 100% local | ✅ | ❌ | ❌ | ✅ |
| Free forever | ✅ | Partial | Partial | ✅ |
| Visual UI | ✅ | ✅ | ✅ | ❌ |
| Token tracking | ✅ | ✅ | ✅ | ❌ |
| Cost tracking | ✅ | ✅ | ✅ | ❌ |
| Zero config | ✅ | ❌ | ❌ | ✅ |

OpenJCK is the only tool built specifically to debug **agentic loops** — the multi-step, tool-using, decision-making flows that break in ways traditional logging cannot explain.

---

## Changelog

### v0.2.1 (Current)

**New Features:**
- Live dashboard with real-time updates at http://localhost:7823
- Agent drill-down view with patterns analysis
- Trace detail view with step timeline
- Failure Intelligence Engine — automatic root cause analysis
- Recovery point detection
- Dependency chain tracing
- SQLite database for persistent storage
- Non-blocking HTTP emit client
- SSE (Server-Sent Events) for live updates
- Mobile responsive design
- Time filters (24h, 7d, all)
- Dashboard documentation pages

**Bug Fixes:**
- Fixed intelligence endpoint subprocess handling
- Fixed FOREIGN KEY constraint on intelligence table
- Fixed version display inconsistencies

**Python Package:** `openjck` on PyPI
**npm Package:** `openjck` on npm

### v0.2.0 (2026-03-15)

- Initial v0.2 release

### v0.1.0 (2026-03-10)

- Initial release
- Core decorators: `@trace`, `@trace_llm`, `@trace_tool`
- JSON trace persistence
- Visual timeline UI
- Token/cost tracking
- npm CLI

---

## Roadmap

**v0.2.1** *(current)*
- [x] Live dashboard with real-time updates
- [x] Failure Intelligence Engine
- [x] SQLite database
- [x] Agent drill-down view
- [x] Trace detail view
- [x] Mobile responsive design

**v0.3** *(in development)*
- [ ] Side-by-side run comparison
- [ ] Token waterfall chart
- [ ] CrewAI auto-instrumentation
- [ ] LlamaIndex auto-instrumentation
- [ ] CI/CD integration — fail build on regression
- [ ] VS Code extension

**v1.0** *(horizon)*
- [ ] OpenJCK Cloud — share traces across your team
- [ ] Team dashboards + run history
- [ ] Slack / Discord alerts on agent failure
- [ ] Export trace as shareable HTML report

---

## Contributing

Built because debugging agents was making us insane.

```bash
git clone https://github.com/RavaniRoshan/openjck
cd openjck

# Python library
pip install -e ".[server]"
python examples/basic_agent.py     # generates sample traces

# npm CLI
cd openjck-npm
npm install
node bin/openjck.js traces       # verify traces from above
node bin/openjck.js ui           # open UI at localhost:7823
```

Before opening a PR:
- Open an issue first for non-trivial changes
- Add an example for new features
- Keep `collector.py` and `decorators.py` dependency-free (stdlib only)
- Keep `bin/openjck.js` working without any build step

---

## Repository Structure

```
OpenJCK/
├── openjck/               ← Python library (pip install openjck)
│   ├── collector.py         ← core event capture, thread-safe
│   ├── decorators.py        ← @trace @trace_llm @trace_tool
│   ├── intelligence.py      ← failure intelligence engine
│   ├── client.py            ← HTTP emit client
│   ├── storage.py           ← JSON persistence
│   ├── server.py            ← FastAPI server (Python alternative)
│   ├── cli.py               ← Python CLI entry point
│   └── ui/                  ← web viewer UI
├── openjck-npm/           ← npm package (npx openjck)
│   ├── bin/openjck.js     ← CLI entrypoint
│   ├── src/
│   │   ├── server.js        ← Express server
│   │   ├── db.js            ← SQLite database
│   │   ├── commands/        ← ui, traces, clear
│   │   └── ui/index.html    ← dashboard UI
│   └── package.json
├── openjck-site/          ← docs site (Astro + Starlight)
├── examples/
│   ├── basic_agent.py       ← demo agent
│   └── dashboard_demo.py    ← dashboard demo
├── tests/
│   └── test_intelligence.py ← intelligence tests
└── README.md
```

---

## License

[MIT](LICENSE) — use it, fork it, ship it.

---

<div align="center">

<br />

**If this saved you an hour of debugging — [star the repo](https://github.com/RavaniRoshan/openjck).**

That's the only metric that matters right now.

<br />

Made with frustration and Python + Node.js
&nbsp;·&nbsp;
[GitHub](https://github.com/RavaniRoshan/openjck)
&nbsp;·&nbsp;
[npm](https://www.npmjs.com/package/openjck)
&nbsp;·&nbsp;
[PyPI](https://pypi.org/project/openjck/)
&nbsp;·&nbsp;
[Docs](https://openjck.dev)

<br />

</div>
