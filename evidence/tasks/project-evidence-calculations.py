"""Reproduce the November 2026 contribution snapshot using only Git and Python.

This calculates publication-window scenarios, not measured human working hours.
Run from any directory; no packages, network access or Git writes are required.
"""

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = "f63bffe490358a4fba06d27b896d42c5e81bf882"
LOCAL_TIME = timezone(timedelta(hours=1))  # Europe/Budapest on 11-12 Nov 2026.


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def snapshot(revision):
    revision = git("rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    lines = git(
        "log", "--reverse", "--topo-order", "--format=%H|%aN|%aI|%cI|%s", revision
    ).decode("utf-8").splitlines()
    commits = []
    for line in lines:
        commit, author, authored, committed, subject = line.split("|", 4)
        commits.append({
            "commit": commit,
            "author": author,
            "authored_at": authored,
            "committed_at": committed,
            "subject": subject,
        })
    # Sort by publication/committer time for the timing calculation. Keep authorship
    # as Git records it; a commit identity does not establish exclusive human labor.
    commits.sort(key=lambda c: c["committed_at"])
    people = defaultdict(lambda: {
        "commits": 0, "within_day_gap_seconds": 0, "first_publications_of_day": 0
    })
    windows = []
    previous = None
    for commit in commits:
        moment = datetime.fromisoformat(commit["committed_at"]).astimezone(LOCAL_TIME)
        person = people[commit["author"]]
        person["commits"] += 1
        if previous is not None and moment.date() == previous[0].date():
            seconds = int((moment - previous[0]).total_seconds())
            person["within_day_gap_seconds"] += seconds
            windows.append({
                "from_commit": previous[1], "to_commit": commit["commit"],
                "attributed_author": commit["author"], "seconds": seconds,
            })
        else:
            person["first_publications_of_day"] += 1
        previous = moment, commit["commit"]
    for person in people.values():
        gap = person["within_day_gap_seconds"] / 3600
        starts = person["first_publications_of_day"]
        person["scenarios_hours"] = {
            "low_assumption": round(gap * 0.5 + starts * 0.5, 6),
            "central_assumption": round(gap * 0.75 + starts * 0.75, 6),
            "high_assumption": round(gap + starts, 6),
        }
    first = datetime.fromisoformat(commits[0]["committed_at"])
    last = datetime.fromisoformat(commits[-1]["committed_at"])
    paths = git("ls-tree", "-r", "--name-only", revision).decode("utf-8").splitlines()
    sources = []
    for path in paths:
        if path.startswith(("evidence/", "prompts/", "specs/", "docs/decisions/")) or path in {
            "AGENTS.md", "next_work.md", "original_idea.md", ".specify/memory/constitution.md"
        }:
            content = git("show", f"{revision}:{path}")
            sources.append({"path": path, "sha256": hashlib.sha256(content).hexdigest()})
    all_commits = set(git("rev-list", "--all").decode().splitlines())
    pinned_commits = {commit["commit"] for commit in commits}
    return {
        "baseline": revision,
        "date": "2026-11-12",
        "timezone": "Europe/Budapest, UTC+01:00 on the covered dates",
        "scope": "Locally available Git history through baseline; no remote fetch",
        "available_ref_commits_outside_baseline": sorted(all_commits - pinned_commits),
        "commit_count": len(commits),
        "git_author_count": len(people),
        "first_commit_at": commits[0]["committed_at"],
        "last_commit_at": commits[-1]["committed_at"],
        "elapsed_seconds": int((last - first).total_seconds()),
        "within_day_gap_seconds": sum(p["within_day_gap_seconds"] for p in people.values()),
        "method": {
            "attribution": "Each same-day gap is assigned once to the next commit's author",
            "low_assumption": "50% of gaps plus 30 min before first daily publication",
            "central_assumption": "75% of gaps plus 45 min before first daily publication",
            "high_assumption": "100% of gaps plus 60 min before first daily publication",
            "limits": (
                "Assumed activity shares; not measured labor or confidence bounds; "
                "excludes overnight gaps, unnamed work and this report"
            ),
        },
        "people": dict(people),
        "total_scenarios_hours": {
            key: round(sum(
                (p["within_day_gap_seconds"] / 3600 + p["first_publications_of_day"]) * factor
                for p in people.values()
            ), 6)
            for key, factor in (
                ("low_assumption", 0.5),
                ("central_assumption", 0.75),
                ("high_assumption", 1),
            )
        },
        "commits": commits,
        "publication_windows": windows,
        "source_inventory": sources,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default=BASELINE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(snapshot(args.revision), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
