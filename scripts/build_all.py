#!/usr/bin/env python3
"""Regenerate every SVG in assets/ (hero, contact buttons, about, credentials).
Standard library only — run from anywhere:

    python3 scripts/build_all.py

The projects panel is built by CI (.github/workflows/projects.yml) into the
`projects` branch; its language data comes from .github/scripts/refresh_languages.py.
"""
import os
import runpy
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero")
sys.path.insert(0, HERE)
for name in ("build_hero", "build_contact", "build_about", "build_credentials"):
    runpy.run_path(os.path.join(HERE, f"{name}.py"), run_name="__main__")
