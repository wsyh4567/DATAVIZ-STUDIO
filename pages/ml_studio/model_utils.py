# -*- coding: utf-8 -*-
"""机器学习核心工具函数"""
import numpy as np

try:
    from sklearn.ensemble import (
        RandomForestClassifier, RandomForestRegressor,
        GradientBoostingClassifier, GradientBoostingRegressor,
    )
    from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
    from sklearn.svm import SVC, SVR
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.metrics import (
        accuracy_score, f1_score, precision_score, recall_score,
        r2_score, mean_squared_error, mean_absolute_error,
    )
except ImportError:
    pass

# 全局内存级模型缓存，用于跨回调推断
_MODEL_CACHE = {
    "latest_model": None,
    "scaler": None,
    "imputer": None,
    "imputer_cat": None,
    "features": None,
    "target": None
}

def get_cached_model_context():
    return _MODEL_CACHE

def update_cached_model_context(model, scaler, imputer, imputer_cat, features, target):
    _MODEL_CACHE.update({
        "latest_model": model,
        "scaler": scaler,
        "imputer": imputer,
        "imputer_cat": imputer_cat,
        "features": features,
        "target": target
    })


def build_classifier(algo, params):
    n_est = int(params.get("n_estimators", 100))
    md = params.get("max_depth")
    md = int(md) if md and int(md) > 0 else None

    if algo == "rf_clf":
        return RandomForestClassifier(n_estimators=n_est, max_depth=md, random_state=42, n_jobs=-1)
    elif algo == "gbm_clf":
        return GradientBoostingClassifier(n_estimators=n_est, max_depth=md or 3, random_state=42)
    elif algo == "svm_clf":
        kernel = params.get("kernel", "rbf")
        c = float(params.get("C", 1.0))
        return SVC(C=c, kernel=kernel, probability=True, random_state=42)
    elif algo == "lr_clf":
        c = float(params.get("C", 1.0))
        return LogisticRegression(C=c, max_iter=1000, random_state=42)
    elif algo == "knn_clf":
        k = int(params.get("k", 5))
        return KNeighborsClassifier(n_neighbors=k)
    elif algo == "dt_clf":
        return DecisionTreeClassifier(max_depth=md, random_state=42)
    return RandomForestClassifier(random_state=42)


def build_regressor(algo, params):
    n_est = int(params.get("n_estimators", 100))
    md = params.get("max_depth")
    md = int(md) if md and int(md) > 0 else None

    if algo == "rf_reg":
        return RandomForestRegressor(n_estimators=n_est, max_depth=md, random_state=42, n_jobs=-1)
    elif algo == "gbm_reg":
        return GradientBoostingRegressor(n_estimators=n_est, max_depth=md or 3, random_state=42)
    elif algo == "lr_reg":
        return LinearRegression()
    elif algo == "ridge_reg":
        alpha = float(params.get("alpha", 1.0))
        return Ridge(alpha=alpha)
    elif algo == "svr_reg":
        kernel = params.get("kernel", "rbf")
        c = float(params.get("C", 1.0))
        return SVR(C=c, kernel=kernel)
    return LinearRegression()


def calculate_clf_metrics(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    
    # 无论几分类都使用 weighted 兼顾不平衡分布而且不会产生 pos_label=1 问题
    avg = "weighted"
    
    f1 = f1_score(y_true, y_pred, average=avg, zero_division=0)
    prec = precision_score(y_true, y_pred, average=avg, zero_division=0)
    rec = recall_score(y_true, y_pred, average=avg, zero_division=0)
    return {"accuracy": acc, "f1": f1, "precision": prec, "recall": rec, "avg_type": avg}


def calculate_reg_metrics(y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    # avoid division by zero
    y_true_safe = np.array(y_true) + 1e-10
    mape = np.mean(np.abs((np.array(y_true) - np.array(y_pred)) / y_true_safe)) * 100
    return {"r2": r2, "rmse": rmse, "mae": mae, "mape": mape}
