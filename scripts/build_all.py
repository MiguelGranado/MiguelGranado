#!/usr/bin/env python3
"""Regenerate every SVG in assets/ (hero, contact, about, expertise, services, credentials).
Standard library only — run from anywhere:

    python3 scripts/build_all.py

Built by CI instead: the projects panel (projects.yml -> `projects` branch, language data
from .github/scripts/refresh_languages.py) and the activity panel (activity.yml ->
`output` branch, live GitHub data).
"""
from __future__ import annotations

import os
import runpy
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero")
sys.path.insert(0, HERE)
for name in ("build_hero", "build_contact", "build_about", "build_expertise", "build_services",
             "build_credentials"):
    runpy.run_path(os.path.join(HERE, f"{name}.py"), run_name="__main__")
