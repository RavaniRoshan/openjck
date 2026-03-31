import { useState, useEffect } from "react";
import { useTraces } from "./hooks/useTraces";
import { Sidebar } from "./components/Sidebar";
import { Timeline } from "./components/Timeline";
import { DetailPanel } from "./components/DetailPanel";
import { formatStamp, formatDuration, formatCurrency } from "./lib/utils";

export default function App() {
  const { traces, selectedTraceId, setSelectedTraceId, selectedTraceData, loading } = useTraces();
  const [selectedStepId, setSelectedStepId] = useState(null);

  useEffect(() => {
    if (selectedTraceData?.steps?.length > 0) {
      setSelectedStepId(selectedTraceData.steps[0].step_id);
    } else {
      setSelectedStepId(null);
    }
  }, [selectedTraceData?.trace_id]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-[260px_minmax(0,1fr)] h-screen overflow-hidden bg-bg text-[#ededed] selection:bg-accent/30 font-sans">
      
      <Sidebar 
        traces={traces} 
        loading={loading}
        selectedTraceId={selectedTraceId} 
        onSelectTrace={setSelectedTraceId} 
      />

      <main className="flex flex-col min-w-0 min-h-0 bg-[#1c1c1c] relative">
        
        {selectedTraceData && (
          <header className="px-8 pt-6 pb-4 border-b border-border flex-none">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div className="min-w-0 flex items-center gap-4">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  selectedTraceData.status === 'completed' ? 'bg-success' : 
                  selectedTraceData.status === 'failed' ? 'bg-error' : 'bg-warning'
                }`} />
                <div>
                  <h1 className="text-xl font-bold tracking-tight mb-1 truncate">
                    {selectedTraceData.run_name || "Unnamed run"}
                  </h1>
                  <div className="flex gap-4 text-xs text-muted">
                    <span>Trace: <span className="font-mono text-[#c2c2c2]">{selectedTraceData.trace_id}</span></span>
                    <span>{formatStamp(selectedTraceData.started_at)}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 h-fit items-center">
                <div className="px-4 py-2 flex flex-col items-end border-r border-[#3e3e3e]">
                  <span className="text-[10px] uppercase tracking-widest text-[#8b8d91] font-semibold">Steps</span>
                  <span className="text-sm font-semibold">{Array.isArray(selectedTraceData.steps) ? selectedTraceData.steps.length : 0}</span>
                </div>
                <div className="px-4 py-2 flex flex-col items-end border-r border-[#3e3e3e]">
                  <span className="text-[10px] uppercase tracking-widest text-[#8b8d91] font-semibold">Duration</span>
                  <span className="text-sm font-semibold">{formatDuration(selectedTraceData.total_duration_ms)}</span>
                </div>
                <div className="px-4 py-2 flex flex-col items-end">
                  <span className="text-[10px] uppercase tracking-widest text-[#8b8d91] font-semibold">Tokens</span>
                  <span className="text-sm font-semibold">{Number(selectedTraceData.total_tokens || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </header>
        )}

        {selectedTraceData && selectedTraceData.steps?.length > 0 && (
          <div className="flex-none border-b border-border bg-[#1E1E1E]">
            <Timeline 
              steps={selectedTraceData.steps} 
              selectedStepId={selectedStepId}
              onSelectStep={setSelectedStepId}
            />
          </div>
        )}

        <DetailPanel 
          trace={selectedTraceData} 
          selectedStepId={selectedStepId} 
          onSelectStep={setSelectedStepId} 
        />
        
      </main>
    </div>
  );
}
