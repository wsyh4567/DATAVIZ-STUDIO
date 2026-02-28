# -*- coding: utf-8 -*-
"""DataViz Studio — 全局配置"""

from pathlib import Path
from typing import Final


# ── 路径 ─────────────────────────────────────────────
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
ASSETS_DIR: Final[Path] = PROJECT_ROOT / "assets"
UPLOAD_DIR: Final[Path] = PROJECT_ROOT / "uploads"

# ── 服务器 ───────────────────────────────────────────
HOST: Final[str] = "127.0.0.1"
PORT: Final[int] = 8050
DEBUG: Final[bool] = True

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
    {"icon": "📊", "label": "数据画布", "href": "/canvas"},
    {"icon": "📁", "label": "数据中心", "href": "/data"},
    {"icon": "🧹", "label": "数据工坊", "href": "/workshop"},
    {"icon": "📈", "label": "图表工作室", "href": "/charts"},
    {"icon": "🧮", "label": "统计实验室", "href": "/stats"},
    {"icon": "📋", "label": "仪表盘", "href": "/dashboard"},
    {"icon": "⚡", "label": "高级工具", "href": "/advanced"},
]
