import pytest
from dash.development.base_component import Component

pytest.importorskip("dash_bootstrap_components")

from pages.data_canvas import create_data_canvas_page
from services.eda_service import EDAService


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



def test_data_canvas_contains_new_eda_state_components():
    layout = create_data_canvas_page()
    ids = _collect_ids(layout)

    assert "eda-analysis-mode" in ids
    assert "eda-sample-size" in ids
    assert "eda-user-sampling-choice" in ids
    assert "eda-last-analysis-meta" in ids
    assert "eda-sampling-modal" in ids



def test_sampling_threshold_and_recommendation():
    assert EDAService.should_recommend_sampling(60000, 10) is True
    assert EDAService.should_recommend_sampling(1000, 60) is True
    assert EDAService.should_recommend_sampling(1000, 10) is False
    assert EDAService.recommended_sample_size(80000) == 10000
