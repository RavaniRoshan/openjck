"""
AgentTrace — Basic Agent Example
Demonstrates tracing of a simple agent workflow.
"""

import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentrace import trace, trace_tool, trace_llm


# Simulated LLM call with token counting
class MockLLMResponse:
    def __init__(self, content, input_tokens, output_tokens):
        self.content = content
        self.usage = MockUsage(input_tokens, output_tokens)
        self.message = MockMessage(content)
        self.choices = [MockChoice(content)]


class MockUsage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)


@trace_tool
def search_web(query: str) -> str:
    """Simulate a web search tool."""
    time.sleep(0.1)
    return f"Found results for '{query}': [search result 1, search result 2, ...]"


@trace_tool
def read_document(path: str) -> str:
    """Simulate reading a document."""
    time.sleep(0.05)
    return f"Document content from {path}: Lorem ipsum dolor sit amet..."


@trace_llm(model="gpt-4o-mini")
def call_llm_with_context(messages: list) -> MockLLMResponse:
    """Simulate an LLM API call with token counting."""
    time.sleep(0.2)
    # Simulate token counts based on message length
    input_tokens = sum(len(msg.get("content", "")) // 4 for msg in messages) + 100
    output_tokens = 150
    return MockLLMResponse(
        "I found relevant information about the query. Here's my analysis...",
        input_tokens,
        output_tokens,
    )


@trace
def agent_run_success() -> dict:
    """A successful agent run."""
    print("[Agent] Starting successful run...")

    query = "What are the latest AI developments?"
    print(f"[Agent] Searching for: {query}")
    search_results = search_web(query)

    print("[Agent] Reading related document...")
    doc_content = read_document("ai_trends_2024.md")

    print("[Agent] Calling LLM with context...")
    messages = [
        {"role": "user", "content": f"Based on these search results and document: {search_results} {doc_content}"},
        {"role": "user", "content": query},
    ]
    response = call_llm_with_context(messages)

    print("[Agent] Agent completed successfully")
    return {
        "status": "success",
        "result": response.content,
        "search_results": search_results,
    }


@trace
def agent_run_with_error() -> dict:
    """An agent run that encounters an error."""
    print("[Agent] Starting run that will fail...")

    try:
        query = "This query will cause an error"
        print(f"[Agent] Attempting problematic operation: {query}")

        # Simulate a failed tool call
        result = search_web(query)
        print(f"[Agent] Search result: {result}")

        # This will simulate an error scenario
        raise ValueError("Simulated error: API rate limit exceeded")

    except ValueError as e:
        print(f"[Agent] Encountered error: {e}")
        raise


def main():
    """Run example traces."""
    print("=" * 60)
    print("AgentTrace — Basic Agent Example")
    print("=" * 60)
    print()

    # Run 1: Successful trace
    print(">>> Running successful agent trace...")
    try:
        agent_run_success()
        print("✓ Successful run completed")
        print()
    except Exception as e:
        print(f"✗ Unexpected error in successful run: {e}")
        sys.exit(1)

    print()
    print(">>> Running agent trace with error...")

    # Run 2: Failed trace
    try:
        agent_run_with_error()
    except ValueError:
        print("✓ Error handling trace completed (expected)")
        print()

    # Verify traces were created
    traces_dir = Path.home() / ".agentrace" / "traces"
    if traces_dir.exists():
        trace_files = list(traces_dir.glob("*.json"))
        print(f"\n✓ {len(trace_files)} trace files created in {traces_dir}")
    else:
        print(f"\n✗ No traces directory found at {traces_dir}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Example completed! View traces in the AgentTrace UI:")
    print("http://localhost:7823")
    print("=" * 60)


if __name__ == "__main__":
    main()
