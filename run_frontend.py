"""Запуск десктоп-приложения: python run_frontend.py"""

import frontend.dpi_fix  # noqa: F401 — переменные Qt до PyQt5

from frontend.main_app import main

if __name__ == "__main__":
    main()
