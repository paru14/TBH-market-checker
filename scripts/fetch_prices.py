"""
TBH (Task Bar Hero) Steam Market Price Fetcher
Fetches current prices and saves to data/prices.json
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

APP_ID = 3678970
CURRENCY = 8  # JPY

# Items to track - add or remove as needed
TRACKED_ITEMS = [
    # Soul Stones
    "Soul Stone",
    "Soul Stone (Low)",
    "Soul Stone (High)",
    # Equipment
    "Night Boots",
    "Iron Sword",
    "Iron Shield",
    "Iron Armor",
    "Iron Helmet",
    # Crafting Materials
    "Moonstone",
    "Dark Crystal",
    "Shadow Rune",
    "Fire Essence",
    "Ice Shard",
    "Thunder Core",
    "Void Fragment",
    "Magic Gem",
    # Currency / Other
    "Gold Coin",
    "Iron Ore",
    "Copper Ore",
    "Silver Ore",
]

SEARCH_QUERIES = [
    "Soul Stone",
    "Night Boot",
    "Moonstone",
    "Crystal",
    "Rune",
    "Essence",
    "Shard",
    "Core",
    "Fragment",
    "Gem",
    "Coin",
    "Ore",
]


def fetch_search(query: str, count: int = 20) -> list[dict]:
    """Fetch items from Steam Market search API."""
    params = urllib.parse.urlencode({
        "query": query,
        "appid": APP_ID,
        "norender": 1,
        "count": count,
        "currency": CURRENCY,
        "l": "japanese",
    })
    url = f"https://steamcommunity.com/market/search/render/?{params}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; TBH-PriceFetcher/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("results", [])
    except Exception as e:
        print(f"  [WARN] Search '{query}' failed: {e}")
        return []


def fetch_price_overview(hash_name: str) -> dict | None:
    """Fetch price overview for a single item."""
    params = urllib.parse.urlencode({
        "country": "JP",
        "currency": CURRENCY,
        "appid": APP_ID,
        "market_hash_name": hash_name,
    })
    url = f"https://steamcommunity.com/market/priceoverview/?{params}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; TBH-PriceFetcher/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("success"):
                return data
    except Exception as e:
        print(f"  [WARN] Price overview for '{hash_name}' failed: {e}")
    return None


def load_existing(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": {}, "history": {}, "last_updated": None, "fetch_count": 0}


def save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {path}")


def main():
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    now_jst = datetime.fromtimestamp(now.timestamp() + 9 * 3600).strftime("%Y-%m-%d %H:%M JST")

    print(f"=== TBH Market Fetch: {now_jst} ===")

    data_path = "data/prices.json"
    db = load_existing(data_path)
    db["fetch_count"] = db.get("fetch_count", 0) + 1

    seen_hashes: set[str] = set()
    new_items: list[dict] = []

    # Search for items
    for query in SEARCH_QUERIES:
        print(f"\nSearching: '{query}'")
        results = fetch_search(query, count=15)
        print(f"  Found {len(results)} results")

        for r in results:
            hash_name = r.get("hash_name", "")
            if not hash_name or hash_name in seen_hashes:
                continue
            seen_hashes.add(hash_name)
            new_items.append({
                "hash_name": hash_name,
                "name": r.get("name", hash_name),
                "sell_price": r.get("sell_price"),
                "sell_price_text": r.get("sell_price_text", ""),
                "sell_listings": r.get("sell_listings", 0),
            })

        time.sleep(1.5)  # Respect Steam rate limits

    print(f"\nTotal unique items found: {len(new_items)}")

    # Update items and history
    timestamp_key = now.strftime("%Y-%m-%dT%H:00:00Z")  # Round to hour

    updated = 0
    for item in new_items:
        h = item["hash_name"]
        price_raw = item.get("sell_price")
        price_text = item.get("sell_price_text", "")
        listings = item.get("sell_listings", 0)

        # Update current snapshot
        db["items"][h] = {
            "name": item["name"],
            "hash_name": h,
            "sell_price": price_raw,
            "sell_price_text": price_text,
            "sell_listings": listings,
            "last_updated": now_iso,
            "market_url": f"https://steamcommunity.com/market/listings/{APP_ID}/{urllib.parse.quote(h)}",
        }

        # Append to hourly history (keep last 168 entries = 7 days)
        if h not in db["history"]:
            db["history"][h] = []
        history = db["history"][h]
        # Avoid duplicate entries for same hour
        if not history or history[-1].get("t") != timestamp_key:
            history.append({
                "t": timestamp_key,
                "p": price_raw,
                "l": listings,
            })
        # Trim to 168 entries
        if len(history) > 168:
            db["history"][h] = history[-168:]

        updated += 1

    db["last_updated"] = now_iso
    db["last_updated_jst"] = now_jst
    db["app_id"] = APP_ID
    db["total_items"] = len(db["items"])

    save_json(data_path, db)
    print(f"\n✓ Done. {updated} items updated. Total tracked: {len(db['items'])}")


if __name__ == "__main__":
    main()
