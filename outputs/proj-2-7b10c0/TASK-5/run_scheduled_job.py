#!/usr/bin/env python3
"""Thin wrapper for one-shot execution from cron or Task Scheduler."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    command = [
        sys.executable,
        str(base_dir / "scheduler_service.py"),
        "--config",
        str(base_dir / "config" / "scheduler.yaml"),
        "--run-once",
    ]
    completed = subprocess.run(command, cwd=base_dir)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
