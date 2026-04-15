# -*- coding: utf-8 -*-
"""Configuration for ML Studio."""

from __future__ import annotations

from pathlib import Path


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

CLASSIFIER_OPTIONS = [
    {"label": "随机森林 Random Forest", "value": "rf_clf"},
    {"label": "梯度提升 Gradient Boosting", "value": "gbm_clf"},
    {"label": "支持向量机 SVM", "value": "svm_clf"},
    {"label": "逻辑回归 Logistic Regression", "value": "lr_clf"},
    {"label": "K 近邻 KNN", "value": "knn_clf"},
    {"label": "决策树 Decision Tree", "value": "dt_clf"},
]

REGRESSOR_OPTIONS = [
    {"label": "随机森林回归 Random Forest", "value": "rf_reg"},
    {"label": "梯度提升回归 Gradient Boosting", "value": "gbm_reg"},
    {"label": "线性回归 Linear Regression", "value": "lr_reg"},
    {"label": "岭回归 Ridge Regression", "value": "ridge_reg"},
    {"label": "支持向量回归 SVR", "value": "svr_reg"},
]

CLUSTER_OPTIONS = [
    {"label": "K-Means 聚类", "value": "kmeans"},
    {"label": "DBSCAN", "value": "dbscan"},
    {"label": "层次聚类 Agglomerative", "value": "agg"},
]

TRAINING_MODE_OPTIONS = [
    {"label": "快速训练：先拿到可读结果", "value": "quick"},
    {"label": "交叉验证：更稳的离线评估", "value": "cv"},
    {"label": "随机搜索：自动尝试多组参数", "value": "random_search"},
]

CV_STRATEGY_OPTIONS = [
    {"label": "留出验证 Holdout", "value": "holdout"},
    {"label": "K 折交叉验证", "value": "kfold"},
    {"label": "分层 K 折（分类更稳）", "value": "stratified_kfold"},
]

PRIMARY_METRIC_OPTIONS = {
    "classification": [
        {"label": "F1 加权", "value": "f1_weighted"},
        {"label": "准确率 Accuracy", "value": "accuracy"},
        {"label": "精确率加权", "value": "precision_weighted"},
        {"label": "召回率加权", "value": "recall_weighted"},
    ],
    "regression": [
        {"label": "RMSE 均方根误差", "value": "rmse"},
        {"label": "MAE 平均绝对误差", "value": "mae"},
        {"label": "R2", "value": "r2"},
        {"label": "MAPE", "value": "mape"},
    ],
}

ALGORITHM_LABELS = {
    "rf_clf": "随机森林 Random Forest",
    "gbm_clf": "梯度提升 Gradient Boosting",
    "svm_clf": "支持向量机 SVM",
    "lr_clf": "逻辑回归 Logistic Regression",
    "knn_clf": "K 近邻 KNN",
    "dt_clf": "决策树 Decision Tree",
    "rf_reg": "随机森林回归 Random Forest",
    "gbm_reg": "梯度提升回归 Gradient Boosting",
    "lr_reg": "线性回归 Linear Regression",
    "ridge_reg": "岭回归 Ridge Regression",
    "svr_reg": "支持向量回归 SVR",
    "kmeans": "K-Means 聚类",
    "dbscan": "DBSCAN",
    "agg": "层次聚类 Agglomerative",
    "ts_linear": "线性趋势基线",
    "ts_rf": "随机森林时序基线",
    "ts_arima": "AR-like 基线",
}

TASK_LABELS = {
    "classification": "分类任务",
    "regression": "回归任务",
    "clustering": "聚类任务",
    "timeseries": "时间序列任务",
}

DEFAULT_PRIMARY_METRIC = {
    "classification": "f1_weighted",
    "regression": "rmse",
}

TRAINING_MODE_LABELS = {
    "quick": "快速训练",
    "cv": "交叉验证",
    "random_search": "随机搜索",
}

CV_STRATEGY_LABELS = {
    "holdout": "留出验证",
    "kfold": "K 折交叉验证",
    "stratified_kfold": "分层 K 折交叉验证",
}

METRIC_LABELS = {
    "f1_weighted": "F1 加权",
    "accuracy": "准确率",
    "precision_weighted": "精确率加权",
    "recall_weighted": "召回率加权",
    "rmse": "RMSE",
    "mae": "MAE",
    "r2": "R2",
    "mape": "MAPE",
}

WORKFLOW_GUIDE_STEPS = [
    {
        "id": "01",
        "title": "先定目标",
        "description": "先选你要预测的列，再补 2-8 个最相关特征。目标列不要再放回特征里。",
    },
    {
        "id": "02",
        "title": "再选训练策略",
        "description": "先用快速训练跑通流程；结果稳定后，再切到交叉验证或随机搜索。",
    },
    {
        "id": "03",
        "title": "最后发布复用",
        "description": "训练完成先看总览与特征重要性，确认无误后再发布并做预测。",
    },
]

ALGORITHM_GUIDANCE = {
    "classification": {
        "rf_clf": {
            "title": "随机森林是分类任务的稳妥起点",
            "summary": "适合大多数表格数据，混合数值和类别特征时通常更省心。",
            "best_for": ["想先拿到可靠基线", "特征关系可能非线性", "不想一开始就精调参数"],
            "watchouts": ["模型体积通常更大", "解释性弱于线性模型"],
            "recommendation": "起步建议：先保留默认参数，重点确认目标列和特征是否合理。",
        },
        "gbm_clf": {
            "title": "梯度提升更适合追求更高分数",
            "summary": "通常比随机森林更吃调参，但在中等规模数据上可能给出更强表现。",
            "best_for": ["已经有稳定基线", "愿意多跑几轮验证", "关注最终分数而非训练速度"],
            "watchouts": ["训练更慢", "参数不合适时更容易过拟合"],
            "recommendation": "如果随机森林已经稳定，可再试梯度提升做对照。",
        },
        "svm_clf": {
            "title": "支持向量机适合边界清晰的小中型数据",
            "summary": "对特征缩放较敏感，样本量较大时训练成本会上升。",
            "best_for": ["样本量不大", "类别边界较明显", "愿意配合标准化"],
            "watchouts": ["大数据集训练较慢", "参数和核函数选择影响较大"],
            "recommendation": "只有在数据量不大且你愿意调 C / kernel 时再优先考虑。",
        },
        "lr_clf": {
            "title": "逻辑回归适合解释性优先场景",
            "summary": "当你需要快速解释各特征方向，逻辑回归往往比树模型更直观。",
            "best_for": ["需要可解释系数", "特征关系接近线性", "想要轻量可复用模型"],
            "watchouts": ["对复杂非线性关系表达有限", "对异常值更敏感"],
            "recommendation": "如果你的重点是业务解释而不是极限分数，可以先试逻辑回归。",
        },
        "knn_clf": {
            "title": "KNN 更像近邻投票基线",
            "summary": "实现直观，但对量纲和噪声敏感，更适合做快速对照。",
            "best_for": ["做简单基线比较", "特征数不多", "样本量较小"],
            "watchouts": ["预测阶段可能更慢", "对缩放和离群点敏感"],
            "recommendation": "只把它当对照模型，不建议作为默认长期方案。",
        },
        "dt_clf": {
            "title": "决策树容易解释，但单树稳定性一般",
            "summary": "规则路径清晰，适合教学或快速解释单条决策逻辑。",
            "best_for": ["需要可视化规则", "做业务演示", "想观察特征切分逻辑"],
            "watchouts": ["更容易过拟合", "通常不如随机森林稳"],
            "recommendation": "适合解释，不适合作为默认主力模型。",
        },
    },
    "regression": {
        "rf_reg": {
            "title": "随机森林回归适合多数非线性回归问题",
            "summary": "对表格数据容错较好，通常是数值预测任务的第一选择。",
            "best_for": ["价格/销量等非线性预测", "特征较多且关系复杂", "先建立稳妥基线"],
            "watchouts": ["模型较重", "外推能力弱于线性模型"],
            "recommendation": "先用它跑基线，再根据误差表现决定是否换更轻模型。",
        },
        "gbm_reg": {
            "title": "梯度提升回归偏向更高精度尝试",
            "summary": "在数据质量较好时常能进一步压低误差，但更依赖验证和调参。",
            "best_for": ["已经完成基线", "对误差更敏感", "可以接受更慢训练"],
            "watchouts": ["参数更多", "过拟合风险更高"],
            "recommendation": "建议在随机森林回归之后作为第二候选。",
        },
        "lr_reg": {
            "title": "线性回归适合线性关系和强解释场景",
            "summary": "训练快、易解释，适合先判断关系是否接近线性。",
            "best_for": ["需要解释影响方向", "关系较平滑", "想快速获得对照基线"],
            "watchouts": ["不擅长复杂非线性", "对异常值较敏感"],
            "recommendation": "如果你更看重解释性和速度，可以优先试它。",
        },
        "ridge_reg": {
            "title": "岭回归适合线性基线但特征较多的情况",
            "summary": "比普通线性回归更稳，尤其在特征相关性较高时更有帮助。",
            "best_for": ["特征较多且共线性明显", "想保留线性解释性", "需要更稳的线性基线"],
            "watchouts": ["仍然受限于线性表达能力", "需要关注 alpha 调整"],
            "recommendation": "当普通线性回归波动较大时，优先试岭回归。",
        },
        "svr_reg": {
            "title": "支持向量回归更适合小中型精细拟合",
            "summary": "对缩放和参数很敏感，不适合作为大数据默认方案。",
            "best_for": ["样本量不大", "想尝试更平滑边界", "可以接受多次调参"],
            "watchouts": ["训练慢", "参数选择不当时结果不稳定"],
            "recommendation": "仅在数据量较小、且你愿意细调参数时考虑。",
        },
    },
    "clustering": {
        "kmeans": {
            "title": "聚类仍保留基础模式",
            "summary": "Phase 1 只保留基础聚类入口，不纳入专业训练工作流。",
            "best_for": ["快速做用户分群原型", "样本结构相对规则"],
            "watchouts": ["需要你先假设簇数", "结果强依赖特征缩放"],
            "recommendation": "如需稳定聚类流程，建议放到下一阶段完善。",
        },
        "dbscan": {
            "title": "DBSCAN 适合发现密度簇与异常点",
            "summary": "当前仅保留基础入口，适合探索，不建议当作稳定产线流程。",
            "best_for": ["寻找异常点", "簇形状不规则"],
            "watchouts": ["参数 eps 很敏感", "高维下效果可能退化"],
            "recommendation": "先做探索分析，不建议在 Phase 1 深度依赖。",
        },
        "agg": {
            "title": "层次聚类适合小样本结构观察",
            "summary": "更偏分析型而不是高频生产型工作流。",
            "best_for": ["看层次结构", "小样本探索"],
            "watchouts": ["样本多时成本更高", "Phase 1 未做专业化补强"],
            "recommendation": "保留基础使用，稳定性增强放后续阶段。",
        },
    },
    "timeseries": {
        "ts_linear": {
            "title": "时间序列仍保留基础模式",
            "summary": "当前只提供轻量基线，不做复杂时序建模或自动推荐。",
            "best_for": ["看整体趋势", "快速做一个基线预测"],
            "watchouts": ["无法覆盖复杂季节性", "只适合基础场景"],
            "recommendation": "如果业务强依赖时序质量，建议后续单独治理。",
        },
        "ts_rf": {
            "title": "随机森林时序基线仍是实验入口",
            "summary": "目前只是基础能力，不代表完整时序工作流。",
            "best_for": ["做基线尝试", "探索滞后特征价值"],
            "watchouts": ["Phase 1 不提供完整引导", "结果解释成本更高"],
            "recommendation": "更适合探索，不适合当前阶段作为主流程。",
        },
        "ts_arima": {
            "title": "AR-like 基线用于快速对照",
            "summary": "提供轻量参考值，方便与你的其他方法做比较。",
            "best_for": ["简单趋势对照", "快速验证时序是否可预测"],
            "watchouts": ["能力有限", "未覆盖高级参数和诊断"],
            "recommendation": "把它当基础参考，而不是最终方案。",
        },
    },
}

ARTIFACT_ROOT = Path("artifacts") / "ml"
PROJECT_INDEX_FILE = ARTIFACT_ROOT / "project_index.json"
ARTIFACT_VERSION = 1


try:
    import sklearn  # noqa: F401
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
