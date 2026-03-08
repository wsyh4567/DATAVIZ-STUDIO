# -*- coding: utf-8 -*-
"""DataViz Studio — AG Grid 数据表格封装"""

from __future__ import annotations

from typing import Optional, Literal

import dash_ag_grid as dag
import pandas as pd


def create_data_table(
    df: Optional[pd.DataFrame] = None,
    table_id: str = "main-data-table",
    view_mode: Literal["head", "middle", "tail", "all"] = "head",
    n_rows: int = 10,
) -> dag.AgGrid:
    """创建 AG Grid 数据表格组件。

    Parameters
    ----------
    df : pd.DataFrame | None
        要显示的数据。None 时显示空表格。
    table_id : str
        组件 ID。
    view_mode : str
        数据显示模式：
        - "head": 前N行
        - "middle": 中间N行
        - "tail": 后N行
        - "all": 全部数据（最多10000行）
    n_rows : int
        要显示的行数（仅在非"all"模式下使用），默认10

    Returns
    -------
    dag.AgGrid
    """
    if df is None or df.empty:
        return dag.AgGrid(
            id=table_id,
            rowData=[],
            columnDefs=[],
            className="ag-theme-alpine",
            style={"height": "calc(100vh - 320px)", "width": "100%"},
            dashGridOptions={
                "animateRows": True,
                "pagination": True,
                "paginationPageSize": 100,
                "rowSelection": "multiple",
                "suppressRowClickSelection": True,
                "overlayNoRowsTemplate": "<span style='color: var(--text-muted)'>📭 暂无数据</span>",
            },
        )

    # Build column definitions with auto-sizing
    col_defs = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        col_def = {
            "field": col,
            "headerName": col,
            "sortable": True,
            "filter": True,
            "resizable": True,
            "minWidth": 100,
            "flex": 1,  # Auto-size columns to fill available space
        }

        # Type-specific config
        if "int" in dtype or "float" in dtype:
            col_def["type"] = "numericColumn"
            col_def["filter"] = "agNumberColumnFilter"
            if "float" in dtype:
                col_def["valueFormatter"] = {
                    "function": "d3.format(',.2f')(params.value)"
                }
        elif "datetime" in dtype:
            col_def["filter"] = "agDateColumnFilter"
        else:
            col_def["filter"] = "agTextColumnFilter"

        col_defs.append(col_def)

    # Select data based on view mode
    total_rows = len(df)
    
    # Ensure n_rows is valid
    n = max(1, min(n_rows, total_rows))
    
    if view_mode == "head":
        # First N rows
        display_df = df.head(n)
        info_text = f"显示前 {n:,} 行（共 {total_rows:,} 行）"
    elif view_mode == "middle":
        # Middle N rows
        middle_start = max(0, (total_rows - n) // 2)
        middle_end = min(middle_start + n, total_rows)
        display_df = df.iloc[middle_start:middle_end]
        info_text = f"显示中间 {len(display_df):,} 行（第 {middle_start + 1:,} - {middle_end:,} 行，共 {total_rows:,} 行）"
    elif view_mode == "tail":
        # Last N rows
        display_df = df.tail(n)
        info_text = f"显示后 {n:,} 行（共 {total_rows:,} 行）"
    else:  # "all"
        # All data (limited to 10000 for performance)
        if total_rows > 10000:
            display_df = df.head(10000)
            info_text = f"显示前 10,000 行（共 {total_rows:,} 行，为保证性能仅显示部分数据）"
        else:
            display_df = df
            info_text = f"显示全部 {total_rows:,} 行"

    # Convert to records for AG Grid
    row_data = display_df.to_dict("records")

    return dag.AgGrid(
        id=table_id,
        rowData=row_data,
        columnDefs=col_defs,
        className="ag-theme-alpine",
        style={"height": "calc(100vh - 320px)", "width": "100%"},
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "minWidth": 80,
            "flex": 1,  # Auto-size all columns
        },
        dashGridOptions={
            "animateRows": True,
            "pagination": True,
            "paginationPageSize": 10 if view_mode != "all" else 100,
            "paginationPageSizeSelector": [10, 50, 100, 500] if view_mode == "all" else [10],
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            "domLayout": "normal",
            "suppressColumnVirtualisation": False,
            "suppressRowVirtualisation": False,
        },
        # Auto-size strategy: fit columns to grid width
        columnSize="responsiveSizeToFit",
    )
