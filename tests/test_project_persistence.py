# -*- coding: utf-8 -*-
"""Focused tests for project persistence."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

from core.data_manager import DataManager
from services.project_persistence import PROJECT_EXTENSION, build_project_archive, load_project_archive, restore_project_snapshot


def test_project_archive_round_trip_embedded():
    dm = DataManager()
    dm.clear()
    dm.add_dataset("iris", pd.DataFrame({"sepal": [1, 2], "petal": [3, 4]}), source="sample:iris")

    archive = build_project_archive(
        project_name="persist-check",
        app_state={"theme": "light", "active_dataset": "iris"},
        page_state={"chart_studio": {"active_tab": "tab-gallery"}},
        pathname="/charts",
        storage_mode="embedded",
    )

    snapshot = load_project_archive(archive)
    restored = restore_project_snapshot(snapshot)

    assert snapshot["project_meta"]["name"] == "persist-check"
    assert snapshot["route"] == "/charts"
    assert restored["app_state"]["active_dataset"] == "iris"
    assert restored["route"] == "/charts"
    assert restored["page_state"]["chart_studio"]["active_tab"] == "tab-gallery"
    assert DataManager().active_name == "iris"


def test_project_archive_round_trip_reference_mode():
    dm = DataManager()
    dm.clear()
    dm.add_dataset("sales", pd.DataFrame({"amount": [10, 20]}), source="file:sales.csv")

    archive = build_project_archive(
        project_name="reference-check",
        app_state={"theme": "dark"},
        page_state={},
        pathname="/data",
        storage_mode="reference",
    )

    snapshot = load_project_archive(archive)

    assert snapshot["storage_mode"] == "reference"
    assert snapshot["datasets"][0]["source"] == "file:sales.csv"
    # Non-restorable local uploads fall back to embedded storage to avoid data loss.
    assert snapshot["datasets"][0]["storage_mode"] == "embedded"
    assert "data_json" in snapshot["datasets"][0]


def test_project_archive_round_trip_reference_file_restore():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = Path(tmp_dir) / "sales.csv"
        csv_path.write_text("amount,region\n10,east\n20,west\n", encoding="utf-8")

        dm = DataManager()
        dm.clear()
        dm.add_dataset("sales", pd.read_csv(csv_path), source=f"file:{csv_path}")

        archive = build_project_archive(
            project_name="reference-file-check",
            app_state={"theme": "light"},
            page_state={"data_workshop": {"pipeline": []}},
            pathname="/workshop",
            storage_mode="reference",
        )

        snapshot = load_project_archive(archive)
        restored = restore_project_snapshot(snapshot)

        assert PROJECT_EXTENSION == ".dvs"
        assert snapshot["datasets"][0]["storage_mode"] == "reference"
        assert "data_json" not in snapshot["datasets"][0]
        assert restored["app_state"]["active_dataset"] == "sales"
        assert DataManager().get_dataset("sales") is not None
        assert list(DataManager().get_dataset("sales").columns) == ["amount", "region"]
