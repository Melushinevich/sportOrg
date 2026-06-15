from pathlib import Path

import pytest

from frontend.team_pdf_export import default_pdf_filename, export_final_team_pdf


def test_default_pdf_filename():
    name = default_pdf_filename('Команда "А"')
    assert name.startswith("Итог_")
    assert name.endswith(".pdf")
    assert "/" not in name
    assert "Команда _А_" in name


def test_default_pdf_filename_empty_team():
    name = default_pdf_filename("   ")
    assert name.startswith("Итог_команда_")


def test_export_final_team_pdf(tmp_path: Path):
    out = tmp_path / "report.pdf"
    export_final_team_pdf(
        out,
        team_name="DREAM TEAM",
        rows=[
            {"name": "Иванов Иван", "percent": "8.5", "notes": "Капитан"},
            {"name": "Петров Пётр", "percent": "7.0", "notes": ""},
        ],
    )
    assert out.is_file()
    assert out.read_bytes()[:4] == b"%PDF"
