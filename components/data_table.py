"""DataViz Studio — AG Grid 数据表格封装"""

from __future__ import annotations

from typing import Optional

import dash_ag_grid as dag
import pandas as pd


def create_data_table(
    df: Optional[pd.DataFrame] = None,
    table_id: str = "main-data-table",
) -> dag.AgGrid:
    """创建 AG Grid 数据表格组件。

    Parameters
    ----------
    df : pd.DataFrame | None
        要显示的数据。None 时显示空表格。
    table_id : str
        组件 ID。

    Returns
    -------
    dag.AgGrid
    """
    if df is None or df.empty:
        return dag.AgGrid(
            id=table_id,
            rowData=[],
            columnDefs=[],
            className="ag-theme-alpine-dark",
            style={"height": "calc(100vh - 240px)", "width": "100%"},
            dashGridOptions={
                "animateRows": True,
                "pagination": True,
                "paginationPageSize": 100,
                "rowSelection": "multiple",
                "suppressRowClickSelection": True,
                "overlayNoRowsTemplate": "<span style='color: var(--text-muted)'>📭 暂无数据</span>",
            },
        )

    # Build column definitions
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

    # Convert to records for AG Grid
    row_data = df.head(10000).to_dict("records")

    return dag.AgGrid(
        id=table_id,
        rowData=row_data,
        columnDefs=col_defs,
        className="ag-theme-alpine-dark",
        style={"height": "calc(100vh - 240px)", "width": "100%"},
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "minWidth": 80,
        },
        dashGridOptions={
            "animateRows": True,
            "pagination": True,
            "paginationPageSize": 100,
            "paginationPageSizeSelector": [50, 100, 500, 1000],
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
        },
    )
