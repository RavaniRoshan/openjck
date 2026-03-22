import Database from 'better-sqlite3';
import { homedir } from 'os';
import { join } from 'path';
import { existsSync, mkdirSync } from 'fs';

const TRACES_DIR = join(homedir(), '.openjck');
const DB_PATH = join(TRACES_DIR, 'openjck.db');

if (!existsSync(TRACES_DIR)) mkdirSync(TRACES_DIR, { recursive: true });

const db = new Database(DB_PATH);

db.exec(`
  CREATE TABLE IF NOT EXISTS runs (
    trace_id TEXT PRIMARY KEY,
    run_name TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    started_at TEXT NOT NULL,
    ended_at TEXT,
    total_steps INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0,
    total_duration_ms INTEGER DEFAULT 0,
    error TEXT,
    metadata TEXT
  );

  CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    step_id INTEGER NOT NULL,
    type TEXT,
    name TEXT,
    input TEXT,
    output TEXT,
    model TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    error TEXT,
    timestamp TEXT,
    FOREIGN KEY (trace_id) REFERENCES runs(trace_id)
  );

  CREATE TABLE IF NOT EXISTS intelligence (
    trace_id TEXT PRIMARY KEY,
    root_cause_step INTEGER,
    root_cause_reason TEXT,
    recovery_point_step INTEGER,
    dependency_chain TEXT,
    anomalies TEXT,
    patterns TEXT,
    computed_at TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at);
  CREATE INDEX IF NOT EXISTS idx_runs_run_name ON runs(run_name);
  CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
  CREATE INDEX IF NOT EXISTS idx_steps_trace_id ON steps(trace_id);
`);

export function insertRun(data) {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO runs (trace_id, run_name, status, started_at, metadata)
    VALUES ( @trace_id, @run_name, @status, @started_at, @metadata)
  `);
  return stmt.run({
    trace_id: data.trace_id,
    run_name: data.run_name || 'agent',
    status: 'running',
    started_at: data.started_at || new Date().toISOString(),
    metadata: JSON.stringify(data.metadata || {})
  });
}

export function insertStep(data) {
  const stmt = db.prepare(`
    INSERT INTO steps
    (trace_id, step_id, type, name, input, output, model, tokens_in, tokens_out, cost_usd, duration_ms, error, timestamp)
    VALUES
    ( @trace_id, @step_id, @type, @name, @input, @output, @model, @tokens_in, @tokens_out, @cost_usd, @duration_ms, @error, @timestamp)
  `);
  db.prepare(`UPDATE runs SET total_steps = total_steps + 1, total_tokens = total_tokens + @tokens, total_cost_usd = total_cost_usd + @cost WHERE trace_id = @trace_id`)
    .run({ tokens: (data.tokens_in || 0) + (data.tokens_out || 0), cost: data.cost_usd || 0, trace_id: data.trace_id });
  return stmt.run({
    trace_id: data.trace_id,
    step_id: data.step_id || 0,
    type: data.type || 'agent_step',
    name: data.name || '',
    input: JSON.stringify(data.input || {}),
    output: JSON.stringify(data.output || {}),
    model: data.model || null,
    tokens_in: data.tokens_in || 0,
    tokens_out: data.tokens_out || 0,
    cost_usd: data.cost_usd || 0,
    duration_ms: data.duration_ms || 0,
    error: data.error || null,
    timestamp: data.timestamp || new Date().toISOString()
  });
}

export function finalizeRun(data) {
  return db.prepare(`
    UPDATE runs SET
      status = @status,
      ended_at = @ended_at,
      total_duration_ms = @total_duration_ms,
      error = @error
    WHERE trace_id = @trace_id
  `).run({
    trace_id: data.trace_id,
    status: data.status || 'completed',
    ended_at: data.ended_at || new Date().toISOString(),
    total_duration_ms: data.total_duration_ms || 0,
    error: data.error || null
  });
}

export function getRuns(filter = {}) {
  let where = '1=1';
  const params = {};
  if (filter.since) { where += ' AND started_at >= @since'; params.since = filter.since; }
  if (filter.status) { where += ' AND status = @status'; params.status = filter.status; }
  if (filter.run_name) { where += ' AND run_name = @run_name'; params.run_name = filter.run_name; }
  return db.prepare(`SELECT * FROM runs WHERE ${where} ORDER BY started_at DESC LIMIT 100`).all(params);
}

export function getRunById(trace_id) {
  const run = db.prepare('SELECT * FROM runs WHERE trace_id = ?').get(trace_id);
  if (!run) return null;
  const steps = db.prepare('SELECT * FROM steps WHERE trace_id = ? ORDER BY step_id ASC').all(trace_id);
  return { ...run, steps: steps.map(s => ({ ...s, input: JSON.parse(s.input || '{}'), output: JSON.parse(s.output || '{}') })) };
}

export function getStats(since) {
  const params = since ? { since } : {};
  const where = since ? 'WHERE started_at >= @since' : '';
  return db.prepare(`
    SELECT
      COUNT(*) as total_runs,
      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
      SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
      SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_runs,
      ROUND(SUM(total_cost_usd), 4) as total_cost,
      ROUND(AVG(CASE WHEN status != 'running' THEN total_duration_ms END), 0) as avg_duration_ms,
      ROUND(AVG(CASE WHEN status != 'running' THEN total_steps END), 1) as avg_steps
    FROM runs ${where}
  `).get(params);
}

export function getAgents(since) {
  const where = since ? 'WHERE started_at >= @since' : '';
  const params = since ? { since } : {};
  return db.prepare(`
    SELECT
      run_name,
      COUNT(*) as total_runs,
      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
      SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
      ROUND(SUM(total_cost_usd), 4) as total_cost,
      ROUND(AVG(total_duration_ms), 0) as avg_duration_ms,
      MAX(started_at) as last_run
    FROM runs ${where}
    GROUP BY run_name
    ORDER BY last_run DESC
  `).all(params);
}

export function saveIntelligence(data) {
  return db.prepare(`
    INSERT OR REPLACE INTO intelligence
    (trace_id, root_cause_step, root_cause_reason, recovery_point_step, dependency_chain, anomalies, patterns, computed_at)
    VALUES ( @trace_id, @root_cause_step, @root_cause_reason, @recovery_point_step, @dependency_chain, @anomalies, @patterns, @computed_at)
  `).run({
    trace_id: data.trace_id,
    root_cause_step: data.root_cause_step || null,
    root_cause_reason: data.root_cause_reason || null,
    recovery_point_step: data.recovery_point_step || null,
    dependency_chain: JSON.stringify(data.dependency_chain || []),
    anomalies: JSON.stringify(data.anomalies || []),
    patterns: JSON.stringify(data.patterns || []),
    computed_at: new Date().toISOString()
  });
}

export function getIntelligence(trace_id) {
  const row = db.prepare('SELECT * FROM intelligence WHERE trace_id = ?').get(trace_id);
  if (!row) return null;
  return {
    ...row,
    dependency_chain: JSON.parse(row.dependency_chain || '[]'),
    anomalies: JSON.parse(row.anomalies || '[]'),
    patterns: JSON.parse(row.patterns || '[]')
  };
}

export default db;
