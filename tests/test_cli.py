"""Tests for the command line interface helper commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from expense_manager.cli import main


def _write_data(file_path: Path) -> None:
    data = {
        "wallets": [
            {
                "name": "Personal",
                "currency": "USD",
                "balance": 1000.0,
                "expenses": [
                    {
                        "description": "Groceries",
                        "amount": 100.0,
                        "category": "food",
                    }
                ],
            }
        ]
    }
    file_path.write_text(json.dumps(data), encoding="utf-8")


def test_preview_command_outputs_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_file = tmp_path / "data.json"
    _write_data(data_file)

    main(["--data-file", str(data_file), "preview"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    preview = payload["preview"]

    assert preview["target_currency"] == "USD"
    assert preview["total_balance"] == pytest.approx(1000.0)
    assert preview["total_spent"] == pytest.approx(100.0)
    assert preview["net_position"] == pytest.approx(900.0)
    assert preview["using_demo_data"] is False


def test_preview_demo_uses_sample_data(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_file = tmp_path / "data.json"

    main(["--data-file", str(data_file), "preview", "--demo"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    preview = payload["preview"]

    assert preview["target_currency"] == "USD"
    assert preview["total_balance"] == pytest.approx(2457.7639751552797)
    assert preview["total_spent"] == pytest.approx(1067.391304347826)
    assert preview["net_position"] == pytest.approx(1390.3726708074537)
    assert preview["using_demo_data"] is True
    assert not data_file.exists()
