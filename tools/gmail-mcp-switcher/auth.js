#!/usr/bin/env node
// Account setup CLI for the Gmail MCP switcher.
//
//   node auth.js add <email>            authorize an account and store its tokens
//   node auth.js list                   show registered accounts
//   node auth.js remove <email>         remove an account and its tokens
//   node auth.js default <email>        set the default account
//   node auth.js alias <email> <alias>  add an alias (e.g. "biz", "clientco")

import http from "node:http";
import { spawn } from "node:child_process";
import { google } from "googleapis";
import {
  loadRegistry,
  saveRegistry,
  loadClientConfig,
  saveTokens,
  deleteTokens,
} from "./lib/store.js";

const SCOPES = [
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/gmail.compose",
];

function openBrowser(url) {
  const cmd =
    process.platform === "darwin"
      ? "open"
      : process.platform === "win32"
        ? "start"
        : "xdg-open";
  try {
    spawn(cmd, [url], { stdio: "ignore", detached: true }).unref();
  } catch {
    // user can copy the printed URL instead
  }
}

async function addAccount(email) {
  const { clientId, clientSecret } = loadClientConfig();

  const server = http.createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = server.address().port;

  const oauth2 = new google.auth.OAuth2(
    clientId,
    clientSecret,
    `http://127.0.0.1:${port}/oauth2callback`
  );
  const authUrl = oauth2.generateAuthUrl({
    access_type: "offline",
    prompt: "consent",
    scope: SCOPES,
    login_hint: email,
  });

  console.log(`\nAuthorize ${email} in your browser. If it doesn't open, visit:\n\n${authUrl}\n`);
  openBrowser(authUrl);

  const code = await new Promise((resolve, reject) => {
    server.on("request", (req, res) => {
      const url = new URL(req.url, `http://127.0.0.1:${port}`);
      if (url.pathname !== "/oauth2callback") {
        res.writeHead(404).end();
        return;
      }
      res.writeHead(200, { "Content-Type": "text/plain" });
      if (url.searchParams.get("error")) {
        res.end("Authorization failed. You can close this tab.");
        reject(new Error(`OAuth error: ${url.searchParams.get("error")}`));
      } else {
        res.end("Authorized. You can close this tab and return to the terminal.");
        resolve(url.searchParams.get("code"));
      }
    });
  });
  server.close();

  const { tokens } = await oauth2.getToken(code);
  oauth2.setCredentials(tokens);

  // Confirm which mailbox Google actually authorized.
  const gmail = google.gmail({ version: "v1", auth: oauth2 });
  const profile = await gmail.users.getProfile({ userId: "me" });
  const actual = profile.data.emailAddress.toLowerCase();
  if (email && actual !== email.toLowerCase()) {
    console.warn(
      `Note: you signed in as ${actual}, not ${email}. Registering ${actual}.`
    );
  }

  saveTokens(actual, tokens);

  const registry = loadRegistry();
  if (!registry.accounts.some((a) => a.email === actual)) {
    registry.accounts.push({ email: actual, aliases: [] });
  }
  registry.defaultAccount ||= actual;
  saveRegistry(registry);

  console.log(`\nRegistered ${actual}.`);
  if (registry.defaultAccount === actual) {
    console.log(`It is the default account.`);
  }
}

function listAccounts() {
  const registry = loadRegistry();
  if (!registry.accounts.length) {
    console.log("No accounts registered. Run: node auth.js add <email>");
    return;
  }
  for (const account of registry.accounts) {
    const marks = [];
    if (account.email === registry.defaultAccount) marks.push("default");
    if (account.aliases?.length) marks.push(`aliases: ${account.aliases.join(", ")}`);
    console.log(`  ${account.email}${marks.length ? `  (${marks.join("; ")})` : ""}`);
  }
}

function removeAccount(email) {
  const registry = loadRegistry();
  const before = registry.accounts.length;
  registry.accounts = registry.accounts.filter(
    (a) => a.email !== email.toLowerCase()
  );
  if (registry.accounts.length === before) {
    console.error(`No registered account ${email}.`);
    process.exit(1);
  }
  if (registry.defaultAccount === email.toLowerCase()) {
    registry.defaultAccount = registry.accounts[0]?.email || null;
  }
  saveRegistry(registry);
  deleteTokens(email.toLowerCase());
  console.log(`Removed ${email} and deleted its stored tokens.`);
}

function setDefault(email) {
  const registry = loadRegistry();
  if (!registry.accounts.some((a) => a.email === email.toLowerCase())) {
    console.error(`No registered account ${email}. Run: node auth.js add ${email}`);
    process.exit(1);
  }
  registry.defaultAccount = email.toLowerCase();
  saveRegistry(registry);
  console.log(`Default account is now ${email}.`);
}

function addAlias(email, alias) {
  const registry = loadRegistry();
  const account = registry.accounts.find((a) => a.email === email.toLowerCase());
  if (!account) {
    console.error(`No registered account ${email}.`);
    process.exit(1);
  }
  account.aliases ||= [];
  if (!account.aliases.includes(alias.toLowerCase())) {
    account.aliases.push(alias.toLowerCase());
  }
  saveRegistry(registry);
  console.log(`"${alias}" now routes to ${account.email}.`);
}

const [, , command, ...args] = process.argv;
try {
  switch (command) {
    case "add":
      if (!args[0]) throw new Error("usage: node auth.js add <email>");
      await addAccount(args[0]);
      break;
    case "list":
      listAccounts();
      break;
    case "remove":
      if (!args[0]) throw new Error("usage: node auth.js remove <email>");
      removeAccount(args[0]);
      break;
    case "default":
      if (!args[0]) throw new Error("usage: node auth.js default <email>");
      setDefault(args[0]);
      break;
    case "alias":
      if (!args[0] || !args[1])
        throw new Error("usage: node auth.js alias <email> <alias>");
      addAlias(args[0], args[1]);
      break;
    default:
      console.log(
        "usage: node auth.js <add|list|remove|default|alias> [email] [alias]"
      );
      process.exit(command ? 1 : 0);
  }
} catch (err) {
  console.error(err.message || err);
  process.exit(1);
}
