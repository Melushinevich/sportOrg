#!/usr/bin/env python3
"""Запуск Flask API и десктоп-приложения одной командой.

  python run_dev.py

Читает .env (SPORTORG_API_URL). На Mac, если порт 5000 занят AirPlay,
укажите в .env порт 5001 и SPORTORG_API_URL=http://127.0.0.1:5001.
"""

from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def _python_executable() -> str:
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    return sys.executable


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        env_path = ROOT / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=True)
    except ImportError:
        pass


def _api_base_url() -> str:
    return (os.environ.get("SPORTORG_API_URL") or "http://127.0.0.1:5000").rstrip("/")


def _api_port(base_url: str) -> int:
    parsed = urlparse(base_url)
    if parsed.port is not None:
        return parsed.port
    return 5000


def _wait_for_api(base_url: str, timeout_sec: float = 30.0) -> bool:
    health_url = f"{base_url}/api/v1/health"
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            with urlopen(health_url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (URLError, TimeoutError, OSError):
            time.sleep(0.3)
    return False


def main() -> int:
    os.chdir(ROOT)
    _load_env()

    base_url = _api_base_url()
    port = _api_port(base_url)
    env = os.environ.copy()

    print(f"Запуск Flask API на {base_url} ...")
    python = _python_executable()
    flask_proc = subprocess.Popen(
        [
            python,
            "-m",
            "flask",
            "--app",
            "app",
            "run",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env=env,
    )

    def stop_flask() -> None:
        if flask_proc.poll() is not None:
            return
        flask_proc.terminate()
        try:
            flask_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_proc.kill()
            flask_proc.wait()

    atexit.register(stop_flask)

    def on_signal(signum, _frame):
        del signum
        stop_flask()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    if flask_proc.poll() is not None:
        print("Flask завершился с ошибкой. Проверьте порт и зависимости.", file=sys.stderr)
        return flask_proc.returncode or 1

    if not _wait_for_api(base_url):
        print(
            f"API не ответил за 30 с ({base_url}/api/v1/health). "
            "Если порт 5000 занят на Mac, задайте в .env порт 5001.",
            file=sys.stderr,
        )
        stop_flask()
        return 1

    print("Запуск десктоп-приложения ...")
    frontend_proc = subprocess.Popen(
        [python, "run_frontend.py"],
        cwd=ROOT,
        env=env,
    )

    try:
        return frontend_proc.wait()
    finally:
        stop_flask()


if __name__ == "__main__":
    raise SystemExit(main())
