import { RefreshCw, Activity } from "lucide-react";
import { cn, formatDuration, formatRelative, statusClass } from "../lib/utils";

const statusDots = {
  completed: "bg-success",
  failed: "bg-error",
  running: "bg-warning",
  unknown: "bg-info",
};

export function Sidebar({ traces, loading, selectedTraceId, onSelectTrace }) {
  return (
    <aside className="flex flex-col h-full bg-[#131313] border-r border-[#2a2a2a]">
      <div className="p-4 border-b border-[#2a2a2a]">
        <div className="flex items-center gap-2 font-bold text-[#ededed] text-lg">
          <Activity className="w-5 h-5 text-accent" />
          OpenJCK
        </div>
        <p className="mt-2 text-muted text-xs leading-relaxed">
          Visual debugger for AI agent loops.
        </p>
      </div>

      <div className="flex justify-between items-center px-4 py-3 border-b border-[#2a2a2a]">
        <div className="text-[11px] font-bold text-muted uppercase tracking-wider">Recent Runs</div>
        <button 
          className="p-1 hover:bg-[#2a2a2a] rounded text-muted hover:text-[#ededed] transition-colors"
          onClick={() => window.location.reload()}
          title="Refresh"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2">
        {loading ? (
          <div className="text-muted text-sm p-4 text-center">Loading...</div>
        ) : traces.length === 0 ? (
          <div className="text-muted text-sm p-4 text-center">
            No traces yet. Run your agent to begin.
          </div>
        ) : (
          <div className="flex flex-col">
            {traces.map((trace) => {
              const isActive = trace.trace_id === selectedTraceId;
              const status = statusClass(trace.status);

              return (
                <button
                  key={trace.trace_id}
                  onClick={() => onSelectTrace(trace.trace_id)}
                  className={cn(
                    "w-full text-left px-4 py-3 border-l-2 transition-colors",
                    isActive
                      ? "bg-[#2a2a2a] border-accent"
                      : "border-transparent hover:bg-[#1E1E1E]"
                  )}
                >
                  <div className={cn(
                    "font-semibold text-[13px] truncate",
                    isActive ? "text-[#ededed]" : "text-[#c2c2c2]"
                  )}>
                    {trace.run_name || "Unnamed run"}
                  </div>
                  <div className="flex justify-between items-center mt-1.5 text-xs text-muted">
                    <span className="flex items-center gap-1.5 capitalize">
                      <span className={cn("w-1.5 h-1.5 rounded-full", statusDots[status])}></span>
                      {status}
                    </span>
                    <span>{trace.step_count || 0} steps</span>
                  </div>
                  <div className="flex justify-between items-center mt-1 text-[11px] text-muted/70">
                    <span>{formatDuration(trace.total_duration_ms)}</span>
                    <span>{formatRelative(trace.started_at)}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}
