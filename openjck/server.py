"""
OpenJCK — Web Server
FastAPI-based UI server for trace visualization.
Runs on port 7823 by default.
"""

import uvicorn
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .storage import TraceStorage

app = FastAPI(title="OpenJCK", version="0.2.1")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the UI directory path
UI_DIR = Path(__file__).parent / "ui"


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.2.1"}


@app.get("/api/traces")
def list_traces(
    q: Optional[str] = None,
    status: Optional[str] = None,
    model: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """List or search traces with optional filtering."""
    return TraceStorage.search(
        q=q, status=status, model=model, from_date=from_date, to_date=to_date
    )


@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str):
    """Get full trace details."""
    trace = TraceStorage.load(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    return trace


@app.delete("/api/traces/{trace_id}")
def delete_trace(trace_id: str):
    """Delete a trace."""
    if not TraceStorage.delete(trace_id):
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    return {"deleted": trace_id}


@app.get("/")
def serve_index():
    """Serve the main UI."""
    index_path = UI_DIR / "index.html"
    if not index_path.exists():
        return {"message": "Dashboard UI moved to npm package. Run: npx openjck"}
    return FileResponse(str(index_path), media_type="text/html")


@app.get("/trace/{trace_id}")
def serve_trace_page(trace_id: str):
    """Serve the UI for a specific trace."""
    index_path = UI_DIR / "index.html"
    if not index_path.exists():
        return {"message": "Dashboard UI moved to npm package. Run: npx openjck"}
    return FileResponse(str(index_path), media_type="text/html")


def main():
    """CLI entry point."""
    port = 7823
    print(f"[OpenJCK] Starting server on http://localhost:{port}")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="error",
    )


if __name__ == "__main__":
    main()
