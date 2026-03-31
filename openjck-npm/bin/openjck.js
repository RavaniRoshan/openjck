#!/usr/bin/env node

const VERSION = "0.2.1";

const HELP_TEXT = `
  OpenJCK — Visual debugger for AI agent loops

  Usage:
    npx openjck              Start the UI viewer
    npx openjck ui           Start the UI viewer
    npx openjck traces       List all recorded traces in terminal
    npx openjck clear        Delete all traces
    npx openjck --version    Show version
    npx openjck --help       Show this help

  The UI opens at http://localhost:7823
  Traces are read from ~/.openjck/traces/

  Python library (instrument your agent):
    pip install openjck

  Docs: https://github.com/RavaniRoshan/openjck
`;

async function main() {
  const [rawCommand] = process.argv.slice(2);
  const command = rawCommand ?? "ui";

  switch (command) {
    case "ui":
    case "start": {
      const { startUI } = await import("../src/commands/ui.js");
      await startUI();
      return;
    }
    case "traces":
    case "list": {
      const { listTraces } = await import("../src/commands/traces.js");
      await listTraces();
      return;
    }
    case "clear": {
      const { clearTraces } = await import("../src/commands/clear.js");
      await clearTraces();
      return;
    }
    case "--version":
    case "-v":
      console.log(VERSION);
      return;
    case "--help":
    case "-h":
      console.log(HELP_TEXT);
      return;
    default:
      console.error(`Unknown command: ${command}`);
      console.error("Run openjck --help to see available commands.");
      process.exitCode = 1;
  }
}

try {
  await main();
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Error: ${message}`);
  process.exit(1);
}
