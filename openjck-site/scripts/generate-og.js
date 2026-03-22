import puppeteer from "puppeteer";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { readFileSync } from "fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(__dirname, "../src/og-image.html"), "utf8");

const browser = await puppeteer.launch({ args: ["--no-sandbox"] });
const page    = await browser.newPage();
await page.setViewport({ width: 1200, height: 630 });
await page.setContent(html, { waitUntil: "networkidle0" });
await page.screenshot({ path: join(__dirname, "../public/og.png"), type: "png" });
await browser.close();
console.log("✅ OG image → public/og.png");
