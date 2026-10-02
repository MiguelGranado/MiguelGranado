#!/usr/bin/env python3
"""
Refresh the real language split of every project card. Run LOCALLY by the
owner (needs the gh CLI authenticated as MiguelGranado):

    python3 .github/scripts/refresh_languages.py

Most production code lives in private repos, which the Action's GITHUB_TOKEN
cannot read — so the byte counts are fetched here and stored in projects.json
under "languages" (raw bytes from GET /repos/{repo}/languages, summed across
"lang_repos"). Cards without "lang_repos" never get a language bar: no language
numbers are ever typed by hand.
"""
from __future__ import annotations

import json
import subprocess
import sys

PATH = "projects.json"


def languages(repo: str) -> dict:
    out = subprocess.run(["gh", "api", f"repos/{repo}/languages"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> None:
    with open(PATH) as f:
        projects = json.load(f)
    for p in projects:
        repos = p.get("lang_repos") or []
        if not repos:
            p.pop("languages", None)
            continue
        total: dict[str, int] = {}
        for repo in repos:
            for lang, n in languages(repo).items():
                total[lang] = total.get(lang, 0) + n
        if not total:
            sys.exit(f"{p['name']}: {repos} returned no languages — refusing to write an empty language bar")
        p["languages"] = dict(sorted(total.items(), key=lambda kv: -kv[1]))
        top = next(iter(p["languages"]))
        print(f"{p['name']}: {top} {100 * p['languages'][top] / sum(total.values()):.1f}% ({', '.join(repos)})")
    with open(PATH, "w") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
