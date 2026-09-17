"""
Auto-News Site — Daily Article Generator
Reads config.yml for all settings. No other file needs to be edited.
"""

import os
import re
import datetime
import requests
import yaml

# ── Load config ───────────────────────────────────────────────────────────────
def load_config() -> dict:
    with open("config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)

CFG = load_config()

# API keys — env vars take priority (for GitHub Actions secrets), then config.yml
NEWS_API_KEY   = os.getenv("NEWS_API_KEY")   or CFG.get("news_api_key", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or CFG.get("gemini_api_key", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") or CFG.get("pexels_api_key", "")

SITE_NAME   = CFG.get("site_name", "My News Site")
SITE_TOPIC  = CFG.get("site_topic", "technology")
SKIP_WORDS  = [w.strip() for w in CFG.get("skip_keywords", "").split(",") if w.strip()]
EXTRA_TOPICS = [t.strip() for t in CFG.get("extra_topics", "").split(",") if t.strip()]

OUTPUT_DIR = os.path.join("site", "_posts")
USED_FILE  = os.path.join("site", "_data", "used_stories.txt")

# Build category search list from topic
BASE_CATEGORIES = {
    "gaming":   ["gaming", "video games", "game console", "esports", "gaming hardware"],
    "fitness":  ["fitness", "workout", "gym", "health", "nutrition"],
    "finance":  ["personal finance", "investing", "stock market", "crypto", "economy"],
    "cooking":  ["cooking", "food", "recipe", "restaurant", "cuisine"],
    "crypto":   ["cryptocurrency", "bitcoin", "blockchain", "defi", "web3"],
    "travel":   ["travel", "tourism", "destination", "flights", "hotels"],
    "tech":     ["technology", "artificial intelligence", "gadgets", "software", "startup"],
}
CATEGORIES = BASE_CATEGORIES.get(SITE_TOPIC, [SITE_TOPIC]) + EXTRA_TOPICS

# ── Deduplication ─────────────────────────────────────────────────────────────
def load_used() -> set:
    if not os.path.exists(USED_FILE):
        return set()
    with open(USED_FILE, encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}

def mark_used(url: str, title: str):
    os.makedirs(os.path.dirname(USED_FILE), exist_ok=True)
    with open(USED_FILE, "a", encoding="utf-8") as f:
        f.write(url.strip().lower() + "\n")
        f.write(title.strip().lower() + "\n")

# ── Pexels image ──────────────────────────────────────────────────────────────
def fetch_image(query: str) -> str:
    fallbacks = [
        "https://images.pexels.com/photos/3165335/pexels-photo-3165335.jpeg",
        "https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg",
        "https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg",
    ]
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_KEY_HERE":
        return fallbacks[0]
    try:
        clean = re.sub(r'[^a-z0-9 ]', '', query.lower()).strip()[:60]
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": clean, "per_page": 3, "orientation": "landscape"},
            timeout=10
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        if photos:
            # Strip query params to avoid YAML front matter issues
            url = photos[0]["src"]["large2x"].split("?")[0]
            return url
    except Exception as e:
        print(f"[Pexels] {e}")
    return fallbacks[0]

# ── NewsAPI ───────────────────────────────────────────────────────────────────
def fetch_top_story() -> dict:
    used = load_used()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    seen_urls: set = set()

    for category in CATEGORIES:
        params = {
            "q": category, "from": yesterday,
            "sortBy": "popularity", "language": "en",
            "pageSize": 10, "apiKey": NEWS_API_KEY,
        }
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        resp.raise_for_status()
        for a in resp.json().get("articles", []):
            url   = (a.get("url") or "").lower()
            title = (a.get("title") or "").strip()
            if any(kw in title.lower() for kw in SKIP_WORDS):
                continue
            if (a.get("description")
                    and "[Removed]" not in title
                    and url not in seen_urls
                    and url not in used
                    and title.lower() not in used):
                seen_urls.add(url)
                print(f"[NewsAPI] Found: {title}")
                return a
    raise RuntimeError("No new stories found today.")

# ── Gemini article generation ─────────────────────────────────────────────────
def generate_article(story: dict) -> str:
    today     = datetime.date.today().isoformat()
    image_url = fetch_image(story["title"])
    title  = story["title"].encode("ascii", "ignore").decode()[:200]
    desc   = (story.get("description") or "").encode("ascii", "ignore").decode()[:400]
    source = (story.get("source", {}).get("name") or "Unknown").encode("ascii", "ignore").decode()[:100]

    prompt = f"""You are a senior journalist at {SITE_NAME}, a professional website covering {SITE_TOPIC}.
Write a LONG (minimum 900 words), engaging, SEO-optimized article based on this news story.
Write like a professional at IGN or The Verge — insightful, opinionated, with real depth.

NEWS TITLE: {title}
NEWS DESCRIPTION: {desc}
SOURCE: {source}

SEO RULES:
- Title under 65 characters, include main keyword
- Description under 155 characters, include main keyword
- Use keyword in first paragraph
- Write for humans first

Return ONLY valid Jekyll Markdown with EXACTLY this structure:

---
layout: post
title: "COMPELLING SEO TITLE UNDER 65 CHARS"
date: {today}
description: "META DESCRIPTION UNDER 155 CHARS"
categories: ["pick most accurate: Gaming OR AR/VR OR Tech"]
tags: ["tag1", "tag2", "tag3", "tag4", "tag5"]
image: "{image_url}"
---

## TL;DR

3-4 punchy sentences that hook the reader.

## What's Happening

3 detailed paragraphs with full context, names, numbers, dates.

## Deep Dive

2-3 paragraphs of expert analysis with comparisons and data.

## Key Specs & Facts

| Specification | Detail |
|---|---|
| [6+ rows of real relevant specs] | [values] |

## Why This Matters to You

2-3 paragraphs on real-world impact for the reader.

## The Bigger Picture

2 paragraphs on industry trends and the next 12-24 months.

## How It Stacks Up Against the Competition

1-2 paragraphs naming direct rivals.

## Our Take

> 3-4 sentence sharp editorial opinion. Take a clear stance.

## Final Verdict

2 strong paragraphs with a forward-looking prediction.
"""

    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.72, "maxOutputTokens": 8192}
    }
    resp = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
        json=payload, headers=headers, timeout=90
    )
    if not resp.ok:
        print(f"[Gemini Error] {resp.status_code}: {resp.text[:300]}")
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    text = re.sub(r'^```(?:markdown|md)?\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
    print(f"[{SITE_NAME}] Article generated successfully.")
    return text.strip()

# ── Save Jekyll post ──────────────────────────────────────────────────────────
def save_article(content: str, story: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    title_match = re.search(r'^title:\s*["\'](.+?)["\']', content, re.MULTILINE)
    slug = re.sub(r'[^a-z0-9]+', '-', title_match.group(1).lower()).strip('-')[:60] if title_match else "daily-article"
    filepath = os.path.join(OUTPUT_DIR, f"{datetime.date.today().isoformat()}-{slug}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    mark_used(story.get("url", ""), story["title"])
    print(f"[{SITE_NAME}] Saved: {filepath}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{SITE_NAME}] Starting daily generation...")
    story   = fetch_top_story()
    article = generate_article(story)
    save_article(article, story)
    print(f"[{SITE_NAME}] Done.")
