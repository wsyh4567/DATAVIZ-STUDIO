# DataViz Studio

[中文](./README.md) | [English](./README_EN.md)

A local-first Python low-code analytics workspace for data analysts, data scientists, and business teams.  
Built with Dash, pandas, Plotly, and scikit-learn, it covers data import, EDA, data cleaning, visualization, statistics, machine learning, and exportable project/code workflows.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-orange.svg)](https://plotly.com/)
[![Version](https://img.shields.io/badge/version-0.4.0-success.svg)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Latest Release

### v0.4.0 · 2026-03-09

The latest formal release entry is recorded in [CHANGELOG.md](/Users/Toxic/Desktop/python/python项目DataViz%20Studio/CHANGELOG.md).

- Rebuilt Data Workshop around a more structured step-based cleaning flow.
- Expanded ML Studio with time-series, interactive inference, and batch prediction workflows.
- Improved Chart Studio with better parameter validation and chart interaction fixes.
- Fixed multiple stability issues across DataTable, Seaborn rendering, and global notifications.

### Additional enhancements currently on `main`

- Project open/save actions are available in the top bar through `.dvs` project files.
- Reopening a project restores route, datasets, page state, and part of the analysis context.
- Chart Studio, Data Workshop, and Advanced Tools now share a unified `.py` and `.ipynb` export workflow.
- ML Studio now surfaces Chinese workflow guidance, algorithm fit notes, and clearer next-step prompts directly in the main page flow.
- Chart Studio recommendation cards now expose rationale and use cases, and common `city -> sales` / `date -> sales` recommendations are more stable.
- The top bar now includes system status, Python version, dataset badges, and quick actions.
- Runtime dependencies were completed, including `requests`, `scipy`, `scikit-learn`, `sqlalchemy`, and `kaleido`.

## Showcase

| Home / Overview | Data Workshop |
| --- | --- |
| ![Home](./assets/screenshots/showcase_home.png) | ![Workshop](./assets/screenshots/showcase_workshop.png) |
| Chart Studio | ML Studio |
| ![Charts](./assets/screenshots/showcase_charts.png) | ![ML](./assets/screenshots/showcase_ml.webp) |

## Features By Navigation Area

### Home

- Acts as the workspace landing page and quick navigation surface.
- Helps users understand the main modules at a glance.

### Data Hub

- Imports CSV, Excel, JSON, Parquet, Feather, and more.
- Supports local files, sample datasets, and reference-based restores.
- Manages multiple datasets and the active dataset.

### Data Canvas

- Provides dataset overview, schema inspection, exports, and report entry points.
- Useful for quick exploratory analysis and quality checks.

### Data Workshop

- Builds cleaning pipelines with visual steps such as filtering, sorting, missing-value handling, deduplication, and renaming.
- Supports preview, undo/redo, and pipeline export.
- Exports both Python scripts and Jupyter notebooks.

### Chart Studio

- Supports both Plotly and Seaborn.
- Includes chart configuration, live preview, and PNG / HTML export. SVG export is currently limited to supported Plotly flows, while Seaborn charts explicitly fall back to PNG.
- Generates reproducible Python code and notebook exports.

### Statistics Lab

- Includes descriptive statistics, correlations, grouped summaries, and common statistical tests.

### ML Studio

- Covers classification, regression, clustering, and time-series related workflows.
- Saves part of page state into project files for later continuation.

### Advanced Tools

- Aggregates current project context into a unified export pipeline.
- Helps bridge interactive exploration into script-based delivery.

## Top Bar And Project Workflow

### Top bar

- Open project
- Save project
- System status
- Python version display
- Active dataset badges
- Quick actions

### `.dvs` project files

- Saving supports both `embedded` and `reference` storage modes.
- `embedded` stores data inside the project archive and is best for portability.
- `reference` keeps the project smaller by reloading from the original source when possible.

### Project restore

- Reopening a project can restore route, datasets, app state, and part of page state.
- Chart Studio, Data Workshop, and ML Studio currently integrate with this restore flow.

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
- Plotly static export depends on `kaleido`; without it, HTML export still works but PNG / SVG export will surface a dependency warning.
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
