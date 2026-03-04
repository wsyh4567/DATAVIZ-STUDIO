# -*- coding: utf-8 -*-
"""DataViz Studio — 命令行入口

Usage
-----
    $ dataviz-studio                    # 通过 pip install -e . 后可用
    $ dataviz-studio --port 9000        # 指定端口
    $ dataviz-studio --no-browser       # 不自动打开浏览器
    $ python cli.py                     # 直接运行
"""

from __future__ import annotations

import argparse
import webbrowser
import threading
import time


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        prog="dataviz-studio",
        description="DataViz Studio — 免费开源的零代码数据分析可视化平台",
    )
    parser.add_argument("--host", type=str, default=None, help="服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="服务器端口 (默认: 8050)")
    parser.add_argument("--debug", action="store_true", default=None, help="开启调试模式")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    return parser.parse_args()


def main() -> None:
    """启动 DataViz Studio 服务器并打开浏览器。"""
    args = parse_args()

    from app import app
    import config

    host = args.host or config.HOST
    port = args.port or config.PORT
    debug = args.debug if args.debug is not None else config.DEBUG

    url = f"http://{host}:{port}"

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    print(f"\n  🧪 DataViz Studio v{config.APP_VERSION}")
    print(f"  → 正在启动：{url}")
    print(f"  → 按 Ctrl+C 停止服务器\n")

    if not args.no_browser:
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        host=host,
        port=port,
        debug=debug,
    )


if __name__ == "__main__":
    main()
