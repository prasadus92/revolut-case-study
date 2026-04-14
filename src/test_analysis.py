"""
Tests for the GP L90D analysis.

Philosophy: Every numeric claim that appears in the presentation has a test here.
If a slide says "£8.34M", the test asserts £8.34M. If a slide says "+14.8% daily
run rate", the test asserts +14.8%. When the slides change, these tests update
in lockstep so the deliverable stays consistent with the data.

Methodology note: month comparisons use daily run rates (May÷31 days, Jun÷30,
Jul÷23). July is a partial month — the dataset was extracted on 23 Jul 2024 so
the rolling 91-day L90D window runs Apr 24 – Jul 23. Raw monthly totals would
under-represent July by 8 days and produce a false decline signal.

Run: python -m pytest src/test_analysis.py -v
"""

import pandas as pd
from pathlib import Path
import pytest

from charts import load_data

ROOT = Path(__file__).resolve().parent.parent
CHART_DIR = ROOT / "output" / "charts_final"

# Canonical day counts per month in the L90D window
DAYS = {"2024-04": 7, "2024-05": 31, "2024-06": 30, "2024-07": 23}


# ─── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def df():
    """Full dataset with amount_gbp in actual pounds (load_data handles *1000)."""
    data = load_data()
    data["pnl_date"] = pd.to_datetime(data["pnl_date"])
    return data


@pytest.fixture(scope="module")
def monthly_totals(df):
    return df.groupby("pnl_month")["amount_gbp"].sum()


@pytest.fixture(scope="module")
def daily_rates(df):
    """Daily GP run rate per month, indexed by pnl_month."""
    return df.groupby("pnl_month")["amount_gbp"].sum() / pd.Series(DAYS)


# ─── Data integrity ────────────────────────────────────────────────────────

class TestDataIntegrity:
    def test_row_count(self, df):
        assert len(df) == 196_187

    def test_unique_users(self, df):
        assert df["user_id"].nunique() == 191_412

    def test_date_range(self, df):
        assert df["pnl_date"].min().date().isoformat() == "2024-04-24"
        assert df["pnl_date"].max().date().isoformat() == "2024-07-23"

    def test_l90d_window_is_91_days(self, df):
        """91-day rolling window ending Jul 23."""
        assert df["pnl_date"].dt.date.nunique() == 91

    def test_april_is_7_days(self, df):
        """April starts the window on Apr 24 → 7 days."""
        apr = df[df["pnl_month"] == "2024-04"]
        assert apr["pnl_date"].dt.date.nunique() == 7

    def test_may_is_31_days(self, df):
        assert df[df["pnl_month"] == "2024-05"]["pnl_date"].dt.date.nunique() == 31

    def test_june_is_30_days(self, df):
        assert df[df["pnl_month"] == "2024-06"]["pnl_date"].dt.date.nunique() == 30

    def test_july_is_23_days(self, df):
        """July ends the window on Jul 23 → 23 days (partial month).
        This is the subtle discrepancy the brief's FAQ #5 warns about."""
        assert df[df["pnl_month"] == "2024-07"]["pnl_date"].dt.date.nunique() == 23

    def test_no_null_amounts(self, df):
        assert df["amount_gbp"].isna().sum() == 0

    def test_no_duplicates(self, df):
        assert df.duplicated().sum() == 0

    def test_expected_account_level_1(self, df):
        assert set(df["account_level_1"].unique()) == {
            "Treasury", "Revolut Business", "Revolut Retail"
        }


# ─── Slide 1: Executive summary ────────────────────────────────────────────

class TestSlide1Headlines:
    def test_l90d_total_is_8_34M(self, df):
        """Slide 1 stat card: '£8.34M GP L90D'."""
        total = df["amount_gbp"].sum()
        assert 8_340_000 <= total <= 8_350_000, f"L90D total = £{total:,.0f}"

    def test_daily_run_rate_trajectory_positive(self, daily_rates):
        """Slide 1 stat card: '+£390K/mo run-rate trajectory'."""
        may = daily_rates["2024-05"]
        jul = daily_rates["2024-07"]
        monthly_delta = (jul - may) * 30
        assert 380_000 < monthly_delta < 400_000, \
            f"Daily rate projected to 30 days: £{monthly_delta:,.0f}"

    def test_daily_run_rate_grew_15_percent(self, daily_rates):
        """Slide 1 and slide 2: '+15% May→Jul daily run rate'."""
        may = daily_rates["2024-05"]
        jul = daily_rates["2024-07"]
        pct = (jul - may) / may * 100
        assert 14 < pct < 16, f"Daily rate change = {pct:.1f}%"

    def test_top3_share_of_sized_recovery(self):
        """Slide 1: 'Three moves drive ~75% of sized recovery'."""
        levers = [
            (800, 1300), (190, 500), (170, 340),   # top 3
            (100, 200), (90, 180), (80, 115), (31, 156), (45, 70)
        ]
        top3_mid = sum((l[0] + l[1]) / 2 for l in levers[:3])
        all_mid = sum((l[0] + l[1]) / 2 for l in levers)
        share = top3_mid / all_mid * 100
        assert 74 < share < 77, f"Top 3 share = {share:.1f}%"


# ─── Slide 2: Waterfall by L2 category (daily rates) ───────────────────────

class TestSlide2Waterfall:
    def test_may_daily_rate(self, daily_rates):
        """Slide 2 waterfall: May starts at £88K/day."""
        assert 87_000 < daily_rates["2024-05"] < 88_500

    def test_jul_daily_rate(self, daily_rates):
        """Slide 2 waterfall: Jul ends at £101K/day."""
        assert 100_000 < daily_rates["2024-07"] < 101_500

    def _l2_daily_delta(self, df, cat):
        may = df[(df.pnl_month == "2024-05") & (df.account_level_2 == cat)]["amount_gbp"].sum() / 31
        jul = df[(df.pnl_month == "2024-07") & (df.account_level_2 == cat)]["amount_gbp"].sum() / 23
        return jul - may

    def test_fx_daily_declined(self, df):
        """Slide 2: FX −£5.2K/day."""
        assert -5_400 < self._l2_daily_delta(df, "FX") < -5_100

    def test_interest_income_daily_declined(self, df):
        """Slide 2: Interest Income −£2.6K/day."""
        assert -2_800 < self._l2_daily_delta(df, "Interest Income") < -2_500

    def test_bank_payments_daily_declined(self, df):
        """Slide 2: Bank Payments −£1.8K/day."""
        assert -2_000 < self._l2_daily_delta(df, "Bank Payments") < -1_600

    def test_lifestyle_daily_grew(self, df):
        """Slide 2: Lifestyle +£9.1K/day."""
        assert 9_000 < self._l2_daily_delta(df, "Lifestyle") < 9_300

    def test_card_payments_daily_grew(self, df):
        """Slide 2: Card Payments +£9.1K/day."""
        assert 9_000 < self._l2_daily_delta(df, "Card Payments") < 9_200

    def test_subscriptions_daily_grew(self, df):
        """Slide 2: Subscriptions +£4.1K/day (growing, not declining)."""
        assert 4_000 < self._l2_daily_delta(df, "Subscriptions") < 4_300

    def test_savings_daily_grew(self, df):
        """Slide 2: Savings +£2.3K/day."""
        assert 2_200 < self._l2_daily_delta(df, "Savings") < 2_500


# ─── Slide 3: Vending Machine NAP economics ────────────────────────────────

class TestSlide3VendingMachine:
    def test_vm_full_l90d_cost(self, df):
        """Slide 3: '£2.8M across the L90D window'."""
        vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        assert -2_810_000 < vm["amount_gbp"].sum() < -2_780_000

    def test_vm_not_napped_share_is_76pct(self, df):
        """Slide 3: '76% went to users who never activated'."""
        vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        total = vm["amount_gbp"].sum()
        not_napped = vm[vm["is_nap"] == "Not Napped"]["amount_gbp"].sum()
        share = not_napped / total * 100
        assert 75 < share < 77, f"Not Napped share = {share:.1f}%"

    def test_nap_activated_excl_reward(self, df):
        """Slide 3 NAP chart: £57 GP/user activated, excluding VM reward."""
        nv = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        nap = nv[nv["is_nap"] == "Napped"]
        gp_per = nap["amount_gbp"].sum() / nap["user_id"].nunique()
        assert 56 < gp_per < 58, f"Napped excl VM = £{gp_per:.0f}"

    def test_nap_not_activated_excl_reward(self, df):
        """Slide 3 NAP chart: £115 GP/user not activated, excluding VM reward."""
        nv = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        nn = nv[nv["is_nap"] == "Not Napped"]
        gp_per = nn["amount_gbp"].sum() / nn["user_id"].nunique()
        assert 113 < gp_per < 117, f"Not Napped excl VM = £{gp_per:.0f}"

    def test_not_napped_user_count(self, df):
        """6,455 Not Napped users total."""
        assert df[df["is_nap"] == "Not Napped"]["user_id"].nunique() == 6_455

    def test_vm_daily_cost_may_and_jul(self, df):
        """Slide 3 spend cap: 'May and Jul run rate: £32K and £31K/day'."""
        vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
        may_daily = abs(vm[vm.pnl_month == "2024-05"]["amount_gbp"].sum()) / 31
        jul_daily = abs(vm[vm.pnl_month == "2024-07"]["amount_gbp"].sum()) / 23
        assert 31_500 < may_daily < 32_500
        assert 30_500 < jul_daily < 32_000


# ─── Slide 4: Structural revenue pressure ──────────────────────────────────

class TestSlide4RevenuePressure:
    def test_fx_spread_daily_decline_41pct(self, df):
        """Slide 4: 'FX spread £12.8K→£7.5K/day (−41%)'."""
        fxs = df[df["account_level_3"] == "FX Spread"]
        may = fxs[fxs.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = fxs[fxs.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert -42 < pct < -40, f"FX Spread daily decline = {pct:.0f}%"
        assert 12_700 < may < 13_000
        assert 7_400 < jul < 7_600

    def test_romania_fx_spread_daily_decline(self, df):
        """Slide 4: 'Romania FX Spread fell 66% daily'."""
        ro = df[(df.account_level_3 == "FX Spread") & (df.user_country == "Romania")]
        may = ro[ro.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = ro[ro.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert -68 < pct < -64, f"Romania FX Spread daily decline = {pct:.0f}%"

    def test_bank_payments_daily_decline_25pct(self, df):
        """Slide 4: 'Bank payments £7.2K→£5.4K/day (−25%)'."""
        bp = df[df.account_level_2 == "Bank Payments"]
        may = bp[bp.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = bp[bp.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert -26 < pct < -24, f"Bank Pay daily decline = {pct:.0f}%"

    def test_uk_bank_payments_decline(self, df):
        """Slide 4: 'UK (−£918/day)'."""
        bp = df[(df.account_level_2 == "Bank Payments") & (df.user_country == "United Kingdom")]
        may = bp[bp.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = bp[bp.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        assert -950 < (jul - may) < -890

    def test_romania_bank_payments_decline(self, df):
        """Slide 4: 'Romania (−£466/day)'."""
        bp = df[(df.account_level_2 == "Bank Payments") & (df.user_country == "Romania")]
        may = bp[bp.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = bp[bp.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        assert -480 < (jul - may) < -450

    def test_cash_at_banks_actually_grew_daily(self, df):
        """Slide 4 nuance: 'Cash at banks is actually +3% daily'."""
        cb = df[df.account_level_3 == "Cash at Banks"]
        may = cb[cb.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = cb[cb.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert 2 < pct < 4, f"Cash at banks daily change = {pct:.1f}%"

    def test_other_financial_assets_declined_34pct(self, df):
        """Slide 4: 'Other Financial Assets (−34% daily)'."""
        ofa = df[df.account_level_3 == "Other Financial Assets"]
        may = ofa[ofa.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = ofa[ofa.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert -36 < pct < -32, f"OFA daily change = {pct:.0f}%"

    def test_subscriptions_daily_grew_15pct(self, df):
        """Slide 4: 'Subscriptions £28.0K→£32.1K/day (+15%)' — GROWING not declining."""
        s = df[df.account_level_2 == "Subscriptions"]
        may = s[s.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = s[s.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert 13 < pct < 17, f"Subs daily change = {pct:.1f}%"

    def test_plan_fees_june_trough(self, df):
        """Slide 4: 'Plan Fees recovered to £29.2K/day in Jul after a £20.2K/day June trough'."""
        pf = df[df.account_level_3 == "Plan Fees"]
        jun = pf[pf.pnl_month == "2024-06"]["amount_gbp"].sum() / 30
        jul = pf[pf.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        assert 20_000 < jun < 20_500
        assert 28_900 < jul < 29_500


# ─── Slide 5: Card payments ─────────────────────────────────────────────────

class TestSlide5Cards:
    def test_card_payments_daily_growth(self, df):
        """Slide 5: 'Card payments is a +£273K/month run-rate growth engine'."""
        cp = df[df.account_level_2 == "Card Payments"]
        may = cp[cp.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = cp[cp.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        delta_monthly = (jul - may) * 30
        assert 270_000 < delta_monthly < 275_000

    def test_interchange_fees_daily_growth(self, df):
        """Slide 5: 'Interchange fees up +£7.5K/day (+16%)'."""
        ic = df[df.account_level_3 == "Interchange Fees"]
        may = ic[ic.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = ic[ic.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        delta = jul - may
        assert 7_300 < delta < 7_600
        pct = delta / may * 100
        assert 14 < pct < 17

    def test_atm_costs_daily_improvement(self, df):
        """Slide 5: 'ATM costs improved +29% daily'."""
        atm = df[df.account_level_3 == "ATM"]
        may = atm[atm.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = atm[atm.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        # Both negative; improvement means less negative
        pct_improvement = (jul - may) / abs(may) * 100
        assert 27 < pct_improvement < 31

    def test_card_production_daily_increase_87pct(self, df):
        """Slide 5: 'Card production: +87% daily (£3.2K→£6.0K/day)'."""
        cp = df[df.account_level_4.str.contains("Card Production", case=False, na=False)]
        may = abs(cp[cp.pnl_month == "2024-05"]["amount_gbp"].sum()) / 31
        jul = abs(cp[cp.pnl_month == "2024-07"]["amount_gbp"].sum()) / 23
        pct = (jul - may) / may * 100
        assert 85 < pct < 90, f"Card production daily increase = {pct:.0f}%"
        assert 3_100 < may < 3_300
        assert 5_900 < jul < 6_100

    def test_card_production_monthly_cost_increase(self, df):
        """Slide 5: 'added £83K/month extra cost'."""
        cp = df[df.account_level_4.str.contains("Card Production", case=False, na=False)]
        may = abs(cp[cp.pnl_month == "2024-05"]["amount_gbp"].sum()) / 31
        jul = abs(cp[cp.pnl_month == "2024-07"]["amount_gbp"].sum()) / 23
        monthly_extra = (jul - may) * 30
        assert 80_000 < monthly_extra < 85_000


# ─── Slide 6: Growth engines ────────────────────────────────────────────────

class TestSlide6Growth:
    def test_lifestyle_daily_growth_3_5x(self, df):
        """Slide 6: 'Lifestyle daily run rate grew 3.5x May→Jul'."""
        ls = df[df.account_level_2 == "Lifestyle"]
        may = ls[ls.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = ls[ls.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        ratio = jul / may
        assert 3.4 < ratio < 3.6

    def test_esim_daily_growth_11_5x(self, df):
        """Slide 6: 'eSIMs 11.5x daily growth'."""
        es = df[df.account_level_4.str.contains("eSIM|eSim", case=False, na=False)]
        may = es[es.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = es[es.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        ratio = jul / may
        assert 11 < ratio < 12

    def test_esim_unique_users(self, df):
        """Slide 6 and slide 1: '9 users' for eSIM across the full dataset."""
        es = df[df.account_level_4.str.contains("eSIM|eSim", case=False, na=False)]
        assert es["user_id"].nunique() == 9

    def test_revpoints_daily_growth_4_8x(self, df):
        """Slide 6: 'RevPoints 4.8x daily growth'."""
        rp = df[df.account_level_3 == "RevPoints"]
        may = rp[rp.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = rp[rp.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        ratio = jul / may
        assert 4.7 < ratio < 5.0

    def test_standard_plan_user_count(self, df):
        """Slide 6: '111,167 Standard users'."""
        assert df[df.user_plan == "STANDARD"]["user_id"].nunique() == 111_167

    @pytest.mark.parametrize("plan,expected", [
        ("STANDARD", 15), ("PLUS", 43), ("PREMIUM", 40),
        ("METAL", 65), ("ULTRA", 232),
    ])
    def test_plan_gp_per_user(self, df, plan, expected):
        """Slide 6: plan ARPUs '£15/£43/£232'."""
        d = df[df.user_plan == plan]
        gp_per = d["amount_gbp"].sum() / d["user_id"].nunique()
        assert abs(gp_per - expected) < 1, f"{plan} = £{gp_per:.0f}"


# ─── Slide 7: Additional levers ────────────────────────────────────────────

class TestSlide7Levers:
    @pytest.mark.parametrize("country,expected", [
        ("Poland", -417), ("Lithuania", -329), ("Romania", -208),
        ("Germany", -126),
    ])
    def test_loan_daily_declines_by_country(self, df, country, expected):
        """Slide 7: 'Poland −£417/day, Lithuania −£329/day, Romania −£208/day, Germany −£126/day'."""
        loans = df[(df.account_level_3 == "Loans") & (df.user_country == country)]
        may = loans[loans.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = loans[loans.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        delta = jul - may
        assert abs(delta - expected) < 25, f"{country}: {delta:.0f}/day vs expected {expected}"

    def test_ireland_loans_flat(self, df):
        """Slide 7: 'Ireland flat'."""
        loans = df[(df.account_level_3 == "Loans") & (df.user_country == "Ireland")]
        may = loans[loans.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = loans[loans.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        delta = jul - may
        assert abs(delta) < 50, f"Ireland loans delta should be near zero, got {delta:.0f}/day"

    def test_credit_cards_turned_positive(self, df):
        """Slide 7: 'Credit Cards turned positive'."""
        cc = df[df.account_level_3 == "Credit Cards"]
        may = cc[cc.pnl_month == "2024-05"]["amount_gbp"].sum()
        jul = cc[cc.pnl_month == "2024-07"]["amount_gbp"].sum()
        assert may < 0 and jul > 0

    def test_bnpl_daily_growth_8_9x(self, df):
        """Slide 7: 'BNPL grew 8.9x daily'."""
        bnpl = df[df.account_level_3 == "Buy Now Pay Later"]
        may = bnpl[bnpl.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = bnpl[bnpl.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        assert 8.5 < (jul / may) < 9.3

    def test_business_segment_gp_per_user(self, df):
        """Slide 7: '2,348 business users at £913 GP/user'."""
        biz = df[df.user_type == "BUSINESS"]
        assert biz["user_id"].nunique() == 2_348
        gp_per = biz["amount_gbp"].sum() / biz["user_id"].nunique()
        assert 912 < gp_per < 915

    def test_personal_segment_gp_per_user(self, df):
        """Slide 7: '185,894 personal at £34'."""
        pers = df[df.user_type == "PERSONAL"]
        assert pers["user_id"].nunique() == 185_894
        gp_per = pers["amount_gbp"].sum() / pers["user_id"].nunique()
        assert 33 < gp_per < 35

    @pytest.mark.parametrize("country,expected", [
        ("United Kingdom", 90), ("France", 23),
        ("Romania", 17), ("Poland", 31),
    ])
    def test_geographic_arpu(self, df, country, expected):
        """Slide 7: 'UK £90 vs France £23, Romania £17, Poland £31'."""
        d = df[df.user_country == country]
        arpu = d["amount_gbp"].sum() / d["user_id"].nunique()
        assert abs(arpu - expected) < 1, f"{country} = £{arpu:.0f}"

    def test_youth_segment(self, df):
        """Slide 7: 'Youth segment (3,153 users) runs at −£58/user'."""
        y = df[df.user_type == "YOUTH"]
        assert y["user_id"].nunique() == 3_153
        gp_per = y["amount_gbp"].sum() / y["user_id"].nunique()
        assert -60 < gp_per < -56


# ─── Slide 10: Appendix — Scale plan and cohort ────────────────────────────

class TestSlide10Appendix:
    def test_scale_plan(self, df):
        """Slide 10: 'Scale plan: 187 users at £2,768 GP/user'."""
        s = df[df.user_plan == "COMPANY_SCALE"]
        assert s["user_id"].nunique() == 187
        gp_per = s["amount_gbp"].sum() / s["user_id"].nunique()
        assert 2_760 < gp_per < 2_775

    def test_2024_cohort_gp_per_user(self, df):
        """Slide 10 assumption: '2024 cohort £14/user vs £49 for pre-2024'."""
        df_copy = df.copy()
        df_copy["onboarded_year"] = pd.to_datetime(
            df_copy.onboarded_date, errors="coerce"
        ).dt.year
        c24 = df_copy[df_copy.onboarded_year == 2024]
        pre24 = df_copy[df_copy.onboarded_year < 2024]
        gp_24 = c24["amount_gbp"].sum() / c24["user_id"].nunique()
        gp_pre = pre24["amount_gbp"].sum() / pre24["user_id"].nunique()
        assert 13 < gp_24 < 15
        assert 48 < gp_pre < 50

    def test_instant_access_daily_growth_84pct(self, df):
        """Slide 10 initiative mapping #2: 'Instant Access daily +84%' (volume offsets rate cost)."""
        ia = df[df.account_level_3 == "Instant Access"]
        may = ia[ia.pnl_month == "2024-05"]["amount_gbp"].sum() / 31
        jul = ia[ia.pnl_month == "2024-07"]["amount_gbp"].sum() / 23
        pct = (jul - may) / may * 100
        assert 82 < pct < 86, f"Instant Access daily change = {pct:.0f}%"


# ─── Sizing math ───────────────────────────────────────────────────────────

class TestSizing:
    LEVERS = [
        ("Restructure vending machine campaign", 800, 1300),
        ("Scale eSIM distribution", 190, 500),
        ("Recover FX spread pricing", 170, 340),
        ("Complete card vendor migration", 100, 200),
        ("Optimise bank payment pricing", 90, 180),
        ("Fix card production costs", 80, 115),
        ("Subscription upgrade campaign", 31, 156),
        ("Selective credit repricing", 45, 70),
    ]

    def test_low_end_is_1_5M(self):
        """Slide 8: 'Eight interventions total £1.5M to £2.9M' — low end."""
        low = sum(l[1] for l in self.LEVERS)
        assert 1_500 <= low <= 1_510

    def test_high_end_is_2_9M(self):
        """Slide 8: 'Eight interventions total £1.5M to £2.9M' — high end."""
        high = sum(l[2] for l in self.LEVERS)
        assert 2_850 <= high <= 2_870

    def test_full_range_with_supplementary(self):
        """Slide 8 bottom bar: 'Full range: £2.1M to £4.0M'."""
        # Supplementary: business growth 300-600, geographic ARPU 200-400, balance 50-100
        low = sum(l[1] for l in self.LEVERS) + 300 + 200 + 50
        high = sum(l[2] for l in self.LEVERS) + 600 + 400 + 100
        assert 2_050 < low < 2_100
        assert 3_950 < high < 4_000

    def test_slide_7_three_operational_levers_range(self):
        """Slide 7 title: 'Three operational levers add £157K to £272K'.
        The three = Credit (45-70) + Bank payment (90-180) + SMS (~22).
        Card production sits on slide 5 and is in the sizing chart separately.
        Business segment is supplementary, named in the title separately.
        """
        # Pull from the canonical LEVERS in this class
        lever_map = {name: (low, high) for name, low, high in self.LEVERS}
        credit_low, credit_high = lever_map["Selective credit repricing"]
        bp_low, bp_high = lever_map["Optimise bank payment pricing"]
        sms_low = sms_high = 22
        low_sum = credit_low + bp_low + sms_low
        high_sum = credit_high + bp_high + sms_high
        assert low_sum == 157, f"low sum = {low_sum}"
        assert high_sum == 272, f"high sum = {high_sum}"


# ─── Charts ────────────────────────────────────────────────────────────────

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
