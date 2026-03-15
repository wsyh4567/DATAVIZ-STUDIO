# -*- coding: utf-8 -*-
"""DataViz Studio — 全局配置"""

import os
from pathlib import Path
from typing import Final


# ── 路径 ─────────────────────────────────────────────
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
ASSETS_DIR: Final[Path] = PROJECT_ROOT / "assets"
UPLOAD_DIR: Final[Path] = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── 服务器 ───────────────────────────────────────────
HOST: str = os.environ.get("DATAVIZ_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("DATAVIZ_PORT", "8050"))
DEBUG: bool = os.environ.get("DATAVIZ_DEBUG", "false").lower() == "true"

# ── 应用元数据 ────────────────────────────────────────
APP_NAME: Final[str] = "DataViz Studio"
APP_VERSION: Final[str] = "0.1.0"
APP_DESCRIPTION: Final[str] = "免费开源的零代码数据分析可视化平台"

# ── 数据 ─────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB: Final[int] = 500
SUPPORTED_FILE_TYPES: Final[list[str]] = [
    ".csv", ".tsv", ".xlsx", ".xls", ".json",
    ".parquet", ".feather", ".ftr",
]

# ── 主题 ─────────────────────────────────────────────
DEFAULT_THEME: Final[str] = "dark"

# ── 导航 ─────────────────────────────────────────────
NAV_ITEMS: Final[list[dict]] = [
    {"icon": "bi bi-house", "label": "主页", "href": "/home"},
    {"icon": "bi bi-server", "label": "数据中心", "href": "/data"},
    {"icon": "bi bi-grid-1x2", "label": "数据画布", "href": "/canvas"},
    {"icon": "bi bi-hammer", "label": "数据工坊", "href": "/workshop"},
    {"icon": "bi bi-graph-up", "label": "图表工作室", "href": "/charts"},
    {"icon": "bi bi-calculator", "label": "统计实验室", "href": "/stats"},
    {"icon": "bi bi-robot", "label": "机器学习", "href": "/ml"},
    {"icon": "bi bi-lightning", "label": "高级工具", "href": "/advanced"},
]
