# Auto-News Site

An automated AI-powered news website that publishes a fresh article every day — completely free to run, no coding required after setup.

## What It Does

Every morning at 9AM, the system automatically:
1. Finds the top trending news story in your niche
2. Writes a full professional article using AI
3. Finds a matching photo
4. Publishes it to your website
5. Updates Google's index

**Cost: $0/month. Effort after setup: $0.**

---

## Setup Guide (15 minutes)

### Step 1 — Get your free API keys

You need 3 free API keys. Click each link, sign up, and copy your key.

| Service | What it does | Get key |
|---|---|---|
| NewsAPI | Finds trending news | [newsapi.org/register](https://newsapi.org/register) |
| Google Gemini | Writes the articles | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Pexels | Article photos | [pexels.com/api](https://www.pexels.com/api/) |

### Step 2 — Edit config.yml

Open `config.yml` in any text editor (Notepad works). Fill in:

```yaml
site_name: "Your Site Name"
github_username: "your_github_username"
repo_name: "your_repo_name"
site_topic: "gaming"        # your niche
news_api_key: "paste key here"
gemini_api_key: "paste key here"
pexels_api_key: "paste key here"
```

**Available topics:** gaming, fitness, finance, cooking, crypto, travel, tech

### Step 3 — Run setup

Open a terminal in this folder and run:
```
python setup.py
```

This automatically configures your site with your settings.

### Step 4 — Create a GitHub repo

1. Go to [github.com/new](https://github.com/new)
2. Create a **public** repo with the same name as `repo_name` in your config
3. Leave it empty (no README)

### Step 5 — Push to GitHub

In your terminal:
```
git init
git add .
git commit -m "initial setup"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 6 — Add secrets to GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:
- `NEWS_API_KEY` → your NewsAPI key
- `GEMINI_API_KEY` → your Gemini key
- `PEXELS_API_KEY` → your Pexels key

### Step 7 — Enable GitHub Pages

Go to repo → **Settings** → **Pages** → Source → **GitHub Actions** → Save

### Step 8 — Run the first article

Go to repo → **Actions** → **Daily Article Publisher** → **Run workflow**

Your site will be live at `https://YOUR_USERNAME.github.io/YOUR_REPO/` in 2-3 minutes.

---

## Changing Your Niche

Edit `site_topic` in `config.yml` and run `python setup.py` again.

## Changing Publishing Time

Edit `publish_hour` in `config.yml` (UTC time, 0-23) and run `python setup.py` again.

## Support

If something doesn't work, check:
1. All 3 API keys are correctly added as GitHub secrets
2. GitHub Pages source is set to "GitHub Actions"
3. The workflow ran successfully (green checkmark in Actions tab)
