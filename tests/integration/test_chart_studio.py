# -*- coding: utf-8 -*-
"""Assertion-based Chart Studio integration coverage for current APIs."""

from __future__ import annotations

import json

import pandas as pd

from services.chart_recommender import ChartRecommender
from services.chart_service import ChartLibrary, ChartService, ChartType


def _sales_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": ["北京", "上海", "广州", "深圳"],
            "sales": [120, 180, 160, 140],
            "profit": [18, 30, 22, 20],
            "date": pd.date_range("2024-01-01", periods=4, freq="D"),
        }
    )


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
