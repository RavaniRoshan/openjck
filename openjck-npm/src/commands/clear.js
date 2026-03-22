import { TRACES_DIR } from "../server.js";
import chalk from "chalk";
import { existsSync, readdirSync, rmSync } from "fs";
import { join } from "path";

function readConfirmation() {
  process.stdin.setEncoding("utf8");
  process.stdin.resume();

  return new Promise((resolve) => {
    process.stdin.once("data", (data) => {
      process.stdin.pause();
      resolve(String(data).trim().toLowerCase());
    });
  });
}

export async function clearTraces() {
  if (!existsSync(TRACES_DIR)) {
    console.log(chalk.gray("\n  No traces to clear.\n"));
    return;
  }

  const files = readdirSync(TRACES_DIR).filter((fileName) => fileName.endsWith(".json"));

  if (files.length === 0) {
    console.log(chalk.gray("\n  No traces to clear.\n"));
    return;
  }

  process.stdout.write(
    `${chalk.yellow(`\n  Delete ${files.length} trace(s)? `)}${chalk.gray("(y/N) ")}`,
  );

  const answer = await readConfirmation();

  if (answer !== "y" && answer !== "yes") {
    console.log(chalk.gray("\n  Cancelled.\n"));
    return;
  }

  let deletedCount = 0;

  for (const fileName of files) {
    try {
      rmSync(join(TRACES_DIR, fileName));
      deletedCount += 1;
    } catch {
      // Ignore individual file failures and continue clearing the rest.
    }
  }

  console.log(chalk.green(`\n  ✓ Cleared ${deletedCount} trace(s).\n`));
}
