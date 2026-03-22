"""Demo script to populate the OpenJCK dashboard with sample traces."""
from openjck import trace, trace_llm, trace_tool
import time, random


@trace(name="research_agent")
def successful_run(task: str):
    data = fetch_data(task)
    result = process(data)
    return result


@trace(name="research_agent")
def failing_run(task: str):
    data = fetch_bad_data(task)
    result = process(data)  # will fail
    return result


@trace_tool
def fetch_data(query: str):
    time.sleep(0.5)
    return {"rows": 42, "file": "data/output.csv"}


@trace_tool
def fetch_bad_data(query: str):
    time.sleep(0.3)
    return {"file": "data/missing_2026.csv"}


@trace_tool
def process(data: dict):
    time.sleep(0.2)
    if "missing" in str(data.get("file", "")):
        raise FileNotFoundError(f"{data['file']} not found")
    return {"summary": "done", "rows": data.get("rows", 0)}


if __name__ == "__main__":
    print("Creating demo traces...")
    
    successful_run("quarterly report")
    successful_run("user analytics")
    
    try:
        failing_run("missing data report")
    except Exception:
        pass
    
    try:
        failing_run("another missing file")
    except Exception:
        pass
    
    print("Done. Open: npx openjck")
