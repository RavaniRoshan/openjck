---
title: CrewAI
description: Using AgentTrace with CrewAI.
---

# CrewAI Integration

## @trace Wrapping Crew.kickoff()
The primary way to trace CrewAI applications is by wrapping the `kickoff()` method with the `@trace` decorator:

```python
from agentrace import trace
from crewai import Crew, Agent, Task

@trace(name="research_crew")
def run_research_crew():
    # Define agents
    researcher = Agent(
        role='Researcher',
        goal='Find and summarize information',
        backstory='You are an expert researcher with years of experience',
        verbose=True
    )
    
    analyst = Agent(
        role='Analyst',
        goal='Analyze data and provide insights',
        backstory='You are a skilled data analyst',
        verbose=True
    )
    
    # Define tasks
    research_task = Task(
        description='Research the latest developments in AI agents',
        agent=researcher
    )
    
    analysis_task = Task(
        description='Analyze the research findings and create a report',
        agent=analyst
    )
    
    # Create crew
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        verbose=2
    )
    
    # Kickoff the crew - this is what we trace
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    result = run_research_crew()
    print(result)
```

## @trace_tool Wrapping CrewAI Tools
For custom tools used by CrewAI agents, wrap them with `@trace_tool`:

```python
from agentrace import trace_tool
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")

class SearchTool(BaseTool):
    name = "search"
    description = "Useful for searching the internet for information"
    args_schema: Type[BaseModel] = SearchInput

    @trace_tool(name="Internet Search")
    def _run(self, query: str) -> str:
        # Implement your search logic here
        # This could be a call to Google, DuckDuckGo, or any search API
        return f"Search results for: {query}"

    async def _arun(self, query: str) -> str:
        # Async version if needed
        return self._run(query)
```

## Full Working Example

```python
from agentrace import trace, trace_tool
from crewai import Crew, Agent, Task, Process
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# Custom traced tool
class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")

class SearchTool(BaseTool):
    name = "search"
    description = "Search for information on a topic"
    args_schema: Type[BaseModel] = SearchInput

    @trace_tool(name="Web Search")
    def _run(self, query: str) -> str:
        # Simulated search - replace with real search API
        if "capital" in query.lower() and "france" in query.lower():
            return "Paris is the capital of France."
        return f"Information about {query}: [simulated search results]"

# Agents
@trace(name="researcher_agent")
def create_researcher():
    return Agent(
        role='Researcher',
        goal='Find accurate information',
        backstory='You are a meticulous researcher who verifies facts from multiple sources',
        verbose=True,
        tools=[SearchTool()]
    )

@trace(name="writer_agent")  
def create_writer():
    return Agent(
        role='Writer',
        goal='Create clear and concise summaries',
        backstory='You are a skilled writer known for making complex topics easy to understand',
        verbose=True
    )

# Tasks
def create_research_task(agent):
    return Task(
        description='Research the capital of France and provide key facts',
        agent=agent
    )

def create_writing_task(agent):
    return Task(
        description='Write a brief summary of the research findings',
        agent=agent
    )

# Main function
@trace(name="crewai_research_project")
def run_crewai_project():
    # Create agents
    researcher = create_researcher()
    writer = create_writer()
    
    # Create tasks
    research_task = create_research_task(researcher)
    writing_task = create_writing_task(writer)
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=2
    )
    
    # Execute the crew
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    result = run_crewai_project()
    print("\nFinal Result:")
    print(result)
```

## Note on CrewAI Async Support
AgentTrace supports both synchronous and asynchronous CrewAI usage:

- **Synchronous**: Works out of the box with `@trace` and `@trace_tool` decorators
- **Asynchronous**: Use `@trace` and `@trace_tool` on async methods - AgentTrace automatically handles async functions

For async CrewAI implementations, ensure your custom tools and agent methods are declared as `async def` and decorated appropriately:

```python
from agentrace import trace_tool

class AsyncSearchTool(BaseTool):
    @trace_tool(name="Async Search")
    async def _arun(self, query: str) -> str:
        # async search implementation
        pass
```

## How AgentTrace Integrates with CrewAI
When you trace CrewAI applications with AgentTrace:

1. **Top-level tracing**: `@trace` on the `kickoff()` call captures overall crew execution
2. **Agent-level tracing**: Decorate agent creation or execution methods to trace individual agent behavior
3. **Tool-level tracing**: `@trace_tool` on custom tools captures every tool invocation with inputs/outputs
4. **Task-level tracing**: Trace task execution methods to see how each task contributes to the overall workflow

The resulting trace shows:
- Hierarchical view of crew → agents → tasks → tool calls
- Token usage and costs for any LLM calls made within the crew
- Execution timing for each step
- Error handling with tracebacks for any failed steps