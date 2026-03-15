# -*- coding: utf-8 -*-
"""Basic smoke tests for app composition and imports."""

from __future__ import annotations

import pandas as pd
import pytest


def _require_runtime_stack():
    pytest.importorskip('dash')
    pytest.importorskip('dash_ag_grid')
    pytest.importorskip('dash_bootstrap_components')
    pytest.importorskip('plotly')
    pytest.importorskip('matplotlib')
    pytest.importorskip('openpyxl')
    pytest.importorskip('chardet')


def test_runtime_dependencies_import():
    _require_runtime_stack()
    import numpy  # noqa: F401
    import pandas  # noqa: F401


def test_app_modules_import_and_layout():
    _require_runtime_stack()
    from app import app, server

    assert app is not None
    assert server is not None
    assert app.layout is not None


def test_data_manager_basic_lifecycle():
    from core.data_manager import DataManager

    dm = DataManager()
    dm.clear()

    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    name = dm.add_dataset("test", df)
    meta = dm.get_meta()

    assert name == "test"
    assert dm.active_name == "test"
    assert meta is not None
    assert meta.rows == 3
    assert meta.cols == 2
    assert len(dm.list_datasets()) == 1

    dm.clear()


def test_sample_datasets_load():
    from services.data_loader import SAMPLE_DATASETS, load_sample_dataset

    for name in SAMPLE_DATASETS:
        df = load_sample_dataset(name)
        assert df is not None
        assert not df.empty


def test_core_components_render():
    _require_runtime_stack()
    from components.data_table import create_data_table
    from components.navbar import create_navbar
    from components.sidebar import create_sidebar
    from components.statusbar import create_statusbar

    assert create_navbar() is not None
    assert create_sidebar() is not None
    assert create_statusbar() is not None
    assert create_data_table(None) is not None
    assert create_data_table(pd.DataFrame({"A": [1], "B": [2]})) is not None


def test_core_pages_render():
    _require_runtime_stack()
    from pages.data_canvas import create_data_canvas_page
    from pages.data_hub import create_data_hub_page
    from pages.home import create_home_page

    assert create_home_page() is not None
    assert create_data_hub_page() is not None
    assert create_data_canvas_page() is not None
