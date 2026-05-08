#!/usr/bin/env python3
"""Jupiter Signal Lab: read-only signal ranking from Jupiter APIs."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

BASE = "https://api.jup.ag"
LITE_BASE = "https://lite-api.jup.ag"


def get_json(path: str, api_key: str | None = None, timeout: int = 25) -> Any:
    """Fetch JSON with a small retry/fallback path for keyless demo rate limits."""
    url = path if path.startswith("http") else BASE + path
    headers = {"Accept": "application/json", "User-Agent": "jupiter-signal-lab/0.1"}
    if api_key:
        headers["x-api-key"] = api_key

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status < 200 or r.status >= 300:
                    raise RuntimeError(f"HTTP {r.status}: {url}")
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            # Keyless api.jup.ag is intentionally low rate. For read-only endpoints,
            # lite-api.jup.ag is a practical fallback for demos.
            if "429" in str(exc) and not api_key and url.startswith(BASE):
                url = url.replace(BASE, LITE_BASE, 1)
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def n(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def token_stats_score(token: dict[str, Any]) -> tuple[float, list[str]]:
    reasons: list[str] = []
    liq = n(token.get("liquidity"))
    holder_count = n(token.get("holderCount"))
    organic_score = n(token.get("organicScore"))
    stats1h = token.get("stats1h") or {}
    stats24h = token.get("stats24h") or {}

    pc1h = n(stats1h.get("priceChange"))
    pc24h = n(stats24h.get("priceChange"))
    buy_organic = n(stats1h.get("buyOrganicVolume"))
    sell_organic = n(stats1h.get("sellOrganicVolume"))
    num_traders = n(stats1h.get("numTraders"))
    holder_change = n(stats24h.get("holderChange"))

    # Scoring deliberately rewards interpretable, robust signals over pure momentum.
    score = 0.0
    score += clamp(math.log10(max(liq, 1)) * 8, 0, 60)
    score += clamp(math.log10(max(holder_count, 1)) * 5, 0, 35)
    score += clamp(organic_score / 2, 0, 50)
    score += clamp(abs(pc1h) * 1.2, 0, 18)
    score += clamp(abs(pc24h) * 0.7, 0, 18)
    score += clamp(math.log10(max(num_traders, 1)) * 4, 0, 18)

    organic_delta = buy_organic - sell_organic
    if buy_organic + sell_organic > 0:
        imbalance = organic_delta / (buy_organic + sell_organic)
        score += clamp(abs(imbalance) * 15, 0, 15)
        if imbalance > 0.15:
            reasons.append("organic buy pressure")
        elif imbalance < -0.15:
            reasons.append("organic sell pressure")

    if liq > 1_000_000:
        reasons.append("deep liquidity")
    elif liq < 100_000:
        reasons.append("thin liquidity risk")
        score -= 15

    if organic_score >= 70:
        reasons.append("high organic score")
    elif organic_score and organic_score < 35:
        reasons.append("low organic score risk")
        score -= 10

    if pc1h > 3:
        reasons.append("strong 1h momentum")
    elif pc1h < -3:
        reasons.append("sharp 1h drawdown")

    if holder_change < -0.05:
        reasons.append("holder drift negative")
        score -= 5
    elif holder_change > 0.05:
        reasons.append("holder base expanding")

    if not reasons:
        reasons.append("mixed/neutral signal")

    return round(max(score, 0), 2), reasons[:4]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("JUP_API_KEY")
    limit = max(3, min(args.limit, 50))

    trending = get_json(f"/tokens/v2/toptrending/1h?limit={limit}", api_key)
    toptraded = get_json(f"/tokens/v2/toptraded/1h?limit={limit}", api_key)

    by_id: dict[str, dict[str, Any]] = {}
    source_tags: dict[str, set[str]] = {}
    for source, rows in [("toptrending", trending), ("toptraded", toptraded)]:
        for row in rows:
            mint = row.get("id")
            if not mint:
                continue
            by_id[mint] = {**by_id.get(mint, {}), **row}
            source_tags.setdefault(mint, set()).add(source)

    ids = list(by_id)[:50]
    price_map = get_json("/price/v3?" + urllib.parse.urlencode({"ids": ",".join(ids)}), api_key)

    signals = []
    for mint, token in by_id.items():
        score, reasons = token_stats_score(token)
        price = price_map.get(mint, {}) if isinstance(price_map, dict) else {}
        signals.append({
            "symbol": token.get("symbol"),
            "name": token.get("name"),
            "mint": mint,
            "sources": sorted(source_tags.get(mint, [])),
            "usdPrice": price.get("usdPrice", token.get("usdPrice")),
            "priceChange24h": price.get("priceChange24h", (token.get("stats24h") or {}).get("priceChange")),
            "liquidity": token.get("liquidity"),
            "holderCount": token.get("holderCount"),
            "organicScore": token.get("organicScore"),
            "organicScoreLabel": token.get("organicScoreLabel"),
            "signalScore": score,
            "reasons": reasons,
        })

    signals.sort(key=lambda x: x["signalScore"], reverse=True)
    payload = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "apiBase": BASE,
        "apisUsed": ["tokens/v2/toptrending", "tokens/v2/toptraded", "price/v3"],
        "signals": signals[:limit],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print("Jupiter Signal Lab — read-only token intelligence")
    print(f"Generated: {payload['generatedAt']}")
    print()
    for i, s in enumerate(payload["signals"], 1):
        price = s["usdPrice"]
        p24 = s["priceChange24h"]
        print(f"{i:02d}. {s['symbol']} — {s['name']}")
        print(f"    score={s['signalScore']} price=${price:.6g} 24h={p24:.2f}% sources={','.join(s['sources'])}")
        print(f"    mint={s['mint']}")
        print(f"    why: {', '.join(s['reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
