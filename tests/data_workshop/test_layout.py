from __future__ import annotations

from collections import Counter

import pytest
from dash.development.base_component import Component

pytest.importorskip("dash")
pytest.importorskip("dash_bootstrap_components")

from pages.data_workshop import layout


def _collect_ids(node, ids=None):
    if ids is None:
        ids = []
    if isinstance(node, Component):
        component_id = getattr(node, "id", None)
        if component_id is not None:
            ids.append(component_id)
        children = getattr(node, "children", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                _collect_ids(child, ids)
        elif children is not None:
            _collect_ids(children, ids)
    return ids


def test_data_workshop_layout_has_no_duplicate_component_ids():
    ids = [str(component_id) for component_id in _collect_ids(layout())]
    duplicates = {component_id for component_id, count in Counter(ids).items() if count > 1}

    assert duplicates == set()
