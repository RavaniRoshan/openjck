---
title: CLI Commands
description: All OpenJCK CLI commands.
---

# CLI Commands

## Full Command Table

| Command | Description | Example |
|---------|-------------|---------|
| `ui` | Start the web UI at localhost:7823 | `npx openjck ui` |
| `traces` | List all trace runs in terminal | `npx openjck traces` |
| `clear` | Delete all traces from ~/.openjck/traces/ | `npx openjck clear` |
| `--version` | Print the OpenJCK version | `npx openjck --version` |
| `--help` | Show help message with all commands | `npx openjck --help` |

## Environment Variables
- `TRACES_DIR`: Directory where trace JSON files are stored (defaults to `~/.openjck/traces/`)

## Port
The web UI runs on port **7823** by default. If this port is in use, the CLI will attempt to find the next available port.

## npx vs Global Install Tradeoffs

### npx `openjck` (Recommended)
- ✅ Always runs the latest version
- ✅ No installation required
- ✅ No version conflicts
- ❌ Slightly slower startup (downloads on first use)

### Global Install (`npm install -g openjck`)
- ✅ Faster startup after initial install
- ✅ Works offline after installation
- ❌ Requires manual updates (`npm update -g openjck`)
- ❌ Potential version conflicts in shared environments

## Command Details

### `ui`
Starts the Express server that serves the OpenJCK web UI. By default, it opens at http://localhost:7823. The server automatically loads traces from `~/.openjck/traces/`.

```bash
# Start UI (same as running with no arguments)
npx openjck ui
npx openjck  # equivalent

# Specify custom traces directory
TRACES_DIR=/my/custom/path npx openjck ui
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
npx openjck traces
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
npx openjck clear
# Prompts for confirmation by default
npx openjck clear --force  # skip confirmation
```

### `--version`
Outputs the current OpenJCK version:

```bash
npx openjck --version
# Example output: 0.1.0
```

### `--help`
Displays the help menu with all available commands and options:

```bash
npx openjck --help
```