# Jupiter Signal Lab

A small, agent-built market intelligence prototype for the Superteam Frontier / Jupiter "Not Your Regular Bounty" track.

It combines multiple Jupiter Developer Platform APIs in a way that is useful for builders, traders, and agent workflows:

- **Tokens API V2**: discovers trending and top-traded Solana tokens.
- **Price API V3**: fetches real-time USD prices and 24h price changes.
- **Signal engine**: ranks tokens using liquidity, organic activity, price movement, volume imbalance, and holder drift.
- **DX report**: documents the actual onboarding and API friction found while building.

This is intentionally not a trading bot and does not execute swaps. It is a read-only research layer that can be extended into Trigger, Swap V2, or Recurring strategies once a user connects a wallet and explicitly authorizes execution.

## Why this is not a regular bounty submission

Most dashboards show trending tokens. Jupiter Signal Lab tries to answer a more developer-useful question:

> "Which tokens look interesting, and why should an agent trust or distrust the signal?"

The output explains each token with compact reasons instead of just dumping API JSON.

## APIs used

- `GET https://api.jup.ag/tokens/v2/toptrending/1h?limit=10`
- `GET https://api.jup.ag/tokens/v2/toptraded/1h?limit=10`
- `GET https://api.jup.ag/price/v3?ids=<comma-separated-mints>`

The prototype works with keyless Jupiter API access for lightweight demos. For production, set a Jupiter API key and send it via the `x-api-key` header.

## Run

```bash
python3 jupiter_signal_lab.py
```

Optional:

```bash
JUP_API_KEY=your_key python3 jupiter_signal_lab.py --limit 15 --json
```

## Output

The script prints a ranked list of token signals with:

- symbol/name/mint
- current USD price
- 24h price change
- liquidity
- holder count
- organic score label
- computed signal score
- short explanation

## Files

- `jupiter_signal_lab.py` — working prototype
- `DX-REPORT.md` — developer experience report for Jupiter Developer Platform
- `sample-output.json` — generated example output from a real API run

## Safety

Read-only. No wallet required. No transaction signing. No trading execution.
