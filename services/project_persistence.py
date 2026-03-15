# -*- coding: utf-8 -*-
"""Project archive save/load helpers."""

from __future__ import annotations

import copy
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any

import config
from core.data_manager import DataManager
from core.state_manager import get_initial_state


SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_app_state(app_state: dict[str, Any] | None) -> dict[str, Any]:
    state = dict(app_state or {})
    state.pop("toast", None)
    return state


def build_project_snapshot(
    *,
    project_name: str,
    app_state: dict[str, Any] | None,
    page_state: dict[str, Any] | None,
    pathname: str | None,
    storage_mode: str = "embedded",
) -> dict[str, Any]:
    dm = DataManager()
    clean_state = _clean_app_state(app_state)
    return {
        "schema_version": SCHEMA_VERSION,
        "project_meta": {
            "name": project_name,
            "saved_at": _utc_now(),
            "app_version": config.APP_VERSION,
        },
        "route": pathname or "/home",
        "storage_mode": storage_mode,
        "app_state": clean_state,
        "datasets": dm.export_datasets(storage_mode=storage_mode),
        "page_state": copy.deepcopy(page_state or {}),
    }


def build_project_archive(
    *,
    project_name: str,
    app_state: dict[str, Any] | None,
    page_state: dict[str, Any] | None,
    pathname: str | None,
    storage_mode: str = "embedded",
) -> bytes:
    snapshot = build_project_snapshot(
        project_name=project_name,
        app_state=app_state,
        page_state=page_state,
        pathname=pathname,
        storage_mode=storage_mode,
    )
    archive_snapshot = copy.deepcopy(snapshot)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for index, dataset in enumerate(archive_snapshot.get("datasets", [])):
            if dataset.get("storage_mode") != "embedded":
                continue
            data_json = dataset.pop("data_json", None)
            if not data_json:
                continue
            dataset_name = dataset.get("name") or f"dataset-{index + 1}"
            safe_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in dataset_name)
            data_ref = f"datasets/{index:03d}-{safe_name}.json"
            zf.writestr(data_ref, data_json)
            dataset["data_ref"] = data_ref
        zf.writestr("project.json", json.dumps(archive_snapshot, ensure_ascii=False, indent=2))
    return buffer.getvalue()


def load_project_archive(archive_bytes: bytes) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as zf:
        snapshot = json.loads(zf.read("project.json").decode("utf-8"))
        if snapshot.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"Unsupported project schema version: {snapshot.get('schema_version')}")
        for dataset in snapshot.get("datasets", []):
            if dataset.get("storage_mode") != "embedded":
                continue
            data_ref = dataset.get("data_ref")
            if not data_ref:
                continue
            dataset["data_json"] = zf.read(data_ref).decode("utf-8")
    return snapshot


def restore_project_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    dm = DataManager()
    dm.restore_datasets(snapshot.get("datasets", []))

    app_state = get_initial_state()
    app_state.update(snapshot.get("app_state", {}))
    app_state["active_dataset"] = dm.active_name
    app_state["datasets"] = dm.dataset_names
    app_state["project_name"] = snapshot.get("project_meta", {}).get("name")
    app_state["project_storage_mode"] = snapshot.get("storage_mode", "embedded")

    return {
        "app_state": app_state,
        "page_state": snapshot.get("page_state", {}),
        "route": snapshot.get("route") or "/home",
        "project_meta": snapshot.get("project_meta", {}),
    }
