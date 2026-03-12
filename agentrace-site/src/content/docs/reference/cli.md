---
title: CLI Commands
description: All AgentTrace CLI commands.
---

# CLI Commands

## Full Command Table

| Command | Description | Example |
|---------|-------------|---------|
| `ui` | Start the web UI at localhost:7823 | `npx @ravaniroshan/agentrace ui` |
| `traces` | List all trace runs in terminal | `npx @ravaniroshan/agentrace traces` |
| `clear` | Delete all traces from ~/.agentrace/traces/ | `npx @ravaniroshan/agentrace clear` |
| `--version` | Print the AgentTrace version | `npx @ravaniroshan/agentrace --version` |
| `--help` | Show help message with all commands | `npx @ravaniroshan/agentrace --help` |

## Environment Variables
- `TRACES_DIR`: Directory where trace JSON files are stored (defaults to `~/.agentrace/traces/`)

## Port
The web UI runs on port **7823** by default. If this port is in use, the CLI will attempt to find the next available port.

## npx vs Global Install Tradeoffs

### npx `@ravaniroshan/agentrace` (Recommended)
- ✅ Always runs the latest version
- ✅ No installation required
- ✅ No version conflicts
- ❌ Slightly slower startup (downloads on first use)

### Global Install (`npm install -g @ravaniroshan/agentrace`)
- ✅ Faster startup after initial install
- ✅ Works offline after installation
- ❌ Requires manual updates (`npm update -g @ravaniroshan/agentrace`)
- ❌ Potential version conflicts in shared environments

## Command Details

### `ui`
Starts the Express server that serves the AgentTrace web UI. By default, it opens at http://localhost:7823. The server automatically loads traces from `~/.agentrace/traces/`.

```bash
# Start UI (same as running with no arguments)
npx @ravaniroshan/agentrace ui
npx @ravaniroshan/agentrace  # equivalent

# Specify custom traces directory
TRACES_DIR=/my/custom/path npx @ravaniroshan/agentrace ui
```

### `traces`
Prints a formatted table of all trace runs to the terminal, showing:
- Trace ID
- Run name
- Timestamp
- Status (completed/failed/running)
- Step count
- Total tokens
- Duration

```bash
npx @ravaniroshan/agentrace traces
```

Sample output:
```
Trace ID        | Run Name         | Started At          | Status    | Steps | Tokens | Duration
----------------|------------------|---------------------|-----------|-------|--------|----------
a3f9c1b2        | research_agent   | 2026-03-12 10:00:00 | completed | 3     | 180    | 1.2s
b4d0e2c3        | chatbot_v2       | 2026-03-12 09:45:00 | failed    | 5     | 420    | 2.1s
```

### `clear`
Permanently deletes all trace JSON files from the traces directory. Use with caution!

```bash
npx @ravaniroshan/agentrace clear
# Prompts for confirmation by default
npx @ravaniroshan/agentrace clear --force  # skip confirmation
```

### `--version`
Outputs the current AgentTrace version:

```bash
npx @ravaniroshan/agentrace --version
# Example output: 0.1.0
```

### `--help`
Displays the help menu with all available commands and options:

```bash
npx @ravaniroshan/agentrace --help
```