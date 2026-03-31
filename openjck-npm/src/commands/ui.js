import { createApp, PORT, TRACES_DIR, migrateLegacyTraces } from "../server.js";
import { existsSync, mkdirSync } from "fs";
import { createServer } from "http";
import chalk from "chalk";
import ora from "ora";
import open from "open";
import { showWelcome } from "../welcome.js";

export async function startUI() {
  if (!existsSync(TRACES_DIR)) {
    mkdirSync(TRACES_DIR, { recursive: true });
  }

  const spinner = ora({
    text: "Starting OpenJCK...",
    color: "magenta",
  }).start();

  const app = createApp();
  migrateLegacyTraces();
  const server = createServer(app);

  await new Promise((resolve, reject) => {
    server.once("error", (error) => {
      if (error?.code === "EADDRINUSE") {
        spinner.stop();
        console.log("");
        console.log("  Port 7823 is already in use.");
        console.log("  OpenJCK may already be running.");
        console.log("  Open: http://localhost:7823");
        console.log("");
        process.exit(0);
      }

      reject(error);
    });

    server.listen(PORT, () => {
      server.removeAllListeners("error");
      resolve();
    });
  });

  spinner.stop();

  // Show the branded welcome banner after server is ready
  showWelcome(TRACES_DIR);

  try {
    await open("http://localhost:7823");
  } catch {
    // Best effort: keep server running even if browser launch fails.
  }

  process.once("SIGINT", () => {
    console.log(chalk.gray("\n\n  OpenJCK stopped.\n"));
    process.exit(0);
  });

  await new Promise(() => {});
}
