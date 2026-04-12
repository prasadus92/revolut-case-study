"""
Tests for the GP L90D analysis.
Validates data integrity and key analytical findings used in the presentation.

Run: python -m pytest src/test_analysis.py -v
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pytest

from charts import load_data

ROOT = Path(__file__).resolve().parent.parent
CHART_DIR = ROOT / "output" / "charts_final"


@pytest.fixture(scope="module")
def df():
    data = load_data()
    data["pnl_date"] = pd.to_datetime(data["pnl_date"])
    return data


class TestDataIntegrity:
    def test_row_count(self, df):
        assert len(df) == 196_187

    def test_unique_users(self, df):
        assert df["user_id"].nunique() == 191_412

    def test_date_range(self, df):
        assert df["pnl_date"].min().date().isoformat() == "2024-04-24"
        assert df["pnl_date"].max().date().isoformat() == "2024-07-23"

    def test_no_null_amounts(self, df):
        assert df["amount_gbp"].isna().sum() == 0

    def test_months_present(self, df):
        months = set(df["pnl_month"].unique())
        assert {"2024-04", "2024-05", "2024-06", "2024-07"}.issubset(months)


class TestKeyFindings:
    def test_gp_l90d(self, df):
        m = df.groupby("pnl_month")["amount_gbp"].sum()
        l90d = m["2024-05"] + m["2024-06"] + m["2024-07"]
        assert abs(l90d - 7_673_718) < 1000

    def test_monthly_decline(self, df):
        m = df.groupby("pnl_month")["amount_gbp"].sum()
        assert abs((m["2024-07"] - m["2024-05"]) + 402_850) < 1000

    def test_decline_acceleration(self, df):
        m = df.groupby("pnl_month")["amount_gbp"].sum()
        jun_may = m["2024-06"] - m["2024-05"]
        jul_jun = m["2024-07"] - m["2024-06"]
        assert abs(jun_may) < abs(jul_jun), "Decline should accelerate"

    def test_vending_machine_cost(self, df):
        vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        total = vm[vm["pnl_month"].isin(["2024-05", "2024-06", "2024-07"])]["amount_gbp"].sum()
        assert -2_700_000 < total < -2_500_000

    def test_nap_economics(self, df):
        nv = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        nn = nv[nv["is_nap"] == "Not Napped"]
        gp_per_user = nn["amount_gbp"].sum() / nn["user_id"].nunique()
        assert gp_per_user > 100, f"Not-napped GP/user excl. reward: {gp_per_user}"

    def test_esim_growth(self, df):
        esim = df[df["account_level_4"].str.contains("eSIM|eSim", case=False, na=False)]
        em = esim.groupby("pnl_month")["amount_gbp"].sum()
        assert em.get("2024-07", 0) / max(em.get("2024-05", 1), 1) > 7

    def test_fx_spread_decline(self, df):
        fx = df[df["account_level_3"] == "FX Spread"].groupby("pnl_month")["amount_gbp"].sum()
        assert (fx["2024-07"] - fx["2024-05"]) / fx["2024-05"] < -0.5

    def test_card_cost_improvement(self, df):
        card = df[df["account_level_2"] == "Card Payments"].groupby("pnl_month")["amount_gbp"].sum()
        assert card["2024-07"] > card["2024-05"]

    def test_business_gp_per_user(self, df):
        biz = df[df["user_type"] == "BUSINESS"]
        gp_per_user = biz["amount_gbp"].sum() / biz["user_id"].nunique()
        assert gp_per_user > 900


class TestCharts:
    EXPECTED = ["waterfall", "nap", "fx", "card_costs", "card_prod",
                "esim", "revpoints", "esim_revpoints", "sizing"]

    def test_chart_directory_exists(self):
        assert CHART_DIR.exists()

    @pytest.mark.parametrize("name", EXPECTED)
    def test_chart_exists(self, name):
        assert (CHART_DIR / f"{name}.png").exists()

    @pytest.mark.parametrize("name", EXPECTED)
    def test_chart_not_empty(self, name):
        assert (CHART_DIR / f"{name}.png").stat().st_size > 1000
