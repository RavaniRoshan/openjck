"""LangChain auto-instrumentation for AgentTrace."""

from __future__ import annotations

import functools
import threading
from typing import Any, Callable, Tuple

from ..collector import EventCapture

_PATCH_LOCK = threading.Lock()
_PATCHED = False
_ORIGINALS: dict[tuple[type, str], Callable[..., Any]] = {}


def patch() -> None:
    """Monkey-patch LangChain primitives for automatic tracing.

    Raises:
        ImportError: If LangChain is not installed.
    """
    global _PATCHED

    if _PATCHED:
        return

    with _PATCH_LOCK:
        if _PATCHED:
            return

        try:
            from langchain.chains.base import Chain
            from langchain_core.language_models.base import BaseLanguageModel
            from langchain_core.tools.base import BaseTool
        except ImportError as exc:
            raise ImportError(
                "LangChain is not installed. Install it with `pip install langchain` "
                "(and provider packages), then call `agentrace.patch_langchain()`."
            ) from exc

        _patch_sync_llm_method(BaseLanguageModel, "__call__")
        _patch_sync_llm_method(BaseLanguageModel, "invoke")

        _patch_sync_tool_method(BaseTool, "_run")
        _patch_async_tool_method(BaseTool, "_arun")

        _patch_sync_chain_method(Chain, "__call__")
        _patch_sync_chain_method(Chain, "invoke")

        _PATCHED = True


def _save_original(cls: type, method_name: str) -> Callable[..., Any] | None:
    key = (cls, method_name)
    current = getattr(cls, method_name, None)
    if current is None:
        return None
    if key not in _ORIGINALS:
        _ORIGINALS[key] = current
    return _ORIGINALS[key]


def _patch_sync_llm_method(cls: type, method_name: str) -> None:
    original = _save_original(cls, method_name)
    if original is None:
        return

    @functools.wraps(original)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        messages = _extract_llm_input(args, kwargs)
        model_name = _detect_model_name(self)
        with EventCapture("llm_call", model_name, input=messages, model=model_name) as cap:
            result = original(self, *args, **kwargs)
            cap.output = _extract_output_content(result)
            cap.tokens_in, cap.tokens_out = _extract_token_counts(result)
            return result

    setattr(cls, method_name, wrapped)


def _patch_sync_tool_method(cls: type, method_name: str) -> None:
    original = _save_original(cls, method_name)
    if original is None:
        return

    @functools.wraps(original)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        tool_input = _extract_tool_input(args, kwargs)
        tool_name = getattr(self, "name", self.__class__.__name__)
        with EventCapture("tool_call", str(tool_name), input=tool_input) as cap:
            result = original(self, *args, **kwargs)
            cap.output = _coerce_to_string(result)
            return result

    setattr(cls, method_name, wrapped)


def _patch_async_tool_method(cls: type, method_name: str) -> None:
    original = _save_original(cls, method_name)
    if original is None:
        return

    @functools.wraps(original)
    async def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        tool_input = _extract_tool_input(args, kwargs)
        tool_name = getattr(self, "name", self.__class__.__name__)
        with EventCapture("tool_call", str(tool_name), input=tool_input) as cap:
            result = await original(self, *args, **kwargs)
            cap.output = _coerce_to_string(result)
            return result

    setattr(cls, method_name, wrapped)


def _patch_sync_chain_method(cls: type, method_name: str) -> None:
    original = _save_original(cls, method_name)
    if original is None:
        return

    @functools.wraps(original)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        inputs = _extract_chain_inputs(args, kwargs)
        chain_name = getattr(self, "name", self.__class__.__name__)
        with EventCapture("agent_step", str(chain_name), input=inputs):
            return original(self, *args, **kwargs)

    setattr(cls, method_name, wrapped)


def _extract_llm_input(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if "input" in kwargs:
        return kwargs["input"]
    if "messages" in kwargs:
        return kwargs["messages"]
    return args[0] if args else None


def _extract_tool_input(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if "tool_input" in kwargs:
        return kwargs["tool_input"]
    if len(args) == 1:
        return args[0]
    if args:
        return {"args": args, "kwargs": kwargs}
    return kwargs or None


def _extract_chain_inputs(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if "inputs" in kwargs:
        return kwargs["inputs"]
    if "input" in kwargs:
        return kwargs["input"]
    return args[0] if args else kwargs or None


def _detect_model_name(llm: Any) -> str:
    for attr in ("model_name", "model", "model_id", "deployment_name"):
        value = getattr(llm, attr, None)
        if value:
            return str(value)
    return llm.__class__.__name__


def _extract_output_content(result: Any) -> Any:
    if result is None:
        return None
    content = getattr(result, "content", None)
    if content is not None:
        return content
    if isinstance(result, dict):
        if "content" in result:
            return result["content"]
        if "output" in result:
            return result["output"]
    return str(result)


def _extract_token_counts(result: Any) -> Tuple[int, int]:
    if result is None:
        return 0, 0

    usage = getattr(result, "usage_metadata", None)
    if isinstance(usage, dict):
        return int(usage.get("input_tokens", 0) or 0), int(usage.get("output_tokens", 0) or 0)

    response_metadata = getattr(result, "response_metadata", None)
    if isinstance(response_metadata, dict):
        token_usage = response_metadata.get("token_usage") or response_metadata.get("usage")
        if isinstance(token_usage, dict):
            return (
                int(token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0)) or 0),
                int(token_usage.get("completion_tokens", token_usage.get("output_tokens", 0)) or 0),
            )

    usage_obj = getattr(result, "usage", None)
    if usage_obj is not None:
        return (
            int(getattr(usage_obj, "prompt_tokens", 0) or 0),
            int(getattr(usage_obj, "completion_tokens", 0) or 0),
        )

    if isinstance(result, dict):
        token_usage = result.get("token_usage") or result.get("usage")
        if isinstance(token_usage, dict):
            return (
                int(token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0)) or 0),
                int(token_usage.get("completion_tokens", token_usage.get("output_tokens", 0)) or 0),
            )

    return 0, 0


def _coerce_to_string(value: Any) -> str:
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)
