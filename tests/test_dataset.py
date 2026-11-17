from pathlib import Path
import pandas as pd

DATA = Path(__file__).parents[1] / "data" / "synthetic_customers.csv"

def test_dataset_has_expected_size_and_fields():
    df = pd.read_csv(DATA)
    required = {
        "customer_id", "segment", "industry", "licensed_seats", "active_users",
        "active_seat_rate", "weekly_sessions", "module_adoption_rate",
        "usage_change_30d", "days_since_last_login", "nps_score",
        "licenses_core_workspace", "licenses_advanced_analytics",
        "licenses_collaboration", "licenses_automation",
    }
    assert len(df) == 120
    assert required.issubset(df.columns)

def test_active_users_do_not_exceed_licensed_seats():
    df = pd.read_csv(DATA)
    assert (df["active_users"] <= df["licensed_seats"]).all()
    assert (df["active_users"] >= 0).all()

def test_module_licenses_sum_to_total_licenses():
    df = pd.read_csv(DATA)
    cols = [
        "licenses_core_workspace", "licenses_advanced_analytics",
        "licenses_collaboration", "licenses_automation",
    ]
    assert (df[cols].sum(axis=1) == df["licensed_seats"]).all()

def test_dataset_has_unique_accounts_and_valid_rates():
    df = pd.read_csv(DATA)
    assert df["customer_id"].is_unique
    assert df["active_seat_rate"].between(0, 1).all()
    assert df["module_adoption_rate"].between(0, 1).all()
