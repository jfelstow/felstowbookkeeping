# Gmail MCP Switcher

One MCP server for **multiple Gmail accounts**, with automatic switching based on
the mailbox you ask Claude to work in — the Gmail companion to the QuickBooks
MCP switcher. Per-account OAuth tokens are stored in the OS keychain (macOS
Keychain via `security`, Linux via `secret-tool`), never in this repo.

Say "check billing@clientco.com for the Stripe invoice" or "draft a reply from
my business address" and Claude passes the mailbox as the `account` argument;
the server resolves it (full email, alias, or unique fragment like `clientco`),
uses that account's tokens, and keeps it active until you name another.

Scopes are read + compose only (`gmail.readonly`, `gmail.compose`) — the server
can search, read, and create drafts, but can never send.

## One-time Google Cloud setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create (or reuse)
   a project and enable the **Gmail API**.
2. Configure the OAuth consent screen (External + your accounts as test users is
   fine for personal use).
3. Create an OAuth client of type **Desktop app** and download its JSON.
4. Save it as `~/.gmail-mcp/oauth-client.json` (create the folder if needed).

## Add your accounts

```bash
cd tools/gmail-mcp-switcher
npm install

node auth.js add jake.felstow@gmail.com     # browser opens; sign in to that account
node auth.js add you@yourbusiness.com       # repeat per mailbox
node auth.js default jake.felstow@gmail.com # used when no account is named
node auth.js alias you@yourbusiness.com biz # optional shorthand
node auth.js list
```

`auth.js remove <email>` deregisters an account and deletes its stored tokens.

## Register the MCP server

Claude Code:

```bash
claude mcp add gmail-switcher -- node /absolute/path/to/tools/gmail-mcp-switcher/index.js
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gmail-switcher": {
      "command": "node",
      "args": ["/absolute/path/to/tools/gmail-mcp-switcher/index.js"]
    }
  }
}
```

## Tools

| Tool | What it does |
| --- | --- |
| `list_accounts` | Show registered accounts, aliases, active/default |
| `switch_account` | Pin the active account explicitly |
| `search_emails` | Gmail query-syntax search (`from:`, `newer_than:7d`, …) |
| `read_thread` | Full thread by id |
| `list_drafts` | List drafts |
| `create_draft` | Create a draft (new thread or threaded reply); never sends |
| `list_labels` | List labels |

Every tool takes an optional `account` — that's the switch. Resolution order:
explicit `account` → currently active account → configured default → the only
account if just one is registered.

## Where things live

| Path | Contents |
| --- | --- |
| `~/.gmail-mcp/oauth-client.json` | OAuth client id/secret (you download this) |
| `~/.gmail-mcp/accounts.json` | Account registry — emails and aliases only, no secrets |
| OS keychain, service `gmail-mcp-switcher` | Per-account OAuth tokens |

On systems without a keychain, tokens fall back to `~/.gmail-mcp/tokens/*.json`
(chmod 600); set `GMAIL_MCP_TOKEN_STORE=file` to force that mode.
