"""
Точка входа для Flask CLI: `flask --app app run`
(фабрика и приложение в пакете sportorg).
"""

from sportorg.app import create_app

__all__ = ["app", "create_app"]


def __getattr__(name: str):
    if name == "app":
        return create_app()
    raise AttributeError(name)
