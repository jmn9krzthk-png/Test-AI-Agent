# Prospex (business-leads-ai-automation): what it is and what it could do for Onyx Media

Source: https://github.com/asiifdev/business-leads-ai-automation (reviewed November 2026)

> Assumption: Onyx Media is a St. Louis media/marketing agency whose clients are mostly local and regional businesses. Where that assumption matters, it is called out.

## 1. What the repository is

**Prospex** is an open-source, self-hostable AI sales-and-marketing tool built by PT Asiifdev Digital Agency (Indonesia). It finds local businesses, scores them, writes personalized first messages with AI, holds every message for human approval, sends them slowly, and tracks each lead to a won/lost deal.

The core idea: **the AI does the typing, a person does the deciding.** Nothing is sent until someone approves it.

### The workflow

| Step | What Prospex does |
|------|-------------------|
| 1. Understand your offer | Reads your website (up to 40 pages, sitemap, `llms.txt`), PDFs, DOCX or pasted text and writes a *Marketing Brief*. Claims it cannot find in your sources are listed as "missing", not invented. |
| 2. Find leads | Scrapes Google Maps by business type + city (up to 2,000 leads per campaign). Can also pull from Overture Maps, OpenStreetMap, or a CSV/Excel import. Duplicates are merged. |
| 3. Score | 0–100 score from listing signals (phone, rating x review count, review volume) plus an AI "fit" judgement with a written reason. |
| 4. Draft | AI writes each first message from the lead's real data, your brief, your knowledge base and (optionally) your own writing style learned from exported chats. Three openings rotate so you can compare reply rates. |
| 5. Approve | Every draft sits in an *Outbox*: approve, edit or reject. |
| 6. Send | WhatsApp (linked device) or email via your own SMTP, with hourly/daily caps, quiet hours, random gaps, opt-out/unsubscribe and a circuit breaker. |
| 7. Reply & follow up | Classifies replies (interested, wants a meeting, asked price, not now, not interested…), moves the lead in the pipeline, drafts a reply, and drafts up to two follow-ups (day 3 and day 5) for silent leads. |
| 8. Pipeline | Stages, deal values, lost reasons, results per campaign. Deals are only closed by a person. |

### Tech stack

Next.js 16 dashboard · NestJS 10 API · PostgreSQL 16 + pgvector · Redis/BullMQ · Playwright (headless Chromium) · Baileys (WhatsApp) · any OpenAI-compatible AI provider (OpenAI, OpenRouter — including Claude models — or fully local via Ollama). Runs with Docker Compose.

Multi-workspace: one login can run several businesses, each with its own brief, voice, knowledge base, sending number and AI key.

### Licence

- **AGPL-3.0** — free to use and self-host. If you *modify it and let others use it over a network* (e.g. client logins), you must publish your changes.
- **Commercial licence** available from the author for closed-source, white-label or modified hosted use.
- **Hosted version** at alatpintar.id needs no licence.

## 2. How it could benefit Onyx Media

### A. Onyx's own new-business pipeline
The most direct win. Local businesses are exactly Onyx's buyers.
- **Targeted prospect lists in minutes:** e.g. "restaurants in St. Louis", "dentists in Clayton", "HVAC in St. Charles" — with phone, website, rating and review count.
- **Built-in qualification signals for a media agency:** a business with a weak website, few reviews or no website at all is a natural prospect for web, content, video or reputation work. The AI-fit score can be pointed at Onyx's own service brief to rank those first.
- **Personalized outreach at scale without sounding like a bulk blast:** drafts reference the prospect's own business, and the human-approval step keeps Onyx's brand safe.
- **Follow-up discipline:** automatic day-3/day-5 follow-up drafts and a pipeline view mean fewer leads go cold.
- **Brand voice:** the Marketing Brief + knowledge base (case studies, pricing, portfolio) keep every message grounded in what Onyx can actually prove.

### B. A service Onyx can offer clients
- Run lead-generation campaigns *for* clients using a separate workspace per client (separate brief, voice, sender, AI key).
- Package it as "AI-assisted local outreach" alongside existing media services, with reporting from the pipeline/analytics pages.
- Note the licence point below before giving clients their own logins.

### C. Market research
Even without sending anything, the scraping + map + area filters give a quick picture of a vertical in a territory (how many businesses, their ratings, how many lack websites) — useful for pitches, proposals and choosing niches.

## 3. Caveats specific to a US agency

| Issue | Why it matters | Mitigation |
|-------|----------------|------------|
| **WhatsApp-first design** | Built for Indonesia, where business runs on WhatsApp. US local businesses mostly don't. | Use the **email channel** (your own SMTP). Treat WhatsApp as optional. |
| **Email replies aren't read yet** | Reply classification and auto-drafted responses currently work for WhatsApp only (on the roadmap). | Handle email replies in your normal inbox and update the pipeline manually. |
| **CAN-SPAM** | US cold email needs a real sender, physical postal address, and working opt-out. Prospex adds an unsubscribe link and requires a public HTTPS API URL for it. | Add Onyx's postal address to the email template; use a dedicated sending domain with SPF/DKIM/DMARC. |
| **TCPA / texting** | Cold messaging to phones in the US is legally risky. | Don't use the WhatsApp/phone channel for cold US outreach without legal review. |
| **Google Maps scraping** | Scraping may conflict with Google's Terms of Service. | Prefer the Overture / OpenStreetMap sources or CSV imports from a licensed data provider; use Maps scraping knowingly. |
| **Indonesian defaults** | Some examples, area lookup ("Seluruh Indonesia"), and a UI in EN/ID. Messages can be written in any language/country. | Set campaign country = US, language = en. |
| **AGPL** | Giving clients access to a modified copy obliges Onyx to publish its changes. | Use internally, keep it unmodified, or buy the commercial licence for white-label use. |
| **Self-hosting effort** | Postgres, Redis, Chromium, an AI key, a server and maintenance. | Start with a small cloud VM + Docker Compose, or trial the hosted version first. |
| **Maturity** | The author notes high-volume sending and reply-rate impact are not yet proven in the field. | Pilot with 30–50 leads, measure reply rate, then scale. |

## 4. Suggested pilot (2–3 weeks)

1. Deploy locally or on a small VM with Docker Compose; connect an AI provider (e.g. OpenRouter with a Claude model, or OpenAI).
2. Feed it onyxmediastl.com plus a one-page services/case-study doc to build the Marketing Brief and knowledge base.
3. Pick **one** vertical + area (e.g. independent restaurants in St. Louis city) and pull ~200 leads; review the top 50 by score.
4. Send via email only, from a dedicated domain, with CAN-SPAM-compliant footer, at a slow pace.
5. Measure: % of drafts approved without edits, reply rate, meetings booked. Compare to Onyx's current outreach.
6. Decide: adopt internally, offer as a client service (consider the commercial licence), or drop.

## 5. Bottom line

Prospex is a well-built, honest-by-design tool for local-business prospecting with a human approval gate — a good fit for an agency that sells to local businesses. For Onyx, its biggest value is **faster, better-targeted, consistently followed-up new-business outreach**, with a possible second life as a **client-facing lead-gen service**. The main gaps for a US agency are its WhatsApp-centric design and the lack of email-reply handling, plus the usual US compliance (CAN-SPAM, TCPA) and Google ToS considerations. A small email-only pilot is the low-risk way to find out whether it moves the needle.
