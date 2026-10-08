import pandas as pd

from process.common import build_case_result, round_value

try:
    from sklearn.ensemble import RandomForestClassifier
except Exception:  # pragma: no cover
    RandomForestClassifier = None


RANDOM_STATE = 42
N_ESTIMATORS = 240
MAX_DEPTH = 6
MIN_SAMPLES_LEAF = 4


def _build_feature_frame(df, predict_days):
    working_df = df.copy()
    working_df["return_1d"] = working_df["close"].pct_change(1) * 100
    working_df["return_3d"] = working_df["close"].pct_change(3) * 100
    working_df["return_5d"] = working_df["close"].pct_change(5) * 100
    working_df["momentum_10d"] = working_df["close"].pct_change(10) * 100
    working_df["ma5"] = working_df["close"].rolling(5).mean()
    working_df["ma10"] = working_df["close"].rolling(10).mean()
    working_df["ma20"] = working_df["close"].rolling(20).mean()
    working_df["ma_gap_5"] = (working_df["close"] - working_df["ma5"]) / working_df["ma5"] * 100
    working_df["ma_gap_10"] = (working_df["close"] - working_df["ma10"]) / working_df["ma10"] * 100
    working_df["ma_gap_20"] = (working_df["close"] - working_df["ma20"]) / working_df["ma20"] * 100
    working_df["volatility_10d"] = working_df["close"].pct_change().rolling(10).std() * 100
    working_df["target_return"] = working_df["close"].shift(-predict_days) / working_df["close"] - 1
    working_df["target"] = working_df["target_return"].apply(lambda value: 1 if value > 0 else 0)

    feature_columns = [
        "return_1d",
        "return_3d",
        "return_5d",
        "momentum_10d",
        "ma_gap_5",
        "ma_gap_10",
        "ma_gap_20",
        "volatility_10d",
    ]
    modeling_df = working_df.dropna(subset=feature_columns + ["target"]).reset_index(drop=True)
    return modeling_df, feature_columns


def run_case(df, predict_days=1):
    if RandomForestClassifier is None:
        return build_case_result(
            "random_forest",
            "Random Forest 分类",
            "neutral",
            0,
            "当前环境未安装 scikit-learn，无法运行真实 Random Forest 分类。",
            {"predict_days": predict_days, "library": "scikit-learn", "available": False},
        )

    modeling_df, feature_columns = _build_feature_frame(df, predict_days)
    if modeling_df.empty:
        return build_case_result(
            "random_forest",
            "Random Forest 分类",
            "neutral",
            0,
            "历史特征不足，无法完成 Random Forest 分类。",
            {"predict_days": predict_days, "library": "scikit-learn", "available": True},
        )

    latest_features = modeling_df.iloc[-1][feature_columns].to_dict()
    training_df = modeling_df.iloc[:-1].copy() if len(modeling_df) > 1 else modeling_df.copy()
    if training_df.empty:
        training_df = modeling_df.copy()

    X_train = training_df[feature_columns]
    y_train = training_df["target"].astype(int)
    latest_frame = pd.DataFrame([latest_features], columns=feature_columns)

    if y_train.nunique() < 2:
        bullish_probability = 100.0 if int(y_train.iloc[0]) == 1 else 0.0
        feature_importance = {column: None for column in feature_columns}
    else:
        model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            min_samples_leaf=MIN_SAMPLES_LEAF,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample",
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        bullish_probability = float(model.predict_proba(latest_frame)[0][1]) * 100
        feature_importance = {
            column: round_value(importance * 100, 2)
            for column, importance in zip(feature_columns, model.feature_importances_)
        }

    bearish_probability = 100.0 - bullish_probability

    signal = "neutral"
    score = 0
    if bullish_probability >= 64:
        signal = "bullish"
        score = 2
    elif bullish_probability >= 56:
        signal = "bullish"
        score = 1
    elif bullish_probability <= 36:
        signal = "bearish"
        score = -2
    elif bullish_probability <= 44:
        signal = "bearish"
        score = -1

    summary = (
        f"基于 scikit-learn RandomForestClassifier 对 {len(training_df)} 条样本进行训练，"
        f"预测未来 {predict_days} 天上涨概率约为 {round_value(bullish_probability, 2)}%，"
        f"下跌概率约为 {round_value(bearish_probability, 2)}%，综合判断为{signal}。"
    )
    return build_case_result(
        "random_forest",
        "Random Forest 分类",
        signal,
        score,
        summary,
        {
            "predict_days": predict_days,
            "library": "scikit-learn",
            "available": True,
            "sample_size": len(training_df),
            "n_estimators": N_ESTIMATORS,
            "max_depth": MAX_DEPTH,
            "min_samples_leaf": MIN_SAMPLES_LEAF,
            "bullish_probability": round_value(bullish_probability, 2),
            "bearish_probability": round_value(bearish_probability, 2),
            "feature_snapshot": {key: round_value(value, 4) for key, value in latest_features.items()},
            "feature_importance": feature_importance,
        },
    )
