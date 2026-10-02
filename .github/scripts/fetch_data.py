#!/usr/bin/env python3
"""
Copy projects.json to merged.json for the generator (run inside the Action).

Language splits are NOT fetched here: most of the code lives in private repos
the Action's GITHUB_TOKEN cannot read. They are real byte counts written into
projects.json by .github/scripts/refresh_languages.py, run locally by the
owner. This step only validates that no card carries hand-typed numbers.
"""
import json
import sys


def main():
    with open("projects.json") as f:
        projects = json.load(f)
    for p in projects:
        if p.get("languages") and not p.get("lang_repos"):
            sys.exit(f"{p['name']}: 'languages' without 'lang_repos' — numbers must come from refresh_languages.py")
    with open("merged.json", "w") as f:
        json.dump(projects, f)
    print(f"merged {len(projects)} projects")


if __name__ == "__main__":
    main()
