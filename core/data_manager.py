# -*- coding: utf-8 -*-
"""DataViz Studio — 数据管理器

管理多个 DataFrame 实例，提供活跃数据集追踪和 undo/redo 功能。
"""

from __future__ import annotations

from io import StringIO
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class DatasetMeta:
    """单个数据集的元数据"""
    name: str
    rows: int
    cols: int
    memory_mb: float
    dtypes: dict[str, str]
    source: str  # e.g. "file:sales.csv" or "sample:iris"


class DataManager:
    """全局数据管理中心 — 单例模式

    Features
    --------
    - 多 DataFrame 存储（name → DataFrame）
    - 活跃数据集追踪
    - Undo / Redo 操作历史
    - 数据集元数据计算
    """

    _instance: Optional["DataManager"] = None

    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._datasets: dict[str, pd.DataFrame] = {}
        self._sources: dict[str, str] = {}
        self._active: Optional[str] = None
        self._history: list[dict] = []       # undo stack
        self._future: list[dict] = []        # redo stack
        self._max_history: int = 50
        self._initialized = True

    # ── Dataset CRUD ──────────────────────────────────

    def add_dataset(self, name: str, df: pd.DataFrame, source: str = "") -> str:
        """添加数据集，返回最终使用的名称（自动去重）。"""
        final_name = self._unique_name(name)
        self._datasets[final_name] = df
        self._sources[final_name] = source
        if self._active is None:
            self._active = final_name
        return final_name

    def remove_dataset(self, name: str) -> None:
        """删除指定数据集。"""
        self._datasets.pop(name, None)
        self._sources.pop(name, None)
        if self._active == name:
            self._active = next(iter(self._datasets), None)

    def get_dataset(self, name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """获取数据集。name 为 None 时返回活跃数据集。"""
        key = name or self._active
        if key is None:
            return None
        return self._datasets.get(key)

    def rename_dataset(self, old_name: str, new_name: str) -> str:
        """重命名数据集。"""
        if old_name not in self._datasets:
            return old_name
        final = self._unique_name(new_name)
        self._datasets[final] = self._datasets.pop(old_name)
        self._sources[final] = self._sources.pop(old_name, "")
        if self._active == old_name:
            self._active = final
        return final

    # ── Active dataset ────────────────────────────────

    @property
    def active_name(self) -> Optional[str]:
        return self._active

    @active_name.setter
    def active_name(self, name: str) -> None:
        if name in self._datasets:
            self._active = name

    @property
    def active_df(self) -> Optional[pd.DataFrame]:
        return self.get_dataset()

    @active_df.setter
    def active_df(self, df: pd.DataFrame) -> None:
        """更新活跃数据集"""
        if self._active and self._active in self._datasets:
            self._datasets[self._active] = df

    def update_active_dataset(self, df: pd.DataFrame, snapshot: bool = True) -> None:
        """更新活跃数据集，可选择是否保存快照"""
        if snapshot and self._active:
            self.snapshot(f"Update {self._active}")
        if self._active and self._active in self._datasets:
            self._datasets[self._active] = df

    # ── Metadata ──────────────────────────────────────

    def get_meta(self, name: Optional[str] = None) -> Optional[DatasetMeta]:
        """返回数据集元数据。"""
        key = name or self._active
        df = self._datasets.get(key) if key else None
        if df is None:
            return None
        mem = df.memory_usage(deep=True).sum() / (1024 * 1024)
        dtypes = {col: str(dt) for col, dt in df.dtypes.items()}
        return DatasetMeta(
            name=key,
            rows=len(df),
            cols=len(df.columns),
            memory_mb=round(mem, 2),
            dtypes=dtypes,
            source=self._sources.get(key, ""),
        )

    def list_datasets(self) -> list[DatasetMeta]:
        """列出所有数据集的元数据。"""
        return [self.get_meta(n) for n in self._datasets if self.get_meta(n)]

    @property
    def dataset_names(self) -> list[str]:
        return list(self._datasets.keys())

    def export_datasets(self, storage_mode: str = "embedded") -> list[dict]:
        exported: list[dict] = []
        for name, df in self._datasets.items():
            item = {
                "name": name,
                "source": self._sources.get(name, ""),
                "active": name == self._active,
                "storage_mode": storage_mode,
            }
            if storage_mode == "embedded":
                item["data_json"] = df.to_json(date_format="iso", orient="split")
            exported.append(item)
        return exported

    def restore_datasets(self, datasets: list[dict]) -> None:
        self.clear()
        active_name: Optional[str] = None
        for dataset in datasets or []:
            data_json = dataset.get("data_json")
            if not data_json:
                continue
            df = pd.read_json(StringIO(data_json), orient="split")
            final_name = self.add_dataset(
                dataset.get("name") or "dataset",
                df,
                source=dataset.get("source", ""),
            )
            if dataset.get("active"):
                active_name = final_name
        if active_name and active_name in self._datasets:
            self._active = active_name

    # ── Undo / Redo ───────────────────────────────────

    def snapshot(self, label: str = "") -> None:
        """保存当前活跃数据集快照到历史栈。"""
        if self._active and self._active in self._datasets:
            self._history.append({
                "name": self._active,
                "df": self._datasets[self._active].copy(),
                "label": label,
            })
            if len(self._history) > self._max_history:
                self._history.pop(0)
            self._future.clear()

    def undo(self) -> bool:
        if not self._history:
            return False
        snap = self._history.pop()
        name = snap["name"]
        if name in self._datasets:
            self._future.append({
                "name": name,
                "df": self._datasets[name].copy(),
                "label": snap["label"],
            })
            self._datasets[name] = snap["df"]
        return True

    def redo(self) -> bool:
        if not self._future:
            return False
        snap = self._future.pop()
        name = snap["name"]
        if name in self._datasets:
            self._history.append({
                "name": name,
                "df": self._datasets[name].copy(),
                "label": snap["label"],
            })
            self._datasets[name] = snap["df"]
        return True

    # ── Helpers ────────────────────────────────────────

    def _unique_name(self, name: str) -> str:
        """保证名称不重复。"""
        if name not in self._datasets:
            return name
        i = 2
        while f"{name} ({i})" in self._datasets:
            i += 1
        return f"{name} ({i})"

    def clear(self) -> None:
        """清空所有数据集和历史。"""
        self._datasets.clear()
        self._sources.clear()
        self._history.clear()
        self._future.clear()
        self._active = None

    @classmethod
    def reset(cls) -> None:
        """重置单例实例（用于测试）。"""
        cls._instance = None
