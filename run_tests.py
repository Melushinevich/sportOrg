#!/usr/bin/env python3
"""Запуск pytest из корня репозитория (не зависит от текущей папки в shell)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.setdefault("PYTEST_QT_API", "pyqt5")
    cmd = [sys.executable, "-m", "pytest", *sys.argv[1:]]
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
