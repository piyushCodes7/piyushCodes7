#!/usr/bin/env python3
"""
PIYUSH_SHARMA :: README GENERATOR
Fetches live GitHub data and regenerates README.md
Runs via GitHub Actions on schedule + push
"""

import os
import json
import urllib.request
import urllib.error
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
    repos = []
    page = 1
    while True:
        data = gh_get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated")
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos

def fetch_orgs():
    return gh_get(f"https://api.github.com/users/{USERNAME}/orgs") or []

def fetch_events():
    return gh_get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=30") or []

def fetch_pinned_via_api(repos):
    sorted_repos = sorted(repos, key=lambda r: (r.get("stargazers_count",0) + r.get("forks_count",0)), reverse=True)
    return sorted_repos[:4]

def compute_stats(repos):
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_repos = len(repos)
    not_forked = [r for r in repos if not r.get("fork", True)]

    langs = {}
    for r in repos:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    top_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "stars": total_stars,
        "forks": total_forks,
        "total_repos": total_repos,
        "original_repos": len(not_forked),
        "top_langs": top_langs,
    }

def recent_activity(events):
    lines = []
    seen = set()
    type_labels = {
        "PushEvent": "PUSH  ",
        "CreateEvent": "CREATE",
        "WatchEvent": "STAR  ",
        "ForkEvent": "FORK  ",
        "IssuesEvent": "ISSUE ",
        "PullRequestEvent": "PR    ",
    }
    for e in events:
        t = e.get("type", "")
        repo = e.get("repo", {}).get("name", "?").split("/")[-1]
        key = f"{t}:{repo}"
        if key in seen:
            continue
        seen.add(key)
        label = type_labels.get(t, "EVENT ")
        if t == "PushEvent":
            msg = e.get("payload", {}).get("commits", [{}])[-1].get("message", "pushed code")[:45]
            lines.append(f"  [{label}]  {repo[:25]:<25}  // {msg}")
        elif t == "CreateEvent":
            ref = e.get("payload", {}).get("ref", "new ref")[:30]
            lines.append(f"  [{label}]  {repo[:25]:<25}  // {ref}")
        else:
            lines.append(f"  [{label}]  {repo[:25]:<25}")
        if len(lines) >= 8:
            break
    return lines

def bar(value, max_val, width=20):
    filled = int((value / max(max_val, 1)) * width)
    return "█" * filled + "░" * (width - filled)

def lang_bar(count, max_count, width=14):
    filled = int((count / max(max_count, 1)) * width)
    return "▓" * filled + "░" * (width - filled)

def generate_readme(user, repos, orgs, events):
    stats = compute_stats(repos)
    activity = recent_activity(events)
    pinned = fetch_pinned_via_api(repos)

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    score = min(99, stats["total_repos"] * 2 + stats["stars"] * 5 + stats["forks"] * 3)
    threat_bar = bar(score, 100, 20)

    name = (user.get("name") or USERNAME)[:30]
    bio = (user.get("bio") or "Building. Learning. Becoming.")[:50]
    followers = user.get("followers", 0)
    following = user.get("following", 0)
    public_repos = user.get("public_repos", 0)
    created = user.get("created_at", "")[:4]

    org_names = [o.get("login", "") for o in orgs]
    org_str = (", ".join(org_names) if org_names else "NONE DETECTED")[:40]

    # Language bars — simple table rows, no box borders
    max_lang_count = stats["top_langs"][0][1] if stats["top_langs"] else 1
    lang_lines = []
    for lang, count in stats["top_langs"]:
        lb = lang_bar(count, max_lang_count)
        lang_lines.append(f"  {lang:<16} [{lb}]  {count} repo{'s' if count != 1 else ''}")
    lang_block = "\n".join(lang_lines) if lang_lines else "  NO LANGUAGE DATA"

    # Project mission blocks
    mission_blocks = []
    for i, r in enumerate(pinned[:4]):
        rname = r.get("name", "UNKNOWN")[:35]
        desc = (r.get("description") or "No description logged.")[:55]
        lang = r.get("language") or "?"
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        updated = r.get("updated_at", "")[:10]
        status = "ARCHIVED" if r.get("archived") else "ACTIVE"
        url = r.get("html_url", "#")
        mission_blocks.append(
f"""  MISSION_{i+1:02d}  >>  {rname.upper()}
  STATUS      :  [{status}]
  DESC        :  {desc}
  STACK       :  {lang}  |  STARS {stars}  |  FORKS {forks}
  UPDATED     :  {updated}
  LINK        :  {url}
  {"─" * 60}"""
        )
    missions_str = "\n\n".join(mission_blocks) if mission_blocks else "  NO MISSIONS LOGGED YET."

    activity_str = "\n".join(activity) if activity else "  > NO RECENT ACTIVITY DETECTED"

    readme = f"""<!-- AUTO-GENERATED @ {timestamp} | DO NOT EDIT MANUALLY -->

<div align="center">

```
 ██████╗ ██╗██╗   ██╗██╗   ██╗███████╗██╗  ██╗
 ██╔══██╗██║╚██╗ ██╔╝██║   ██║██╔════╝██║  ██║
 ██████╔╝██║ ╚████╔╝ ██║   ██║███████╗███████║
 ██╔═══╝ ██║  ╚██╔╝  ██║   ██║╚════██║██╔══██║
 ██║     ██║   ██║   ╚██████╔╝███████║██║  ██║
 ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝
              piyushCodes7 :: SYSTEM ONLINE
```

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=13&duration=2000&pause=700&color=00FF41&center=true&vCenter=true&multiline=true&repeat=true&width=680&height=80&lines=%3E+OPERATOR%3A+PIYUSH+SHARMA+%7C+NODE%3A+piyushCodes7;%3E+REPOS%3A+{public_repos}+%7C+FOLLOWERS%3A+{followers}+%7C+BUILDING+SINCE+{created};%3E+STATUS%3A+ONLINE+%7C+LEARNING+%7C+BECOMING)](https://git.io/typing-svg)

</div>

---

## `> whoami`

```
  OPERATOR    : {name}
  HANDLE      : @{USERNAME}
  ORIGIN      : {created} — STILL RUNNING
  FOLLOWERS   : {followers}   FOLLOWING : {following}   REPOS : {public_repos}
  ORGS        : {org_str}
  BIO         : {bio}
  THREAT LVL  : [{threat_bar}] {score}%
  UPTIME      : AMBITION.EXE — NOT STOPPING
  LAST SYNC   : {timestamp}
```

---

## `> cat /sys/stats/live_feed.dat`

```
  GITHUB TELEMETRY                      [ LIVE PULL ]
  ════════════════════════════════════════════════════

  TOTAL REPOS   : {public_repos:<5}   ORIGINAL    : {stats["original_repos"]}
  TOTAL STARS   : {stats["stars"]:<5}   TOTAL FORKS : {stats["forks"]}
  FOLLOWERS     : {followers:<5}   FOLLOWING   : {following}

  LANGUAGE DISTRIBUTION
  ────────────────────────────────────────────────────
{lang_block}
```

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=chartreuse-dark&border_color=00FF41&title_color=00FF41&icon_color=00FF41&text_color=c9d1d9&bg_color=0d1117&hide_border=false&rank_icon=github&count_private=true)

![GitHub Streak](https://streak-stats.demolab.com?user={USERNAME}&theme=dark&border=00FF41&ring=00FF41&fire=FF6B35&currStreakLabel=00FF41&sideLabels=00FF41&dates=8b949e&background=0d1117)

</div>

---

## `> tail -f /var/log/projects/mission_log`

```
  ACTIVE DEPLOYMENTS :: LIVE FROM GITHUB API
  ════════════════════════════════════════════════════════════

{missions_str}
```

---

## `> journalctl --recent -n 8`

```
  RECENT ACTIVITY                       [ AUTO-FETCHED ]
  ════════════════════════════════════════════════════════════

{activity_str}
```

---

## `> ps aux | grep current_mission`

```
  PROCESS                              STATUS
  ─────────────────────────────────────────────────────────
  python_mastery.exe                   RUNNING
  dsa_grind.daemon                     RUNNING
  machine_learning.service             INSTALLING...
  project_shipping.exe                 RUNNING
  ambition_core.sys                    MAX PRIORITY

  OBJECTIVE  : High-impact developer role
  APPROACH   : Build real things. Learn relentlessly.
  README     : Auto-regenerated every 6h by GitHub Actions
```

---

## `> ping connection_endpoints`

```
  ENDPOINT          TARGET                          STATUS
  ─────────────────────────────────────────────────────────
  [GITHUB]          github.com/{USERNAME:<22}  200 OK
  [DASHBOARD]       piyushcodes7.vercel.app         LIVE
  [CONTACT]         open an issue to connect        OPEN
```

---

<div align="center">

```
  ─────────────────────────────────────────────────────────
  [SYS]  This README regenerates itself every 6 hours.
  [SYS]  Real repos. Real commits. Real data. No fluff.
  [SYS]  Not where I want to be yet. Building there.
  [SYS]  Last sync: {timestamp}
  ─────────────────────────────────────────────────────────
```

![Visitor Count](https://komarev.com/ghpvc/?username={USERNAME}&color=00ff41&style=flat-square&label=NODES+CONNECTED)

```
[ END OF TRANSMISSION ]  ///  piyush_sharma.exe — still running
```

</div>
"""
    return readme

def main():
    print("[BOOT] Starting README generation...")
    user = fetch_user()
    if not user:
        print("[ERROR] Could not fetch user data. Check GH_TOKEN.")
        return

    print(f"[OK] User: {user.get('login')}")
    repos = fetch_repos()
    print(f"[OK] Repos: {len(repos)}")
    orgs = fetch_orgs()
    print(f"[OK] Orgs: {len(orgs)}")
    events = fetch_events()
    print(f"[OK] Events: {len(events)}")

    readme = generate_readme(user, repos, orgs, events)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("[DONE] README.md regenerated successfully.")

if __name__ == "__main__":
    main()