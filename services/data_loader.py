# -*- coding: utf-8 -*-
"""DataViz Studio — 数据加载服务

支持 CSV / Excel / JSON 以及内置示例数据集。
"""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path
from typing import Optional

import chardet
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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


def load_parquet(file_content: bytes) -> pd.DataFrame:
    """加载 Parquet 文件。"""
    return pd.read_parquet(io.BytesIO(file_content))


def load_feather(file_content: bytes) -> pd.DataFrame:
    """加载 Feather 文件。"""
    return pd.read_feather(io.BytesIO(file_content))


def _optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """优化 DataFrame 的数据类型以减少内存使用。"""
    for col in df.columns:
        # 尝试转换为数值类型
        if pd.api.types.is_numeric_dtype(df[col]):
            if pd.api.types.is_integer_dtype(df[col]):
                # 尝试转换为更小的整数类型
                min_val = df[col].min()
                max_val = df[col].max()
                if min_val >= np.iinfo(np.int8).min and max_val <= np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif min_val >= np.iinfo(np.int16).min and max_val <= np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif min_val >= np.iinfo(np.int32).min and max_val <= np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
            # 浮点数可以考虑 downcast，但通常不显著且可能损失精度
            # df[col] = pd.to_numeric(df[col], downcast='float')
        # 尝试转换为日期时间类型
        elif pd.api.types.is_string_dtype(df[col]):
            try:
                # 尝试转换为日期时间，errors='coerce' 会将无法解析的转换为 NaT
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # 如果转换后大部分是 NaT，则可能不是日期时间，恢复为字符串
                if df[col].isnull().sum() > len(df) * 0.5:
                    df[col] = df[col].astype(str)
            except Exception:
                pass # 保持为字符串
        # 尝试转换为 Categorical 类型
        if df[col].nunique() / len(df) < 0.5 and len(df[col]) > 50: # 阈值可调整
            df[col] = df[col].astype('category')
    return df


def load_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """支持 Excel, CSV, TSV, JSON, Parquet, Feather"""
    try:
        if filename.endswith('.csv'):
            try:
                # 首先尝试 utf-8
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            except UnicodeDecodeError:
                # 失败则尝试 gbk/gb18030
                df = pd.read_csv(io.BytesIO(file_content), encoding='gb18030')
        elif filename.endswith('.tsv'):
            df = pd.read_csv(io.BytesIO(file_content), sep='\t')
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(file_content))
        elif filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(file_content))
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(io.BytesIO(file_content))
        elif filename.endswith('.feather'):
            df = pd.read_feather(io.BytesIO(file_content))
        else:
            raise ValueError(f"不受支持的文件格式: {filename}")
        
        # Optimize dtypes
        df = _optimize_dtypes(df)
        return df

    except Exception as e:
        logger.error(f"Failed to load file {filename}: {e}")
        raise ValueError(f"无法加载文件 {filename}: {str(e)}")


def load_from_database(connection_string: str, query: str) -> pd.DataFrame:
    """
    通过 SQLAlchemy 从数据库加载指定查询语句的结果。
    适用于 MySQL, PostgreSQL, SQLite, SQL Server 等。
    """
    try:
        import sqlalchemy
        from sqlalchemy import create_engine
    except ImportError:
        raise ImportError("连接数据库需要安装 'sqlalchemy'。请执行 pip install sqlalchemy")

    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
        
        df = _optimize_dtypes(df)
        return df
    except Exception as e:
        logger.error(f"Failed to load from database: {e}")
        raise ValueError(f"无法从数据库加载数据: {str(e)}")


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
    "gapminder": {
        "label": "🌍 国家经济 (Gapminder)",
        "description": "全球经济发展数据 — 1704 行 × 6 列",
    },
    "stocks": {
        "label": "科技股票 (Stocks)",
        "description": "股票价格数据 — 504 行 × 7 列",
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
    elif name == "gapminder":
        return _make_gapminder()
    elif name == "stocks":
        return _make_stocks()
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


def _make_gapminder() -> pd.DataFrame:
    """全球国家经济发展数据集"""
    rng = np.random.RandomState(42)

    countries = {
        "China": ("Asia", 1300, 3000, 72),
        "India": ("Asia", 1100, 1800, 65),
        "United States": ("Americas", 300, 40000, 78),
        "Indonesia": ("Asia", 230, 2500, 68),
        "Brazil": ("Americas", 190, 8000, 72),
        "Japan": ("Asia", 127, 35000, 82),
        "Germany": ("Europe", 82, 38000, 80),
        "United Kingdom": ("Europe", 62, 36000, 79),
        "France": ("Europe", 64, 34000, 81),
        "Nigeria": ("Africa", 160, 2000, 52),
        "Egypt": ("Africa", 85, 5000, 70),
        "South Africa": ("Africa", 50, 8000, 55),
        "Mexico": ("Americas", 115, 9000, 75),
        "Canada": ("Americas", 35, 42000, 81),
        "Australia": ("Oceania", 22, 45000, 82),
        "South Korea": ("Asia", 50, 28000, 79),
        "Argentina": ("Americas", 42, 12000, 76),
        "Kenya": ("Africa", 45, 1500, 60),
    }

    years = list(range(1952, 2008, 5))
    rows = []

    for country, (continent, base_pop, base_gdp, base_life) in countries.items():
        for i, year in enumerate(years):
            growth = 1 + i * 0.08 + rng.normal(0, 0.02)
            pop = int(base_pop * (1 + i * 0.03) * 1_000_000 * (1 + rng.normal(0, 0.02)))
            gdp = round(base_gdp * growth * (1 + rng.normal(0, 0.05)), 1)
            life = round(base_life + i * 0.5 + rng.normal(0, 0.5), 1)
            life = min(life, 85)
            rows.append({
                "country": country,
                "continent": continent,
                "year": year,
                "lifeExp": life,
                "pop": pop,
                "gdpPercap": gdp,
            })

    return pd.DataFrame(rows)


def _make_stocks() -> pd.DataFrame:
    """科技公司股票数据集"""
    rng = np.random.RandomState(7)

    companies = {
        "AAPL": 150, "GOOGL": 2800, "MSFT": 300,
        "AMZN": 3300, "TSLA": 700, "META": 330, "NVDA": 220,
    }

    dates = pd.date_range("2023-01-01", periods=72, freq="W")
    rows = []

    for symbol, base_price in companies.items():
        price = base_price
        for date in dates:
            change = rng.normal(0.001, 0.03)
            price *= (1 + change)
            volume = int(rng.uniform(5_000_000, 50_000_000))
            high = price * (1 + abs(rng.normal(0, 0.015)))
            low = price * (1 - abs(rng.normal(0, 0.015)))
            rows.append({
                "date": date,
                "symbol": symbol,
                "close": round(price, 2),
                "open": round(price * (1 + rng.normal(0, 0.005)), 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": volume,
            })

    return pd.DataFrame(rows)

