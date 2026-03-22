---
title: LangChain
description: Using OpenJCK with LangChain.
---

# LangChain Integration

## Auto-patch (Recommended)
The easiest way to trace LangChain components is with the auto-patch function:

```python
from openjck import patch_langchain

# Patch LangChain before importing/using it
patch_langchain()

# Now all LangChain components are automatically traced
from langchain.agents import initialize_agent, Tool
from langchain.llms import Ollama

llm = Ollama(model="qwen2.5:7b")
tools = [
    Tool(
        name="Search",
        func=lambda q: "Paris is the capital of France.",
        description="Useful for answering factual questions"
    )
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
result = agent.run("What is the capital of France?")
```

## Manual Decorator Fallback
If you prefer more control or can't use the patcher, you can manually decorate LangChain components:

```python
from openjck import trace, trace_llm, trace_tool
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Trace the LLM calls
@trace_llm
def call_llm(prompt):
    llm = Ollama(model="qwen2.5:7b")
    return llm(prompt)

# Trace tool usage
@trace_tool(name="Calculator")
def calculate(expression):
    return eval(expression)  # In practice, use a safe evaluator

# Trace the overall chain
@trace(name="math_chain")
def math_chain(question):
    template = """You are a math assistant. Question: {question}"""
    prompt = PromptTemplate(template=template, input_variables=["question"])
    chain = LLMChain(llm=call_llm, prompt=prompt)
    return chain.run(question)
```

## Full Working Example

```python
from openjck import trace, trace_llm, trace_tool, patch_langchain
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.llms import Ollama

# Auto-patch LangChain components
patch_langchain()

# Define tools with tracing
@trace_tool(name="Search")
def search_tool(query):
    # Simulate a search tool
    if "capital" in query.lower():
        return "Paris is the capital of France."
    return "I couldn't find information about that."

@trace_tool(name="Calculator")
def calculator_tool(expression):
    try:
        return str(eval(expression))  # Simplified for example
    except:
        return "Error in calculation"

# Initialize LLM
llm = Ollama(model="qwen2.5:7b")

# Create agent
tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="Useful for answering factual questions"
    ),
    Tool(
        name="Calculator",
        func=calculator_tool,
        description="Useful for mathematical calculations"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Trace the overall agent execution
@trace(name="langchain_agent")
def run_agent(question):
    return agent.run(question)

# Run the agent
if __name__ == "__main__":
    result = run_agent("What is the capital of France?")
    print(result)
```

## Supported LangChain Versions
OpenJCK is tested and compatible with LangChain version **0.1.0** and above. The auto-patch function works with:
- LLMs (Ollama, OpenAI, etc.)
- Chains (LLMChain, SequentialChain, etc.)
- Agents (Zero-shot, Structured-chat, etc.)
- Tools (custom and built-in)

## How It Works
When you call `patch_langchain()`:
1. OpenJCK wraps LangChain's core classes with tracing decorators
2. LLM calls are automatically wrapped with `@trace_llm` 
3. Tool executions are wrapped with `@trace_tool`
4. Agent runs are wrapped with `@trace`
5. All trace data flows to the standard OpenJCK system and appears in the UI

## Manual Instrumentation Tips
For fine-grained tracing within LangChain components:
- Use `@trace_llm` on custom LLM wrappers
- Use `@trace_tool` on custom tools
- Use `@trace` on agent initialization and execution functions
- Combine with `EventCapture` for tracing specific internal steps