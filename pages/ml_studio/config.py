# -*- coding: utf-8 -*-
"""机器学习工作室常量配置"""

# 颜色常量
CARD_STYLE = {
    "backgroundColor": "var(--bg-secondary)",
    "border": "1px solid var(--border)",
    "borderRadius": "10px",
    "padding": "16px",
}

ACCENT_COLORS = {
    "blue": "#3B82F6",
    "green": "#10B981",
    "purple": "#8B5CF6",
    "orange": "#F59E0B",
    "red": "#EF4444",
    "cyan": "#06B6D4",
}

# 算法选项
CLASSIFIER_OPTIONS = [
    {"label": "🌲 随机森林 Random Forest", "value": "rf_clf"},
    {"label": "🚀 梯度提升 Gradient Boosting", "value": "gbm_clf"},
    {"label": "📐 支持向量机 SVM", "value": "svm_clf"},
    {"label": "📈 逻辑回归 Logistic Regression", "value": "lr_clf"},
    {"label": "🔍 K近邻 KNN", "value": "knn_clf"},
    {"label": "🌿 决策树 Decision Tree", "value": "dt_clf"},
]

REGRESSOR_OPTIONS = [
    {"label": "🌲 随机森林回归 Random Forest", "value": "rf_reg"},
    {"label": "🚀 梯度提升回归 Gradient Boosting", "value": "gbm_reg"},
    {"label": "📏 线性回归 Linear Regression", "value": "lr_reg"},
    {"label": "🔷 岭回归 Ridge Regression", "value": "ridge_reg"},
    {"label": "🛡 支持向量回归 SVR", "value": "svr_reg"},
]

CLUSTER_OPTIONS = [
    {"label": "🔵 K均值聚类 K-Means", "value": "kmeans"},
    {"label": "🌀 密度聚类 DBSCAN", "value": "dbscan"},
    {"label": "🌳 层次聚类 Agglomerative", "value": "agg"},
]

# 依赖检查标志
try:
    import sklearn
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
