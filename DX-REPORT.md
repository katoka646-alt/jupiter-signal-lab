# Jupiter Developer Platform DX Report

Project: **Jupiter Signal Lab**

Listing: **Not Your Regular Bounty** / Frontier Hackathon track

Builder: Kato agent-assisted build

Date: 2026-05-08 UTC

## 1. Project summary

Jupiter Signal Lab is a read-only market intelligence prototype that combines Jupiter **Tokens API V2** and **Price API V3** to rank Solana tokens by explainable signal quality.

Instead of just showing "trending" tokens, the script answers a more practical builder question:

> Which tokens look interesting right now, and what makes the signal trustworthy or risky?

The prototype uses:

- `GET /tokens/v2/toptrending/1h?limit=...`
- `GET /tokens/v2/toptraded/1h?limit=...`
- `GET /price/v3?ids=...`

It deduplicates mints, combines token metadata/trading stats with fresh price data, computes a compact signal score, and prints human-readable reasons such as:

- deep liquidity
- high organic score
- organic buy pressure
- organic sell pressure
- strong 1h momentum
- thin liquidity risk
- holder drift negative

The tool is intentionally **read-only**: no wallet, no signing, no swap execution, no order placement.

## 2. Onboarding timeline

Approximate onboarding path:

1. Opened the Superteam listing and identified required Jupiter Developer Platform components.
2. Opened `https://developers.jup.ag/docs/ai` and found links to `llms.txt`, API docs, CLI, Skills, and MCP.
3. Tried `https://developers.jup.ag/llms.txt`; this returned **404**.
4. Found the correct docs index at `https://developers.jup.ag/docs/llms.txt` and `https://dev.jup.ag/docs/llms.txt`.
5. Used `llms.txt` to discover relevant markdown pages:
   - `/docs/tokens/index.md`
   - `/docs/tokens/token-information.md`
   - `/docs/price/index.md`
   - `/docs/swap/index.md`
   - `/docs/trigger/index.md`
6. Made first successful keyless API calls to:
   - `https://api.jup.ag/tokens/v2/search?query=JUP`
   - `https://api.jup.ag/price/v3?ids=So11111111111111111111111111111111111111112,JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN`
7. Built the prototype around Tokens + Price because they allow a complete read-only demo without a wallet or private key.

Time to first successful useful API call: **under 10 minutes**.

Time to working prototype: **roughly 30–45 minutes**, including docs exploration and API shape validation.

## 3. What worked well

### 3.1 Markdown docs are extremely agent-friendly

The markdown pages are the strongest part of the DX. The pages at URLs like:

- `https://developers.jup.ag/docs/price/index.md`
- `https://developers.jup.ag/docs/tokens/token-information.md`

are easy for agents to fetch, parse, quote, and turn into working code. This is much better than forcing an agent to scrape a rendered docs app.

### 3.2 Keyless access is great for prototyping

The docs mention keyless access at low rate limits. That made it possible to validate the idea quickly without account setup. For hackathon experimentation, this is a big advantage.

### 3.3 Tokens API response is rich enough to build real products

The Tokens API includes more than token names and mints. Fields like liquidity, holder count, organic score, buy/sell volume, trader counts, price change, and verification status make it possible to build useful ranking/filtering logic without joining multiple external APIs.

### 3.4 Price API is simple

`GET /price/v3?ids=<comma-separated-mints>` is exactly the kind of API an agent can use reliably. The 50-id limit is clear and easy to code around.

## 4. What was confusing or broken

### 4.1 `developers.jup.ag/llms.txt` returned 404

The listing and docs emphasize LLM-optimized docs. The correct URLs I found were:

- `https://developers.jup.ag/docs/llms.txt`
- `https://dev.jup.ag/docs/llms.txt`

But `https://developers.jup.ag/llms.txt` returned 404.

**Why this matters:** many agents and humans will guess the root `/llms.txt` path first because that is the common convention.

**Suggested fix:** add a redirect from `/llms.txt` to `/docs/llms.txt`, or publish a small root file that points to the canonical docs index.

### 4.2 The rendered docs app is heavy for agents

Fetching pages like `/docs/ai` returns a large Next.js HTML document. It contains useful links, but the signal is buried in hundreds of KB of application shell.

**Suggested fix:** every rendered page should expose a visible `.md` alternate link in metadata, e.g.:

```html
<link rel="alternate" type="text/markdown" href="/docs/ai/index.md" />
```

This would let agents switch to markdown automatically.

### 4.3 API key requirement language can feel inconsistent

Some docs say endpoints require an API key, while the overview also explains keyless access. In practice, I successfully used Tokens and Price without an API key, but hit low-rate constraints.

**Suggested fix:** add a short "Auth modes" box to every API page:

- Keyless: works, 0.5 RPS / low limit, no analytics
- API key: recommended, higher rate limits, analytics
- JWT/wallet auth: only for authenticated user actions where applicable

### 4.4 429 behavior appeared quickly during normal prototyping

I hit a `429 Too Many Requests` when calling multiple read-only endpoints back-to-back. This is understandable for keyless access, but it happened during a very small prototype run.

**Suggested fix:** document practical retry guidance for agents:

- minimum delay between keyless calls
- expected `Retry-After` header behavior
- whether `lite-api.jup.ag` is recommended as a fallback for read-only public endpoints

The prototype added retry logic and fallback to `https://lite-api.jup.ag` for read-only endpoints.

## 5. API observations

### 5.1 Tokens API shape is powerful but should be schema-pinned

The Tokens API response includes many useful fields, but the docs also warn the response may change. For hackathon builders, that is fine. For production agents, it creates fragility.

**Suggested improvement:** publish a minimal stable schema for common fields:

- `id`
- `symbol`
- `name`
- `decimals`
- `usdPrice`
- `liquidity`
- `holderCount`
- `organicScore`
- `organicScoreLabel`
- `stats5m/1h/6h/24h.priceChange`
- `stats*.buyOrganicVolume`
- `stats*.sellOrganicVolume`
- `stats*.numTraders`

Everything else can remain best-effort / evolving.

### 5.2 Category endpoints are excellent for agents

The category endpoints from the docs are very useful:

- `/tokens/v2/toptrending/{interval}`
- `/tokens/v2/toptraded/{interval}`
- `/tokens/v2/toporganicscore/{interval}`

These are agent-friendly because they reduce the need for discovery heuristics. A coding agent can start with top categories and build immediately.

### 5.3 Price API batch semantics are clear

The 50-token batch limit is easy to understand and implement. This is a good example of low-friction API design.

## 6. AI stack feedback

### 6.1 `llms.txt` was the most useful AI tool

The docs index made discovery fast. It summarized APIs and linked to markdown pages. This directly influenced the project architecture.

### 6.2 Skills and CLI look promising, but discoverability could improve

The `/docs/ai` page mentions:

- Agent Skills
- Jupiter CLI
- Docs MCP
- llms.txt

But an agent landing on the HTML page has to extract links from a large app shell. A simple plain-text "AI quickstart" endpoint would be very useful.

Suggested endpoint:

```text
https://developers.jup.ag/docs/ai/quickstart.md
```

It should include:

1. canonical `llms.txt` URL
2. install command for CLI
3. `npx skills add ...` examples
4. MCP server URL
5. three copy-paste API calls that work keyless
6. rate-limit note

### 6.3 Agent Skills should include "read-only prototype" paths

Many agent workflows should not start by signing transactions. A useful agent skill would offer paths like:

- read-only market scanner using Tokens + Price
- quote-only swap planner using Swap V2 `/order` without execution
- wallet-required execution path with explicit human approval

This would help prevent unsafe autonomous trading behavior.

## 7. How I would rebuild developers.jup.ag for faster shipping

### 7.1 Add a "Start building without a wallet" lane

A lot of developers want to test before connecting keys or wallets. Jupiter already supports this through read-only APIs, but the docs could make it more explicit.

Suggested landing page sections:

1. **Read-only in 60 seconds**: Price + Tokens examples.
2. **Quote in 2 minutes**: Swap V2 order/quote flow without execution.
3. **Execute with wallet**: signing, execute endpoint, safety.
4. **Advanced automation**: Trigger, Recurring, Lend, Prediction.

### 7.2 Add copy-paste agent tasks

Example:

```text
Task: Build a token scanner using Tokens API and Price API.
Constraints: read-only, no wallet, no trading.
APIs: /tokens/v2/toptrending/1h, /price/v3.
Expected output: ranked table with reasons.
```

This would make agents productive immediately.

### 7.3 Expose API health and rate-limit hints

For autonomous agents, a `429` without clear retry behavior causes brittle builds. A small page with rate-limit examples would help.

### 7.4 Make root LLM discovery conventional

Add these redirects/files:

- `/llms.txt` -> `/docs/llms.txt`
- `/llms-full.txt` -> full docs content, if available
- `/openapi.json` or an index of OpenAPI specs

## 8. What I wish existed

1. A normalized "token signal" endpoint that returns curated fields for scoring.
2. A read-only quote/simulation endpoint that does not require transaction handling.
3. Example agent workflows that explicitly separate analysis, quote, build transaction, human approval, and execution.
4. Official Python snippets in addition to JavaScript snippets.
5. A docs page showing common API failure modes and exact retry/backoff recommendations.
6. A machine-readable API capability matrix:
   - requires API key?
   - requires JWT?
   - requires wallet signature?
   - safe for read-only agents?
   - supports keyless demo?

## 9. Project limitations

- This prototype does not execute trades.
- It does not use Trigger, Swap, Lend, Recurring, Perps, or Prediction yet.
- It uses a simple scoring heuristic, not a predictive model.
- It should not be interpreted as financial advice.
- It needs a production API key for reliable repeated runs.

## 10. Next steps

If extended, I would add:

1. Swap V2 quote-only integration for top-ranked tokens.
2. Trigger order simulation suggestions, still without execution.
3. A web UI showing ranked signals and explanations.
4. Optional wallet-gated execution with explicit human approval.
5. Historical snapshots to evaluate whether signal score correlates with useful outcomes.

## 11. Bottom line

Jupiter's Developer Platform is already strong for agent-based builds because the APIs are clean REST/JSON and the markdown docs are accessible. The biggest DX wins would come from polishing the AI-entry path:

- root `/llms.txt` redirect
- clearer keyless vs API-key docs
- retry/rate-limit guidance
- obvious markdown alternate links
- read-only prototype recipes

Those changes would reduce time-to-first-working-agent from "pretty fast" to "almost immediate."
