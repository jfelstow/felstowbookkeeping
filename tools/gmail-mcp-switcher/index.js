#!/usr/bin/env node
// Gmail MCP switcher — one MCP server, many Gmail accounts.
//
// Every tool accepts an optional `account` argument (email, alias, or unique
// fragment like "clientco"). Naming an account switches to it and it stays
// active for subsequent calls; with no account named, the active account —
// or the configured default — is used. Companion to the QuickBooks switcher:
// tokens live in the OS keychain, one entry per mailbox.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { google } from "googleapis";
import {
  loadRegistry,
  loadClientConfig,
  loadTokens,
  saveTokens,
} from "./lib/store.js";

const MAX_BODY_CHARS = 4000;

let activeAccount = null;
const gmailClients = new Map();

// ---------- account resolution (the "auto switch") ----------

function registeredEmails(registry) {
  return registry.accounts.map((a) => a.email).join(", ");
}

function resolveAccount(requested) {
  const registry = loadRegistry();
  if (!registry.accounts.length) {
    throw new Error(
      "No Gmail accounts are set up. Run `node auth.js add <email>` in tools/gmail-mcp-switcher."
    );
  }

  if (requested) {
    const q = requested.toLowerCase().trim();
    let match =
      registry.accounts.find((a) => a.email.toLowerCase() === q) ||
      registry.accounts.find((a) =>
        (a.aliases || []).some((alias) => alias.toLowerCase() === q)
      );
    if (!match) {
      const partial = registry.accounts.filter((a) =>
        a.email.toLowerCase().includes(q)
      );
      if (partial.length === 1) match = partial[0];
      else if (partial.length > 1) {
        throw new Error(
          `"${requested}" matches several accounts (${partial
            .map((a) => a.email)
            .join(", ")}). Be more specific.`
        );
      }
    }
    if (!match) {
      throw new Error(
        `No registered Gmail account matches "${requested}". Registered: ${registeredEmails(registry)}. ` +
          `To add it, run \`node auth.js add ${requested}\` in tools/gmail-mcp-switcher.`
      );
    }
    activeAccount = match.email;
    return match.email;
  }

  if (activeAccount) return activeAccount;
  if (registry.defaultAccount) return registry.defaultAccount;
  if (registry.accounts.length === 1) return registry.accounts[0].email;
  throw new Error(
    `Several accounts are registered (${registeredEmails(registry)}) and none is active. ` +
      `Pass \`account\` or call switch_account first.`
  );
}

function getGmail(email) {
  if (gmailClients.has(email)) return gmailClients.get(email);

  const tokens = loadTokens(email);
  if (!tokens) {
    throw new Error(
      `No stored tokens for ${email}. Re-authorize with \`node auth.js add ${email}\`.`
    );
  }
  const { clientId, clientSecret } = loadClientConfig();
  const oauth2 = new google.auth.OAuth2(clientId, clientSecret);
  oauth2.setCredentials(tokens);
  // Persist refreshed access tokens so the keychain copy stays current.
  oauth2.on("tokens", (fresh) => {
    saveTokens(email, { ...tokens, ...fresh });
  });

  const gmail = google.gmail({ version: "v1", auth: oauth2 });
  gmailClients.set(email, gmail);
  return gmail;
}

// ---------- Gmail helpers ----------

function header(message, name) {
  const found = message.payload?.headers?.find(
    (h) => h.name.toLowerCase() === name.toLowerCase()
  );
  return found?.value || "";
}

function decodeBody(data) {
  return Buffer.from(data, "base64url").toString("utf8");
}

function extractText(payload) {
  if (!payload) return "";
  if (payload.mimeType === "text/plain" && payload.body?.data) {
    return decodeBody(payload.body.data);
  }
  for (const part of payload.parts || []) {
    const text = extractText(part);
    if (text) return text;
  }
  if (payload.mimeType === "text/html" && payload.body?.data) {
    return decodeBody(payload.body.data)
      .replace(/<style[\s\S]*?<\/style>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/[ \t]+/g, " ")
      .trim();
  }
  return "";
}

function clip(text) {
  return text.length > MAX_BODY_CHARS
    ? text.slice(0, MAX_BODY_CHARS) + "\n…[truncated]"
    : text;
}

function buildMime({ from, to, cc, bcc, subject, body, inReplyTo, references }) {
  const lines = [`From: ${from}`, `To: ${to}`];
  if (cc) lines.push(`Cc: ${cc}`);
  if (bcc) lines.push(`Bcc: ${bcc}`);
  lines.push(`Subject: ${subject}`);
  if (inReplyTo) {
    lines.push(`In-Reply-To: ${inReplyTo}`);
    lines.push(`References: ${references || inReplyTo}`);
  }
  lines.push(
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: 8bit",
    "",
    body
  );
  return Buffer.from(lines.join("\r\n")).toString("base64url");
}

function ok(account, text) {
  return {
    content: [{ type: "text", text: `[account: ${account}]\n${text}` }],
  };
}

function fail(err) {
  return {
    content: [{ type: "text", text: `Error: ${err.message || err}` }],
    isError: true,
  };
}

const accountParam = z
  .string()
  .optional()
  .describe(
    "Which Gmail account to use: an email address, alias, or unique fragment " +
      "(e.g. 'clientco'). Whenever the user names or implies a specific mailbox, " +
      "pass it here — the switcher routes automatically and keeps that account " +
      "active for later calls. Omit to reuse the active/default account."
  );

// ---------- server ----------

const server = new McpServer(
  { name: "gmail-switcher", version: "1.0.0" },
  {
    instructions:
      "Multi-account Gmail access with automatic account switching. When the user " +
      "mentions which mailbox to work in (their own address, a client's inbox, an " +
      "alias like 'biz'), pass it as the `account` argument on any tool — the server " +
      "resolves it and keeps it active for subsequent calls. Use list_accounts to see " +
      "what's registered if unsure.",
  }
);

server.registerTool(
  "list_accounts",
  {
    description:
      "List the registered Gmail accounts, their aliases, and which one is active/default.",
    inputSchema: {},
  },
  async () => {
    try {
      const registry = loadRegistry();
      if (!registry.accounts.length) {
        return {
          content: [
            {
              type: "text",
              text: "No accounts registered. Run `node auth.js add <email>` in tools/gmail-mcp-switcher.",
            },
          ],
        };
      }
      const lines = registry.accounts.map((a) => {
        const marks = [];
        if (a.email === activeAccount) marks.push("active");
        if (a.email === registry.defaultAccount) marks.push("default");
        if (a.aliases?.length) marks.push(`aliases: ${a.aliases.join(", ")}`);
        return `- ${a.email}${marks.length ? ` (${marks.join("; ")})` : ""}`;
      });
      return { content: [{ type: "text", text: lines.join("\n") }] };
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "switch_account",
  {
    description:
      "Explicitly switch the active Gmail account. Usually unnecessary — passing " +
      "`account` on any tool switches automatically — but useful to set context up front.",
    inputSchema: { account: z.string().describe("Email, alias, or unique fragment") },
  },
  async ({ account }) => {
    try {
      const email = resolveAccount(account);
      return ok(email, `Active Gmail account is now ${email}.`);
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "search_emails",
  {
    description:
      "Search a Gmail mailbox using Gmail query syntax (e.g. 'from:stripe.com newer_than:7d', " +
      "'has:attachment invoice'). Returns matching threads with ids, senders, subjects, dates, snippets.",
    inputSchema: {
      query: z.string().describe("Gmail search query"),
      account: accountParam,
      max_results: z.number().int().min(1).max(50).optional().describe("Default 10"),
    },
  },
  async ({ query, account, max_results }) => {
    try {
      const email = resolveAccount(account);
      const gmail = getGmail(email);
      const list = await gmail.users.threads.list({
        userId: "me",
        q: query,
        maxResults: max_results || 10,
      });
      const threads = list.data.threads || [];
      if (!threads.length) return ok(email, `No results for: ${query}`);

      const rows = [];
      for (const t of threads) {
        const thread = await gmail.users.threads.get({
          userId: "me",
          id: t.id,
          format: "metadata",
          metadataHeaders: ["From", "Subject", "Date"],
        });
        const messages = thread.data.messages || [];
        const last = messages[messages.length - 1];
        rows.push(
          `- thread_id: ${t.id} (${messages.length} msg)\n` +
            `  From: ${header(last, "From")}\n` +
            `  Subject: ${header(last, "Subject")}\n` +
            `  Date: ${header(last, "Date")}\n` +
            `  Snippet: ${t.snippet || ""}`
        );
      }
      return ok(email, rows.join("\n"));
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "read_thread",
  {
    description:
      "Read a full email thread by thread_id (from search_emails). Returns headers and message bodies.",
    inputSchema: {
      thread_id: z.string(),
      account: accountParam,
    },
  },
  async ({ thread_id, account }) => {
    try {
      const email = resolveAccount(account);
      const gmail = getGmail(email);
      const thread = await gmail.users.threads.get({
        userId: "me",
        id: thread_id,
        format: "full",
      });
      const parts = (thread.data.messages || []).map((m, i) => {
        const body = clip(extractText(m.payload) || m.snippet || "");
        return (
          `--- Message ${i + 1} of ${thread.data.messages.length} ---\n` +
          `From: ${header(m, "From")}\n` +
          `To: ${header(m, "To")}\n` +
          `Date: ${header(m, "Date")}\n` +
          `Subject: ${header(m, "Subject")}\n\n${body}`
        );
      });
      return ok(email, parts.join("\n\n"));
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "list_drafts",
  {
    description: "List draft emails in a Gmail account.",
    inputSchema: {
      account: accountParam,
      max_results: z.number().int().min(1).max(50).optional().describe("Default 10"),
    },
  },
  async ({ account, max_results }) => {
    try {
      const email = resolveAccount(account);
      const gmail = getGmail(email);
      const list = await gmail.users.drafts.list({
        userId: "me",
        maxResults: max_results || 10,
      });
      const drafts = list.data.drafts || [];
      if (!drafts.length) return ok(email, "No drafts.");

      const rows = [];
      for (const d of drafts) {
        const draft = await gmail.users.drafts.get({
          userId: "me",
          id: d.id,
          format: "metadata",
        });
        const m = draft.data.message;
        rows.push(
          `- draft_id: ${d.id}\n` +
            `  To: ${header(m, "To")}\n` +
            `  Subject: ${header(m, "Subject")}\n` +
            `  Snippet: ${m.snippet || ""}`
        );
      }
      return ok(email, rows.join("\n"));
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "create_draft",
  {
    description:
      "Create a draft email in a Gmail account (never sends). To draft a reply, pass " +
      "reply_to_thread_id from search_emails/read_thread and the draft threads correctly.",
    inputSchema: {
      to: z.string().describe("Recipient(s), comma-separated"),
      body: z.string().describe("Plain-text body"),
      subject: z
        .string()
        .optional()
        .describe("Required for new threads; defaults to 'Re: …' for replies"),
      cc: z.string().optional(),
      bcc: z.string().optional(),
      reply_to_thread_id: z
        .string()
        .optional()
        .describe("Thread to reply within"),
      account: accountParam,
    },
  },
  async ({ to, body, subject, cc, bcc, reply_to_thread_id, account }) => {
    try {
      const email = resolveAccount(account);
      const gmail = getGmail(email);

      let inReplyTo, references, threadId;
      if (reply_to_thread_id) {
        const thread = await gmail.users.threads.get({
          userId: "me",
          id: reply_to_thread_id,
          format: "metadata",
          metadataHeaders: ["Message-ID", "References", "Subject"],
        });
        const messages = thread.data.messages || [];
        const last = messages[messages.length - 1];
        if (last) {
          inReplyTo = header(last, "Message-ID");
          const prior = header(last, "References");
          references = [prior, inReplyTo].filter(Boolean).join(" ");
          threadId = reply_to_thread_id;
          if (!subject) {
            const orig = header(last, "Subject");
            subject = /^re:/i.test(orig) ? orig : `Re: ${orig}`;
          }
        }
      }
      if (!subject) {
        throw new Error("subject is required when not replying to a thread.");
      }

      const raw = buildMime({
        from: email,
        to,
        cc,
        bcc,
        subject,
        body,
        inReplyTo,
        references,
      });
      const draft = await gmail.users.drafts.create({
        userId: "me",
        requestBody: { message: { raw, ...(threadId ? { threadId } : {}) } },
      });
      return ok(
        email,
        `Draft created (draft_id: ${draft.data.id})\nTo: ${to}\nSubject: ${subject}`
      );
    } catch (err) {
      return fail(err);
    }
  }
);

server.registerTool(
  "list_labels",
  {
    description: "List labels in a Gmail account.",
    inputSchema: { account: accountParam },
  },
  async ({ account }) => {
    try {
      const email = resolveAccount(account);
      const gmail = getGmail(email);
      const res = await gmail.users.labels.list({ userId: "me" });
      const names = (res.data.labels || []).map((l) => `- ${l.name}`);
      return ok(email, names.join("\n") || "No labels.");
    } catch (err) {
      return fail(err);
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
