import { listAllTraces, TRACES_DIR } from "../server.js";
import chalk from "chalk";
import { existsSync } from "fs";

function formatDuration(durationMs) {
  if (durationMs == null) {
    return "—";
  }

  if (durationMs < 1000) {
    return `${Math.round(durationMs)}ms`;
  }

  return `${(durationMs / 1000).toFixed(2)}s`;
}

function getStatusColor(status) {
  if (status === "completed") {
    return chalk.green;
  }

  if (status === "failed") {
    return chalk.red;
  }

  return chalk.yellow;
}

export async function listTraces() {
  const traces = existsSync(TRACES_DIR) ? listAllTraces() : [];

  if (!existsSync(TRACES_DIR) || traces.length === 0) {
    console.log(chalk.gray("\n  No traces found. Run your agent first.\n"));
    console.log(`${chalk.gray("  Traces are stored at: ")}${chalk.white(TRACES_DIR)}`);
    console.log("");
    return;
  }

  console.log("");
    console.log(chalk.hex("#7c6af7")("  OpenJCK — Recorded Runs"));
  console.log("");
  console.log(
    chalk.gray(
      `  ${"ID".padEnd(12)}${"Name".padEnd(28)}${"Status".padEnd(12)}${"Steps".padEnd(8)}${"Duration".padEnd(12)}Tokens`,
    ),
  );
  console.log(chalk.gray(`  ${"─".repeat(76)}`));

  for (const trace of traces) {
    const statusText = String(trace.status ?? "unknown");
    const statusCell = getStatusColor(statusText)(statusText.padEnd(12));
    const costSuffix =
      Number(trace.total_cost_usd) > 0
        ? chalk.gray(` ($${Number(trace.total_cost_usd).toFixed(4)})`)
        : "";

    const row =
      `  ${chalk.hex("#7c6af7")(String(trace.trace_id ?? "").padEnd(12))}` +
      `${chalk.white(String(trace.run_name ?? "").slice(0, 26).padEnd(28))}` +
      `${statusCell}` +
      `${chalk.gray(String(trace.step_count ?? 0).padEnd(8))}` +
      `${chalk.gray(formatDuration(trace.total_duration_ms).padEnd(12))}` +
      `${chalk.gray(String(trace.total_tokens || 0))}` +
      costSuffix;

    console.log(row);

    if (trace.error != null && String(trace.error).trim() !== "") {
      console.log(`  ${" ".repeat(12)}${chalk.red(`✕ ${String(trace.error).slice(0, 60)}`)}`);
    }
  }

  console.log("");
  process.stdout.write(chalk.gray(`  ${traces.length} run(s) total  ·  `));
  process.stdout.write(chalk.cyan("npx openjck ui"));
  process.stdout.write(chalk.gray(" to view in browser"));
  process.stdout.write("\n\n");
}
