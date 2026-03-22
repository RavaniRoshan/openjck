---
title: Dashboard
description: Live monitoring dashboard for all your AI agent runs.
---

The OpenJCK dashboard is a live web interface that shows all your agent runs in real-time. No configuration required — it automatically discovers traces as your agents run.

## Opening the Dashboard

```bash
npx openjck
```

Or with the global install:

```bash
openjck ui
```

The dashboard opens at `http://localhost:7823`.

## Dashboard Views

### Overview (Home)

The main view shows all agent runs across all agents:

- **Stat row**: Total runs, total cost, success rate, average duration
- **Runs table**: Every run with status, name, steps, cost, duration, and time
- **Live updates**: New runs appear automatically every 2 seconds
- **Time filters**: Switch between last 24h, 7 days, or all time

### Agent Drill-down

Click any agent name to see runs filtered to that specific agent:

- Agent-specific stats (runs, cost, success rate, avg steps)
- Patterns section showing:
  - Most common failure step
  - Most expensive step on average
- Filtered runs table

### Trace Detail

Click any run row to see the full execution timeline:

- Step-by-step timeline with color-coded dots
- Step detail panel with input/output/error
- Intelligence panel (for failed runs) showing root cause analysis
- Click any step dot to inspect that step

## Live Updates

The dashboard polls the server every 2 seconds. New runs appear with a brief amber flash animation. The "last updated" counter in the top-right shows how fresh the data is.

## Time Filters

Three time ranges are available:

- **24h**: Last 24 hours (default)
- **7d**: Last 7 days
- **all**: All time

Click any filter button to switch. The stat row and runs table update immediately.

## Status Indicators

Each run shows a colored status dot:

- 🟢 **Green**: Completed successfully
- 🔴 **Red**: Failed with error
- 🟡 **Amber (pulsing)**: Currently running

## Failed Run Intelligence

Failed runs show an inline intelligence preview:

```
🔍 Root cause: Step 3 — FileNotFoundError: data/missing.csv
[View Step 3 →]
```

Click "View Step N" to open the trace detail focused on the root cause step.

## Mobile Support

The dashboard is responsive:

- **Desktop**: Full 4-column stat cards, all table columns
- **Tablet**: 2-column stats, all table columns
- **Mobile**: 2-column stats, simplified table (hides cost/duration columns)

## Keyboard Shortcuts

- Click any row to open trace detail
- Click agent name to filter by agent
- Click "Back" button to return to previous view
- URL updates automatically — share `/trace/:id` links

## Troubleshooting

**Dashboard shows "Cannot connect to OpenJCK server"**

The server isn't running. Start it with:

```bash
npx openjck
```

**No traces appear**

Run your instrumented agent first:

```python
from openjck import trace

@trace(name="my_agent")
def run():
    # your agent code
    pass

run()
```

Traces appear automatically in the dashboard.
