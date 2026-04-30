#!/usr/bin/env python3
"""Run TASK-6 unit and integration tests with unittest discovery."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    tests_dir = base_dir / "tests"
    tests_dir_str = str(tests_dir)
    if tests_dir_str not in sys.path:
        sys.path.insert(0, tests_dir_str)
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(tests_dir),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
