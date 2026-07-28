#!/usr/bin/env python3
"""
PIYUSH_SHARMA :: README GENERATOR v3 (Professional Layout)
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
            "status": "🟢 Deployed",
            "desc": "AI-Powered travel guide web application for tourists in Himachal Pradesh."
        },
        {
            "name": "SentinAI",
            "match": ["sentinai", "sentin"],
            "stack": "Python, Android, ONNX, Liquid CfC",
            "status": "🏆 Hackathon",
            "desc": "Android ML Network Security System with Biometric Traffic Entanglement."
        },
        {
            "name": "ASHA-VANI",
            "match": ["asha", "vani", "ashavani"],
            "stack": "Python, ML",
            "status": "⚡ In Progress",
            "desc": "3-Stage Voice Assistant Pipeline (STT → Inference → TTS)."
        },
        {
            "name": "LARVI",
            "match": ["larvi"],
            "stack": "—",
            "status": "⚡ Early Build",
            "desc": "Classified Early Build"
        },
    ]

    live_map = {}
    for r in repos:
        rname = r["name"].lower().replace("-","").replace("_","")
        live_map[rname] = r

    blocks = []
    blocks.append("| Project | Description | Tech Stack | Status |")
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
        stars_str = f" ⭐ {stars}" if stars > 0 else ""
        
        blocks.append(f"| **[{proj['name']}]({url})**{stars_str} | {proj['desc']} | {proj['stack']} | {proj['status']} |")

    # Add latest extra public repos
    extras = [r for r in repos if not r.get("fork") and r["name"] not in shown_repos]
    extras = sorted(extras, key=lambda r: r.get("updated_at",""), reverse=True)[:2]
    
    for r in extras:
        desc = (r.get("description") or "Repository")[:65]
        lang = r.get("language") or "?"
        stars = r.get("stargazers_count", 0)
        stars_str = f" ⭐ {stars}" if stars > 0 else ""
        blocks.append(f"| **[{r['name']}]({r['html_url']})**{stars_str} | {desc} | {lang} | 🟢 Active |")

    return "\n".join(blocks)

def build_activity(events):
    labels = {
        "PushEvent":        "🚀 Pushed to",
        "CreateEvent":      "🎉 Created",
        "WatchEvent":       "⭐ Starred",
        "ForkEvent":        "🍴 Forked",
        "PullRequestEvent": "🔄 Opened PR in",
        "IssuesEvent":      "🐛 Opened issue in",
    }
    lines, seen = [], set()
    for e in events:
        t    = e.get("type","")
        repo = e.get("repo",{}).get("name","?").split("/")[-1]
        key  = f"{t}:{repo}"
        if key in seen: continue
        seen.add(key)
        label = labels.get(t, "📝 Activity in")
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

<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=65&duration=2500&pause=500&color=00FF41&center=true&vCenter=true&width=800&height=120&lines=PIYUSH+SHARMA;BACKEND+ENGINEER;AI%2FML+DEVELOPER;INNOVATOR" alt="Piyush Sharma" />
  
  <p align="center">
    <b>Building intelligent systems, scalable APIs, and exploring the depths of machine learning.</b>
    <br />
    <i>BE CSE (AI/ML) @ Chitkara University | CGPA: 9.6</i>
  </p>

  <p align="center">
    <a href="https://linkedin.com/in/piyushCodes7"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
    <a href="mailto:sharmapiyush74860@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
    <a href="https://leetcode.com/piyushCodes7"><img src="https://img.shields.io/badge/-LeetCode-FFA116?style=for-the-badge&logo=LeetCode&logoColor=black" alt="LeetCode" /></a>
  </p>
</div>

---

## 👨‍💻 About Me

- 🚀 Currently compiling my way through **Python → FastAPI → Machine Learning**.
- 🛠️ I specialize in **Backend Development**: APIs, pipelines, system architecture.
- 💡 Learning every day. **Mantra:** *Ship it. Break it. Learn. Ship again.*
- 🏆 **Hackathons & Competitions:** Built *SentinAI* at NIT Hamirpur.
- ⚡ **Fun Fact:** I treat every commit as a diff from who I was yesterday.

---

## 🛠️ Tech Stack & Arsenal

<div align="center">
  
### Languages
<img src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white" />
<img src="https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
<img src="https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white" />

### Frameworks & Libraries
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />

### Databases & Tools
<img src="https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white" />
<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" />
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" />

</div>

---

## 🚀 Highlighted Projects

{project_block}

---

## ⚡ Recent Activity

{activity_block}

---

## 📊 GitHub Analytics

<div align="center">

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight&rank_icon=github&count_private=true)](https://github.com/piyushCodes7)
[![GitHub Streak](https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=tokyonight)](https://github.com/piyushCodes7)
<br><br>
[![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=tokyonight)](https://github.com/piyushCodes7)
<br><br>
[![Profile Views](https://komarev.com/ghpvc/?username={USERNAME}&color=00FF41&style=for-the-badge&label=PROFILE+VIEWS)](https://github.com/piyushCodes7)

</div>

<div align="center">
  <br />
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Alien%20Monster.png" alt="Alien Monster" width="35" height="35" />
  <p><i>Thanks for dropping by! Feel free to reach out for collaborations.</i></p>
</div>
"""

def main():
    print("[BOOT] README generator v3 starting...")
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