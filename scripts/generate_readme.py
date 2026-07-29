#!/usr/bin/env python3
"""
PIYUSH_SHARMA :: README GENERATOR v4 (Elite Engineer Layout)
Auto-runs via GitHub Actions every 6 hours
"""

import os
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "piyushCodes7"
TOKEN = os.environ.get("GH_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "piyushCodes7-readme-generator"
}
if not TOKEN:
    del HEADERS["Authorization"]

def gh_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[WARN] Failed: {url} → {e}")
        return None

def fetch_user():
    return gh_get(f"https://api.github.com/users/{USERNAME}")

def fetch_repos():
    repos, page = [], 1
    while True:
        data = gh_get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated")
        if not data: break
        repos.extend(data)
        if len(data) < 100: break
        page += 1
    return repos

def fetch_events():
    return gh_get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=40") or []

def build_projects(repos):
    hardcoded = [
        {
            "name": "Himachal AI Tour Guide",
            "match": ["himachal", "tour", "guide"],
            "stack": "Python, Flask, AI/ML",
            "status": "Production",
            "desc": "AI-Powered travel guide web application for tourists in Himachal Pradesh."
        },
        {
            "name": "SentinAI",
            "match": ["sentinai", "sentin"],
            "stack": "Python, Android, ONNX",
            "status": "Hackathon Build",
            "desc": "Android ML Network Security System with Biometric Traffic Entanglement."
        },
        {
            "name": "ASHA-VANI",
            "match": ["asha", "vani", "ashavani"],
            "stack": "Python, ML",
            "status": "In Progress",
            "desc": "3-Stage Voice Assistant Pipeline (STT → Inference → TTS)."
        }
    ]

    live_map = {}
    for r in repos:
        rname = r["name"].lower().replace("-","").replace("_","")
        live_map[rname] = r

    blocks = []
    blocks.append("| Project | Description | Architecture / Stack | Status |")
    blocks.append("| :--- | :--- | :--- | :--- |")

    shown_repos = set()
    for proj in hardcoded:
        live = {}
        for keyword in proj["match"]:
            for key, r in live_map.items():
                if keyword in key:
                    live = r
                    shown_repos.add(r["name"])
                    break
            if live:
                break
        
        url = live.get("html_url", f"https://github.com/{USERNAME}")
        stars = live.get("stargazers_count", 0)
        stars_str = f" ★ {stars}" if stars > 0 else ""
        
        blocks.append(f"| **[{proj['name']}]({url})**{stars_str} | {proj['desc']} | `{proj['stack']}` | {proj['status']} |")

    # Add latest extra public repos
    extras = [r for r in repos if not r.get("fork") and r["name"] not in shown_repos]
    extras = sorted(extras, key=lambda r: r.get("updated_at",""), reverse=True)[:3]
    
    for r in extras:
        desc = (r.get("description") or "Repository")[:65]
        lang = r.get("language") or "Mixed"
        stars = r.get("stargazers_count", 0)
        stars_str = f" ★ {stars}" if stars > 0 else ""
        blocks.append(f"| **[{r['name']}]({r['html_url']})**{stars_str} | {desc} | `{lang}` | Active |")

    return "\n".join(blocks)

def build_activity(events):
    labels = {
        "PushEvent":        "Pushed code to",
        "CreateEvent":      "Created repository",
        "WatchEvent":       "Starred",
        "ForkEvent":        "Forked",
        "PullRequestEvent": "Opened PR in",
        "IssuesEvent":      "Opened issue in",
    }
    lines, seen = [], set()
    for e in events:
        t    = e.get("type","")
        repo = e.get("repo",{}).get("name","?").split("/")[-1]
        key  = f"{t}:{repo}"
        if key in seen: continue
        seen.add(key)
        label = labels.get(t, "Activity in")
        lines.append(f"- {label} **{repo}**")
        if len(lines) >= 5: break

    if not lines:
        return "- No recent public activity."
    return "\n".join(lines)


def generate_readme(user, repos, events):
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    
    project_block = build_projects(repos)
    activity_block = build_activity(events)

    return f"""<!-- AUTO-GENERATED @ {ts} — DO NOT EDIT MANUALLY -->

# Piyush Sharma
**Backend Engineer & AI/ML Developer**
<br/>
[LinkedIn](https://linkedin.com/in/piyushCodes7) · [Email](mailto:sharmapiyush74860@gmail.com) · [LeetCode](https://leetcode.com/piyushCodes7)

Building intelligent systems, scalable APIs, and exploring the depths of machine learning. Currently compiling my way through Python, FastAPI, and ML architectures.

---

### Core Competencies

- **Languages:** Python, C++, C, JavaScript, PHP
- **Frameworks & Libs:** FastAPI, Flask, NumPy, Pandas
- **Infrastructure & Tools:** MySQL, Git, Linux
- **Focus Areas:** System Architecture, API Design, Data Pipelines, AI/ML Integration

---

### Engineering Projects

{project_block}

---

### Telemetry & Analytics

<p align="left">
  <img src="https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=github_dark&hide_border=true&rank_icon=github&count_private=true" alt="GitHub Stats" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=github_dark&hide_border=true" alt="Top Langs" />
</p>

---

### Recent Activity

{activity_block}

<br>
<i>Automated via GitHub Actions. Last synced: {ts}.</i>
"""

def main():
    print("[BOOT] README generator v4 starting...")
    user = fetch_user()
    if not user:
        print("[ERROR] Could not fetch user. Check GH_TOKEN.")
        return

    print(f"[OK] User   : {user.get('login')}")
    repos  = fetch_repos();  print(f"[OK] Repos  : {len(repos)}")
    events = fetch_events(); print(f"[OK] Events : {len(events)}")

    readme = generate_readme(user, repos, events)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("[DONE] README.md regenerated.")

if __name__ == "__main__":
    main()