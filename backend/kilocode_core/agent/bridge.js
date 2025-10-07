#!/usr/bin/env node
// bridge.js — Kilocode subprocess adapter
import fs from "fs";
import path from "path";
import { runAgent } from "./dist/index.js"; // adjust if exported differently

async function main() {
  const inputPath = process.argv[2];
  if (!inputPath) {
    console.error("Missing input path");
    process.exit(1);
  }
  const raw = fs.readFileSync(inputPath, "utf8");
  const data = JSON.parse(raw);

  const result = await runAgent(data.mode, data.input);
  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error("Agent error:", err);
  process.exit(1);
});