"""DataViz Studio — 命令行入口

Usage
-----
    $ dataviz-studio          # 通过 pip install -e . 后可用
    $ python cli.py           # 直接运行
"""

from __future__ import annotations

import webbrowser
import threading
import time


def main() -> None:
    """启动 DataViz Studio 服务器并打开浏览器。"""
    from app import app
    import config

    url = f"http://{config.HOST}:{config.PORT}"

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    print(f"\n  🧪 DataViz Studio v{config.APP_VERSION}")
    print(f"  → 正在启动：{url}")
    print(f"  → 按 Ctrl+C 停止服务器\n")

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )


if __name__ == "__main__":
    main()
