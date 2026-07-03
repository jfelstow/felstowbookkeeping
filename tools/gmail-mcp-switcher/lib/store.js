// Shared storage for the Gmail MCP switcher.
//
// - Account registry (which emails are set up, aliases, default) lives in
//   ~/.gmail-mcp/accounts.json — no secrets in it.
// - OAuth tokens are stored per-account in the OS keychain (macOS `security`,
//   Linux `secret-tool`), mirroring the QuickBooks switcher setup. Falls back
//   to chmod-600 files under ~/.gmail-mcp/tokens/ when no keychain is present.

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const CONFIG_DIR =
  process.env.GMAIL_MCP_HOME || path.join(os.homedir(), ".gmail-mcp");

const REGISTRY_PATH = path.join(CONFIG_DIR, "accounts.json");
const TOKEN_DIR = path.join(CONFIG_DIR, "tokens");
const KEYCHAIN_SERVICE = "gmail-mcp-switcher";

function ensureConfigDir() {
  fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
}

// ---------- account registry ----------

export function loadRegistry() {
  try {
    const reg = JSON.parse(fs.readFileSync(REGISTRY_PATH, "utf8"));
    reg.accounts ||= [];
    return reg;
  } catch {
    return { defaultAccount: null, accounts: [] };
  }
}

export function saveRegistry(registry) {
  ensureConfigDir();
  fs.writeFileSync(REGISTRY_PATH, JSON.stringify(registry, null, 2) + "\n", {
    mode: 0o600,
  });
}

// ---------- OAuth client config ----------

export function loadClientConfig() {
  const p =
    process.env.GMAIL_OAUTH_CLIENT || path.join(CONFIG_DIR, "oauth-client.json");
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    throw new Error(
      `Missing or unreadable OAuth client file at ${p}. ` +
        `Download a "Desktop app" OAuth client JSON from Google Cloud Console ` +
        `and save it there (see README).`
    );
  }
  const keys = raw.installed || raw.web || raw;
  if (!keys.client_id || !keys.client_secret) {
    throw new Error(`${p} does not look like an OAuth client JSON.`);
  }
  return { clientId: keys.client_id, clientSecret: keys.client_secret };
}

// ---------- token storage ----------

function commandExists(cmd) {
  try {
    execFileSync("sh", ["-c", `command -v ${cmd}`], { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function backend() {
  if (process.env.GMAIL_MCP_TOKEN_STORE === "file") return "file";
  if (process.platform === "darwin") return "keychain";
  if (process.platform === "linux" && commandExists("secret-tool"))
    return "secret-tool";
  return "file";
}

function tokenFile(email) {
  return path.join(TOKEN_DIR, `${email}.json`);
}

export function saveTokens(email, tokens) {
  const json = JSON.stringify(tokens);
  switch (backend()) {
    case "keychain":
      execFileSync("security", [
        "add-generic-password",
        "-U",
        "-s",
        KEYCHAIN_SERVICE,
        "-a",
        email,
        "-w",
        json,
      ]);
      return;
    case "secret-tool":
      execFileSync(
        "secret-tool",
        [
          "store",
          `--label=Gmail MCP switcher (${email})`,
          "service",
          KEYCHAIN_SERVICE,
          "account",
          email,
        ],
        { input: json }
      );
      return;
    default:
      fs.mkdirSync(TOKEN_DIR, { recursive: true, mode: 0o700 });
      fs.writeFileSync(tokenFile(email), json + "\n", { mode: 0o600 });
  }
}

export function loadTokens(email) {
  try {
    switch (backend()) {
      case "keychain":
        return JSON.parse(
          execFileSync(
            "security",
            [
              "find-generic-password",
              "-s",
              KEYCHAIN_SERVICE,
              "-a",
              email,
              "-w",
            ],
            { encoding: "utf8" }
          ).trim()
        );
      case "secret-tool":
        return JSON.parse(
          execFileSync(
            "secret-tool",
            ["lookup", "service", KEYCHAIN_SERVICE, "account", email],
            { encoding: "utf8" }
          ).trim()
        );
      default:
        return JSON.parse(fs.readFileSync(tokenFile(email), "utf8"));
    }
  } catch {
    return null;
  }
}

export function deleteTokens(email) {
  try {
    switch (backend()) {
      case "keychain":
        execFileSync(
          "security",
          ["delete-generic-password", "-s", KEYCHAIN_SERVICE, "-a", email],
          { stdio: "ignore" }
        );
        return;
      case "secret-tool":
        execFileSync(
          "secret-tool",
          ["clear", "service", KEYCHAIN_SERVICE, "account", email],
          { stdio: "ignore" }
        );
        return;
      default:
        fs.rmSync(tokenFile(email), { force: true });
    }
  } catch {
    // already gone — fine
  }
}
