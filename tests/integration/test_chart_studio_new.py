# -*- coding: utf-8 -*-
"""Assertion-based coverage for the Python-first Chart Studio services."""

from __future__ import annotations

import base64
import json

import pandas as pd

from services.chart_service import ChartLibrary, ChartService, ChartType
from services.code_generator import CodeGenerator


def _chart_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 6, 8, 10],
            "category": ["A", "B", "A", "B", "A"],
            "sales": [100, 120, 90, 140, 160],
        }
    )


def test_plotly_chart_returns_json_payload_with_expected_layout():
    service = ChartService()
    service.set_library(ChartLibrary.PLOTLY)

    result = service.create_chart(
        _chart_df(),
        ChartType.scatter,
        {
            "x": "x",
            "y": "y",
            "color": "category",
            "title": "测试散点图",
        },
    )
    payload = json.loads(result["chart"])

    assert result["library"] == "plotly"
    assert payload["data"]
    assert payload["data"][0]["type"] == "scatter"
    assert payload["layout"]["title"]["text"] == "测试散点图"


def test_plotly_pie_chart_remaps_generic_xy_params():
    service = ChartService()
    service.set_library(ChartLibrary.PLOTLY)

    pie_df = pd.DataFrame({"category": ["A", "B", "C"], "sales": [10, 20, 30]})
    result = service.create_chart(
        pie_df,
        ChartType.pie,
        {
            "x": "category",
            "y": "sales",
            "title": "类别占比",
        },
    )
    payload = json.loads(result["chart"])

    assert payload["data"][0]["type"] == "pie"
    assert set(payload["data"][0]["labels"]) == {"A", "B", "C"}
    assert payload["layout"]["title"]["text"] == "类别占比"


def test_seaborn_chart_returns_png_data_url():
    service = ChartService()
    service.set_library(ChartLibrary.SEABORN)

    result = service.create_chart(
        _chart_df(),
        ChartType.scatter,
        {
            "x": "x",
            "y": "y",
            "hue": "category",
            "title": "静态散点图",
        },
    )
    image_bytes = base64.b64decode(result["chart"].split(",", 1)[1])

    assert result["library"] == "seaborn"
    assert result["chart"].startswith("data:image/png;base64,")
    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_plotly_code_generation_keeps_style_settings_out_of_px_call():
    code = CodeGenerator.generate_plotly_code(
        "scatter",
        {
            "x": "sales",
            "y": "y",
            "color": "category",
            "template": "plotly_dark",
            "title": "销售关系图",
        },
    )
    plotly_call, _, layout_block = code.partition("fig.update_layout(")

    assert "fig = px.scatter(" in code
    assert "template='plotly_dark'" not in plotly_call
    assert "title='销售关系图'" not in plotly_call
    assert "template='plotly_dark'" in layout_block
    assert "title='销售关系图'" in layout_block


def test_seaborn_pairplot_code_generation_uses_pairplot_api():
    code = CodeGenerator.generate_seaborn_code(
        "pairplot",
        {
            "hue": "category",
            "title": "配对概览",
        },
    )

    assert "g = sns.pairplot(" in code
    assert "ax=ax" not in code
    assert "g.fig.suptitle('配对概览'" in code
