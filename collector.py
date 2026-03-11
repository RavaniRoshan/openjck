"""
AgentTrace — Core Collector
Captures every event in an agent run. Zero magic. 100% transparent.
"""

import time
import uuid
import threading
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TraceEvent:
    step_id: int
    type: str  # "llm_call" | "tool_call" | "agent_step" | "custom"
    name: str
    started_at: str
    duration_ms: Optional[float] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    tokens_in: int = 0
    tokens_out: int = 0
    model: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Trace:
    trace_id: str
    run_name: str
    started_at: str
    status: str = "running"
    finished_at: Optional[str] = None
    total_duration_ms: Optional[float] = None
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    error: Optional[str] = None
    steps: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        d["total_tokens"] = self.total_tokens_in + self.total_tokens_out
        return d


class TraceCollector:
    """
    Thread-local trace collector. Each thread gets its own active trace.
    Supports nested traces via a stack.
    """

    _local = threading.local()

    @classmethod
    def _get_stack(cls) -> list:
        if not hasattr(cls._local, "stack"):
            cls._local.stack = []
        return cls._local.stack

    @classmethod
    def current(cls) -> Optional[Trace]:
        stack = cls._get_stack()
        return stack[-1] if stack else None

    @classmethod
    def start(cls, run_name: str, metadata: dict = None) -> Trace:
        trace = Trace(
            trace_id=str(uuid.uuid4())[:8],
            run_name=run_name,
            started_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        cls._get_stack().append(trace)
        return trace

    @classmethod
    def finish(cls, trace: Trace, error: str = None):
        finished_at = datetime.now(timezone.utc).isoformat()
        start = datetime.fromisoformat(trace.started_at)
        end = datetime.fromisoformat(finished_at)
        trace.finished_at = finished_at
        trace.total_duration_ms = round((end - start).total_seconds() * 1000, 2)
        trace.status = "failed" if error else "completed"
        trace.error = error

        stack = cls._get_stack()
        if trace in stack:
            stack.remove(trace)

    @classmethod
    def add_event(cls, event: TraceEvent):
        trace = cls.current()
        if trace:
            trace.steps.append(event.to_dict())
            trace.total_tokens_in += event.tokens_in
            trace.total_tokens_out += event.tokens_out

    @classmethod
    def next_step_id(cls) -> int:
        trace = cls.current()
        if trace:
            return len(trace.steps) + 1
        return 1


class EventCapture:
    """
    Context manager for capturing a single step.
    Usage:
        with EventCapture("tool_call", "web_search", input={"query": "..."}) as cap:
            result = do_thing()
            cap.output = result
    """

    def __init__(
        self,
        event_type: str,
        name: str,
        input: Any = None,
        model: str = None,
        metadata: dict = None,
    ):
        self.event_type = event_type
        self.name = name
        self.input = input
        self.model = model
        self.metadata = metadata or {}
        self.output = None
        self.tokens_in = 0
        self.tokens_out = 0
        self._start_time = None
        self._step_id = None

    def __enter__(self):
        self._start_time = time.time()
        self._step_id = TraceCollector.next_step_id()
        self._started_at = datetime.now(timezone.utc).isoformat()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = round((time.time() - self._start_time) * 1000, 2)
        error = str(exc_val) if exc_val else None

        event = TraceEvent(
            step_id=self._step_id,
            type=self.event_type,
            name=self.name,
            started_at=self._started_at,
            duration_ms=duration_ms,
            input=self.input,
            output=self.output if not error else None,
            error=error,
            metadata=self.metadata,
            tokens_in=self.tokens_in,
            tokens_out=self.tokens_out,
            model=self.model,
        )
        TraceCollector.add_event(event)
        return False  # don't suppress exceptions
