import pandas as pd

from services.eda_service import EDAService


def make_dataset(rows: int = 120) -> pd.DataFrame:
    base = list(range(rows))
    return pd.DataFrame(
        {
            "id_col": [f"ID-{i:04d}" for i in base],
            "sales": [i * 10 for i in base],
            "sales_copy": [i * 10 + (1 if i % 25 == 0 else 0) for i in base],
            "segment": ["A" if i % 3 == 0 else "B" if i % 3 == 1 else "C" for i in base],
            "text": ["" if i % 20 == 0 else f"value-{i}" for i in base],
            "event_time": pd.date_range("2024-01-01", periods=rows, freq="D"),
        }
    ).assign(
        sales=lambda df: df["sales"].mask(df.index % 12 == 0),
        text=lambda df: df["text"].mask(df.index % 15 == 0),
    )


def test_eda_report_contains_stable_sections():
    report = EDAService.analyze_dataset(make_dataset())

    assert set(report.keys()) == {
        "overview",
        "sample_meta",
        "quality_alerts",
        "missingness",
        "numeric_profiles",
        "categorical_profiles",
        "datetime_profiles",
        "relationship_findings",
        "quick_distributions",
    }
    assert report["overview"]["rows"] == 120
    assert report["missingness"]["summary"]
    assert report["numeric_profiles"]
    assert report["categorical_profiles"]
    assert report["datetime_profiles"]


def test_eda_detects_key_alerts():
    report = EDAService.analyze_dataset(make_dataset())
    alert_types = {item["type"] for item in report["quality_alerts"]}

    assert "missing" in alert_types or report["overview"]["missing_pct"] > 0
    assert "id_like" in alert_types
    assert report["relationship_findings"]["numeric_pairs"]


def test_sampling_mode_reports_sample_metadata():
    large_df = make_dataset(20000)
    report = EDAService.analyze_dataset(large_df, mode="sample", sample_size=2500)

    assert report["sample_meta"]["used_sampling"] is True
    assert report["sample_meta"]["sample_rows"] == 2500
    assert report["sample_meta"]["mode"] == "sample"
    assert report["overview"]["rows"] == 20000
