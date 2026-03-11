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
SERVER_PORT = 7823
_server_started = False
_server_lock = threading.Lock()


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
                    traces.append({
                        "trace_id": data["trace_id"],
                        "run_name": data["run_name"],
                        "started_at": data["started_at"],
                        "status": data["status"],
                        "total_duration_ms": data.get("total_duration_ms"),
                        "total_tokens": data.get("total_tokens", 0),
                        "step_count": len(data.get("steps", [])),
                        "error": data.get("error"),
                    })
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
                print(f"[AgentTrace] Start manually: python -m agentrace.server")

        t = threading.Thread(target=start, daemon=True)
        t.start()
        # Give it a moment to start
        import time
        time.sleep(1.5)
