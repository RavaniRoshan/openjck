"""
AgentTrace — Storage
Saves traces as JSON to ~/.agentrace/traces/
Zero dependencies beyond stdlib.
"""

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional
from .collector import Trace


TRACES_DIR = Path.home() / ".agentrace" / "traces"
COSTS_FILE = Path.home() / ".agentrace" / "costs.json"
SERVER_PORT = 7823
_server_started = False
_server_lock = threading.Lock()


# Default model costs (in $/1M tokens)
_DEFAULT_COSTS = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "qwen2.5:7b": {"input": 0.0, "output": 0.0},  # Ollama local
    "llama3.1:8b": {"input": 0.0, "output": 0.0},  # Ollama local
    "default": {"input": 1.0, "output": 3.0},
}


def _ensure_costs_file():
    """Create costs.json if it doesn't exist, with default prices."""
    if COSTS_FILE.exists():
        return
    COSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COSTS_FILE, "w") as f:
        json.dump(_DEFAULT_COSTS, f, indent=2)


# Initialize costs file on module import
_ensure_costs_file()


class TraceStorage:
    @staticmethod
    def save(trace: Trace) -> Path:
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        path = TRACES_DIR / f"{trace.trace_id}.json"
        with open(path, "w") as f:
            json.dump(trace.to_dict(), f, indent=2, default=str)
        return path

    @staticmethod
    def load(trace_id: str) -> Optional[dict]:
        path = TRACES_DIR / f"{trace_id}.json"
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def list_all() -> list[dict]:
        if not TRACES_DIR.exists():
            return []
        traces = []
        for path in sorted(TRACES_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(path) as f:
                    data = json.load(f)
                    # Return summary only for list view
                    traces.append(
                        {
                            "trace_id": data["trace_id"],
                            "run_name": data["run_name"],
                            "started_at": data["started_at"],
                            "status": data["status"],
                            "total_duration_ms": data.get("total_duration_ms"),
                            "total_tokens": data.get("total_tokens", 0),
                            "total_cost_usd": data.get("total_cost_usd", 0.0),
                            "step_count": len(data.get("steps", [])),
                            "error": data.get("error"),
                        }
                    )
            except Exception:
                continue
        return traces

    @staticmethod
    def delete(trace_id: str) -> bool:
        path = TRACES_DIR / f"{trace_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    @staticmethod
    def search(
        q: Optional[str] = None,
        status: Optional[str] = None,
        model: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> list[dict]:
        """Search traces by multiple criteria.

        Args:
            q: Substring search in run_name (case-insensitive)
            status: Exact status match ("completed", "failed", etc.)
            model: Model name used in any step
            from_date: Start date in ISO format (inclusive)
            to_date: End date in ISO format (inclusive)

        Returns:
            List of matching trace summaries sorted by recency
        """
        if not TRACES_DIR.exists():
            return []

        results = []
        for path in sorted(TRACES_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(path) as f:
                    data = json.load(f)

                # Filter by q (run_name substring)
                if q and q.lower() not in data.get("run_name", "").lower():
                    continue

                # Filter by status
                if status and data.get("status") != status:
                    continue

                # Filter by model (check any step)
                if model:
                    has_model = any(step.get("model") == model for step in data.get("steps", []))
                    if not has_model:
                        continue

                # Filter by date range
                started_at = data.get("started_at", "")
                if from_date and started_at < from_date:
                    continue
                if to_date and started_at > to_date:
                    continue

                # Add to results
                results.append(
                    {
                        "trace_id": data["trace_id"],
                        "run_name": data["run_name"],
                        "started_at": data["started_at"],
                        "status": data["status"],
                        "total_duration_ms": data.get("total_duration_ms"),
                        "total_tokens": data.get("total_tokens", 0),
                        "total_cost_usd": data.get("total_cost_usd", 0.0),
                        "step_count": len(data.get("steps", [])),
                        "error": data.get("error"),
                    }
                )
            except Exception:
                continue

        return results

    @staticmethod
    def ensure_server_running():
        """Start the UI server in background if not already running."""
        global _server_started
        with _server_lock:
            if _server_started:
                return
            _server_started = True

        def start():
            try:
                subprocess.Popen(
                    [sys.executable, "-m", "agentrace.server"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"[AgentTrace] Could not start UI server: {e}")
                print("[AgentTrace] Start manually: python -m agentrace.server")

        t = threading.Thread(target=start, daemon=True)
        t.start()
        # Give it a moment to start
        import time

        time.sleep(1.5)
