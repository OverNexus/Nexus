"""
Auto-News Site — One-Time Setup Script
Run this once after editing config.yml to configure your Jekyll site automatically.
Usage: python setup.py
"""

import yaml
import re
import os

def load_config():
    with open("config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)

def update_jekyll_config(cfg):
    username  = cfg["github_username"]
    repo      = cfg["repo_name"]
    name      = cfg["site_name"]
    desc      = cfg["site_description"]
    author    = cfg["site_author"]
    hour      = cfg.get("publish_hour", 9)

    jekyll = f"""title: {name}
description: "{desc}"
baseurl: "/{repo}"
url: "https://{username}.github.io"
author: {author}
lang: en

permalink: /posts/:slug/

plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-paginate

paginate: 9
paginate_path: "/page/:num/"

markdown: kramdown
highlighter: rouge

social:
  name: {name}

feed:
  title: {name}
  description: "{desc}"

defaults:
  - scope:
      path: ""
      type: "posts"
    values:
      layout: "post"
      author: "{author}"
"""
    with open("site/_config.yml", "w", encoding="utf-8") as f:
        f.write(jekyll)
    print(f"✅ site/_config.yml updated")

    # Update workflow schedule
    workflow_path = ".github/workflows/daily_publish.yml"
    with open(workflow_path, encoding="utf-8") as f:
        wf = f.read()
    wf = re.sub(r"cron: '.*?'", f"cron: '0 {hour} * * *'", wf)
    with open(workflow_path, "w", encoding="utf-8") as f:
        f.write(wf)
    print(f"✅ Workflow schedule set to {hour}:00 UTC daily")

    # Update header logo text
    header_path = "site/_includes/header.html"
    with open(header_path, encoding="utf-8") as f:
        h = f.read()
    # Replace logo text between NEXUSNEWS markers
    parts = name.upper().split()
    if len(parts) >= 2:
        logo_html = f"{parts[0]}<strong>{''.join(parts[1:])}</strong>"
    else:
        logo_html = f"<strong>{name.upper()}</strong>"
    h = re.sub(r'NEXUS<strong>NEWS</strong>', logo_html, h)
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(h)

    footer_path = "site/_includes/footer.html"
    with open(footer_path, encoding="utf-8") as f:
        ft = f.read()
    ft = re.sub(r'NEXUS<strong>NEWS</strong>', logo_html, ft)
    with open(footer_path, "w", encoding="utf-8") as f:
        f.write(ft)
    print(f"✅ Site name updated to '{name}'")

if __name__ == "__main__":
    print("🚀 Auto-News Site Setup")
    print("=" * 40)
    cfg = load_config()

    # Validate keys
    warnings = []
    if cfg.get("news_api_key") in ("", "YOUR_NEWSAPI_KEY_HERE"):
        warnings.append("⚠️  news_api_key is not set")
    if cfg.get("gemini_api_key") in ("", "YOUR_GEMINI_KEY_HERE"):
        warnings.append("⚠️  gemini_api_key is not set")
    if cfg.get("pexels_api_key") in ("", "YOUR_PEXELS_KEY_HERE"):
        warnings.append("⚠️  pexels_api_key is not set (images will use fallbacks)")

    update_jekyll_config(cfg)

    if warnings:
        print("\n" + "\n".join(warnings))
        print("\n⚠️  Add your API keys to config.yml and re-run setup.py")
    else:
        print("\n✅ All done! Your site is configured.")
        print(f"\n👉 Next steps:")
        print(f"   1. Push to GitHub: git add . && git commit -m 'setup' && git push")
        print(f"   2. Add secrets in GitHub: Settings → Secrets → Actions")
        print(f"      NEWS_API_KEY, GEMINI_API_KEY, PEXELS_API_KEY")
        print(f"   3. Enable GitHub Pages: Settings → Pages → GitHub Actions")
        print(f"   4. Run the workflow: Actions → Daily Article Publisher → Run workflow")
        print(f"\n🌐 Your site will be live at: https://{cfg['github_username']}.github.io/{cfg['repo_name']}/")
