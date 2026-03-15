# -*- coding: utf-8 -*-
"""Tests for unified export service."""

from __future__ import annotations

import json

import pandas as pd

from core.data_manager import DataManager
from services.export_service import build_advanced_export, build_chart_export, build_workshop_export


def setup_function():
    DataManager.reset()


def test_chart_export_uses_chart_context():
    dm = DataManager()
    dm.add_dataset("sales", pd.DataFrame({"amount": [10, 20], "month": ["Jan", "Feb"]}), source="sample:stocks")

    bundle = build_chart_export(
        {
            "library": "plotly",
            "chart_type": "bar",
            "params": {"x": "month", "y": "amount", "title": "Monthly Sales"},
            "title": "Monthly Sales",
        }
    )

    assert "px.bar" in bundle.py_content
    assert "month" in bundle.py_content
    assert bundle.py_filename.endswith(".py")
    notebook = json.loads(bundle.ipynb_content)
    assert notebook["cells"][0]["cell_type"] == "markdown"


def test_workshop_export_uses_pipeline_steps():
    dm = DataManager()
    dm.add_dataset("customers", pd.DataFrame({"city": ["A", "B"], "value": [1, 2]}), source="file:/tmp/customers.csv")

    pipeline = [
        {"operation": "rename_column", "params": {"old_name": "city", "new_name": "city_name"}},
        {"operation": "fill_missing", "params": {"column": "value", "method": "value", "value": 0}},
    ]

    bundle = build_workshop_export(pipeline)

    assert "rename" in bundle.py_content.lower()
    assert "city_name" in bundle.py_content
    assert bundle.ipynb_filename.endswith(".ipynb")


def test_advanced_export_aggregates_workshop_and_chart():
    dm = DataManager()
    dm.add_dataset("orders", pd.DataFrame({"x": [1, 2], "y": [3, 4]}), source="sample:iris")

    project_state = {
        "data_workshop": {
            "pipeline": [
                {"operation": "drop_duplicates", "params": {"keep": "first"}},
            ]
        },
        "chart_studio": {
            "chart_data": {
                "library": "plotly",
                "chart_type": "scatter",
                "params": {"x": "x", "y": "y", "title": "Orders"},
                "title": "Orders",
            }
        },
    }

    bundle = build_advanced_export(project_state)

    assert "load_sample_dataset" in bundle.py_content
    assert "drop_duplicates" in bundle.py_content
    assert "px.scatter" in bundle.py_content
