# LoanReady — launch guide

LoanReady turns a QuickBooks P&L export into a lender-ready financial package
(DSCR, cash flow, margins, charts, written summary) entirely in the visitor's
browser. Nothing is uploaded — there is no backend, no database, and nothing to
maintain. That's what makes it passive: the product is two static pages that
GitHub Pages serves for free, forever.

**Pages**
- `loanready.html` — sales/landing page (hero, how it works, pricing, FAQ)
- `loanready-app.html` — the report builder itself (free preview with watermark;
  an unlock code removes it)

## What the report computes

- Amortized monthly payment for the requested loan (amount / rate / term)
- **DSCR** before and after the loan: `(avg monthly net income + add-backs) ÷ total
  monthly debt service`, judged against the 1.25× threshold lenders use
- Revenue trend (least-squares slope as %/month), net margin, profitable-month count
- Cash cushion: cash on hand ÷ average monthly expenses
- Monthly figures table + auto-written executive summary

Accepts QuickBooks Online "Profit and Loss by Month" CSV exports (handles quoted
fields, `$1,234.56`, `(negatives)`, and the trailing Total column) or a simple
`Month, Revenue, Expenses` sheet from any system.

## Before launch — 3 things only you can do

1. **Create two payment links** (Stripe Payment Links is the 10-minute option —
   no code, no server; Gumroad or Lemon Squeezy also work and handle sales tax
   for you):
   - Single report, **$99** one-time
   - Unlimited, **$49/month** subscription

   Then replace the placeholders in `loanready.html`:
   - `PRODUCT_URL_SINGLE` → your $99 payment link
   - `PRODUCT_URL_UNLIMITED` → your $49/mo payment link

2. **Deliver the unlock code after purchase.** The current code is
   **`LR-FOUNDER-2026`** (codes are case-insensitive). In Stripe/Gumroad, set the
   post-purchase confirmation message/email to include it. To rotate the code:
   `node -e "console.log(require('crypto').createHash('sha256').update('YOUR-NEW-CODE').digest('hex'))"`
   and paste the result into `UNLOCK_HASH` in `loanready-app.html`. Rotate it
   every quarter or two so shared codes age out. (This is honor-system gating —
   the right trade for a $99 product with zero infrastructure. If revenue
   justifies it later, Lemon Squeezy license keys + a tiny verify endpoint is
   the upgrade path.)

3. **Link it from the homepage** — add LoanReady to the nav/services section of
   `index.html` so your existing traffic and clients find it.

## The path to $10k/month

At $99/report, that's ~100 sales/month, or ~205 Unlimited subscribers, or (more
realistically) a mix. The market: ~400k SBA loan approvals a year plus millions
of conventional small-business loan applications — every one of them gets asked
for financials.

Ranked by effort-to-impact:

1. **SEO content (compounding, near-zero marginal effort).** Pages targeting
   "what documents do I need for a business loan", "what is a good DSCR for an
   SBA loan", "DSCR calculator" — each ending in the free report builder. The
   free preview is the growth engine: it costs nothing to give away and does the
   selling itself. (Ask Claude to generate this article cluster as a follow-up —
   it's the obvious next session.)
2. **Loan brokers and bookkeepers are the $49/mo whales.** One broker processes
   dozens of applications a year. A single post in bookkeeper/broker communities
   (r/loanoriginators, bookkeeping Facebook groups, your own kit.html audience)
   pitching "client-ready loan packages in 5 minutes" reaches people who buy the
   subscription, not the one-off.
3. **Your own client base.** Every bookkeeping client who ever mentions
   financing is a warm demo.
4. **Lender co-marketing (later).** Community banks and CDFIs hate receiving
   shoebox financials. "Send your borrowers here first" is a free distribution
   channel.

Realistic ramp: months 1–3 are $0–500 (validation), months 4–9 grow with search
rankings, and $10k/mo is a 12–24 month outcome if the SEO cluster ranks and
brokers adopt Unlimited. The ongoing input rounds to zero: answer the occasional
support email and rotate the unlock code.

## Maintenance

None required. No dependencies, no build step, no server. The only moving parts
are your payment links and the unlock code.
