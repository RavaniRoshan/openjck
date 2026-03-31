import express from "express";
import {
  existsSync,
  readdirSync,
  readFileSync,
  statSync,
  unlinkSync,
} from "fs";
import { dirname, join } from "path";
import { homedir } from "os";
import { fileURLToPath } from "url";
import { insertRun, insertStep, finalizeRun, getStats, getRuns, getRunById, getAgents, getIntelligence, saveIntelligence } from './db.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const sseClients = new Set();

function emitSSE(payload) {
  const msg = `data: ${JSON.stringify(payload)}\n\n`;
  for (const res of sseClients) {
    try { res.write(msg); } catch { sseClients.delete(res); }
  }
}

export const PORT = 7823;
export const TRACES_DIR = join(homedir(), ".openjck", "traces");
export const UI_FILE = join(__dirname, "ui", "index.html");

function withCors(req, res, next) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.sendStatus(200);
    return;
  }

  next();
}

function toTraceSummary(trace) {
  return {
    trace_id: trace.trace_id,
    run_name: trace.run_name,
    started_at: trace.started_at,
    status: trace.status,
    total_duration_ms: trace.total_duration_ms,
    total_tokens: trace.total_tokens,
    total_cost_usd: trace.total_cost_usd,
    step_count: Array.isArray(trace.steps) ? trace.steps.length : 0,
    error: trace.error,
  };
}

function matchesFilters(trace, filters) {
  const { q, status, model, from_date, to_date } = filters;

  if (q != null) {
    const runName = String(trace.run_name ?? "").toLowerCase();
    if (!runName.includes(String(q).toLowerCase())) {
      return false;
    }
  }

  if (status != null && trace.status !== status) {
    return false;
  }

  if (model != null) {
    const steps = Array.isArray(trace.steps) ? trace.steps : [];
    const hasModel = steps.some((step) => step?.model === model);
    if (!hasModel) {
      return false;
    }
  }

  if (from_date != null) {
    const startedAt = String(trace.started_at ?? "");
    if (startedAt < String(from_date)) {
      return false;
    }
  }

  if (to_date != null) {
    const startedAt = String(trace.started_at ?? "");
    if (startedAt > `${to_date}T23:59:59Z`) {
      return false;
    }
  }

  return true;
}

export function listAllTraces(filters = {}) {
  if (!existsSync(TRACES_DIR)) {
    return [];
  }

  return readdirSync(TRACES_DIR)
    .filter((fileName) => fileName.endsWith(".json"))
    .map((fileName) => {
      const filePath = join(TRACES_DIR, fileName);

      try {
        const trace = JSON.parse(readFileSync(filePath, "utf8"));
        return {
          trace,
          summary: toTraceSummary(trace),
          mtimeMs: statSync(filePath).mtimeMs,
        };
      } catch {
        return null;
      }
    })
    .filter((entry) => entry !== null)
    .sort((a, b) => b.mtimeMs - a.mtimeMs)
    .filter((entry) => matchesFilters(entry.trace, filters))
    .map((entry) => entry.summary);
}

export function loadTrace(traceId) {
  const filePath = join(TRACES_DIR, `${traceId}.json`);

  if (!existsSync(filePath)) {
    return null;
  }

  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

export function deleteTrace(traceId) {
  const filePath = join(TRACES_DIR, `${traceId}.json`);

  if (!existsSync(filePath)) {
    return false;
  }

  unlinkSync(filePath);
  return true;
}

export function createApp() {
  const app = express();

  app.use(withCors);
  app.options("*", (req, res) => {
    res.sendStatus(200);
  });

  app.use(express.json());

  // ─── Event Ingestion ─────────────────────────
  app.post('/v1/run/start', (req, res) => {
    try {
      const data = req.body;
      if (!data.trace_id) return res.status(400).json({ error: 'trace_id required' });
      insertRun(data);
      emitSSE({ event: 'run_start', data });
      res.json({ ok: true, trace_id: data.trace_id });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  app.post('/v1/run/step', (req, res) => {
    try {
      const data = req.body;
      if (!data.trace_id) return res.status(400).json({ error: 'trace_id required' });
      insertStep(data);
      emitSSE({ event: 'run_step', data });
      res.json({ ok: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

app.post('/v1/run/end', (req, res) => {
  try {
    const data = req.body;
    if (!data.trace_id) return res.status(400).json({ error: 'trace_id required' });
    finalizeRun(data);
    emitSSE({ event: 'run_end', data });

    // Intelligence computation for failed runs
    if (data.status === 'failed') {
      setImmediate(async () => {
        try {
          // First try database, then fall back to JSON file
          let fullTrace = getRunById(data.trace_id);
          if (!fullTrace) {
            fullTrace = loadTrace(data.trace_id);
          }
          if (fullTrace) {
            // Call Python intelligence endpoint
            const resp = await fetch(`http://localhost:7823/v1/internal/analyse`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(fullTrace)
            });
            if (resp.ok) {
              const intel = await resp.json();
              saveIntelligence(intel);
              emitSSE({ event: 'intelligence_ready', data: { trace_id: data.trace_id, intel } });
            }
          }
        } catch (e) { 
          // Intelligence is best-effort, don't crash
        }
      });
    }

    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

  // ─── Dashboard Data ───────────────────────────
  app.get('/v1/stats', (req, res) => {
    const since = getSinceTimestamp(req.query.period || '24h');
    res.json(getStats(since));
  });

  app.get('/v1/traces', (req, res) => {
    const since = getSinceTimestamp(req.query.period || '24h');
    const runs = getRuns({
      since,
      status: req.query.status || null,
      run_name: req.query.agent || null
    });
    res.json(runs);
  });

  app.get('/v1/traces/:id', (req, res) => {
    const run = getRunById(req.params.id);
    if (!run) return res.status(404).json({ error: 'not found' });
    const intel = getIntelligence(req.params.id);
    res.json({ ...run, intelligence: intel });
  });

  app.get('/v1/agents', (req, res) => {
    const since = getSinceTimestamp(req.query.period || '24h');
    res.json(getAgents(since));
  });

  app.get('/v1/intelligence/:id', (req, res) => {
    const intel = getIntelligence(req.params.id);
    if (!intel) return res.status(404).json({ error: 'not found' });
    res.json(intel);
  });

  // Helper: convert period string to ISO timestamp
  function getSinceTimestamp(period) {
    if (period === 'all') return null;
    const ms = { '24h': 86400000, '7d': 604800000, '30d': 2592000000 };
    return new Date(Date.now() - (ms[period] || ms['24h'])).toISOString();
  }

  // Internal intelligence analysis endpoint
  app.post('/v1/internal/analyse', async (req, res) => {
    try {
      // Spawn Python to run intelligence analysis
      const { spawn } = await import('child_process');
      const trace = JSON.stringify(req.body);
      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
      const py = spawn(pythonCmd, ['-c', `
import sys, json
from openjck.intelligence import analyse_trace

trace = json.loads(sys.stdin.read())
result = analyse_trace(trace)
print(json.dumps({
    'trace_id': result.trace_id,
    'root_cause_step': result.root_cause_step,
    'root_cause_reason': result.root_cause_reason,
    'recovery_point_step': result.recovery_point_step,
    'dependency_chain': result.dependency_chain,
    'anomalies': result.anomalies,
    'patterns': result.patterns
}))
`], { env: process.env });

      let output = '';
      
      py.stdin.write(trace);
      py.stdin.end();
      
      py.stdout.on('data', d => output += d.toString());
      
      py.on('close', (code) => {
        const trimmed = output.trim();
        if (trimmed) {
          try {
            res.json(JSON.parse(trimmed));
          } catch (e) {
            res.json({ trace_id: req.body.trace_id || null });
          }
        } else {
          res.json({ trace_id: req.body.trace_id || null });
        }
      });
    } catch (e) {
      res.status(500).json({ trace_id: req.body.trace_id || null });
    }
  });

  app.get('/v1/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.write('data: {"event":"connected"}\n\n');
    sseClients.add(res);
    req.on('close', () => sseClients.delete(res));
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", version: "0.2.1", runtime: "node" });
  });

  app.get("/api/traces", (req, res) => {
    const { q, status, model, from_date, to_date } = req.query;
    const traces = listAllTraces({ q, status, model, from_date, to_date });
    res.json(traces);
  });

  app.get("/api/traces/:traceId", (req, res) => {
    const trace = loadTrace(req.params.traceId);

    if (trace === null) {
      res.status(404).json({ error: "Trace not found" });
      return;
    }

    res.json(trace);
  });

  app.delete("/api/traces/:traceId", (req, res) => {
    const deleted = deleteTrace(req.params.traceId);

    if (!deleted) {
      res.status(404).json({ error: "Trace not found" });
      return;
    }

    res.json({ deleted: req.params.traceId });
  });

  // Serve the compiled Vite static assets from src/ui/
  const UI_DIR = join(__dirname, "ui");
  app.use(express.static(UI_DIR));

  app.get("*", (req, res) => {
    res.sendFile(join(UI_DIR, "index.html"));
  });

  return app;
}

export function migrateLegacyTraces() {
      const legacyDir = join(homedir(), '.openjck', 'traces');
  if (!existsSync(legacyDir)) return;
  const files = readdirSync(legacyDir).filter(f => f.endsWith('.json'));
  let migrated = 0;
  for (const file of files) {
    try {
      const raw = JSON.parse(readFileSync(join(legacyDir, file), 'utf8'));
      const existing = getRunById(raw.trace_id);
      if (existing) continue;
      insertRun({
        trace_id: raw.trace_id,
        run_name: raw.run_name || 'agent',
        started_at: raw.started_at || new Date().toISOString(),
      });
      for (const step of (raw.steps || [])) {
        insertStep({ ...step, trace_id: raw.trace_id });
      }
      finalizeRun({
        trace_id: raw.trace_id,
        status: raw.status || 'completed',
        ended_at: raw.ended_at || raw.started_at,
        total_duration_ms: raw.total_duration_ms || 0,
        error: raw.error || null
      });
      migrated++;
    } catch { /* skip malformed files */ }
  }
  if (migrated > 0) console.log(`[OpenJCK] Migrated ${migrated} legacy traces to dashboard`);
}


