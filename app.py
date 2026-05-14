"""
Точка входа для Flask CLI: `flask --app app run`
(фабрика и приложение в пакете sportorg).
"""

from sportorg.app import app, create_app

__all__ = ["app", "create_app"]
