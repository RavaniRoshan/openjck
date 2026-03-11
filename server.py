"""
AgentTrace — Server
FastAPI backend. Serves trace data + the UI.
Run: python -m agentrace.server
"""

import sys
from difflib import unified_diff
from pathlib import Path
from typing import Any

# Add parent to path when run as module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    import uvicorn
except ImportError:
    print("[AgentTrace] Missing dependencies. Run: pip install agentrace[server]")
    print("Or: pip install fastapi uvicorn")
    sys.exit(1)

from agentrace.storage import TraceStorage, SERVER_PORT

app = FastAPI(title="AgentTrace", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/traces")
def list_traces(
    q: str | None = None,
    status: str | None = Query(default=None, pattern="^(completed|failed|running)$"),
    model: str | None = None,
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
):
    return TraceStorage.search(
        q=q, status=status, model=model, from_date=from_date, to_date=to_date
    )


def _safe_json(value: Any) -> str:
    import json

    try:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
    except TypeError:
        return str(value)


def _diff_text(a: Any, b: Any) -> str:
    left = _safe_json(a).splitlines()
    right = _safe_json(b).splitlines()
    return "\n".join(unified_diff(left, right, fromfile="left", tofile="right", lineterm=""))


@app.get("/api/traces/compare")
def compare_traces(
    left_trace_id: str = Query(..., alias="left"),
    right_trace_id: str = Query(..., alias="right"),
):
    left = TraceStorage.load(left_trace_id)
    right = TraceStorage.load(right_trace_id)

    if not left or not right:
        raise HTTPException(status_code=404, detail="One or both traces not found")

    left_steps = left.get("steps", [])
    right_steps = right.get("steps", [])
    max_len = max(len(left_steps), len(right_steps))
    comparisons = []

    for idx in range(max_len):
        left_step = left_steps[idx] if idx < len(left_steps) else None
        right_step = right_steps[idx] if idx < len(right_steps) else None
        same_name = bool(
            left_step
            and right_step
            and left_step.get("name")
            and left_step.get("name") == right_step.get("name")
        )

        left_tokens = (left_step or {}).get("tokens_in", 0) + (left_step or {}).get("tokens_out", 0)
        right_tokens = (right_step or {}).get("tokens_in", 0) + (right_step or {}).get(
            "tokens_out", 0
        )

        comparisons.append(
            {
                "step_index": idx,
                "left_step": left_step,
                "right_step": right_step,
                "name_match": same_name,
                "missing_on_left": left_step is None,
                "missing_on_right": right_step is None,
                "duration_diff_ms": (
                    (left_step or {}).get("duration_ms", 0)
                    - (right_step or {}).get("duration_ms", 0)
                ),
                "token_diff": left_tokens - right_tokens,
                "input_diff": _diff_text(left_step.get("input"), right_step.get("input"))
                if same_name
                else None,
                "output_diff": _diff_text(left_step.get("output"), right_step.get("output"))
                if same_name
                else None,
            }
        )

    return {
        "left_trace": left,
        "right_trace": right,
        "step_comparisons": comparisons,
    }


@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str):
    trace = TraceStorage.load(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@app.delete("/api/traces/{trace_id}")
def delete_trace(trace_id: str):
    deleted = TraceStorage.delete(trace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"deleted": trace_id}


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


# Serve UI for all other routes
UI_PATH = Path(__file__).parent / "ui" / "index.html"


@app.get("/", response_class=HTMLResponse)
@app.get("/trace/{trace_id}", response_class=HTMLResponse)
def serve_ui(trace_id: str = None):
    if UI_PATH.exists():
        return UI_PATH.read_text()
    return HTMLResponse("<h1>AgentTrace UI not found. Run: agentrace build-ui</h1>")


if __name__ == "__main__":
    print(f"\n[AgentTrace] UI running at http://localhost:{SERVER_PORT}")
    print("[AgentTrace] Serving traces from ~/.agentrace/traces/\n")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT, log_level="error")
