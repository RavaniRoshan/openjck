import chalk from "chalk";
import figlet from "figlet";

const amber = chalk.hex("#f59e0b");
const dimAmber = chalk.hex("#b47a00");
const brand = chalk.hex("#7c6af7");
const dim = chalk.gray;
const bright = chalk.white;
const green = chalk.green;

const VERSION = "0.2.1";

export function showWelcome(tracesDir) {
  // Generate Figlet text synchronously
  const bannerText = figlet.textSync("OpenJCK", {
    font: "Standard",
    horizontalLayout: "default",
    verticalLayout: "default",
  });

  // Apply colors to the generated text
  const coloredBanner = bannerText
    .split("\n")
    .map((line) => amber(line))
    .join("\n");

  console.log("");
  console.log(coloredBanner);
  console.log(`\n      ${dimAmber("Observability + Reliability for AI Agents")}\n`);

  // ── Status ────────────────────────────────────────
  console.log(`  ${green("✅")} ${bright("OpenJCK")} ${dim(`v${VERSION}`)} ${green("started")}`);
  console.log("");

  // ── Quick Start ───────────────────────────────────
  console.log(`  ${amber("🚀")} ${bright("Quick Start:")}`);
  console.log("");
  console.log(`     ${bright("Open dashboard:")}   ${chalk.cyan("http://localhost:7823")}`);
  console.log(`     ${bright("Trace your code:")}  ${dim("@trace(name=\"agent_name\")")}`);
  console.log(`     ${bright("View results:")}     ${dim("Live in the dashboard")}`);
  console.log("");

  // ── Code Example ──────────────────────────────────
  console.log(`  ${dim("─────────────────────────────────────────────────")}`);
  console.log(`  ${dim("from openjck import trace")}`);
  console.log("");
  console.log(`  ${dim("@trace(name=\"my_agent\")")}`);
  console.log(`  ${dim("def my_function():")}`);
  console.log(`  ${dim("    # Your code here")}`);
  console.log(`  ${dim("    pass")}`);
  console.log(`  ${dim("─────────────────────────────────────────────────")}`);
  console.log("");

  // ── Resources ─────────────────────────────────────
  console.log(`  ${amber("📚")} ${bright("Resources:")}`);
  console.log(`     ${bright("Docs:")}     ${chalk.cyan("https://openjck.dev")}`);
  console.log(`     ${bright("GitHub:")}   ${chalk.cyan("https://github.com/ravaniroshan/openjck")}`);
  console.log(`     ${bright("Issues:")}   ${chalk.cyan("https://github.com/ravaniroshan/openjck/issues")}`);
  console.log("");

  // ── What's Tracked ────────────────────────────────
  console.log(`  ${amber("💡")} ${bright("What's Tracked:")}`);
  console.log(`     ${dim("•")} Step execution with timing`);
  console.log(`     ${dim("•")} Token usage + cost (USD)`);
  console.log(`     ${dim("•")} Tool calls and results`);
  console.log(`     ${dim("•")} Failure root causes`);
  console.log(`     ${dim("•")} Loop detection (same tool 3x)`);
  console.log("");

  // ── Footer ────────────────────────────────────────
  console.log(`  ${dim("Your data stays local. Dashboard runs at")} ${chalk.cyan("http://localhost:7823")}`);
  if (tracesDir) {
    console.log(`  ${dim("Traces:")} ${dim(tracesDir)}`);
  }
  console.log("");
  console.log(`  ${dim("Press")} ${bright("Ctrl+C")} ${dim("to stop the server.")}`);
  console.log("");
}
