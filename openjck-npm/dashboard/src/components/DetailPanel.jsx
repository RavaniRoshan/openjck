import { ChevronLeft, ChevronRight, Ban } from "lucide-react";
import { formatStamp, formatDuration } from "../lib/utils";

function JsonViewer({ data }) {
  const jsonStr = data === undefined ? "undefined" : JSON.stringify(data, null, 2);
  
  if (!jsonStr || jsonStr === "null") return <span className="text-error">null</span>;

  const parts = jsonStr.split(/("[\w]+":|"[^"]*"|\btrue\b|\bfalse\b|\bnull\b|-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?)/g);
  
  return (
    <pre className="text-sm font-mono leading-relaxed whitespace-pre-wrap">
      {parts.map((part, i) => {
        if (/^"[\w]+":$/.test(part)) return <span key={i} className="text-[#8b8d91]">{part}</span>;
        if (/^".*"$/.test(part)) return <span key={i} className="text-[#3ecf8e]">{part}</span>;
        if (/true|false/.test(part)) return <span key={i} className="text-[#f5a623]">{part}</span>;
        if (part === "null") return <span key={i} className="text-[#ff5b5b]">{part}</span>;
        if (/^-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?$/.test(part)) return <span key={i} className="text-[#4da6ff]">{part}</span>;
        return <span key={i} className="text-[#e2e2e2]">{part}</span>;
      })}
    </pre>
  );
}

export function DetailPanel({ trace, selectedStepId, onSelectStep }) {
  if (!trace) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 bg-[#161616]">
        <div className="text-center max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded bg-[#1E1E1E] border border-[#2a2a2a] text-sm font-semibold mb-4 text-[#ededed]">
            <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
            OpenJCK
          </div>
          <h2 className="text-2xl font-bold tracking-tight mb-2 text-[#ededed]">
            Trace every loop.<br />Debug every turn.
          </h2>
          <p className="text-[#8b8d91] text-sm">
            Instrument your Python agent, run it locally, and every trace shows up here automatically.
          </p>
        </div>
      </div>
    );
  }

  const steps = Array.isArray(trace.steps) ? trace.steps : [];
  if (steps.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-[#1E1E1E] border border-[#2a2a2a] rounded p-6">
          <h3 className="text-[#ededed] font-semibold text-lg">This trace has no recorded steps yet.</h3>
        </div>
      </div>
    );
  }

  const selected = steps.find((s) => String(s.step_id) === String(selectedStepId)) || steps[0];
  const index = steps.findIndex((s) => String(s.step_id) === String(selected.step_id));
  const totalTokens = Number(selected.tokens_in || 0) + Number(selected.tokens_out || 0);

  const moveStep = (dir) => {
    const next = steps[index + dir];
    if (next) onSelectStep(next.step_id);
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-[#161616]">
      <div className="bg-[#1E1E1E] border border-[#2a2a2a] rounded-lg flex flex-col min-h-full">
        {/* Step Header */}
        <div className="p-5 border-b border-[#2a2a2a]">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="px-2.5 py-1 text-xs font-mono bg-[#2c2c2c] border border-[#3e3e3e] text-[#ededed] rounded">
                Step {selected.step_id}
              </span>
              <h2 className="text-lg font-bold text-[#ededed]">
                {selected.name || selected.type || "Unnamed step"}
              </h2>
              <span className="px-2.5 py-1 text-xs bg-[#2c2c2c] border border-[#3e3e3e] text-[#8b8d91] rounded">
                {selected.type || "unknown"}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2c2c2c] border border-[#3e3e3e] rounded text-sm text-[#ededed] font-semibold">
              <span className="text-[#8b8d91] font-normal text-xs uppercase">Duration</span>
              {formatDuration(selected.duration_ms)}
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="p-5 pb-0">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="bg-[#161616] border border-[#2a2a2a] rounded flex flex-col p-3">
              <div className="text-[10px] uppercase font-bold text-[#8b8d91] mb-1">Started</div>
              <div className="text-[13px] text-[#ededed] font-medium truncate">{formatStamp(selected.started_at)}</div>
            </div>
            <div className="bg-[#161616] border border-[#2a2a2a] rounded flex flex-col p-3">
              <div className="text-[10px] uppercase font-bold text-[#8b8d91] mb-1">Model</div>
              <div className="text-[13px] text-[#ededed] font-medium truncate">{selected.model || "—"}</div>
            </div>
            <div className="bg-[#161616] border border-[#2a2a2a] rounded flex flex-col p-3">
              <div className="text-[10px] uppercase font-bold text-[#8b8d91] mb-1">Tokens In</div>
              <div className="text-[13px] text-[#ededed] font-mono">{Number(selected.tokens_in || 0).toLocaleString()}</div>
            </div>
            <div className="bg-[#161616] border border-[#2a2a2a] rounded flex flex-col p-3">
              <div className="text-[10px] uppercase font-bold text-[#8b8d91] mb-1">Tokens Out</div>
              <div className="text-[13px] text-[#ededed] font-mono">{Number(selected.tokens_out || 0).toLocaleString()}</div>
            </div>
            <div className="bg-[#161616] border border-[#2a2a2a] rounded flex flex-col p-3">
              <div className="text-[10px] uppercase font-bold text-[#8b8d91] mb-1">Total Tokens</div>
              <div className="text-[13px] text-accent font-mono font-bold">{totalTokens.toLocaleString()}</div>
            </div>
          </div>
        </div>

        <div className="flex-1 p-5 flex flex-col gap-5">
          {selected.error && (
            <div className="bg-[#ff5b5b]/10 border border-[#ff5b5b]/30 rounded">
              <div className="px-3 py-2 border-b border-[#ff5b5b]/20 text-[11px] uppercase tracking-wider text-[#ff5b5b] font-bold flex items-center gap-1.5">
                <Ban className="w-3.5 h-3.5" /> Error details
              </div>
              <div className="p-4 overflow-x-auto text-sm text-[#ff5b5b] font-mono">
                {selected.error}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
            <div className="bg-[#161616] border border-[#2a2a2a] rounded overflow-hidden">
              <div className="px-4 py-2 border-b border-[#2a2a2a] bg-[#1a1a1a] text-[11px] uppercase tracking-wider text-[#8b8d91] font-bold">
                Input Payload
              </div>
              <div className="p-4 overflow-x-auto max-h-[500px]">
                <JsonViewer data={selected.input} />
              </div>
            </div>

            <div className="bg-[#161616] border border-[#2a2a2a] rounded overflow-hidden">
              <div className="px-4 py-2 border-b border-[#2a2a2a] bg-[#1a1a1a] text-[11px] uppercase tracking-wider text-[#8b8d91] font-bold">
                Output Payload
              </div>
              <div className="p-4 overflow-x-auto max-h-[500px]">
                <JsonViewer data={selected.output} />
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between p-5 border-t border-[#2a2a2a] mt-auto">
          <div className="flex gap-2">
            <button
              onClick={() => moveStep(-1)}
              disabled={index <= 0}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2c2c2c] hover:bg-[#3e3e3e] border border-[#3e3e3e] rounded text-sm text-[#ededed] transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" /> Prev
            </button>
            <button
              onClick={() => moveStep(1)}
              disabled={index >= steps.length - 1}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2c2c2c] hover:bg-[#3e3e3e] border border-[#3e3e3e] rounded text-sm text-[#ededed] transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="text-xs text-[#8b8d91] font-medium pr-1">
            {index + 1} / {steps.length}
          </div>
        </div>
      </div>
    </div>
  );
}
