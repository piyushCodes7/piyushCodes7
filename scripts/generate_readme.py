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
        if len(lines) >= 6: break

    if not lines:
        return "- 💤 System currently in standby mode."
    return "\n".join(lines)


def generate_readme(user, repos, events):
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    
    project_rows = build_projects(repos)
    activity_block = build_activity(events)

    return f"""<!-- AUTOMATED SYNC @ {ts} -->
<div align="center">
  <img src="assets/banner.png" alt="Cyber Developer Pixel Art" width="100%" style="border-radius:12px; box-shadow: 0 0 20px rgba(255,255,255,0.1);" />
</div>

<br/>

<div align="center">
  <a href="https://github.com/piyushCodes7">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=30&duration=3000&pause=1000&color=FFFFFF&center=true&vCenter=true&width=700&height=50&lines=PIYUSH+SHARMA;BACKEND+ENGINEER;AI%2FML+ARCHITECT;SYSTEMS+BUILDER" alt="Typing Header" />
  </a>
  <p>
    <b>BE CSE (AI/ML) @ Chitkara University</b> • <b>CGPA: 9.6</b><br/>
    <i>Building intelligent systems, scalable APIs, and exploring the depths of machine learning.</i>
  </p>
  
  <p>
    <a href="https://linkedin.com/in/piyushCodes7"><img src="https://img.shields.io/badge/-LinkedIn-000000?style=for-the-badge&logo=linkedin&logoColor=white&color=090909"/></a>
    <a href="mailto:sharmapiyush74860@gmail.com"><img src="https://img.shields.io/badge/-Email-000000?style=for-the-badge&logo=gmail&logoColor=white&color=090909"/></a>
    <a href="https://leetcode.com/piyushCodes7"><img src="https://img.shields.io/badge/-LeetCode-000000?style=for-the-badge&logo=leetcode&logoColor=white&color=090909"/></a>
  </p>
</div>

---

### 🚀 Highlighted Engineering Systems

<table>
  <thead>
    <tr>
      <th>Project</th>
      <th>Description</th>
      <th>Architecture</th>
    </tr>
  </thead>
  <tbody>
{project_rows}
  </tbody>
</table>

---

<table width="100%">
<tr>
<td width="50%" valign="top">

### 🛠️ Tech Stack & Arsenal

- **Languages:** Python, C++, C, JavaScript, PHP
- **Frameworks:** FastAPI, Flask, Pandas, NumPy
- **Databases:** MySQL, SQLite
- **Tools:** Linux, Git, Docker, GitHub Actions

</td>
<td width="50%" valign="top">

### ⚡ Live Activity Stream

{activity_block}

</td>
</tr>
</table>

---

### 📊 Real-Time Telemetry

<div align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=piyushCodes7&theme=tokyonight&hide_border=true&border_radius=10" width="48%" alt="Streak Stat" />
  <img src="https://github-readme-stats.vercel.app/api?username=piyushCodes7&show_icons=true&theme=tokyonight&hide_border=true&rank_icon=github&border_radius=10" width="48%" alt="GitHub Stats" />
  <br/><br/>
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=piyushCodes7&layout=compact&theme=tokyonight&hide_border=true&border_radius=10" width="60%" alt="Top Languages" />
  <br/><br/>
  <img src="https://ghchart.rshah.org/FFFFFF/piyushCodes7" alt="Piyush's Github Contributions" width="100%" style="filter: invert(1) hue-rotate(180deg);" />
</div>

<br/>
<div align="center">
  <sub>🤖 <i>Auto-updated every 6 hours via GitHub Actions • Last Sync: {ts}</i></sub>
</div>
"""

def main():
    print("[BOOT] README generator v5 starting...")
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