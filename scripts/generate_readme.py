#!/usr/bin/env python3
"""
generate_readme.py — live GitHub stats -> README.md

Fetches profile stats (repos, stars, forks, followers, contribution streaks,
top languages) from the GitHub GraphQL API and writes them into README.md
between two HTML marker comments:

    <!-- STATS:START -->
    ...generated content...
    <!-- STATS:END -->

Everything outside the markers (bio, project list, animated SVG embeds,
contact info, ...) is left untouched, so this is safe to run on a 6-hour
cron in GitHub Actions without clobbering hand-written sections.

Usage:
    python generate_readme.py --username piyushCodes7

Auth:
    Needs a token with `read:user` scope (classic PAT is fine, it's free):
    GitHub -> Settings -> Developer settings -> Personal access tokens ->
    Tokens (classic) -> Generate new token -> check `read:user` (and
    `public_repo` if you want private-repo language stats too).
    Store it as a repo secret (e.g. README_TOKEN) and export it as
    GH_README_TOKEN, or pass --token directly.

Exit codes:
    0  success (README unchanged or updated)
    1  fetch/auth/render failure
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0

MARKER_START = "<!-- STATS:START -->"
MARKER_END = "<!-- STATS:END -->"

# Filenames this script will link to if found in --svg-dir, matching the
# animated-terminal SVG set (glitch title / boot sequence / skill bars /
# activity feed). Missing files are silently skipped so a broken pipeline
# never means a broken README.
SVG_ASSETS = {
    "glitch": "glitch-title.svg",
    "boot": "boot-sequence.svg",
    "skills": "skill-bars.svg",
    "activity": "activity-feed.svg",
}

PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

logger = logging.getLogger("generate_readme")


class GitHubAPIError(RuntimeError):
    """Raised on a well-formed but unsuccessful GraphQL response."""


@dataclass
class LanguageStat:
    name: str
    bytes_: int
    color: str | None = None


@dataclass
class ProfileStats:
    username: str
    public_repos: int
    total_stars: int
    total_forks: int
    followers: int
    contributions_last_year: int
    current_streak: int
    longest_streak: int
    top_languages: list[LanguageStat] = field(default_factory=list)
    total_language_bytes: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GitHubClient:
    """Thin GraphQL client with retry/backoff for transient failures."""

    def __init__(self, token: str, timeout: float = 15.0) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "generate-readme-script",
            }
        )
        self.timeout = timeout

    def fetch_profile_data(self, username: str) -> dict[str, Any]:
        return self._graphql(PROFILE_QUERY, {"login": username})

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.post(
                    GITHUB_GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                    timeout=self.timeout,
                )
                if response.status_code in (502, 503, 504):
                    raise GitHubAPIError(f"transient {response.status_code} from GitHub")
                response.raise_for_status()

                payload = response.json()
                if "errors" in payload and payload["errors"]:
                    raise GitHubAPIError("; ".join(e.get("message", "?") for e in payload["errors"]))
                if not payload.get("data", {}).get("user"):
                    raise GitHubAPIError("user not found or token lacks read:user scope")
                return payload["data"]

            except (requests.RequestException, GitHubAPIError) as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    break
                wait = RETRY_BACKOFF_SECONDS * attempt
                logger.warning("GraphQL attempt %d/%d failed (%s), retrying in %.1fs", attempt, MAX_RETRIES, exc, wait)
                time.sleep(wait)

        raise GitHubAPIError(f"GitHub API request failed after {MAX_RETRIES} attempts: {last_error}")


class StatsAggregator:
    """Pure functions turning raw GraphQL payloads into ProfileStats fields."""

    @staticmethod
    def compute_streaks(days: list[dict[str, Any]]) -> tuple[int, int]:
        if not days:
            return 0, 0

        today = datetime.now(timezone.utc).date()
        parsed = sorted(
            ((datetime.fromisoformat(d["date"]).date(), d["contributionCount"]) for d in days),
            key=lambda item: item[0],
        )

        longest = running = 0
        for _, count in parsed:
            running = running + 1 if count > 0 else 0
            longest = max(longest, running)

        current = 0
        for date_, count in reversed(parsed):
            if date_ == today and count == 0:
                continue  # today isn't over yet, don't let it break the streak
            if count > 0:
                current += 1
            else:
                break

        return current, longest

    @staticmethod
    def aggregate_languages(
        repo_nodes: list[dict[str, Any]], exclude: set[str] | None = None
    ) -> tuple[list[LanguageStat], int]:
        exclude = exclude or set()
        totals: dict[str, LanguageStat] = {}

        for repo in repo_nodes:
            for edge in repo.get("languages", {}).get("edges", []):
                name = edge["node"]["name"]
                if name in exclude:
                    continue
                if name in totals:
                    totals[name].bytes_ += edge["size"]
                else:
                    totals[name] = LanguageStat(name=name, bytes_=edge["size"], color=edge["node"].get("color"))

        ranked = sorted(totals.values(), key=lambda lang: lang.bytes_, reverse=True)
        total_bytes = sum(lang.bytes_ for lang in ranked)
        return ranked, total_bytes


def build_stats(data: dict[str, Any], username: str, top_n: int, exclude_languages: set[str]) -> ProfileStats:
    user = data["user"]
    repos = user["repositories"]["nodes"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [d for week in calendar["weeks"] for d in week["contributionDays"]]

    current_streak, longest_streak = StatsAggregator.compute_streaks(days)
    languages, total_bytes = StatsAggregator.aggregate_languages(repos, exclude_languages)

    return ProfileStats(
        username=username,
        public_repos=user["repositories"]["totalCount"],
        total_stars=sum(r["stargazerCount"] for r in repos),
        total_forks=sum(r["forkCount"] for r in repos),
        followers=user["followers"]["totalCount"],
        contributions_last_year=calendar["totalContributions"],
        current_streak=current_streak,
        longest_streak=longest_streak,
        top_languages=languages[:top_n],
        total_language_bytes=total_bytes,
    )


def _bar(pct: float, width: int = 20) -> str:
    filled = round(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def render_stats_block(stats: ProfileStats, svg_dir: Path) -> str:
    lines: list[str] = [MARKER_START, ""]

    for label, filename in SVG_ASSETS.items():
        if (svg_dir / filename).exists():
            lines.append(f'<img src="{svg_dir.as_posix()}/{filename}" alt="{label}" />')
            lines.append("")

    lines += [
        "| Metric | Value |",
        "|---|---|",
        f"| Public repos | {stats.public_repos} |",
        f"| Total stars | {stats.total_stars} |",
        f"| Total forks | {stats.total_forks} |",
        f"| Followers | {stats.followers} |",
        f"| Contributions (past year) | {stats.contributions_last_year} |",
        f"| Current streak | {stats.current_streak} day(s) |",
        f"| Longest streak | {stats.longest_streak} day(s) |",
        "",
    ]

    if stats.top_languages and stats.total_language_bytes:
        lines.append("**Top languages**")
        lines.append("```text")
        for lang in stats.top_languages:
            pct = lang.bytes_ / stats.total_language_bytes * 100
            lines.append(f"{lang.name:<12} {_bar(pct)}  {pct:5.1f}%")
        lines.append("```")
        lines.append("")

    timestamp = stats.generated_at.strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"<sub>Last updated {timestamp}</sub>")
    lines.append("")
    lines.append(MARKER_END)
    return "\n".join(lines)


def update_readme(path: Path, block: str) -> bool:
    """Replace content between markers, or append them if absent.

    Returns True if the file's content changed.
    """
    pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL)

    if path.exists():
        original = path.read_text(encoding="utf-8")
    else:
        original = ""

    if pattern.search(original):
        updated = pattern.sub(block, original)
    elif original.strip():
        updated = original.rstrip("\n") + "\n\n" + block + "\n"
    else:
        updated = block + "\n"

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate the stats section of a GitHub profile README.")
    parser.add_argument("--username", default=os.environ.get("GITHUB_ACTOR"), help="GitHub username to fetch stats for")
    parser.add_argument("--token", default=os.environ.get("GH_README_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--output", default="README.md", type=Path)
    parser.add_argument("--svg-dir", default="svg", type=Path)
    parser.add_argument("--top-languages", default=6, type=int)
    parser.add_argument(
        "--exclude-language",
        action="append",
        default=[],
        help="Language name to exclude from the top-languages bar (repeatable)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the generated block instead of writing it")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    if not args.username:
        logger.error("No username given: pass --username or set GITHUB_ACTOR")
        return 1
    if not args.token:
        logger.error("No token given: pass --token or set GH_README_TOKEN (needs `read:user` scope)")
        return 1

    try:
        client = GitHubClient(args.token)
        data = client.fetch_profile_data(args.username)
        stats = build_stats(data, args.username, args.top_languages, set(args.exclude_language))
        block = render_stats_block(stats, args.svg_dir)
    except GitHubAPIError as exc:
        logger.error("Failed to build stats: %s", exc)
        return 1

    if args.dry_run:
        print(block)
        return 0

    changed = update_readme(args.output, block)
    logger.info("%s: %s", args.output, "updated" if changed else "no changes")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"changed={'true' if changed else 'false'}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())