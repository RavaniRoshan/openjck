"""
AgentTrace — Decorators
The entire public API. Three decorators. That's it.
"""

import functools
import inspect
from typing import Any, Callable, Optional
from .collector import TraceCollector, EventCapture
from .storage import TraceStorage


def trace(name: str = None, metadata: dict = None, auto_open: bool = True):
    """
    Wraps an agent entry point. Starts a trace, captures the full run.

    Usage:
        @trace(name="my_agent")
        def run_agent(task: str):
            ...

        @trace  # also works without args
        def run_agent(task: str):
            ...
    """

    def decorator(func: Callable):
        run_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t = TraceCollector.start(run_name, metadata=metadata)
            error_msg = None
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                raise
            finally:
                TraceCollector.finish(t, error=error_msg)
                TraceStorage.save(t)
                print(f"\n[AgentTrace] Run complete → {t.status.upper()}")
                print(
                    f"[AgentTrace] {len(t.steps)} steps | "
                    f"{t.total_tokens_in + t.total_tokens_out} tokens | "
                    f"{t.total_duration_ms}ms"
                )
                print(f"[AgentTrace] View trace: http://localhost:7823/trace/{t.trace_id}")
                if auto_open:
                    TraceStorage.ensure_server_running()

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            t = TraceCollector.start(run_name, metadata=metadata)
            error_msg = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                raise
            finally:
                TraceCollector.finish(t, error=error_msg)
                TraceStorage.save(t)
                print(f"\n[AgentTrace] Run complete → {t.status.upper()}")
                print(
                    f"[AgentTrace] {len(t.steps)} steps | "
                    f"{t.total_tokens_in + t.total_tokens_out} tokens | "
                    f"{t.total_duration_ms}ms"
                )
                print(f"[AgentTrace] View trace: http://localhost:7823/trace/{t.trace_id}")
                if auto_open:
                    TraceStorage.ensure_server_running()

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    # Handle @trace without parentheses
    if callable(name):
        func = name
        name = func.__name__
        return decorator(func)

    return decorator


def trace_llm(func: Callable = None, *, model: str = None):
    """
    Wraps an LLM call. Captures prompt, response, token counts.

    Usage:
        @trace_llm
        def call_llm(messages):
            return ollama.chat(model="qwen2.5:7b", messages=messages)

        # Or with explicit model name
        @trace_llm(model="gpt-4o")
        def call_openai(messages):
            ...
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract input intelligently
            input_data = _extract_input(func, args, kwargs)
            detected_model = model or _detect_model(args, kwargs)

            with EventCapture(
                event_type="llm_call", name=func.__name__, input=input_data, model=detected_model
            ) as cap:
                result = func(*args, **kwargs)
                cap.output = _extract_llm_output(result)
                cap.tokens_in, cap.tokens_out = _extract_tokens(result)
                return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            input_data = _extract_input(func, args, kwargs)
            detected_model = model or _detect_model(args, kwargs)

            with EventCapture(
                event_type="llm_call", name=func.__name__, input=input_data, model=detected_model
            ) as cap:
                result = await func(*args, **kwargs)
                cap.output = _extract_llm_output(result)
                cap.tokens_in, cap.tokens_out = _extract_tokens(result)
                return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def trace_tool(func: Callable = None, *, name: str = None):
    """
    Wraps a tool call. Captures tool name, input, output.

    Usage:
        @trace_tool
        def web_search(query: str) -> str:
            ...

        @trace_tool(name="filesystem.write")
        def write_file(path: str, content: str):
            ...
    """

    def decorator(func: Callable):
        tool_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_data = _extract_input(func, args, kwargs)

            with EventCapture(
                event_type="tool_call",
                name=tool_name,
                input=input_data,
            ) as cap:
                result = func(*args, **kwargs)
                cap.output = _safe_serialize(result)
                return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            input_data = _extract_input(func, args, kwargs)

            with EventCapture(
                event_type="tool_call",
                name=tool_name,
                input=input_data,
            ) as cap:
                result = await func(*args, **kwargs)
                cap.output = _safe_serialize(result)
                return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


# ── Helpers ──────────────────────────────────────────────────────────────────


def _extract_input(func, args, kwargs) -> Any:
    try:
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return {k: _safe_serialize(v) for k, v in bound.arguments.items()}
    except Exception:
        return {"args": str(args), "kwargs": str(kwargs)}


def _safe_serialize(obj: Any, max_len: int = 2000) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj if not isinstance(obj, str) or len(obj) <= max_len else obj[:max_len] + "..."
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in list(obj.items())[:20]}
    if isinstance(obj, (list, tuple)):
        serialized = [_safe_serialize(i) for i in obj[:20]]
        return serialized
    try:
        import json

        s = json.dumps(obj, default=str)
        return json.loads(s[:max_len])
    except Exception:
        return str(obj)[:max_len]


def _detect_model(args, kwargs) -> Optional[str]:
    # Common patterns: ollama.chat(model=".."), openai(model="..")
    if "model" in kwargs:
        return str(kwargs["model"])
    for arg in args:
        if isinstance(arg, str) and any(
            x in arg for x in ["gpt", "claude", "qwen", "llama", "gemma", "mistral"]
        ):
            return arg
    return None


def _extract_llm_output(result: Any) -> Any:
    if result is None:
        return None
    # Ollama response
    if hasattr(result, "message"):
        msg = result.message
        content = getattr(msg, "content", str(msg))
        return {"content": content[:1000]}
    # OpenAI response
    if hasattr(result, "choices"):
        content = result.choices[0].message.content
        return {"content": content[:1000] if content else ""}
    # Dict response (common with raw API calls)
    if isinstance(result, dict):
        if "message" in result:
            msg = result["message"]
            if isinstance(msg, dict):
                return {"content": str(msg.get("content", ""))[:1000]}
        if "content" in result:
            return {"content": str(result["content"])[:1000]}
    return _safe_serialize(result)


def _extract_tokens(result: Any) -> tuple[int, int]:
    try:
        # Ollama
        if hasattr(result, "prompt_eval_count"):
            return result.prompt_eval_count or 0, result.eval_count or 0
        # OpenAI
        if hasattr(result, "usage"):
            u = result.usage
            return getattr(u, "prompt_tokens", 0), getattr(u, "completion_tokens", 0)
        # Dict
        if isinstance(result, dict) and "usage" in result:
            u = result["usage"]
            return u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
    except Exception:
        pass
    return 0, 0
