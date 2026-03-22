"""
OpenJCK — Storage
Saves traces as JSON to ~/.openjck/traces/
Zero dependencies beyond stdlib.
"""

import json
import os
import subprocess
import sys
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from .collector import Trace


TRACES_DIR = Path.home() / ".openjck" / "traces"
SERVER_PORT = 7823
_server_started = False
_server_lock = threading.Lock()


class TraceStorage:
    @staticmethod
    def _trace_summary(data: dict) -> dict:
        return {
            "trace_id": data["trace_id"],
            "run_name": data["run_name"],
            "started_at": data["started_at"],
            "status": data["status"],
            "total_duration_ms": data.get("total_duration_ms"),
            "total_tokens": data.get("total_tokens", 0),
            "step_count": len(data.get("steps", [])),
            "error": data.get("error"),
        }

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _trace_started_date(trace: dict) -> Optional[date]:
        started_at = trace.get("started_at")
        if not started_at:
            return None
        try:
            return datetime.fromisoformat(started_at.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    @staticmethod
    def _matches_filters(
        trace: dict,
        q: Optional[str],
        status: Optional[str],
        model: Optional[str],
        from_date: Optional[date],
        to_date: Optional[date],
    ) -> bool:
        run_name = trace.get("run_name", "")
        if q and q.lower() not in run_name.lower():
            return False

        if status and trace.get("status") != status:
            return False

        if model:
            model_query = model.lower()
            steps = trace.get("steps", [])
            has_model = any(model_query == str(step.get("model", "")).lower() for step in steps)
            if not has_model:
                return False

        trace_date = TraceStorage._trace_started_date(trace)
        if from_date and trace_date and trace_date < from_date:
            return False
        if to_date and trace_date and trace_date > to_date:
            return False

        return True

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
        return TraceStorage.search()

    @staticmethod
    def search(
        q: Optional[str] = None,
        status: Optional[str] = None,
        model: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> list[dict]:
        if not TRACES_DIR.exists():
            return []

        from_date_parsed = TraceStorage._parse_date(from_date)
        to_date_parsed = TraceStorage._parse_date(to_date)

        traces = []
        for path in sorted(TRACES_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(path) as f:
                    data = json.load(f)
                    if TraceStorage._matches_filters(
                        data, q, status, model, from_date_parsed, to_date_parsed
                    ):
                        traces.append(TraceStorage._trace_summary(data))
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
                    [sys.executable, "-m", "openjck.server"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"[OpenJCK] Could not start UI server: {e}")
                print("[OpenJCK] Start manually: python -m openjck.server")

        t = threading.Thread(target=start, daemon=True)
        t.start()
        # Give it a moment to start
        import time

        time.sleep(1.5)
