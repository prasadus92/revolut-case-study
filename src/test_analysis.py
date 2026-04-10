"""
Tests for the GP L90D analysis pipeline.
Validates data integrity, chart generation, and key analytical findings.

Run: python -m pytest src/test_analysis.py -v
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dataset.csv"
CHART_DIR = ROOT / "charts" / "final"
SCALE = 1_000


@pytest.fixture(scope="module")
def df():
    """Load and prepare the dataset."""
    data = pd.read_csv(DATA_PATH)
    if data.columns[0] == "" or data.columns[0].startswith("Unnamed"):
        data = data.drop(columns=[data.columns[0]])
    data["amount_gbp"] = pd.to_numeric(data["amount_gbp"], errors="coerce") * SCALE
    data["pnl_date"] = pd.to_datetime(data["pnl_date"])
    return data


# ---- Data integrity tests ----

class TestDataIntegrity:
    def test_row_count(self, df):
        assert len(df) == 196_187, f"Expected 196,187 rows, got {len(df)}"

    def test_unique_users(self, df):
        assert df["user_id"].nunique() == 191_412

    def test_date_range(self, df):
        assert df["pnl_date"].min().date().isoformat() == "2024-04-24"
        assert df["pnl_date"].max().date().isoformat() == "2024-07-23"

    def test_no_null_amounts(self, df):
        null_count = df["amount_gbp"].isna().sum()
        assert null_count == 0, f"{null_count} null amounts found"

    def test_months_present(self, df):
        months = set(df["pnl_month"].unique())
        assert {"2024-04", "2024-05", "2024-06", "2024-07"}.issubset(months)


# ---- Key finding tests (verified against audit) ----

class TestKeyFindings:
    def test_total_gp(self, df):
        total = df["amount_gbp"].sum()
        assert 8_300_000 < total < 8_400_000, f"Total GP: {total}"

    def test_monthly_decline(self, df):
        monthly = df.groupby("pnl_month")["amount_gbp"].sum()
        may = monthly["2024-05"]
        jul = monthly["2024-07"]
        decline = jul - may
        assert -420_000 < decline < -380_000, f"May-Jul decline: {decline}"

    def test_vending_machine_cost(self, df):
        vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        total = vm["amount_gbp"].sum()
        assert -2_900_000 < total < -2_700_000, f"VM cost: {total}"

    def test_nap_economics(self, df):
        """Non-activated users generate positive GP excluding campaign rewards."""
        non_vm = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        not_napped = non_vm[non_vm["is_nap"] == "Not Napped"]
        gp = not_napped["amount_gbp"].sum()
        users = not_napped["user_id"].nunique()
        gp_per_user = gp / users
        assert gp_per_user > 70, f"Not-napped GP/user excl. reward: {gp_per_user}"

    def test_esim_growth(self, df):
        esim = df[df["account_level_4"].str.contains("eSIM|eSim", case=False, na=False)]
        esim_m = esim.groupby("pnl_month")["amount_gbp"].sum()
        may = esim_m.get("2024-05", 0)
        jul = esim_m.get("2024-07", 0)
        assert jul / max(may, 1) > 7, f"eSIM Jul/May ratio: {jul / max(may, 1)}"

    def test_card_cost_improvement(self, df):
        card = df[df["account_level_2"] == "Card Payments"]
        card_m = card.groupby("pnl_month")["amount_gbp"].sum()
        may = card_m.get("2024-05", 0)
        jul = card_m.get("2024-07", 0)
        assert jul > may, "Card payments GP should improve May to Jul"

    def test_fx_spread_decline(self, df):
        fx_spread = df[df["account_level_3"].str.contains("FX Spread", case=False, na=False)]
        fx_m = fx_spread.groupby("pnl_month")["amount_gbp"].sum()
        may = fx_m.get("2024-05", 0)
        jul = fx_m.get("2024-07", 0)
        decline_pct = (jul - may) / may
        assert decline_pct < -0.5, f"FX spread decline: {decline_pct:.0%}"


# ---- Chart generation tests ----

class TestCharts:
    EXPECTED_CHARTS = [
        "monthly_gp", "bridge", "vending_cost", "nap_economics",
        "fx_decline", "card_costs", "card_prod", "credit",
        "esim", "revpoints", "plan_gp", "sizing",
    ]

    def test_chart_directory_exists(self):
        assert CHART_DIR.exists(), f"Chart directory not found: {CHART_DIR}"

    @pytest.mark.parametrize("chart_name", EXPECTED_CHARTS)
    def test_chart_exists(self, chart_name):
        chart_path = CHART_DIR / f"{chart_name}.png"
        assert chart_path.exists(), f"Missing chart: {chart_name}.png"

    @pytest.mark.parametrize("chart_name", EXPECTED_CHARTS)
    def test_chart_not_empty(self, chart_name):
        chart_path = CHART_DIR / f"{chart_name}.png"
        assert chart_path.stat().st_size > 1000, f"Chart too small: {chart_name}.png"
