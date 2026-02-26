# -*- coding: utf-8 -*-
"""DataViz Studio — 数据加载服务

支持 CSV / Excel / JSON 以及内置示例数据集。
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Optional

import chardet
import numpy as np
import pandas as pd


# ── 文件加载 ───────────────────────────────────────────

def load_csv(
    file_content: bytes,
    filename: str = "data.csv",
    encoding: Optional[str] = None,
    sep: Optional[str] = None,
) -> pd.DataFrame:
    """加载 CSV / TSV 文件。

    Parameters
    ----------
    file_content : bytes
        文件原始字节内容。
    filename : str
        文件名（用于推断分隔符）。
    encoding : str | None
        编码。若为 None，自动检测。
    sep : str | None
        分隔符。若为 None，自动推断。

    Returns
    -------
    pd.DataFrame
    """
    # Auto-detect encoding
    if encoding is None:
        det = chardet.detect(file_content[:10000])
        encoding = det.get("encoding", "utf-8") or "utf-8"

    text = file_content.decode(encoding, errors="replace")

    # Auto-detect separator
    if sep is None:
        if filename.lower().endswith(".tsv"):
            sep = "\t"
        else:
            first_line = text.split("\n", 1)[0]
            for candidate in [",", "\t", ";", "|"]:
                if candidate in first_line:
                    sep = candidate
                    break
            else:
                sep = ","

    return pd.read_csv(io.StringIO(text), sep=sep, engine="python")


def load_excel(
    file_content: bytes,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """加载 Excel 文件 (.xlsx / .xls)。"""
    return pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name, engine="openpyxl")


def load_json(
    file_content: bytes,
    encoding: Optional[str] = None,
) -> pd.DataFrame:
    """加载 JSON 文件（支持数组和嵌套对象）。"""
    if encoding is None:
        det = chardet.detect(file_content[:10000])
        encoding = det.get("encoding", "utf-8") or "utf-8"

    text = file_content.decode(encoding, errors="replace")
    data = json.loads(text)

    if isinstance(data, list):
        return pd.json_normalize(data)
    elif isinstance(data, dict):
        # 尝试找到包含列表的第一个键
        for key, val in data.items():
            if isinstance(val, list):
                return pd.json_normalize(val)
        # 退回到单行 dict
        return pd.json_normalize(data)
    else:
        raise ValueError("JSON 格式不受支持：需要数组或对象。")


def load_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """根据文件扩展名自动选择加载方式。"""
    ext = Path(filename).suffix.lower()
    if ext in (".csv", ".tsv"):
        return load_csv(file_content, filename)
    elif ext in (".xlsx", ".xls"):
        return load_excel(file_content)
    elif ext == ".json":
        return load_json(file_content)
    else:
        raise ValueError(f"不支持的文件格式：{ext}")


# ── 内置示例数据集 ─────────────────────────────────────

SAMPLE_DATASETS: dict[str, dict] = {
    "iris": {
        "label": "🌸 鸢尾花 (Iris)",
        "description": "经典分类数据集 — 150 行 × 5 列",
    },
    "tips": {
        "label": "🍽️ 餐饮小费 (Tips)",
        "description": "餐厅消费数据 — 244 行 × 7 列",
    },
    "titanic": {
        "label": "🚢 泰坦尼克 (Titanic)",
        "description": "乘客生存数据 — 891 行 × 12 列",
    },
}


def load_sample_dataset(name: str) -> pd.DataFrame:
    """加载内置示例数据集。"""
    if name == "iris":
        return _make_iris()
    elif name == "tips":
        return _make_tips()
    elif name == "titanic":
        return _make_titanic()
    else:
        raise ValueError(f"未知示例数据集：{name}")


# ── 内置数据生成（避免依赖 sklearn / seaborn） ────────

def _make_iris() -> pd.DataFrame:
    """经典鸢尾花数据集"""
    rng = np.random.RandomState(42)
    n = 50
    species = []
    data = []
    for sp, means in [
        ("setosa",     [5.0, 3.4, 1.5, 0.2]),
        ("versicolor", [5.9, 2.8, 4.3, 1.3]),
        ("virginica",  [6.6, 3.0, 5.6, 2.0]),
    ]:
        sl = rng.normal(means[0], 0.35, n)
        sw = rng.normal(means[1], 0.38, n)
        pl = rng.normal(means[2], 0.17, n)
        pw = rng.normal(means[3], 0.10, n)
        for i in range(n):
            data.append([round(sl[i], 1), round(sw[i], 1),
                         round(pl[i], 1), round(pw[i], 1)])
            species.append(sp)
    df = pd.DataFrame(data, columns=[
        "sepal_length", "sepal_width", "petal_length", "petal_width",
    ])
    df["species"] = species
    return df


def _make_tips() -> pd.DataFrame:
    """餐饮小费数据集"""
    rng = np.random.RandomState(0)
    n = 244
    total = rng.uniform(3, 50, n).round(2)
    tip = (total * rng.uniform(0.05, 0.3, n)).round(2)
    sex = rng.choice(["Male", "Female"], n)
    smoker = rng.choice(["Yes", "No"], n, p=[0.38, 0.62])
    day = rng.choice(["Thu", "Fri", "Sat", "Sun"], n, p=[0.16, 0.08, 0.40, 0.36])
    time = rng.choice(["Lunch", "Dinner"], n, p=[0.28, 0.72])
    size = rng.choice([1, 2, 3, 4, 5, 6], n, p=[0.04, 0.40, 0.18, 0.24, 0.10, 0.04])
    return pd.DataFrame({
        "total_bill": total,
        "tip": tip,
        "sex": sex,
        "smoker": smoker,
        "day": day,
        "time": time,
        "size": size,
    })


def _make_titanic() -> pd.DataFrame:
    """泰坦尼克号乘客数据集（合成版）"""
    rng = np.random.RandomState(1)
    n = 891
    pclass = rng.choice([1, 2, 3], n, p=[0.24, 0.21, 0.55])
    sex = rng.choice(["male", "female"], n, p=[0.65, 0.35])
    age = rng.normal(30, 12, n).clip(0.5, 80).round(1)
    age[rng.rand(n) < 0.20] = np.nan  # ~20% missing
    sibsp = rng.choice(range(6), n, p=[0.68, 0.23, 0.05, 0.02, 0.01, 0.01])
    parch = rng.choice(range(6), n, p=[0.76, 0.12, 0.08, 0.02, 0.01, 0.01])
    fare = (rng.exponential(30, n) * (4 - pclass) / 3).round(2)
    embarked = rng.choice(["S", "C", "Q"], n, p=[0.72, 0.19, 0.09])
    # survival correlated with class and sex
    prob = 0.15 + 0.15 * (3 - pclass) / 2 + 0.25 * (sex == "female").astype(float)
    survived = (rng.rand(n) < prob).astype(int)

    names = [f"Passenger_{i+1}" for i in range(n)]
    return pd.DataFrame({
        "survived": survived,
        "pclass": pclass,
        "name": names,
        "sex": sex,
        "age": age,
        "sibsp": sibsp,
        "parch": parch,
        "fare": fare,
        "embarked": embarked,
    })
