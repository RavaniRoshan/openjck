import { useState, useEffect, useCallback } from "react";

export function useTraces() {
  const [traces, setTraces] = useState([]);
  const [selectedTraceId, setSelectedTraceId] = useState(null);
  const [selectedTraceData, setSelectedTraceData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTraces = useCallback(async () => {
    try {
      const res = await fetch("/api/traces");
      if (res.ok) {
        const data = await res.json();
        setTraces(data);
      }
    } catch (e) {
      console.error("Failed to fetch traces", e);
    }
  }, []);

  const fetchTraceDetails = useCallback(async (traceId) => {
    if (!traceId) return;
    try {
      const res = await fetch(`/api/traces/${encodeURIComponent(traceId)}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedTraceData(data);
      } else {
        setSelectedTraceData(null);
      }
    } catch (e) {
      console.error("Failed to fetch trace details", e);
      setSelectedTraceData(null);
    }
  }, []);

  useEffect(() => {
    fetchTraces().then(() => setLoading(false));
    const interval = setInterval(fetchTraces, 5000);
    return () => clearInterval(interval);
  }, [fetchTraces]);

  // Sync details when ID changes or interval ticks
  useEffect(() => {
    if (selectedTraceId) {
      fetchTraceDetails(selectedTraceId);
      const interval = setInterval(() => fetchTraceDetails(selectedTraceId), 5000);
      return () => clearInterval(interval);
    } else {
      setSelectedTraceData(null);
    }
  }, [selectedTraceId, fetchTraceDetails]);

  // Auto-select first trace if none selected
  useEffect(() => {
    if (traces.length > 0 && !selectedTraceId) {
      setSelectedTraceId(traces[0].trace_id);
    }
  }, [traces, selectedTraceId]);

  return { traces, selectedTraceId, setSelectedTraceId, selectedTraceData, loading };
}
