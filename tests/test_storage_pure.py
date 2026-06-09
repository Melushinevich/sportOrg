"""Тесты чистых функций storage_postgres (без БД)."""

import os

import pytest

from user_registration import storage_postgres as sp


def test_format_full_name():
    assert sp._format_full_name("Иванов", "Иван", "Иванович") == "Иванов Иван Иванович"
    assert sp._format_full_name(None, None, None) is None


def test_compute_member_score():
    assert sp._compute_member_score([{"rating": 8}, {"rating": 10}]) == 9.0
    assert sp._compute_member_score([{"rating": None}]) is None
    assert sp._compute_member_score([]) is None


def test_normalize_criteria():
    assert sp._normalize_criteria(["Скорость", "Сила"]) == ["Скорость", "Сила"]
    assert sp._normalize_criteria([]) == []
    with pytest.raises(ValueError):
        sp._normalize_criteria([""])
    with pytest.raises(ValueError):
        sp._normalize_criteria("not-list")  # type: ignore[arg-type]


def test_validate_quality_rating():
    assert sp._validate_quality_rating(None) is None
    assert sp._validate_quality_rating(7) == 7
    with pytest.raises(ValueError):
        sp._validate_quality_rating(11)
    with pytest.raises(ValueError):
        sp._validate_quality_rating("x")


def test_database_url_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host:5432/db")
    assert sp._database_url() == "postgresql://u:p@host:5432/db"


def test_database_url_from_parts(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SPORTORG_DB_HOST", "192.168.1.80")
    monkeypatch.setenv("SPORTORG_DB_PORT", "5500")
    monkeypatch.setenv("SPORTORG_DB_USER", "postgres")
    monkeypatch.setenv("SPORTORG_DB_PASSWORD", "12345678")
    monkeypatch.setenv("SPORTORG_DB_NAME", "postgres")
    url = sp._database_url()
    assert "192.168.1.80" in url
    assert "postgres" in url


def test_database_url_requires_host(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTORG_DB_HOST", raising=False)
    with pytest.raises(RuntimeError):
        sp._database_url()
