#!/usr/bin/env python3
"""
PIYUSH_SHARMA :: README GENERATOR v2
Visual language: Unix /proc /var/log dmesg lsmod journalctl
NOT the generic ┌─┐ box-border cyberpunk style
Auto-runs via GitHub Actions every 6 hours
"""

import os
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "piyushCodes7"
TOKEN = os.environ.get("GH_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "piyushCodes7-readme-generator"
}

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

def fetch_orgs():
    return gh_get(f"https://api.github.com/users/{USERNAME}/orgs") or []

def fetch_events():
    return gh_get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=40") or []

def compute_stats(repos):
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    og    = [r for r in repos if not r.get("fork")]
    langs = {}
    for r in repos:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    top_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:8]
    return {"stars": stars, "forks": forks, "original": len(og), "top_langs": top_langs}

def pbar(val, max_val, width=10):
    filled = int((val / max(max_val, 1)) * width)
    return "▓" * filled + "░" * (width - filled)

def build_lsmod(stats):
    skills = [
        ("python",       "3.x",    "ACTIVE",       9),
        ("c / c++",      "—",      "LOADED",        7),
        ("javascript",   "ES6+",   "LOADED",        6),
        ("html / css",   "5/3",    "LOADED",        6),
        ("php",          "8.x",    "INSTALLED",     4),
        ("fastapi",      "latest", "ACTIVE",        7),
        ("flask",        "3.x",    "LOADED",        6),
        ("numpy/pandas", "—",      "INSTALLING",    5),
        ("sql / pl-sql", "—",      "INSTALLING",    4),
        ("git",          "—",      "ACTIVE",        7),
        ("machine_lrng", "—",      "COMPILING...",  3),
    ]
    lines = ["```"]
    lines.append(f"  {'MODULE':<18} {'VER':<8} {'STATE':<14} PROFICIENCY")
    lines.append("  " + "─" * 58)
    for mod, ver, state, p in skills:
        lines.append(f"  {mod:<18} {ver:<8} {state:<14} [{pbar(p,9)}]")

    if stats["top_langs"]:
        lines.append("")
        lines.append(f"  {'LANG IN REPOS':<18} {'REPOS':<8} {'DISTRIBUTION'}")
        lines.append("  " + "─" * 58)
        max_lc = stats["top_langs"][0][1]
        for lang, count in stats["top_langs"]:
            lines.append(f"  {lang:<18} {count:<8} [{pbar(count, max_lc)}]")
    lines.append("```")
    return "\n".join(lines)

def build_projects(repos):
    hardcoded = [
        {
            "name": "HIMACHAL-AI-TOUR-GUIDE",
            "match": ["himachal", "tour", "guide"],
            "type": "AI-Powered Web Application",
            "stack": "Python · Flask · AI/ML Integration",
            "status": "DEPLOYED ✓",
            "desc": [
                "// TODO: ADD_DESCRIPTION",
                "// What problem? Who is it for? What does it do?",
                "// e.g. AI travel guide for Himachal Pradesh tourists",
            ]
        },
        {
            "name": "SENTINAI",
            "match": ["sentinai", "sentin"],
            "type": "Android ML Network Security System",
            "stack": "Python · Android Java · ONNX · Liquid CfC Neural Nets",
            "status": "HACKATHON BUILD ✓  [NIT Hamirpur]",
            "desc": [
                "// TODO: ADD_DESCRIPTION",
                "// Core: Biometric Traffic Entanglement",
                "// Detects: SAFE · C2_BEACON · AI_MIMICRY · DATA_EXFIL",
            ]
        },
        {
            "name": "ASHA-VANI",
            "match": ["asha", "vani", "ashavani"],
            "type": "3-Stage Voice Assistant Pipeline",
            "stack": "Python · STT · Inference Engine · TTS",
            "status": "IN PROGRESS ⚡",
            "desc": [
                "// TODO: ADD_DESCRIPTION",
                "// Pipeline: listen_once() → infer() → speak()",
            ]
        },
        {
            "name": "LARVI",
            "match": ["larvi"],
            "type": "[CLASSIFIED]",
            "stack": "—",
            "status": "EARLY BUILD ⚡",
            "desc": [
                "// TODO: ADD_DESCRIPTION when ready",
            ]
        },
    ]

    # try to match live repo data
    live_map = {}
    for r in repos:
        rname = r["name"].lower().replace("-","").replace("_","")
        live_map[rname] = r

    blocks = []
    shown_repos = set()

    for i, proj in enumerate(hardcoded):
        live = {}
        for keyword in proj["match"]:
            for key, r in live_map.items():
                if keyword in key:
                    live = r
                    shown_repos.add(r["name"])
                    break
            if live:
                break

        stars   = live.get("stargazers_count", 0)
        forks   = live.get("forks_count", 0)
        updated = live.get("updated_at", "")[:10] or "—"
        url     = live.get("html_url", f"github.com/{USERNAME}")
        status  = "ARCHIVED" if live.get("archived") else proj["status"]

        block = [f'**`[JOB_{i+1:02d}]`** &nbsp;**{proj["name"]}**', "```"]
        block.append(f'  TYPE    :  {proj["type"]}')
        block.append(f'  STACK   :  {proj["stack"]}')
        block.append(f'  STATUS  :  {status}')
        if stars or forks:
            block.append(f'  METRICS :  ★ {stars}  ·  ⑂ {forks}  ·  updated {updated}')
        block.append(f'  REPO    :  {url}')
        for d in proj["desc"]:
            block.append(f'  {d}')
        block.append("```")
        blocks.append("\n".join(block))

    # extra live repos not in hardcoded
    extras = [r for r in repos if not r.get("fork") and r["name"] not in shown_repos]
    extras = sorted(extras, key=lambda r: r.get("stargazers_count",0), reverse=True)[:2]
    for i, r in enumerate(extras):
        desc = (r.get("description") or "// No description yet")[:65]
        block = [
            f'**`[JOB_{len(hardcoded)+i+1:02d}]`** &nbsp;**{r["name"].upper()}**',
            "```",
            f'  TYPE    :  Repository',
            f'  STACK   :  {r.get("language") or "?"}',
            f'  STATUS  :  {"ARCHIVED" if r.get("archived") else "ACTIVE"}',
            f'  METRICS :  ★ {r.get("stargazers_count",0)}  ·  ⑂ {r.get("forks_count",0)}  ·  updated {r.get("updated_at","")[:10]}',
            f'  REPO    :  {r.get("html_url","#")}',
            f'  // {desc}',
            "```"
        ]
        blocks.append("\n".join(block))

    return "\n\n".join(blocks)

def build_activity(events):
    labels = {
        "PushEvent":        "[  PUSH  ]",
        "CreateEvent":      "[ CREATE ]",
        "WatchEvent":       "[ STARRED]",
        "ForkEvent":        "[  FORK  ]",
        "PullRequestEvent": "[   PR   ]",
        "IssuesEvent":      "[ ISSUE  ]",
        "DeleteEvent":      "[ DELETE ]",
        "ReleaseEvent":     "[RELEASE ]",
    }
    lines, seen = [], set()
    for e in events:
        t    = e.get("type","")
        repo = e.get("repo",{}).get("name","?").split("/")[-1]
        key  = f"{t}:{repo}"
        if key in seen: continue
        seen.add(key)
        label = labels.get(t, "[  EVENT ]")

        if t == "PushEvent":
            commits = e.get("payload",{}).get("commits",[])
            msg = (commits[-1].get("message","pushed") if commits else "pushed").split("\n")[0][:42]
            lines.append(f"  {label}  {repo:<22}  {msg}")
        elif t == "CreateEvent":
            ref = (e.get("payload",{}).get("ref") or "new ref")[:28]
            lines.append(f"  {label}  {repo:<22}  created {ref}")
        else:
            lines.append(f"  {label}  {repo:<22}")
        if len(lines) >= 10: break

    return "\n".join(lines) if lines else "  [  IDLE  ]  no recent public events"

def build_orgs(orgs):
    if not orgs:
        return (
            "  // No public org memberships detected\n"
            "  // To show orgs: GitHub → Org Settings → Member visibility → Public"
        )
    return "\n".join(
        f"  [{o['login']:<25}]  →  github.com/{o['login']}" for o in orgs
    )

def generate_readme(user, repos, orgs, events):
    stats   = compute_stats(repos)
    now     = datetime.now(timezone.utc)
    ts      = now.strftime("%Y-%m-%d %H:%M UTC")

    followers = user.get("followers", 0)
    following = user.get("following", 0)
    pub_repos = user.get("public_repos", 0)
    created   = user.get("created_at","")[:4]

    try:
        created_dt  = datetime.fromisoformat(user.get("created_at","").replace("Z","+00:00"))
        days_active = (now - created_dt).days
    except:
        days_active = "—"

    kernel_v  = f"{created}.{pub_repos}.{followers}-piyush"

    lsmod_block    = build_lsmod(stats)
    project_block  = build_projects(repos)
    activity_block = build_activity(events)
    org_block      = build_orgs(orgs)

    return f"""<!-- AUTO-GENERATED @ {ts} — DO NOT EDIT MANUALLY -->
<!-- Visual language: Unix system internals (/proc /var/log dmesg lsmod) -->

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=30&duration=1&pause=99999&color=00FF41&center=true&vCenter=true&width=600&height=65&lines=PIYUSH+SHARMA)](https://git.io/typing-svg)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=13&duration=2500&pause=900&color=00FF41&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=65&lines=%24+whoami+%3A%3A+Backend+Engineer+%7C+AI%2FML+Student+%7C+Builder;%24+uptime+%3A%3A+{days_active}+days+%7C+{pub_repos}+repos+%7C+{followers}+followers)](https://git.io/typing-svg)

</div>

---

```
════════════════════════════════════════════════════════════
  /var/log/piyush/identity.log          [{ts}]
════════════════════════════════════════════════════════════

  $ id
  uid=7({USERNAME})  groups=backend,ai-ml,builder,student

  $ uname -a
  HUMAN piyush {kernel_v} BE-CSE-AIML Chitkara-Uni aarch64

  $ uptime
  {days_active} days since init.  no planned downtime.

  $ cat /proc/location
  CURRENT  →  Rajpura, Punjab, IN
  ORIGIN   →  Bilaspur, Himachal Pradesh, IN

  $ cat /proc/stats
  REPOS     →  {pub_repos} total  ({stats["original"]} original)
  STARS     →  {stats["stars"]} earned  ·  FORKS: {stats["forks"]}
  FOLLOWERS →  {followers}  ·  FOLLOWING: {following}
  JOINED    →  {created}

════════════════════════════════════════════════════════════
```

<div align="center">

`BE CSE (AI/ML)` &nbsp;·&nbsp; `Chitkara University` &nbsp;·&nbsp; `2025–2029` &nbsp;·&nbsp; `CGPA: 9.6`

</div>

---

## `$ diff /dev/null /dev/me`

> First-year undergrad. Not an expert — actively becoming one.
> Backend is my home: APIs, pipelines, system logic.
> Frontend? I speak it. Full-time? Not my dialect.
> Currently compiling: **Python → FastAPI → ML → whatever breaks next.**

```python
class PiyushSharma:
    role      = "Backend Engineer"
    studying  = "AI/ML Engineering @ Chitkara University"
    year      = "1st Year (2025–2029)"
    cgpa      = 9.6
    stack     = ["Python", "FastAPI", "Flask", "C", "C++",
                 "JavaScript", "HTML/CSS", "PHP", "SQL/PL-SQL",
                 "NumPy", "Pandas"]
    currently = ["building real projects", "grinding DSA",
                 "learning ML fundamentals", "shipping > perfecting"]
    goal      = "high-impact developer role — no shortcuts"
    mantra    = "ship it. break it. learn. ship again."
    uptime    = "{days_active} days"
```

---

## `$ lsmod | grep skills --all`

{lsmod_block}

---

## `$ journalctl --unit=projects --no-pager`

```
════════════════════════════════════════════════════════════
  PROJECT LOG :: live-pulled from github api @ {ts}
════════════════════════════════════════════════════════════
```

{project_block}

---

## `$ dmesg | tail -n 10`

```
════════════════════════════════════════════════════════════
  KERNEL EVENT LOG :: {USERNAME}          [LIVE FEED]
════════════════════════════════════════════════════════════

{activity_block}

════════════════════════════════════════════════════════════
```

---

## `$ cat /proc/achievements`

```
════════════════════════════════════════════════════════════
  ACHIEVEMENT REGISTRY
════════════════════════════════════════════════════════════

  ACADEMIC
  ─────────────────────────────────────────────────────
  CGPA  9.6 / 10  @  Chitkara University  (Sem 1)
  STATUS  →  semester_1.exe  returned 0  [SUCCESS]

  HACKATHONS
  ─────────────────────────────────────────────────────
  // TODO: ADD → "Name | Role | Year | Result"
  // SentinAI | Builder | 2025 | NIT Hamirpur

  CERTIFICATIONS
  ─────────────────────────────────────────────────────
  // TODO: ADD → "Course | Platform | Year | Status"

════════════════════════════════════════════════════════════
```

---

## `$ cat /sys/class/net/orgs`

```
{org_block}
```

---

## `$ ping --all connection_endpoints`

```
════════════════════════════════════════════════════════════
  NETWORK SCAN :: {USERNAME}
════════════════════════════════════════════════════════════

  github      →  github.com/{USERNAME:<22}  [200 OK]
  linkedin    →  linkedin.com/in/{USERNAME:<16}  [200 OK]
  leetcode    →  leetcode.com/{USERNAME:<22}  [200 OK]
  codeforces  →  codeforces.com/{USERNAME:<20}  [200 OK]
  kaggle      →  kaggle.com/{USERNAME:<24}  [200 OK]
  email       →  sharmapiyush74860@gmail.com        [OPEN]

  LATENCY: <24h  |  RESPONSE_RATE: 100%  |  SPAM: FILTERED

════════════════════════════════════════════════════════════
```

---

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=chartreuse-dark&border_color=00FF41&title_color=00FF41&icon_color=00FF41&text_color=c9d1d9&bg_color=0d1117&rank_icon=github&count_private=true)

![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=chartreuse-dark&border_color=00FF41&title_color=00FF41&text_color=c9d1d9&bg_color=0d1117)

![Streak](https://streak-stats.demolab.com?user={USERNAME}&theme=dark&border=00FF41&ring=00FF41&fire=FF6B35&currStreakLabel=00FF41&sideLabels=00FF41&dates=8b949e&background=0d1117)

![Visitor Count](https://komarev.com/ghpvc/?username={USERNAME}&color=00ff41&style=flat-square&label=profile+views)

</div>

---

```
════════════════════════════════════════════════════════════
  $ exit --graceful

  [LOG]  not an expert. not pretending to be one.
  [LOG]  first year. 9.6 cgpa. building real things.
  [LOG]  every commit is a diff from who i was yesterday.
  [LOG]  {ts}  process still running in background.

  connection closed by remote host.
  piyush_sharma.exe  —  alive.
════════════════════════════════════════════════════════════
```
"""

def main():
    print("[BOOT] README generator v2 starting...")
    user = fetch_user()
    if not user:
        print("[ERROR] Could not fetch user. Check GH_TOKEN.")
        return

    print(f"[OK] User   : {user.get('login')}")
    repos  = fetch_repos();  print(f"[OK] Repos  : {len(repos)}")
    orgs   = fetch_orgs();   print(f"[OK] Orgs   : {len(orgs)}")
    events = fetch_events(); print(f"[OK] Events : {len(events)}")

    readme = generate_readme(user, repos, orgs, events)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("[DONE] README.md regenerated.")

if __name__ == "__main__":
    main()