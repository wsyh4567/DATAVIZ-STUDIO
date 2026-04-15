# -*- coding: utf-8 -*-
"""Assertion-based Chart Studio integration coverage for current APIs."""

from __future__ import annotations

import base64
import json
from unittest.mock import patch

import pandas as pd
import pytest

from core.data_manager import DataManager
from dash.development.base_component import Component
from pages.chart_studio import build_chart_download_payload, validate_params
from services.chart_recommender import ChartRecommender
from services.chart_service import ChartLibrary, ChartService, ChartType

pytest.importorskip("dash")
pytest.importorskip("dash_bootstrap_components")


def _sales_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["北京", "上海", "广州", "深圳"],
            "sales": [120, 180, 160, 140],
            "profit": [18, 30, 22, 20],
            "date": pd.date_range("2024-01-01", periods=4, freq="D"),
            "channel": ["直营网点", "电商", "经销商", "电商"],
        }
    )


def _collect_text(node, chunks=None):
    if chunks is None:
        chunks = []
    if isinstance(node, str):
        chunks.append(node)
        return chunks
    if isinstance(node, Component):
        children = getattr(node, "children", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                _collect_text(child, chunks)
        elif children is not None:
            _collect_text(children, chunks)
    return chunks


def test_recommender_prefers_bar_for_dimension_measure_pair():
    recommendations = ChartRecommender.recommend(_sales_df(), x="city", y="sales")

    assert recommendations
    assert recommendations[0].chart_type == "bar"
    assert recommendations[0].score >= recommendations[-1].score


def test_recommender_prefers_line_for_temporal_measure_pair():
    recommendations = ChartRecommender.recommend(_sales_df(), x="date", y="sales")

    assert recommendations
    assert recommendations[0].chart_type == "line"
    assert recommendations[0].score >= 90


def test_recommender_scores_do_not_leak_between_calls():
    baseline = ChartRecommender.recommend(_sales_df(), x="city", y="sales")
    boosted = ChartRecommender.recommend(_sales_df(), x="city", y="sales", color="channel")
    repeated = ChartRecommender.recommend(_sales_df(), x="city", y="sales")

    assert baseline[0].score == 95
    assert boosted[0].score == 100
    assert [rec.score for rec in repeated] == [rec.score for rec in baseline]


def test_validate_params_surfaces_recommendation_reason_and_scene():
    dm = DataManager()
    dm.clear()
    dm.add_dataset("sales", _sales_df())

    _, _, _, content = validate_params("city", "sales", None)
    text = " ".join(_collect_text(content))

    assert "点击卡片可直接切换图表类型" in text
    assert "对比不同类别的数值大小，直观清晰" in text
    assert "适用场景" in text
    assert "类别对比、排名分析" in text


def test_plotly_horizontal_bar_chart_sets_horizontal_orientation():
    service = ChartService()
    service.set_library(ChartLibrary.PLOTLY)

    result = service.create_chart(
        _sales_df(),
        ChartType.hbar,
        {
            "x": "sales",
            "y": "city",
            "title": "城市销售额",
        },
    )
    payload = json.loads(result["chart"])

    assert result["library"] == "plotly"
    assert payload["data"][0]["type"] == "bar"
    assert payload["data"][0]["orientation"] == "h"
    assert payload["layout"]["title"]["text"] == "城市销售额"


def test_build_chart_download_payload_supports_seaborn_png_export():
    payload, feedback = build_chart_download_payload(
        "export-png-btn",
        "data:image/png;base64," + base64.b64encode(b"fake-png").decode(),
        "seaborn",
    )

    assert feedback is None
    assert payload["filename"] == "chart.png"
    assert payload["base64"] is True
    assert base64.b64decode(payload["content"]) == b"fake-png"


def test_build_chart_download_payload_warns_when_seaborn_svg_requested():
    payload, feedback = build_chart_download_payload(
        "export-svg-btn",
        "data:image/png;base64," + base64.b64encode(b"fake-png").decode(),
        "seaborn",
    )

    assert payload is None
    assert feedback[0] is True
    assert feedback[1] == "导出受限"
    assert "暂不支持 SVG 导出" in feedback[2]


def test_build_chart_download_payload_warns_when_plotly_image_export_needs_kaleido():
    plotly_json = json.dumps(
        {
            "data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}],
            "layout": {"title": {"text": "Test"}},
        }
    )

    with patch("plotly.io.to_image", side_effect=ValueError("Image export using the 'kaleido' engine requires the Kaleido package")):
        payload, feedback = build_chart_download_payload("export-png-btn", plotly_json, "plotly")

    assert payload is None
    assert feedback[1] == "缺少导出依赖"
    assert "Kaleido" in feedback[2]
