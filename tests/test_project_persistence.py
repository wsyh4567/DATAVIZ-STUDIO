# -*- coding: utf-8 -*-
"""Focused tests for project persistence."""

from __future__ import annotations

import pandas as pd

from core.data_manager import DataManager
from services.project_persistence import build_project_archive, load_project_archive, restore_project_snapshot


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
    assert "data_json" not in snapshot["datasets"][0]
