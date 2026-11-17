from pathlib import Path
import pandas as pd

DATA = Path(__file__).parents[1] / "data" / "synthetic_customers.csv"


def test_dataset_has_expected_size_and_fields():
    df = pd.read_csv(DATA)
    required = {
        "customer_id", "licensed_seats", "active_users", "active_seat_rate",
        "weekly_sessions", "monthly_active_days", "module_adoption_rate",
        "most_used_feature", "churn_next_90d", "licenses_core_workspace",
        "licenses_advanced_analytics", "licenses_collaboration", "licenses_automation",
    }
    assert len(df) == 120
    assert required.issubset(df.columns)


def test_active_users_do_not_exceed_licensed_seats():
    df = pd.read_csv(DATA)
    assert (df["active_users"] <= df["licensed_seats"]).all()
    assert (df["active_users"] >= 0).all()


def test_module_licenses_sum_to_total_licenses():
    df = pd.read_csv(DATA)
    cols = ["licenses_core_workspace", "licenses_advanced_analytics", "licenses_collaboration", "licenses_automation"]
    assert (df[cols].sum(axis=1) == df["licensed_seats"]).all()


def test_synthetic_labels_are_binary():
    df = pd.read_csv(DATA)
    assert set(df["churn_next_90d"].unique()).issubset({0, 1})
