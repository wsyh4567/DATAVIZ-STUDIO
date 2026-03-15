# DataViz Studio

[中文](./README.md) | [English](./README_EN.md)

A local-first Python low-code analytics workspace for data analysts, data scientists, and business teams.  
Built with Dash, pandas, Plotly, and scikit-learn, it covers data import, EDA, data cleaning, visualization, statistics, machine learning, and exportable project/code workflows.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-orange.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Recent Updates

- Project persistence is back: the top bar now supports opening and saving `.dvs` project files.
- State restore is available: route, datasets, page state, and part of the analysis context can be restored after reopening a project.
- Unified export flow: Chart Studio, Data Workshop, and Advanced Tools now export both `.py` scripts and `.ipynb` notebooks through the same service layer.
- Top bar status is richer: Python runtime/version, dataset badges, and system status are displayed in one place.
- Recent workspace upgrades include the redesigned EDA canvas, ML Studio workflow improvements, and multiple UX fixes.
- Runtime dependencies were completed, including `requests`, `scipy`, `scikit-learn`, `sqlalchemy`, and `kaleido`.

## Showcase

| Home / Overview | Data Workshop |
| --- | --- |
| ![Home](./assets/screenshots/showcase_home.png) | ![Workshop](./assets/screenshots/showcase_workshop.png) |
| Chart Studio | ML Studio |
| ![Charts](./assets/screenshots/showcase_charts.png) | ![ML](./assets/screenshots/showcase_ml.webp) |

## What It Does

### 1. Data Hub

- Imports CSV, Excel, JSON, Parquet, Feather, and more.
- Supports local files, sample datasets, and reference-based restores.
- Manages multiple datasets and the active dataset.

### 2. Data Canvas / EDA

- Provides dataset overview, schema inspection, exports, and report entry points.
- Useful for quick exploratory analysis and quality checks.

### 3. Data Workshop

- Builds cleaning pipelines with visual steps such as filtering, sorting, missing-value handling, deduplication, and renaming.
- Supports preview, undo/redo, and pipeline export.
- Exports both Python scripts and Jupyter notebooks.

### 4. Chart Studio

- Supports both Plotly and Seaborn.
- Includes chart configuration, live preview, and PNG / SVG / HTML export.
- Generates reproducible Python code and notebook exports.

### 5. Statistics Lab

- Includes descriptive statistics, correlations, grouped summaries, and common statistical tests.

### 6. ML Studio

- Covers classification, regression, clustering, and time-series related workflows.
- Saves part of page state into project files for later continuation.

### 7. Advanced Tools

- Aggregates current project context into a unified export pipeline.
- Helps bridge interactive exploration into script-based delivery.

## What Changed In These Recent Commits

### `.dvs` project files

- Saving supports both `embedded` and `reference` storage modes.
- `embedded` stores data inside the project archive and is best for portability.
- `reference` keeps the project smaller by reloading from the original source when possible.

### Top bar workflow

- The top bar now includes project open/save actions, system status, dataset badges, and a quick action entry point.
- The system status section shows Python runtime state and version information.

### Unified code export

- `services/export_service.py` now centralizes script and notebook export bundles.
- Data Workshop, Chart Studio, and Advanced Tools all reuse this export path.

## Tech Stack

- Python 3.9+
- Dash
- Plotly
- pandas
- NumPy
- Seaborn / Matplotlib
- SciPy
- scikit-learn
- SQLAlchemy
- Dash Bootstrap Components
- Dash AG Grid

## Installation

```bash
git clone https://github.com/wsyh4567/DATAVIZ-STUDIO.git
cd DATAVIZ-STUDIO
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Default URL:

```text
http://127.0.0.1:8050
```

## Project Structure

```text
app.py                    Dash application entry
components/               Shared UI components such as top bar and side bar
core/                     Data and app state management
pages/                    Feature pages
services/                 Import, export, statistics, project persistence, and more
assets/                   Static assets and screenshots
tests/                    Tests
```

## Best Fit

- Data scientists working locally with privacy-sensitive datasets
- Analysts who want a GUI on top of pandas and Plotly workflows
- Teams that need to turn interactive analysis into scripts or notebooks
- Projects that value local execution and reproducibility

## Current Limits

- It is still a single-machine local analytics app, not a multi-user collaboration platform.
- Large-scale workloads are still constrained by the pandas in-memory model.
- Test coverage can be expanded further across several modules.
- Documentation currently focuses on onboarding, not full page-by-page reference coverage.

## Development

Run all tests:

```bash
pytest
```

If you only want to validate the Data Workshop execution layer:

```bash
pytest tests/data_workshop/test_operation_executor.py
```

## License

MIT
