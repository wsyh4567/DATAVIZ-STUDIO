# -*- coding: utf-8 -*-
"""机器学习工作室页面入口及路由注册"""

from dash import html
from .layout import create_ml_studio_page
from . import callbacks 

__all__ = ["create_ml_studio_page"]
