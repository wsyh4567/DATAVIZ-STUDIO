# -*- coding: utf-8 -*-
"""机器学习工作室回调函数"""

from dash import Input, Output, State, callback, no_update, html, dcc, ctx, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

from core.data_manager import DataManager
from .config import HAS_SKLEARN, ACCENT_COLORS
from .components import kpi_card, empty_placeholder, result_interpretation_card
from .model_utils import (
    build_classifier, build_regressor, calculate_clf_metrics, calculate_reg_metrics,
    update_cached_model_context, get_cached_model_context
)

if HAS_SKLEARN:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.impute import SimpleImputer
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics import classification_report, confusion_matrix

# =====================================================================
# 1. 动态 UI 切换 (面板显示与参数控件)
# =====================================================================

@callback(
    Output("ml-clf-panel", "style"),
    Output("ml-reg-panel", "style"),
    Output("ml-cluster-panel", "style"),
    Output("ml-ts-panel", "style"),
    Output("ml-predict-tab", "disabled", allow_duplicate=True),  # 聚类时禁用预测
    Input("ml-algo-tabs", "active_tab"),
    prevent_initial_call=True
)
def toggle_algo_panels(active_tab):
    d_none = {"display": "none"}
    if active_tab == "tab-clf":
        return {"display": "block"}, d_none, d_none, d_none, False
    elif active_tab == "tab-reg":
        return d_none, {"display": "block"}, d_none, d_none, False
    elif active_tab == "tab-cluster":
        return d_none, d_none, {"display": "block"}, d_none, True
    elif active_tab == "tab-ts":
        return d_none, d_none, d_none, {"display": "block"}, False
    return d_none, d_none, d_none, d_none, True


@callback(
    Output("ml-tutorial-offcanvas", "is_open"),
    Input("btn-ml-tutorial", "n_clicks"),
    State("ml-tutorial-offcanvas", "is_open"),
    prevent_initial_call=True
)
def toggle_tutorial(n1, is_open):
    if n1:
        return not is_open
    return is_open

# 动态显隐参数面板 (分类)
@callback(
    Output("wrap-param-n-est", "style"),
    Output("wrap-param-max-depth", "style"),
    Output("wrap-param-c", "style"),
    Output("wrap-param-kernel", "style"),
    Output("wrap-param-lr-c", "style"),
    Output("wrap-param-k", "style"),
    Input("ml-classifier", "value")
)
def toggle_clf_params(algo):
    d_block, d_none = {"display": "block"}, {"display": "none"}
    if algo in ["rf_clf", "gbm_clf"]:
        return d_block, d_block, d_none, d_none, d_none, d_none
    elif algo == "svm_clf":
        return d_none, d_none, d_block, d_block, d_none, d_none
    elif algo == "lr_clf":
        return d_none, d_none, d_none, d_none, d_block, d_none
    elif algo == "knn_clf":
        return d_none, d_none, d_none, d_none, d_none, d_block
    return d_none, d_none, d_none, d_none, d_none, d_none

# 动态显隐参数面板 (回归)
@callback(
    Output("wrap-param-reg-n-est", "style"),
    Output("wrap-param-reg-max-depth", "style"),
    Output("wrap-param-alpha", "style"),
    Output("wrap-param-svr-c", "style"),
    Input("ml-regressor", "value")
)
def toggle_reg_params(algo):
    d_block, d_none = {"display": "block"}, {"display": "none"}
    if algo in ["rf_reg", "gbm_reg"]:
        return d_block, d_block, d_none, d_none
    elif algo == "ridge_reg":
        return d_none, d_none, d_block, d_none
    elif algo == "svr_reg":
        return d_none, d_none, d_none, d_block
    return d_none, d_none, d_none, d_none

# 动态显隐参数面板 (聚类)
@callback(
    Output("wrap-param-n-clusters", "style"),
    Output("wrap-param-eps", "style"),
    Input("ml-cluster-algo", "value")
)
def toggle_cluster_params(algo):
    d_block, d_none = {"display": "block"}, {"display": "none"}
    if algo == "kmeans" or algo == "agg":
        return d_block, d_none
    elif algo == "dbscan":
        return d_none, d_block
    return d_none, d_none

# 保存聚类参数到 Store (解决由上层 display:none 导致拿不到内层状态)
@callback(
    Output("ml-cluster-params-store", "data"),
    Input("ml-cluster-algo", "value"),
    Input("param-n-clusters", "value"),
    Input("param-eps", "value"),
    prevent_initial_call=True
)
def store_cluster_params(algo, k, eps):
    return {"algorithm": algo, "n_clusters": k, "eps": eps}

# 自动填充时序时间列下拉选项
@callback(
    Output("param-ts-timecol", "options"),
    Input("ml-columns-store", "data")
)
def populate_timecol(cols_data):
    if not cols_data:
        return []
    # 如果具备识别出的特定类型的话更好，目前全量提供
    return [{"label": c, "value": c} for c in cols_data.get("all", [])]


# =====================================================================
# 2. 核心训练回调 (整合聚类)
# =====================================================================

@callback(
    Output("ml-train-status", "children"),
    Output("ml-result-store", "data"),
    Output("ml-eval-tabs", "active_tab"),
    Input("btn-ml-train", "n_clicks"),
    State("ml-algo-tabs", "active_tab"),
    State("ml-target-var", "value"),
    State("ml-feature-vars", "value"),
    State("ml-impute-strategy", "value"),
    State("ml-scaler", "value"),
    State("ml-test-size", "value"),
    State("ml-classifier", "value"),
    State("ml-regressor", "value"),
    State("ml-ts-algo", "value"),
    State("param-ts-timecol", "value"),
    State("param-ts-horizon", "value"),
    State("param-ts-ci", "value"),
    State("ml-cluster-params-store", "data"), # 读取 Store 而不是直接读取隐藏控件
    # 读取所有可能存在的 params（存在一些可能为 None，需要在内部做处理）
    State("param-n-est", "value"), State("param-max-depth", "value"),
    State("param-c", "value"), State("param-kernel", "value"), State("param-lr-c", "value"), State("param-k", "value"),
    State("param-reg-n-est", "value"), State("param-reg-max-depth", "value"), State("param-alpha", "value"), State("param-svr-c", "value"),
    prevent_initial_call=True
)
def train_model(
    n_clicks, active_tab, target, features, imputer_strat, scaler_type, test_size,
    clf_algo, reg_algo, ts_algo, ts_timecol, ts_horizon, ts_ci, cluster_params,
    n_est, max_depth, c_val, kernel, lr_c, k_val,
    reg_n_est, reg_max_depth, alpha, svr_c
):
    if not HAS_SKLEARN:
        return dbc.Alert("未安装 scikit-learn", color="danger"), no_update, no_update
    if not features:
        return dbc.Alert("请至少选择一个特征变量(X)", color="warning", className="p-2 text-center", style={"fontSize":"0.8rem"}), no_update, no_update
    
    dm = DataManager()
    df = dm.active_df
    
    # 构建训练数据
    try:
        X = df[features].copy()
        # 预处理：填补缺失值
        if imputer_strat == "drop":
            if target and active_tab != "tab-cluster":
                valid_idx = df[features + [target]].dropna().index
                X = X.loc[valid_idx]
                y = df.loc[valid_idx, target].copy()
            else:
                valid_idx = X.dropna().index
                X = X.loc[valid_idx]
                y = None
        else:
            num_cols = X.select_dtypes(include=np.number).columns
            if len(num_cols) > 0:
                imp = SimpleImputer(strategy=imputer_strat)
                X[num_cols] = imp.fit_transform(X[num_cols])
            cat_cols = X.select_dtypes(exclude=np.number).columns
            if len(cat_cols) > 0:
                imp_cat = SimpleImputer(strategy="most_frequent")
                X[cat_cols] = imp_cat.fit_transform(X[cat_cols])
            
            if target and active_tab != "tab-cluster":
                y = df[target].copy()
                valid_idx = y.dropna().index
                X = X.loc[valid_idx]
                y = y.loc[valid_idx]
            else:
                y = None

        # 分类变量编码
        X_encoded = pd.get_dummies(X, drop_first=True)
        feature_names = X_encoded.columns.tolist()

        # 聚类流程 
        if active_tab == "tab-cluster":
            # 缩放
            if scaler_type == "standard":
                X_scaled = StandardScaler().fit_transform(X_encoded)
            elif scaler_type == "minmax":
                X_scaled = MinMaxScaler().fit_transform(X_encoded)
            else:
                X_scaled = X_encoded.values
            
            algo = cluster_params.get("algorithm", "kmeans")
            eps = float(cluster_params.get("eps") or 0.5)
            k = int(cluster_params.get("n_clusters") or 3)

            if algo == "kmeans":
                model = KMeans(n_clusters=k, random_state=42, n_init="auto")
                labels = model.fit_predict(X_scaled)
            elif algo == "dbscan":
                model = DBSCAN(eps=eps)
                labels = model.fit_predict(X_scaled)
            else:
                model = AgglomerativeClustering(n_clusters=k)
                labels = model.fit_predict(X_scaled)

            # PCA 降维用于可视化
            n_features = X_scaled.shape[1]
            if n_features >= 2:
                pca = PCA(n_components=2)
                coords = pca.fit_transform(X_scaled)
                coords_x = coords[:,0].tolist()
                coords_y = coords[:,1].tolist()
                pca_var = pca.explained_variance_ratio_.tolist()
            else:
                coords_x = X_scaled[:,0].tolist()
                coords_y = [0] * len(coords_x)
                pca_var = [1.0, 0.0]

            result = {
                "task": "clustering",
                "algo": algo,
                "n_clusters": len(np.unique(labels)),
                "n_noise": int(np.sum(labels == -1)) if algo == "dbscan" else 0,
                "labels": labels.tolist(),
                "coords_x": coords_x,
                "coords_y": coords_y,
                "pca_var": pca_var
            }
            return dbc.Alert("聚类完成", color="success", className="p-2 text-center", style={"fontSize":"0.8rem"}), result, "tab-overview"

        # 监督学习/时序预测 必须选 y
        if target is None:
            return dbc.Alert("时序/分类/回归需选择目标变量(Y)作为预测对象", color="warning", className="p-2 text-center", style={"fontSize":"0.8rem"}), no_update, no_update
            
        # -----------------------------
        # 新增的时序预测 (Time Series)
        # -----------------------------
        if active_tab == "tab-ts":
            if not ts_timecol:
                return dbc.Alert("请选择时间列", color="warning", className="p-2 text-center", style={"fontSize":"0.8rem"}), no_update, no_update
            try:
                # 只取有用的列并排序
                df_ts = df[[ts_timecol, target]].copy()
                df_ts[ts_timecol] = pd.to_datetime(df_ts[ts_timecol])
                df_ts = df_ts.dropna().sort_values(by=ts_timecol)
                
                # 提取 X(时间序号) 和 y(目标值)
                time_series = df_ts[ts_timecol].values
                y_series = df_ts[target].values
                X_ts = np.arange(len(y_series)).reshape(-1, 1)
                
                # 基线建模 
                if ts_algo == "ts_linear":
                    from sklearn.linear_model import LinearRegression
                    model = LinearRegression()
                else: 
                    from sklearn.ensemble import RandomForestRegressor
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    
                model.fit(X_ts, y_series)
                
                # 推断未来 Horizon
                horizon = int(ts_horizon or 10)
                ci_pct = float((ts_ci or 95) / 100.0)
                
                X_future = np.arange(len(y_series), len(y_series) + horizon).reshape(-1, 1)
                y_pred_future = model.predict(X_future)
                y_pred_history = model.predict(X_ts)
                
                # 计算粗略置信区间（基于历史残差的标准差展开）
                residuals = y_series - y_pred_history
                std_resid = np.std(residuals)
                # 使用正态分布分位数逼近 (95% -> 1.96, 90% -> 1.64 等)
                import scipy.stats as stats
                z_score = stats.norm.ppf(1 - (1 - ci_pct) / 2)
                margin_of_error = z_score * std_resid
                
                lower_bound = (y_pred_future - margin_of_error).tolist()
                upper_bound = (y_pred_future + margin_of_error).tolist()
                
                # 生成未来的时间戳（简单按历史平均周期间隔向后推断，或直接用pd.date_range预测频率） 
                # 这里做简单的时间差等差推演
                mean_delta = df_ts[ts_timecol].diff().mean()
                future_dates = [time_series[-1] + mean_delta * i for i in range(1, horizon + 1)]
                
                # 转回字符串方便 JSON
                history_dates_str = [str(x)[:10] for x in time_series]
                future_dates_str = [str(x)[:10] for x in future_dates]

                # 回顾验证衡量指标（在训练集上的拟合优度）
                metrics = calculate_reg_metrics(y_series, y_pred_history)
                
                result = {
                    "task": "timeseries",
                    "algo": ts_algo,
                    "target_name": target,
                    "metrics": metrics,
                    "horizon": horizon,
                    "ci_pct": ts_ci,
                    "history_dates": history_dates_str,
                    "history_y": y_series.tolist(),
                    "history_pred": y_pred_history.tolist(),
                    "future_dates": future_dates_str,
                    "future_pred": y_pred_future.tolist(),
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "features_selected": [ts_timecol] 
                }
                return dbc.Alert("时序预测完成", color="success", className="p-2 text-center", style={"fontSize":"0.8rem"}), result, "tab-overview"
            except Exception as e:
                import traceback
                traceback.print_exc()
                return dbc.Alert(f"时间列解析或预测失败: {str(e)}", color="danger"), no_update, no_update

        # 分类或回归流程
        is_classification = active_tab == "tab-clf"
        
        # 切分数据集
        X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=test_size, random_state=42)

        # 缩放
        scaler = None
        if scaler_type == "standard":
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
        elif scaler_type == "minmax":
            scaler = MinMaxScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
        
        # 训练
        if is_classification:
            # 自动处理 Y 类型 (确保为 str/int 等，不是 obj list)
            y_train = y_train.astype(str)
            y_test = y_test.astype(str)
            
            params = {
                "n_estimators": n_est, "max_depth": max_depth,
                "C": c_val if clf_algo == "svm_clf" else lr_c,
                "kernel": kernel, "k": k_val
            }
            model = build_classifier(clf_algo, params)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            metrics = calculate_clf_metrics(y_test, y_pred)
            
            # 特征重要性
            importances = []
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_[0]).tolist()
            
            # 混淆矩阵与报告
            cm = confusion_matrix(y_test, y_pred).tolist()
            classes = np.unique(np.concatenate((y_test, y_pred))).tolist()
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            
            update_cached_model_context(model, scaler, imp if 'imp' in locals() else None, imp_cat if 'imp_cat' in locals() else None, features, target)

            result = {
                "task": "classification",
                "algo": clf_algo,
                "metrics": metrics,
                "importances": importances,
                "feature_names": feature_names,
                "cm": cm,
                "classes": classes,
                "report": report,
                "y_test": y_test.tolist(),
                "y_pred": y_pred.tolist(),
                "features_selected": features
            }
        else: # 回归
            y_train = pd.to_numeric(y_train, errors='coerce').fillna(0)
            y_test = pd.to_numeric(y_test, errors='coerce').fillna(0)
            params = {
                "n_estimators": reg_n_est, "max_depth": reg_max_depth,
                "alpha": alpha, "C": svr_c
            }
            model = build_regressor(reg_algo, params)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            metrics = calculate_reg_metrics(y_test, y_pred)
            
            # 特征重要性
            importances = []
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_).tolist()
                importances = [float(x) for x in np.nditer(importances)] # 压平
                
            update_cached_model_context(model, scaler, imp if 'imp' in locals() else None, imp_cat if 'imp_cat' in locals() else None, features, target)

            result = {
                "task": "regression",
                "algo": reg_algo,
                "metrics": metrics,
                "importances": importances[:len(feature_names)],
                "feature_names": feature_names,
                "y_test": y_test.tolist(),
                "y_pred": y_pred.tolist(),
                "features_selected": features
            }
            
        return dbc.Alert("训练成功", color="success", className="p-2 text-center", style={"fontSize":"0.8rem"}), result, "tab-overview"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"错误: {str(e)}", color="danger", className="p-2", style={"fontSize":"0.75rem", "maxHeight": "100px", "overflowY": "auto"}), no_update, no_update


# =====================================================================
# 3. 渲染评估面板
# =====================================================================

@callback(
    Output("ml-kpi-row", "children"),
    Output("ml-tab-content", "children"),
    Input("ml-result-store", "data"),
    Input("ml-eval-tabs", "active_tab"),
    prevent_initial_call=True
)
def render_results(res, tab):
    if not res:
        return [], empty_placeholder()

    task = res.get("task")
    
    # --- 聚类结果渲染 ---
    if task == "clustering":
        if tab == "tab-overview":
            fig = px.scatter(
                x=res["coords_x"], y=res["coords_y"], color=[str(c) for c in res["labels"]],
                title="PCA 2D 聚类散点图" if res["pca_var"][1] > 0 else "1D 聚类散点图", 
                labels={"x": f"PC1 ({res['pca_var'][0]:.1%})", "y": f"PC2 ({res['pca_var'][1]:.1%})"}
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40))
            
            # AI解读
            interp = [
                html.P(f"算法成功将数据分为了 {res['n_clusters']} 个群体。主成分分析保留了 {sum(res['pca_var']):.1%} 的原始信息空间。"),
                html.P(f"包含被认定为噪声无法分类的离群点：{res['n_noise']} 个。" if res['n_noise'] > 0 else "没有发现明显的离群噪声点。")
            ]
            content = html.Div([
                dcc.Graph(figure=fig),
                result_interpretation_card(interp, icon="bi-pie-chart", color="#8B5CF6")
            ])
            return [
                kpi_card("算法", res["algo"].upper(), "选定算法", ACCENT_COLORS["purple"], "bi-cpu"),
                kpi_card("聚类簇数", str(res["n_clusters"]), "分类数目", ACCENT_COLORS["blue"], "bi-diagram-3"),
                kpi_card("噪声点", str(res["n_noise"]), "DBSCAN专有", ACCENT_COLORS["red"], "bi-bug"),
                kpi_card("投影维度", "2D" if res["pca_var"][1] > 0 else "1D", "PCA降维", ACCENT_COLORS["green"], "bi-arrows-collapse"),
            ], content
        return [], empty_placeholder("未提供聚类的详细报告或请切换到【综合评估】标签")

    # --- 评价指标卡片 ---
    m = res["metrics"]
    if task == "classification":
        kpis = [
            kpi_card("准确率 (Accuracy)", f"{m['accuracy']:.1%}", "总体预测正确的比例", ACCENT_COLORS["blue"], "bi-check2-circle"),
            kpi_card("F1 分数", f"{m['f1']:.3f}", f"调和平均 ({m['avg_type']})", ACCENT_COLORS["green"], "bi-star-fill"),
            kpi_card("精确率 (Precision)", f"{m['precision']:.1%}", "预测为正样本中实际为正的比例", ACCENT_COLORS["purple"], "bi-bullseye"),
            kpi_card("召回率 (Recall)", f"{m['recall']:.1%}", "实际为正样本中被预测出来的比例", ACCENT_COLORS["orange"], "bi-arrow-repeat"),
        ]
    elif task == "regression":
        kpis = [
            kpi_card("决定系数 (R²)", f"{m['r2']:.3f}", "越高越好 (最佳为1)", ACCENT_COLORS["blue"], "bi-graph-up"),
            kpi_card("均方根误差 (RMSE)", f"{m['rmse']:.2f}", "越低越好，极值敏感", ACCENT_COLORS["red"], "bi-rulers"),
            kpi_card("平均绝对误差 (MAE)", f"{m['mae']:.2f}", "绝对误差的均值，越低越好", ACCENT_COLORS["orange"], "bi-bar-chart"),
            kpi_card("相对百分比误差 (MAPE)", f"{m['mape']:.1f}%", "相对预测偏差", ACCENT_COLORS["purple"], "bi-percent"),
        ]
    elif task == "timeseries":
        kpis = [
            kpi_card("预测地平线", f"{res['horizon']} 步", "向未来的预测步长", ACCENT_COLORS["blue"], "bi-calendar-range"),
            kpi_card("置信区间", f"{res['ci_pct']}%", "预测结果的可靠围度", ACCENT_COLORS["purple"], "bi-shield-check"),
            kpi_card("历史拟合误差 (MAE)", f"{m['mae']:.2f}", "绝对误差", ACCENT_COLORS["orange"], "bi-bar-chart"),
            kpi_card("相对百分比误差 (MAPE)", f"{m['mape']:.1f}%", "相对预测偏差", ACCENT_COLORS["red"], "bi-percent"),
        ]

    # --- Tab 渲染 ---
    content = empty_placeholder()
    if tab == "tab-overview":
        if task == "classification":
            cm = np.array(res["cm"])
            fig = px.imshow(cm, x=res["classes"], y=res["classes"], text_auto=True, color_continuous_scale="Blues", aspect="auto")
            fig.update_layout(title="混淆矩阵 (对角线为预测正确数量)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            
            # 智能解读逻辑
            best_idx = np.unravel_index(np.argmax(cm - np.diag(np.diag(cm)) - 99999*np.eye(len(cm))), cm.shape) if len(cm)>1 else (0,0)
            interp = [
                html.P(f"👉 模型整体预测准确率达到了 {m['accuracy']:.1%}。在业务上这意味着：每预测 100 次，模型能正确预测 {int(m['accuracy']*100)} 次。"),
                html.P(f"💡 最容易混淆的地方在哪里？根据混淆矩阵，模型最容易把「{res['classes'][best_idx[0]]}」预测成「{res['classes'][best_idx[1]]}」。如果你想要提高准确率，建议增加这两类的数据，提供区分它们的特征变量。") if len(cm)>1 else html.Span(),
            ]
            content = html.Div([dcc.Graph(figure=fig), result_interpretation_card(interp, color=ACCENT_COLORS["blue"])])
            
        elif task == "regression":
            df_plot = pd.DataFrame({"Actual": res["y_test"], "Predicted": res["y_pred"]})
            fig = px.scatter(df_plot, x="Actual", y="Predicted", opacity=0.6)
            # 添加完美预测对角线
            min_val, max_val = df_plot.min().min(), df_plot.max().max()
            fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="red", dash="dash"))
            fig.update_layout(title="真实值 vs 预测值 (越贴近红虚线预测越准)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            
            interp = [
                html.P(f"👉 模型对结果解释力度 R² 为 {m['r2']:.2f}。在业务上这意味着：目标变量 {m['r2']:.1%} 的波动变化可以被你选定的 {len(res['features_selected'])} 个特征解释。"),
                html.P(f"💡 我们的模型预测平均绝对误差(MAE)为 {m['mae']:.2f}，百分比误差为 {m['mape']:.1f}%。说明真实业务落地时，系统预测的数值平均偏离现实环境约 {m['mape']:.1f}%。"),
            ]
            content = html.Div([dcc.Graph(figure=fig), result_interpretation_card(interp, color=ACCENT_COLORS["blue"])])

        elif task == "timeseries":
            # 构建时序预测图表 
            hist_dates = res["history_dates"]
            fut_dates = res["future_dates"]
            
            fig = go.Figure()
            # 历史真实值
            fig.add_trace(go.Scatter(x=hist_dates, y=res["history_y"], mode="lines", name="历史真实值", line=dict(color=ACCENT_COLORS["blue"])))
            # 未来预测值
            fig.add_trace(go.Scatter(x=fut_dates, y=res["future_pred"], mode="lines", name="预测值", line=dict(color=ACCENT_COLORS["orange"], dash="dash")))
            
            # 置信区间绘制 (高低边界闭合形状)
            x_ci = fut_dates + fut_dates[::-1]
            y_ci = res["upper_bound"] + res["lower_bound"][::-1]
            fig.add_trace(go.Scatter(
                x=x_ci, y=y_ci, fill="toself", fillcolor="rgba(245, 158, 11, 0.2)",
                line=dict(color="rgba(255,255,255,0)"), hoverinfo="skip", showlegend=True, name=f"{res['ci_pct']}% 置信区间"
            ))
            
            fig.update_layout(title=f"【{res['target_name']}】时序预测走势分析", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
            
            interp = [
                html.P(f"👉 模型已基于历史规律生成了未来 {res['horizon']} 个步长的走势预测。橙色阴影区域代表 {res['ci_pct']}% 的统计学置信区间。"),
                html.P(f"💡 注意：当前展现结果是由 {res['algo']} 基线模型生成的外推近似解，适合趋势判断参考，请注意业务层面的潜在黑天鹅事件影响。")
            ]
            content = html.Div([dcc.Graph(figure=fig), result_interpretation_card(interp, icon="bi-graph-up-arrow", color=ACCENT_COLORS["orange"])])

    elif tab == "tab-feature":
        imps = res.get("importances", [])
        if not imps:
            content = empty_placeholder("该算法不提供特征重要性（请尝试随机森林或线性回归）")
        else:
            df_imp = pd.DataFrame({"Feature": res["feature_names"], "Importance": imps}).sort_values("Importance", ascending=True).tail(15)
            fig = px.bar(df_imp, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale="Purples")
            fig.update_layout(title="对预测结果影响最大的特征 Top 15", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            
            top_feat = df_imp.iloc[-1]["Feature"] if len(df_imp)>0 else ""
            interp = [html.P(f"👉 根据模型归因分析，最重要的特征是「{top_feat}」。如果你想干预预测结果，应该优先研究该变量对业务的影响。")]
            content = html.Div([dcc.Graph(figure=fig), result_interpretation_card(interp, icon="bi-key", color=ACCENT_COLORS["purple"])])

    elif tab == "tab-report":
        if task == "classification":
            rep = res["report"]
            df_rep = pd.DataFrame(rep).T.round(3).reset_index().rename(columns={"index": "类别/指标"})
            table = dbc.Table.from_dataframe(df_rep, striped=True, bordered=True, hover=True, size="sm", className="mt-3")
            content = html.Div([html.H6("完整分类报告"), table])
        elif task == "regression":
            y_test = np.array(res["y_test"])
            y_pred = np.array(res["y_pred"])
            res_err = y_test - y_pred 
            fig = px.histogram(res_err, nbins=30, title="预测残差分布 (应大致符合正态分布且居中于0)")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            content = html.Div([dcc.Graph(figure=fig)])
        elif task == "timeseries":
            # 时序在详细报告页可以给表格形式的预估结果
            df_future = pd.DataFrame({
                "未来日期": res["future_dates"], 
                "预测中轴值": np.round(res["future_pred"], 4),
                "估算下沿": np.round(res["lower_bound"], 4),
                "估算上沿": np.round(res["upper_bound"], 4)
            })
            table = dbc.Table.from_dataframe(df_future, striped=True, bordered=True, hover=True, size="sm", className="mt-3")
            content = html.Div([
                html.H6(f"未来 {res['horizon']} 步的详细预估数据表", className="text-primary"), 
                html.P("以下为基于时序引擎产生的确定性预测截面数据：", style={"fontSize": "0.85rem", "color": "var(--text-secondary)"}),
                table
            ])

    elif tab == "tab-predict":
        # 预测特征控件列表
        inputs = []
        for feat in res["features_selected"]:
            inputs.append(html.Div([
                html.Label(feat, style={"fontSize": "0.8rem", "color": "var(--text-secondary)"}),
                dcc.Input(id={"type": "ml-predict-input", "index": feat}, type="text", placeholder=f"输入 {feat}...", className="form-control form-control-sm mb-2")
            ], className="mb-2"))
        
        btn = dbc.Button("执行单样本预测", id="btn-execute-predict", color="primary", outline=True, size="sm", className="mt-2 w-100")
        btn_batch = dbc.Button("🚀 对当前数据集执行全量预测", id="btn-batch-predict", color="success", size="sm", className="mt-4 w-100")
        output_div = html.Div(id="ml-predict-result", style={"marginTop": "20px"})
        batch_out = html.Div(id="ml-batch-result", className="mt-2")
        
        content = dbc.Row([
            dbc.Col([html.H6("填入新样本参数(预览版支持全数值及简单结构)"), *inputs, btn, html.Hr(), btn_batch, batch_out], width=5),
            dbc.Col([output_div], width=7)
        ])

    return kpis, content


# 真实执行模型预测并通过对齐特征生成结果
@callback(
    Output("ml-predict-result", "children"),
    Input("btn-execute-predict", "n_clicks"),
    State({"type": "ml-predict-input", "index": ALL}, "value"),
    State({"type": "ml-predict-input", "index": ALL}, "id"),
    State("ml-result-store", "data"),
    prevent_initial_call=True
)
def execute_prediction(n_clicks, input_values, input_ids, res):
    if not res or not n_clicks: return no_update
    
    ctx_model = get_cached_model_context()
    model = ctx_model.get("latest_model")
    scaler = ctx_model.get("scaler")
    
    if not model:
        return dbc.Alert("内存缓存已被释放或未训练模型，请返回配置部分重新点击【开始训练模型】！", color="danger", className="p-2")

    task = res.get("task")
    try:
        # 重组测试帧
        input_dict = {iid["index"]: (val if val not in [None, ""] else np.nan) for iid, val in zip(input_ids, input_values)}
        df_new = pd.DataFrame([input_dict])
        
        # 类别编码映射与特征对齐
        df_encoded = pd.get_dummies(df_new)
        # 用训练时得到的列强行对齐，找不到的列用0补齐（处理没出现的分类字典）
        train_cols = res.get("feature_names", [])
        for col in train_cols:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[train_cols] # 确保完全按序
        
        # 强制转换为数值类型做兼容
        df_encoded = df_encoded.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # 伸缩还原
        if scaler:
            df_scaled = scaler.transform(df_encoded)
        else:
            df_scaled = df_encoded.values
            
        # 推断
        pred = model.predict(df_scaled)[0]
        
        # UI块组装
        proba_ui = html.Div()
        if task == "classification" and hasattr(model, "predict_proba"):
            probs = model.predict_proba(df_scaled)[0]
            # 找到对应概率分布
            classes_arr = model.classes_
            prob_items = []
            for cls_name, prob in zip(classes_arr, probs):
                prob_items.append(html.Div([
                    html.Span(f"{cls_name} : ", style={"fontWeight": "600", "fontSize": "0.85rem"}),
                    dbc.Progress(value=prob*100, label=f"{prob:.1%}", style={"height": "16px", "fontSize": "0.7rem", "backgroundColor": "var(--bg-primary)"})
                ], className="mb-2"))
                
            proba_ui = html.Div([
                html.Hr(style={"margin": "10px 0"}),
                html.H6("概率分布 (Confidence)", style={"fontSize": "0.85rem", "color": "var(--text-secondary)"}),
                *prob_items
            ])

        return html.Div([
            html.Div([
                html.I(className="bi bi-robot me-2", style={"fontSize": "1.3rem", "color": ACCENT_COLORS["green"]}),
                html.Span("模型研判结果", style={"fontWeight": "600"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
            
            html.Div(f"{pred}", style={
                "fontSize": "2rem", "fontWeight": "700", "color": ACCENT_COLORS["blue"],
                "textAlign": "center", "marginBottom": "10px",
                "padding": "10px", "backgroundColor": f"rgba({_hex_to_rgba(ACCENT_COLORS['blue'])}, 0.1)", "borderRadius": "8px"
            }),
            
            proba_ui
        ], className="p-3 border rounded", style={"backgroundColor": "var(--bg-secondary)", "boxShadow": "0 2px 8px rgba(0,0,0,0.05)"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"输入格式解析/推理失败，请检查输入参数是否合法！错误信息：{str(e)}", color="danger")

# 批量执行模型推断并在 DataManager 内落表
@callback(
    Output("ml-batch-result", "children"),
    Input("btn-batch-predict", "n_clicks"),
    State("ml-result-store", "data"),
    prevent_initial_call=True
)
def execute_batch_prediction(n_clicks, res):
    if not res or not n_clicks: return no_update
    
    ctx_model = get_cached_model_context()
    model = ctx_model.get("latest_model")
    scaler = ctx_model.get("scaler")
    task = res.get("task")
    
    if not model or task == "timeseries":
        return dbc.Alert("批量推理仅限持有内存模型实例的分类/回归任务使用！", color="warning", className="p-2")
        
    try:
        dm = DataManager()
        df = dm.active_df.copy()
        
        train_cols = res.get("feature_names", [])
        raw_features = res.get("features_selected", [])
        
        # 提取并处理原始特征列
        df_sub = df[raw_features].copy()
        # 强制数值及简单缺值填充
        df_sub = df_sub.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        df_encoded = pd.get_dummies(df_sub)
        for col in train_cols:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[train_cols]
        
        if scaler:
            df_scaled = scaler.transform(df_encoded)
        else:
            df_scaled = df_encoded.values
            
        preds = model.predict(df_scaled)
        # 写回原有 DataFrame
        col_name = f"{res['target_name']}_pred" if res.get("target_name") else "ML_Predict_Result"
        df[col_name] = preds
        
        dm.update_active_dataset(df, snapshot=True)
        return dbc.Alert(f"全量预测完成！已新增 '{col_name}' 列，请前往数据工坊查看。", color="success", className="p-2")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"批量推理失败: {str(e)}", color="danger", className="p-2")

def _hex_to_rgba(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    if len(h) != 6: return "0,0,0"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"
