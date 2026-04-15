from __future__ import annotations

import pandas as pd
import pytest
from dash.development.base_component import Component

pytest.importorskip("dash")
pytest.importorskip("dash_bootstrap_components")

from core.data_manager import DataManager
from pages.ml_studio.layout import create_ml_studio_page


def _collect_ids(node, ids=None):
    if ids is None:
        ids = set()
    if isinstance(node, Component) and getattr(node, "id", None):
        ids.add(node.id)
    if isinstance(node, Component):
        children = getattr(node, "children", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                _collect_ids(child, ids)
        elif children is not None:
            _collect_ids(children, ids)
    return ids


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


def test_ml_studio_page_exposes_chinese_guidance_on_main_surface():
    dm = DataManager()
    dm.clear()
    dm.add_dataset(
        "housing",
        pd.DataFrame(
            {
                "面积": [72, 88, 96, 110],
                "房龄": [5, 8, 3, 12],
                "城区": ["东城", "西城", "海淀", "朝阳"],
                "总价": [520, 610, 720, 680],
            }
        ),
    )

    layout = create_ml_studio_page()
    ids = _collect_ids(layout)
    text = " ".join(_collect_text(layout))

    assert "ml-workflow-hint" in ids
    assert "ml-algo-guidance" in ids
    assert "ml-target-var" in ids
    assert "ml-feature-vars" in ids
    assert "btn-ml-train" in ids
    assert "三步完成一次训练" in text
    assert "先定目标" in text
    assert "随机森林是分类任务的稳妥起点" in text
    assert "系统会自动判断这是分类还是回归任务" in text
