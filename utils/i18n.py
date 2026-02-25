"""DataViz Studio — 国际化（i18n）

简易中英文切换，Phase 1 仅提供中文。
"""

from __future__ import annotations

# Phase 1: 仅中文，后续扩展英文和其他语言
STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        "app_name": "DataViz Studio",
        "welcome_title": "欢迎使用 DataViz Studio",
        "welcome_subtitle": "免费开源的零代码数据分析可视化平台",
        "upload_hint": "拖拽文件到此处，或点击选择文件",
        "upload_formats": "支持 CSV、Excel、JSON 格式",
        "sample_datasets": "示例数据集",
        "nav_canvas": "数据画布",
        "nav_data": "数据中心",
        "nav_workshop": "数据工坊",
        "nav_charts": "图表工作室",
        "nav_stats": "统计实验室",
        "nav_dashboard": "仪表盘",
        "nav_advanced": "高级工具",
        "total_rows": "总行数",
        "total_cols": "总列数",
        "missing": "缺失值",
        "duplicates": "重复行",
        "memory": "内存",
        "no_data": "尚未加载数据",
        "load_success": "数据加载成功",
        "load_error": "数据加载失败",
        "coming_soon": "即将推出",
    },
}


def t(key: str, lang: str = "zh") -> str:
    """获取国际化字符串。"""
    return STRINGS.get(lang, STRINGS["zh"]).get(key, key)
