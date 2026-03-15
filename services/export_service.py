# -*- coding: utf-8 -*-
"""Unified export helpers for Python scripts and notebooks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.data_manager import DataManager
from services.code_generator import CodeGenerator as ChartCodeGenerator
from services.data_workshop.code_generator import CodeGenerator as WorkshopCodeGenerator


@dataclass
class ExportBundle:
    py_content: str
    ipynb_content: str
    py_filename: str
    ipynb_filename: str


def _timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_stem(name: str, fallback: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in (name or fallback))
    return cleaned.strip("_") or fallback


def _split_code_lines(code: str) -> list[str]:
    return [f"{line}\n" for line in code.rstrip().splitlines()]


def _build_notebook(title: str, summary: list[str], code_sections: list[tuple[str, str]]) -> str:
    cells: list[dict[str, Any]] = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"# {title}\n", "\n", *[f"{line}\n" for line in summary if line]],
        }
    ]
    for section_title, section_code in code_sections:
        if section_title:
            cells.append(
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [f"## {section_title}\n"],
                }
            )
        cells.append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": _split_code_lines(section_code),
            }
        )
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, ensure_ascii=False, indent=2)


def _reader_from_source(source: str) -> tuple[list[str], str]:
    if source.startswith("sample:"):
        sample_name = source.split(":", 1)[1]
        return (
            ["import pandas as pd", "from services.data_loader import load_sample_dataset"],
            f"# Restore the same built-in sample used in DataViz Studio\ndf = load_sample_dataset({sample_name!r})",
        )
    if source.startswith("file:"):
        path_value = source.split(":", 1)[1]
        suffix = Path(path_value).suffix.lower()
        imports = ["import pandas as pd"]
        reader = "pd.read_csv"
        if suffix in {".xlsx", ".xls"}:
            reader = "pd.read_excel"
        elif suffix == ".json":
            reader = "pd.read_json"
        elif suffix == ".parquet":
            reader = "pd.read_parquet"
        elif suffix == ".feather":
            reader = "pd.read_feather"
        return imports, f"df = {reader}({path_value!r})"
    if source.startswith("url:"):
        url = source.split(":", 1)[1]
        suffix = Path(url.split("?", 1)[0]).suffix.lower()
        imports = ["import pandas as pd"]
        reader = "pd.read_csv"
        if suffix == ".json":
            reader = "pd.read_json"
        return imports, f"df = {reader}({url!r})"
    placeholder = [
        "import pandas as pd",
        "# TODO: replace this with the original dataset loading logic.",
        f"# Original source in DataViz Studio: {source or 'unknown'}",
        "df = pd.read_csv('your_dataset.csv')",
    ]
    return ["import pandas as pd"], "\n".join(placeholder[1:])


def _dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line)
    return result


def _strip_to_section(code: str, marker: str) -> str:
    index = code.find(marker)
    if index == -1:
        return code
    return code[index:]


def _strip_loader_block(code: str) -> str:
    parts = code.split("\n\n", 1)
    return parts[1] if len(parts) == 2 else code


def build_chart_export(chart_config: dict[str, Any] | None, dataset_name: str | None = None) -> ExportBundle:
    dm = DataManager()
    meta = dm.get_meta(dataset_name)
    dataset_label = meta.name if meta else (dataset_name or "dataset")
    source = dm.get_dataset_source(meta.name if meta else dataset_name)
    chart_config = chart_config or {}
    params = dict(chart_config.get("params") or {})
    library = chart_config.get("library", "plotly")
    chart_type = chart_config.get("chart_type", "scatter")
    title = chart_config.get("title") or params.get("title") or f"{chart_type} chart"

    base_code = ChartCodeGenerator.generate_code(
        library=library,
        chart_type=chart_type,
        params=params,
        data_source="df",
    )
    imports, loader_code = _reader_from_source(source)
    chart_body = _strip_to_section(base_code, "# 2.")
    script_lines = _dedupe_lines(imports + [line for line in base_code.splitlines() if line.startswith("import ")])
    script = "\n".join(script_lines)
    script += "\n\n# Load dataset\n"
    script += f"# Dataset: {dataset_label}\n"
    script += f"{loader_code}\n\n"
    script += chart_body.strip() + "\n"

    stem = _safe_stem(f"{dataset_label}_{chart_type}", "chart_export")
    summary = [
        "Generated from Chart Studio using the current chart configuration.",
        f"Dataset: {dataset_label}",
        f"Library: {library}",
        f"Chart type: {chart_type}",
    ]
    notebook = _build_notebook(title, summary, [("Chart Script", script)])
    return ExportBundle(script, notebook, f"{stem}.py", f"{stem}.ipynb")


def build_workshop_export(pipeline: list[dict[str, Any]] | None, dataset_name: str | None = None) -> ExportBundle:
    dm = DataManager()
    meta = dm.get_meta(dataset_name)
    dataset_label = meta.name if meta else (dataset_name or "dataset")
    source = dm.get_dataset_source(meta.name if meta else dataset_name)
    pipeline = pipeline or []
    generator = WorkshopCodeGenerator()
    generated = generator.generate_code(
        pipeline,
        data_source="your_dataset.csv",
        include_imports=True,
        include_comments=True,
    )
    imports, loader_code = _reader_from_source(source)
    parts = generated.split("\n\n", 2)
    import_block = parts[0] if parts else "import pandas as pd"
    pipeline_body = parts[2] if len(parts) == 3 else ""
    script_lines = _dedupe_lines(imports + import_block.splitlines())
    script = "\n".join(script_lines)
    script += "\n\n# Load dataset\n"
    script += f"# Dataset: {dataset_label}\n"
    script += f"{loader_code}\n"
    if pipeline_body.strip():
        script += "\n" + pipeline_body.strip() + "\n"

    stem = _safe_stem(f"{dataset_label}_workshop", "workshop_export")
    summary = [
        "Generated from Data Workshop using the current cleaning pipeline.",
        f"Dataset: {dataset_label}",
        f"Steps: {len(pipeline)}",
    ]
    notebook = _build_notebook("Data Workshop Export", summary, [("Pipeline Script", script)])
    return ExportBundle(script, notebook, f"{stem}.py", f"{stem}.ipynb")


def build_advanced_export(project_state: dict[str, Any] | None, dataset_name: str | None = None) -> ExportBundle:
    dm = DataManager()
    meta = dm.get_meta(dataset_name)
    dataset_label = meta.name if meta else (dataset_name or "dataset")
    source = dm.get_dataset_source(meta.name if meta else dataset_name)
    page_state = dict(project_state or {})
    workshop_state = page_state.get("data_workshop") or {}
    chart_state = page_state.get("chart_studio") or {}

    imports, loader_code = _reader_from_source(source)
    script_lines = _dedupe_lines(imports + ["import pandas as pd"])
    sections: list[tuple[str, str]] = []

    overview = "\n".join(
        [
            "\n".join(script_lines),
            "",
            "# Load dataset",
            f"# Dataset: {dataset_label}",
            loader_code,
            "",
            "print(df.shape)",
            "print(df.head())",
        ]
    )
    sections.append(("Dataset Overview", overview))

    pipeline = workshop_state.get("pipeline") or []
    if pipeline:
        workshop_bundle = build_workshop_export(pipeline, dataset_name)
        workshop_body = _strip_loader_block(workshop_bundle.py_content.split("\n\n# Load dataset\n", 1)[1])
        sections.append(("Data Workshop Pipeline", "df = df.copy()\n" + workshop_body.strip()))

    chart_config = chart_state.get("chart_data")
    if chart_config:
        chart_bundle = build_chart_export(chart_config, dataset_name)
        chart_body = _strip_to_section(chart_bundle.py_content, "# 2.")
        sections.append(("Chart Studio Visualization", chart_body.strip()))

    flat_script = "\n\n".join(section_code for _, section_code in sections).strip() + "\n"
    stem = _safe_stem(f"{dataset_label}_advanced", "advanced_export")
    summary = [
        "Generated from Advanced using the live project context.",
        f"Dataset: {dataset_label}",
        f"Includes workshop pipeline: {'yes' if pipeline else 'no'}",
        f"Includes chart config: {'yes' if chart_config else 'no'}",
    ]
    notebook = _build_notebook("Advanced Export", summary, sections)
    return ExportBundle(flat_script, notebook, f"{stem}.py", f"{stem}.ipynb")
