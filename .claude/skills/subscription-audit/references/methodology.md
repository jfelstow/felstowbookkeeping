# Audit methodology reference

Heuristics, vendor knowledge, and the duplicate-tool map behind the
keep / review / cancel calls. These inform judgment; they don't replace it.

## Classification heuristics

### Lean CANCEL when

- **Zombie signals**: charge began mid-window at a price matching a known
  free-trial conversion; or the tool belongs to a project/category nothing
  else in the statements supports (e.g. a podcast host with no other media
  spend).
- **Redundancy**: a duplicate of a tool the business clearly uses more
  (the duplicate map below) — cancel the cheaper-engagement one, keep the
  one with deeper lock-in (data, integrations).
- **Consumer subscriptions on the business card**: streaming, personal
  storage, dating/fitness apps. Flag for cancel *from the business* even if
  the owner keeps it personally — it's also a books-hygiene issue.
- **Orphan seats/tiers**: per-seat tools billing for more than the business's
  plausible headcount, or a premium tier where the base tier's advertised
  features cover the visible usage.
- **Dormant pattern**: an annual renewal for something with zero related
  activity in the window (a domain registrar charge is fine; six parked
  domains at premium renewal is not).

### Lean REVIEW when

- Usage can't be inferred from statements alone (most SaaS): the tool is
  plausibly useful but only the owner knows if anyone logs in. Write the
  one question that settles it.
- **Price creep detected** but the tool is otherwise a keeper — the review
  action is "renegotiate or downgrade," not cancel. Say which cheaper tier
  exists if you know it.
- Two tools overlap but both show signs of active use.
- Annual renewal coming up soon (charge is 9–12 months old) — the review is
  time-sensitive; say the estimated renewal month.
- Amount is large enough that even a keeper deserves a yearly justification
  (> ~$100/mo).

### Lean KEEP when

- Core operations: payment processing (Stripe/Square/PayPal fees),
  accounting (QuickBooks/Xero), payroll (Gusto/ADP), the business's own
  website hosting + domain, business insurance, POS, industry-specific
  licensed software, phone/internet.
- Anything whose interruption visibly breaks revenue or compliance. When in
  doubt between keep and review for these, still write the price-check note
  ("worth confirming you're on the right tier") in the reason.

**Never** put payment processing, payroll, tax, insurance, or the primary
website's hosting/domain on the cancel list, even if the numbers look odd —
raise oddities as review with a careful note.

## Known subscription vendors (single annual charge still counts)

Domains/hosting: GoDaddy, Namecheap, Google Domains/Squarespace Domains,
Bluehost, HostGator, SiteGround, WP Engine, Cloudflare.
Software renewals: Adobe, Microsoft 365, Intuit/TurboTax, Norton, McAfee,
1Password, LastPass, Dropbox, Evernote, Grammarly, Canva, LinkedIn Premium,
Amazon Prime, Costco/Sam's Club membership, chambers of commerce, state
registered-agent services (Northwest, LegalZoom, ZenBusiness), professional
association dues.

## Duplicate-tool map (categories where two = one too many)

| Job | Tools commonly found overlapping |
|---|---|
| Design | Adobe CC, Canva, Figma, Sketch |
| File storage | Dropbox, Google One/Workspace storage, Box, OneDrive, iCloud |
| Email marketing | Mailchimp, Constant Contact, Klaviyo, ConvertKit, ActiveCampaign |
| Meetings | Zoom, Google Workspace (Meet), Microsoft 365 (Teams) |
| Project management | Asana, Monday, ClickUp, Trello, Notion, Airtable, Basecamp |
| E-signature | DocuSign, Adobe Sign, HelloSign/Dropbox Sign, PandaDoc |
| Scheduling | Calendly, Acuity, Square Appointments |
| Website builders | Squarespace, Wix, WordPress.com, Shopify (when no store activity) |
| CRM | HubSpot, Salesforce, Pipedrive, Zoho |
| Password managers | 1Password, LastPass, Dashlane, Bitwarden |
| Office suites | Google Workspace, Microsoft 365 (both full suites = classic duplicate) |
| Social scheduling | Hootsuite, Buffer, Later, Sprout Social |
| Phone/SMS | RingCentral, Grasshopper, Google Voice, OpenPhone, Dialpad |

Suite overlap deserves a special look: Google Workspace and Microsoft 365
each bundle mail, storage, meetings, and docs — a business paying for both
plus Zoom plus Dropbox is usually paying 3× for one job.

## Where-to-cancel directory (verify link still works before shipping)

| Merchant | Cancel at | Path |
|---|---|---|
| Adobe | account.adobe.com/plans | Manage plan → Cancel plan (watch the annual-plan early-termination fee — note it) |
| QuickBooks Online | app.qbo.intuit.com → Gear | Account and settings → Billing & subscription → Cancel |
| Microsoft 365 | admin.microsoft.com | Billing → Your products → select → Cancel subscription |
| Google Workspace | admin.google.com | Billing → Subscriptions → Cancel |
| Canva | canva.com/settings/billing | Billing & plans → Cancel trial/subscription |
| Dropbox | dropbox.com/account/plan | Cancel plan (downgrade to Basic) |
| Zoom | zoom.us/billing | Current Plans → Cancel Plan |
| Slack | workspace admin → Billing | Change plan → Downgrade to free |
| Mailchimp | Account → Billing | Monthly plans → Pause or delete |
| Shopify | admin → Settings → Plan | Deactivate store (export data first — note this) |
| Squarespace | Settings → Billing | Subscriptions → select site → Cancel |
| Wix | wix.com/account/subscriptions | Subscription → Cancel |
| GoDaddy | account.godaddy.com/subscriptions | Turn off auto-renew per product |
| Norton / McAfee | my.norton.com / home.mcafee.com | Subscription → turn off auto-renewal (both are call-retention heavy; the toggle works) |
| LinkedIn Premium | linkedin.com/settings | Subscriptions & payments → Manage → Cancel |
| Netflix / Spotify / Hulu etc. | account page of each | Standard self-serve cancel — the note is "move off the business card" |
| DocuSign | account.docusign.com | Plans & billing → Cancel (annual plans: at renewal) |
| Calendly | calendly.com/app/admin/billing | Manage subscription → Cancel |
| Notion | Settings & members → Billing | Change plan → Downgrade |
| Asana / Monday / ClickUp | workspace admin billing page | Downgrade/cancel under Billing |
| HubSpot | Account & billing | Products & add-ons → Cancel/downgrade (often requires notice before renewal — check term) |
| Grammarly | account.grammarly.com/subscription | Cancel subscription |
| 1Password / LastPass | account billing page | Cancel/downgrade under Billing |
| Hootsuite / Buffer | admin billing page | Self-serve cancel; Hootsuite annual contracts need notice before renewal |
| Registered-agent services | provider account | Turn off auto-renew; confirm a replacement agent BEFORE canceling (compliance) |

Not listed → search "<merchant> cancel subscription" and link the current
official help page. Phone-only cancels: give the number and the magic words
("cancel effective end of current billing period, confirmation email
please").

## Savings math conventions

- Normalize to monthly: monthly = amount; annual = /12; quarterly = /3;
  weekly = ×4.33.
- Annualized = monthly × 12. Report savings as annual first (the punchy
  number), monthly second.
- Price-creep cost = (new − old) × charges-per-year.
- Never count a review item in "recommended savings" — reviews are reported
  separately as "up to $X/yr more under review."
