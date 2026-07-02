# Felstow Bookkeeping & Consulting — Automation Roadmap

*A CEO-level brainstorm: what to build so the practice grows faster without hiring.*

---

## The strategic frame

The business has three revenue engines, and one constraint:

| Engine | Model | What limits growth |
|---|---|---|
| Monthly bookkeeping | $250–$1,500/mo flat fee | **Your hours per client per month** |
| Cash flow advisory | $300–500/mo, dashboard + Monday email | Your Monday hours + sales pipeline |
| Products (Kit $249, Audit $149) | One-time, semi-passive | Manual fulfillment + marketing time |

The core insight: **you sell flat fees, so every hour automated is pure margin — and more importantly, pure capacity.** If the monthly close for an average client drops from 4 hours to 2, you can serve twice the clients at the same quality bar before you ever think about hiring. The goal of every idea below is one of three things:

1. **Cut per-client recurring time** (raises client capacity)
2. **Speed up lead → paying client** (raises conversion)
3. **Make products truly passive** (revenue that doesn't consume Mondays)

Ranked by impact-per-effort, here's the build order I'd choose.

---

## Tier 1 — Build first (touches every client, every month)

### 1. The Month-End Close Pre-Flight Report
**What:** A script (Claude Code + the QuickBooks connection you already have) that runs on the 1st of the month for each client and produces a one-page "close readiness" brief *before you open QBO*:

- Count of uncategorized / unreviewed bank feed transactions
- Accounts not reconciled through month-end, with last-reconciled dates
- Anomalies vs. prior months: expense categories that spiked, missing recurring bills (rent didn't post?), duplicate-looking transactions, negative balances, stale uncleared checks
- AR/AP aging red flags (new 60+ day receivables, unpaid bills)
- Undeposited funds balance check

**Why first:** the close is the product. You currently *discover* this list by clicking around QBO; this hands it to you finished. If it saves even 45 minutes per client per month across 10 clients, that's ~7.5 hours/month — nearly a full workday returned, every month, forever.

### 2. The Monthly Client Email, Auto-Drafted
**What:** After each close, generate the plain-English check-in email from the client's P&L and cash flow: revenue vs. last month and vs. same month last year, top 3 things that moved, one thing to watch. You edit 10% and hit send.

**Why:** Your site promises "a check-in so the numbers actually mean something" — this is your retention engine and your advisory upsell surface, but writing 10–15 thoughtful emails a month is real time. Drafting is exactly what an LLM with QBO access does well; the judgment stays yours. Bonus: end each email with a soft advisory hook when the data warrants it ("your cash dips in week 6 of next quarter — this is the kind of thing the weekly dashboard catches").

### 3. Categorization Assistant
**What:** Export uncategorized transactions across all clients → batch-suggest categories with confidence scores based on each client's history and chart of accounts → you approve in bulk, low-confidence ones get flagged for real review.

**Why:** Categorization is the highest-volume, lowest-judgment task in the practice. It's also where a per-client "memory" (vendor → account mappings you've made before) compounds: month 6 should be dramatically faster than month 1.

---

## Tier 2 — Sales velocity (lead → signed client)

### 4. Inquiry-to-Brief Pipeline
**What:** Watch Gmail for Web3Forms submissions ("New website inquiry — Felstow Bookkeeping"). For each: draft a personalized reply within the hour (you promise one business day — beat it), and generate a discovery-call prep brief — look up the business, guess the industry and likely tier, list the 5 questions that matter for scoping.

**Why:** Speed-to-lead is the single biggest conversion lever for service businesses. An inquiry answered in 30 minutes converts wildly better than one answered tomorrow. Also: log every inquiry to a simple pipeline sheet in Drive so nothing falls through and you can see conversion rates.

### 5. Proposal Generator
**What:** After the discovery call, feed your rough notes in → get back a tailored proposal from a house template: scope, tier, flat fee, cleanup estimate (at $52/hr with an hours range), start date, next steps. Review, tweak, send same day.

**Why:** "I send a tailored plan" is step 2 of your sales process. Same-day proposals close; proposals that take three evenings to write don't. This also standardizes your scoping so pricing stays consistent as you grow.

### 6. Onboarding Autopilot
**What:** When the onboarding form lands in Gmail, auto-generate: the client's Drive folder structure, a QBO setup/cleanup checklist derived from their actual answers (books 2 years behind + sales tax in 3 states → a very different checklist than clean books), a draft engagement letter, and the secure-credentials instructions email.

**Why:** Onboarding is a burst of low-judgment setup work at exactly the moment you want to look flawless. The form already captures everything — nobody should retype it.

---

## Tier 3 — Make the products actually passive

### 7. Kit Fulfillment Automation
**What:** The kit page already has the swap-point comment for Gumroad/Lemon Squeezy — do that swap. Until then: auto-detect "KIT ORDER" emails, auto-send the payment link, and on payment confirmation auto-deliver the Kit with a welcome email. Add a 4-email drip (setup help on day 2, first-client playbook on day 7, testimonial ask on day 21).

**Why:** A $249 product with manual fulfillment is a service wearing a product costume. This is the one revenue line that can grow while you sleep — but only if zero Jake-minutes per sale.

### 8. Subscription Audit Engine
**What:** Build the internal tool that does the $149 audit: parse uploaded statements (CSV/PDF) → detect recurring charges → cluster by vendor → flag zombies (no usage signal), duplicates (two project-management tools), and price creep (same vendor, rising amount) → generate the client report from a template.

**Why:** Turns a 3-day, several-hour deliverable into a half-day review. That either fattens the margin, lets you drop turnaround to 24 hours as a marketing hook, or lets you raise volume — the audit becomes a genuinely scalable front-door offer that upsells into monthly bookkeeping.

### 9. Advisory Delivery Upgrades
**What:** You already have the Monday cron. Extend it: pull Monday balances from QBO bank feeds where possible (remove the client-text dependency), auto-draft each client's 3-sentence Monday email from the fresh dashboard data, and build yourself a **fleet view** — one internal page showing every advisory client's runway, next tight week, and update status.

**Why:** The Kit pitch says 15 minutes per client per Monday. With drafted emails and a fleet view, it's 5 — which means 20 advisory clients on one Monday morning instead of 10. At $450/mo that's the difference between $54K and $108K a year from the same weekly ritual.

---

## Tier 4 — Run the practice like you advise clients to run theirs

### 10. The CEO Dashboard (drink your own champagne)
**What:** A weekly self-updating internal dashboard — same infrastructure as your client dashboards: MRR by engine, client count and tier mix, pipeline (inquiries → calls → proposals → signed), Kit/Audit sales, your own AR, and hours-per-client trend.

**Why:** You sell exactly this clarity. Having it for your own business tells you when to raise prices, which marketing works, and when you're approaching capacity. It's also a live sales demo: "this is my own dashboard."

### 11. Revenue Protection Monitor
**What:** Quarterly scan of each client's transaction volume, account count, and payroll complexity vs. what their tier assumed. Flag scope creep: "Client X's volume is up 60% since signing — Standard fee, Growth workload."

**Why:** Flat-fee businesses die by silent scope creep. This is found money — a pricing conversation you'd never remember to have.

### 12. Document Chasing & AR
**What:** Automated (but human-sounding) reminder emails for missing statements/receipts at close time, and payment reminders on your own overdue invoices.

**Why:** Chasing is pure toil, and *your own* AR is the classic cobbler's-children problem. Neither deserves your attention.

### 13. Content Flywheel
**What:** A weekly prompt that turns something real from that week's work (anonymized) into a LinkedIn post / short article draft: "the $400/mo zombie subscription I found this week," "why the bank balance, not the book balance, drives the forecast." You approve and post.

**Why:** Your differentiators are real war stories and plain English. Consistent content is the cheapest lead gen for both the practice and the Kit — the constraint is drafting time, which is automatable.

---

## What I would NOT automate

- **The advisory judgment** — the 3-sentence verdict, the "can I afford X?" call. That's the product; automation should hand you the data faster, never replace the read.
- **Discovery calls and proposals-final-review** — trust is the sale.
- **Anything touching client credentials or money movement** without you in the loop. Drafts and reports: automated. Sends and payments: you click the button.

---

## Suggested 90-day sequence

| Weeks | Build | Payoff |
|---|---|---|
| 1–2 | Close Pre-Flight (#1) for 2 pilot clients | Immediate hours back |
| 3–4 | Monthly email drafts (#2) + inquiry pipeline (#4) | Retention + faster conversion |
| 5–6 | Kit fulfillment swap (#7) | First truly passive revenue |
| 7–9 | Categorization assistant (#3) + onboarding autopilot (#6) | Capacity for new signups |
| 10–12 | Audit engine (#8) + CEO dashboard (#10) | Scalable front-door offer + steering data |

Every one of these can run on the stack you already own: Claude Code with your Gmail, Drive, and QuickBooks connections, plus the same Mac cron + GitHub Pages pattern you built for the cash flow dashboards. No new SaaS subscriptions — which, given that you sell a $149 audit hunting exactly those, is on brand.
