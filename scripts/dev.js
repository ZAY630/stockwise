#!/usr/bin/env node

/**
 * StockWise Dev Launcher
 *
 * Single command: `node scripts/dev.js` or `pnpm dev` from root.
 *
 * What it does:
 * 1. Checks .env has ANTHROPIC_API_KEY set
 * 2. Sets up Python venv + deps if needed
 * 3. Installs frontend deps if needed
 * 4. Starts backend and frontend concurrently
 * 5. Opens browser when ready
 */

const { spawn, execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const BACKEND_DIR = path.join(ROOT, "apps", "backend");
const FRONTEND_DIR = path.join(ROOT, "apps", "frontend");

// Colors for terminal output
const colors = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
  bold: "\x1b[1m",
};

function log(color, prefix, msg) {
  console.log(`${color}[${prefix}]${colors.reset} ${msg}`);
}

function checkCommand(cmd, name) {
  try {
    execSync(`${cmd} --version`, { stdio: "pipe" });
    return true;
  } catch {
    log(colors.red, "ERROR", `${name} is not installed or not in PATH.`);
    return false;
  }
}

function isWindows() {
  return process.platform === "win32";
}

function pythonCmd() {
  // Try python3 first, then python
  try {
    execSync("python3 --version", { stdio: "pipe" });
    return "python3";
  } catch {
    return "python";
  }
}

function activateVenvCmd() {
  if (isWindows()) {
    return path.join(BACKEND_DIR, ".venv", "Scripts", "activate");
  }
  return `source ${path.join(BACKEND_DIR, ".venv", "bin", "activate")}`;
}

async function main() {
  console.log("");
  log(
    colors.blue + colors.bold,
    "StockWise",
    "Starting development environment...",
  );
  console.log("");

  // --- Check prerequisites ---
  if (!checkCommand("node", "Node.js")) process.exit(1);

  const python = pythonCmd();
  if (!checkCommand(python, "Python")) {
    log(colors.red, "HINT", "Install Python 3.12+ from https://python.org");
    process.exit(1);
  }

  // Check pnpm or install it
  try {
    execSync("pnpm --version", { stdio: "pipe" });
  } catch {
    log(colors.yellow, "SETUP", "Installing pnpm...");
    execSync("npm install -g pnpm", { stdio: "inherit" });
  }

  // --- Check .env ---
  const envPath = path.join(ROOT, ".env");
  const envExamplePath = path.join(ROOT, ".env.example");

  if (!fs.existsSync(envPath)) {
    log(colors.yellow, "SETUP", "Creating .env from .env.example...");
    fs.copyFileSync(envExamplePath, envPath);
    log(colors.red, "ACTION", "Edit .env and add your ANTHROPIC_API_KEY, then re-run.");
    process.exit(1);
  }

  const envContent = fs.readFileSync(envPath, "utf-8");
  if (envContent.includes("ANTHROPIC_API_KEY=your-api-key-here")) {
    log(colors.red, "ERROR", "ANTHROPIC_API_KEY is not set in .env!");
    log(colors.red, "ACTION", 'Edit .env and replace "your-api-key-here" with your real API key.');
    process.exit(1);
  }
  log(colors.green, "✓", "API key found in .env");

  // --- Setup backend ---
  const venvDir = path.join(BACKEND_DIR, ".venv");
  const venvPython = isWindows()
    ? path.join(venvDir, "Scripts", "python.exe")
    : path.join(venvDir, "bin", "python");

  if (!fs.existsSync(venvPython)) {
    log(colors.yellow, "SETUP", "Creating Python virtual environment...");
    execSync(`"${python}" -m venv "${venvDir}"`, { stdio: "inherit", cwd: BACKEND_DIR });
    log(colors.green, "✓", "Virtual environment created");
  }

  log(colors.yellow, "SETUP", "Installing Python dependencies...");
  if (isWindows()) {
    execSync(
      `"${venvPython}" -m pip install -q -e ".[dev]"`,
      { stdio: "inherit", cwd: BACKEND_DIR, shell: true },
    );
  } else {
    execSync(
      `"${venvPython}" -m pip install -q -e ".[dev]"`,
      { stdio: "inherit", cwd: BACKEND_DIR },
    );
  }
  log(colors.green, "✓", "Backend dependencies ready");

  // --- Setup frontend ---
  if (!fs.existsSync(path.join(FRONTEND_DIR, "node_modules"))) {
    log(colors.yellow, "SETUP", "Installing frontend dependencies...");
    execSync("pnpm install", { stdio: "inherit", cwd: FRONTEND_DIR });
    log(colors.green, "✓", "Frontend dependencies installed");
  }

  // --- Launch ---
  console.log("");
  log(colors.blue + colors.bold, "StockWise", "Starting servers...");
  console.log("");
  console.log(`  Backend  → ${colors.green}http://localhost:8000${colors.reset}`);
  console.log(`  Frontend → ${colors.green}http://localhost:3000${colors.reset}`);
  console.log(`  API Docs → ${colors.green}http://localhost:8000/docs${colors.reset}`);
  console.log("");
  log(colors.yellow, "INFO", "Press Ctrl+C to stop all servers.");
  console.log("");

  // Start backend
  const backendProc = spawn(
    venvPython,
    ["-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
    { cwd: BACKEND_DIR, stdio: "inherit", shell: isWindows() },
  );

  // Wait a moment for backend to start
  await new Promise((r) => setTimeout(r, 3000));

  // Start frontend
  const frontendProc = spawn("pnpm", ["dev"], {
    cwd: FRONTEND_DIR,
    stdio: "inherit",
    shell: isWindows(),
  });

  // Open browser after a moment
  setTimeout(() => {
    const cmd = isWindows()
      ? `start http://localhost:3000`
      : process.platform === "darwin"
        ? `open http://localhost:3000`
        : `xdg-open http://localhost:3000`;
    execSync(cmd, { stdio: "ignore" });
  }, 3000);

  // Handle shutdown
  function cleanup() {
    console.log("");
    log(colors.yellow, "StockWise", "Shutting down...");
    backendProc.kill();
    frontendProc.kill();
    process.exit(0);
  }

  process.on("SIGINT", cleanup);
  process.on("SIGTERM", cleanup);
}

main().catch((err) => {
  log(colors.red, "FATAL", err.message);
  process.exit(1);
});
