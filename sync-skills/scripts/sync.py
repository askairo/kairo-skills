#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backward-compat entrypoint for sync-skills -> skills-loop."""

from pathlib import Path
import runpy
import sys


def main():
    target = Path(__file__).resolve().parents[2] / "skills-loop" / "scripts" / "sync.py"
    if not target.exists():
        raise SystemExit(f"skills-loop entrypoint not found: {target}")

    # Keep argv behavior consistent with direct invocation.
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
