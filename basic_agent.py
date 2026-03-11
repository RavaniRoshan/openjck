"""
AgentTrace — Basic Example
Run this to see AgentTrace in action.

Requirements:
    pip install agentrace ollama

Then: ollama pull qwen2.5-coder:7b-instruct-q4_K_M
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import time
import random
from agentrace import trace, trace_llm, trace_tool


# ── Simulated Tools (no real dependencies) ───────────────────────────────────

@trace_tool
def web_search(query: str) -> str:
    """Simulated web search"""
    time.sleep(random.uniform(0.1, 0.4))
    return json.dumps([
        {"title": f"Result 1 for: {query}", "url": "https://example.com/1", "snippet": "This is a relevant result..."},
        {"title": f"Result 2 for: {query}", "url": "https://example.com/2", "snippet": "Another relevant result..."},
    ])


@trace_tool
def read_file(path: str) -> str:
    """Read a file"""
    time.sleep(0.05)
    if path == "notes.txt":
        return "Meeting notes: Discussed Q4 roadmap, decided to prioritize agent tooling..."
    raise FileNotFoundError(f"File not found: {path}")


@trace_tool
def write_file(path: str, content: str) -> str:
    """Write a file"""
    time.sleep(0.08)
    return f"Written {len(content)} bytes to {path}"


@trace_tool
def run_python(code: str) -> str:
    """Execute Python code"""
    time.sleep(random.uniform(0.1, 0.3))
    # Simulate execution
    return "Output: [1, 4, 9, 16, 25]\nExecution time: 0.002s"


# ── LLM Call (simulated — swap with real ollama.chat) ─────────────────────────

@trace_llm(model="qwen2.5-coder:7b")
def call_llm(messages: list, step_num: int = 0) -> dict:
    """
    Simulated LLM call. Replace with real:
        import ollama
        return ollama.chat(model="qwen2.5-coder:7b-instruct-q4_K_M", messages=messages)
    """
    time.sleep(random.uniform(0.3, 0.8))

    responses = [
        {"content": "I need to search for information about the topic first.", "tokens_in": 250, "tokens_out": 45},
        {"content": "I found relevant results. Let me read the existing notes file.", "tokens_in": 380, "tokens_out": 62},
        {"content": "Now I have enough context. Let me write a Python script to process this.", "tokens_in": 520, "tokens_out": 88},
        {"content": "```python\nnumbers = [1,2,3,4,5]\nsquares = [n**2 for n in numbers]\nprint(squares)\n```", "tokens_in": 680, "tokens_out": 120},
        {"content": "The code ran successfully. Let me write the final summary.", "tokens_in": 720, "tokens_out": 95},
    ]

    r = responses[min(step_num, len(responses) - 1)]

    # Simulate token counts in response
    class FakeResponse:
        class message:
            content = r["content"]
        prompt_eval_count = r["tokens_in"]
        eval_count = r["tokens_out"]

    return FakeResponse()


# ── The Agent Loop ────────────────────────────────────────────────────────────

@trace(name="research_and_summarize")
def run_research_agent(task: str):
    """
    A simple research agent that:
    1. Searches the web
    2. Reads a local file
    3. Writes a processing script
    4. Runs the script
    5. Writes a summary
    """
    print(f"\n[Agent] Starting task: {task}\n")

    messages = [{"role": "user", "content": task}]

    for step in range(5):
        # LLM decides what to do
        response = call_llm(messages, step_num=step)
        content = response.message.content
        messages.append({"role": "assistant", "content": content})
        print(f"[Agent Step {step+1}] LLM: {content[:80]}...")

        # Simulate tool use based on step
        if step == 0:
            result = web_search(task)
            messages.append({"role": "user", "content": f"Search results: {result[:200]}..."})
            print(f"[Tool] web_search → {len(result)} chars")

        elif step == 1:
            result = read_file("notes.txt")
            messages.append({"role": "user", "content": f"File content: {result}"})
            print(f"[Tool] read_file → {result[:60]}...")

        elif step == 2:
            code = "numbers = [1,2,3,4,5]\nprint([n**2 for n in numbers])"
            result = run_python(code)
            messages.append({"role": "user", "content": f"Execution result: {result}"})
            print(f"[Tool] run_python → {result}")

        elif step == 3:
            summary = f"# Research Summary\n\nTask: {task}\n\nFindings: ..."
            result = write_file("summary.md", summary)
            messages.append({"role": "user", "content": result})
            print(f"[Tool] write_file → {result}")

        else:
            print("[Agent] Task complete.")
            break

    return "Research complete. See summary.md"


# ── Run with intentional failure (to demo error tracing) ──────────────────────

@trace(name="agent_with_error")
def run_failing_agent(task: str):
    """Agent that fails at step 3 — shows error tracing"""
    print("\n[Agent] Starting failing task demo...\n")

    messages = [{"role": "user", "content": task}]

    for step in range(5):
        response = call_llm(messages, step_num=step)
        messages.append({"role": "assistant", "content": response.message.content})

        if step == 0:
            result = web_search("python best practices")
            messages.append({"role": "user", "content": result[:200]})

        elif step == 1:
            result = web_search("error handling patterns")
            messages.append({"role": "user", "content": result[:200]})

        elif step == 2:
            # This will FAIL — shows error tracing
            result = read_file("nonexistent_file.txt")  # ← FAILS HERE

        elif step == 3:
            write_file("output.md", "Never reached")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  AgentTrace — Example Agent")
    print("=" * 60)

    # Run 1: Successful agent
    print("\n[Demo 1] Running successful agent...")
    run_research_agent("Research the latest AI agent frameworks and summarize key findings")

    # Run 2: Agent with failure
    print("\n[Demo 2] Running agent that fails at step 3...")
    try:
        run_failing_agent("Read the project notes and create a summary")
    except FileNotFoundError:
        print("[Demo 2] Agent failed as expected — check AgentTrace to see where!")

    print("\n" + "=" * 60)
    print("  Open http://localhost:7823 to see both traces")
    print("=" * 60)
