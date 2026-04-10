"""
Build the final presentation as a single HTML file.
Uses inline SVG charts for crisp rendering and CSS Grid for layout.
Each slide is 1280x720px with proper vertical distribution.

Run: python src/build_slides.py
Then: node src/render_pdf.js
"""

import pandas as pd
import numpy as np
from pathlib import Path
from svg_charts import (
    bar_chart_vertical, bar_chart_grouped, bar_chart_horizontal,
    waterfall_chart, BLUE, BLUE_MID, RED, W, H
)

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dataset.csv"
OUTPUT_HTML = ROOT / "output" / "slides.html"
OUTPUT_HTML.parent.mkdir(exist_ok=True)
SCALE = 1_000

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
        df = df.drop(columns=[df.columns[0]])
    df["amount_gbp"] = pd.to_numeric(df["amount_gbp"], errors="coerce") * SCALE
    return df


# ---------------------------------------------------------------------------
# Generate all chart SVGs from data
# ---------------------------------------------------------------------------
def generate_charts(df):
    months = ["2024-05", "2024-06", "2024-07"]
    charts = {}

    # 1. Monthly GP
    m = df.groupby("pnl_month")["amount_gbp"].sum()
    charts["monthly"] = bar_chart_vertical([
        ("May", m["2024-05"]), ("Jun", m["2024-06"]), ("Jul", m["2024-07"])
    ], w=300, h=200)

    # 2. Bridge (waterfall)
    may_by_l2 = df[df["pnl_month"] == "2024-05"].groupby("account_level_2")["amount_gbp"].sum()
    jul_by_l2 = df[df["pnl_month"] == "2024-07"].groupby("account_level_2")["amount_gbp"].sum()
    changes = (jul_by_l2 - may_by_l2).dropna()
    changes = changes[changes.abs() > 15000].sort_values()

    name_map = {
        "Interest Income": "Interest", "FX": "FX",
        "Card Payments": "Cards", "Subscriptions": "Subs",
        "Other": "Campaigns", "Lifestyle": "Lifestyle",
        "Bank Payments": "Bank Pay", "Credit": "Credit",
        "Savings": "Savings", "Market Making PnL": "Mkt Making",
    }

    bridge_data = [("May GP", m["2024-05"], "total")]
    for cat, delta in changes.items():
        bridge_data.append((name_map.get(cat, cat), delta, "delta"))
    bridge_data.append(("Jul GP", m["2024-07"], "total"))
    charts["bridge"] = waterfall_chart(bridge_data, w=1100, h=360)

    # 3. NAP economics
    nap_gp = df.groupby("is_nap")["amount_gbp"].sum()
    nap_users = df.groupby("is_nap")["user_id"].nunique()
    non_vm = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
    nap_clean = non_vm.groupby("is_nap")["amount_gbp"].sum()

    charts["nap"] = bar_chart_vertical([
        ("Activated\n(with reward)", nap_gp["Napped"] / nap_users["Napped"]),
        ("Activated\n(excl. reward)", nap_clean["Napped"] / nap_users["Napped"]),
        ("Not activated\n(excl. reward)", nap_clean["Not Napped"] / nap_users["Not Napped"]),
    ], w=440, h=280)

    # 4. Card costs by L3
    card = df[df["account_level_2"] == "Card Payments"]
    card_l3 = card.groupby(["pnl_month", "account_level_3"])["amount_gbp"].sum().unstack().fillna(0)
    card_groups = []
    for mon, label in zip(months, ["May", "Jun", "Jul"]):
        series = []
        for cat, color in [("Top-ups", RED), ("ATM", "#F87171"), ("Interchange Fees", BLUE), ("POS Charges", BLUE_MID)]:
            val = card_l3.loc[mon, cat] if mon in card_l3.index and cat in card_l3.columns else 0
            series.append((cat, val, color))
        card_groups.append((label, series))
    charts["card_costs"] = bar_chart_grouped(card_groups, w=480, h=300)

    # 5. eSIM
    esim = df[df["account_level_4"].str.contains("eSIM|eSim", case=False, na=False)]
    esim_m = esim.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)
    charts["esim"] = bar_chart_vertical([
        ("May", esim_m["2024-05"]), ("Jun", esim_m["2024-06"]), ("Jul", esim_m["2024-07"])
    ], w=240, h=240)

    # 6. RevPoints
    rp = df[df["account_level_3"] == "RevPoints"]
    rp_m = rp.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)
    charts["revpoints"] = bar_chart_vertical([
        ("May", rp_m["2024-05"]), ("Jun", rp_m["2024-06"]), ("Jul", rp_m["2024-07"])
    ], w=240, h=240)

    # 7. FX by component
    fx = df[df["account_level_2"] == "FX"]
    fx_l3 = fx.groupby(["pnl_month", "account_level_3"])["amount_gbp"].sum().unstack().fillna(0)
    fx_groups = []
    for mon, label in zip(months, ["May", "Jun", "Jul"]):
        series = []
        for cat, color in [("FX Spread", BLUE), ("FX Fees", BLUE_MID), ("FX Mark-up", "#60A5FA")]:
            val = fx_l3.loc[mon, cat] if mon in fx_l3.index and cat in fx_l3.columns else 0
            series.append((cat.replace("FX ", ""), val, color))
        fx_groups.append((label, series))
    charts["fx"] = bar_chart_grouped(fx_groups, w=440, h=280)

    # 8. Sizing (horizontal)
    charts["sizing"] = bar_chart_horizontal([
        ("Vending machine\ncampaign", 1000, 800, 1200),
        ("Card vendor\nmigration", 450, 350, 550),
        ("eSIM\ndistribution", 350, 250, 450),
        ("FX spread\npricing", 275, 200, 350),
        ("RevPoints and\nlifestyle", 140, 100, 180),
        ("Card production\ncosts", 125, 100, 150),
        ("Credit\nrepricing", 115, 80, 150),
        ("Subscription\nupgrades", 95, 70, 120),
    ], w=1100, h=380, show_target=4000)

    # 9. Plan GP per user (horizontal)
    plans = ["STANDARD", "PLUS", "PREMIUM", "METAL", "ULTRA"]
    plan_gp = df[df["user_plan"].isin(plans)].groupby("user_plan")["amount_gbp"].sum()
    plan_users = df[df["user_plan"].isin(plans)].groupby("user_plan")["user_id"].nunique()
    per_user = (plan_gp / plan_users).reindex(plans)

    charts["plans"] = bar_chart_horizontal([
        ("Standard", per_user["STANDARD"], per_user["STANDARD"], per_user["STANDARD"]),
        ("Plus", per_user["PLUS"], per_user["PLUS"], per_user["PLUS"]),
        ("Premium", per_user["PREMIUM"], per_user["PREMIUM"], per_user["PREMIUM"]),
        ("Metal", per_user["METAL"], per_user["METAL"], per_user["METAL"]),
        ("Ultra", per_user["ULTRA"], per_user["ULTRA"], per_user["ULTRA"]),
    ], w=440, h=240)

    return charts


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0A0A0A; --surface: #131313; --border: #1E1E1E;
  --text: #FFFFFF; --text2: #B0B0B0; --text3: #707070;
  --blue: #0075EB; --red: #EF4444;
}
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; }

.slide {
  width: 1280px; height: 720px; position: relative;
  page-break-after: always; overflow: hidden; background: var(--bg);
  display: grid; grid-template-rows: auto 1fr auto;
  padding: 48px 56px;
}
.slide:last-child { page-break-after: auto; }

.slide-header { margin-bottom: 12px; }
.slide-body { display: flex; flex-direction: column; justify-content: center; }
.slide-footer { }

.tag { font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--blue); margin-bottom: 6px; }
h1 { font-size: 26px; font-weight: 700; line-height: 1.2; color: var(--text); }
.sub { font-size: 14px; line-height: 1.5; color: var(--text2); margin-top: 6px; }

.t2 { font-size: 15px; font-weight: 600; line-height: 1.3; margin-bottom: 4px; }
.t2.blue { color: var(--blue); }
.t2.red { color: var(--red); }
.t3 { font-size: 13px; line-height: 1.5; color: var(--text2); }
.t4 { font-size: 11px; line-height: 1.4; color: var(--text3); }
.t5 { font-size: 34px; font-weight: 800; letter-spacing: -1px; }
b, strong { color: var(--text); font-weight: 600; }

.row { display: flex; gap: 24px; align-items: stretch; }
.col { flex: 1; display: flex; flex-direction: column; }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px 18px;
}
.card + .card { margin-top: 8px; }
.card.bl { border-left: 3px solid var(--blue); }
.card.rl { border-left: 3px solid var(--red); }

.fill { flex: 1; display: flex; flex-direction: column; }
.fill > .row { flex: 1; }
.fill > .row > .card, .fill > .row > .col > .card, .fill > .row > .hz { flex: 1; }

.stats { display: flex; gap: 12px; }
.stat {
  flex: 1; padding: 14px 18px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
}
.stat .n { font-size: 32px; font-weight: 800; letter-spacing: -0.8px; }
.stat .l { font-size: 10px; font-weight: 600; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px; }
.stat .d { font-size: 10px; color: var(--text3); margin-top: 2px; }

.chart-container { display: flex; align-items: center; justify-content: center; flex: 1; }
.chart-container svg { max-height: 100%; }

.pill { display: flex; gap: 8px; align-items: flex-start; margin-bottom: 6px; }
.pill-n {
  width: 22px; height: 22px; border-radius: 50%; background: var(--blue);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: white; flex-shrink: 0; margin-top: 1px;
}

.hz { flex: 1; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }
.hz-h { padding: 10px 16px; font-size: 13px; font-weight: 700; color: white; }
.hz-b { padding: 12px 16px; background: var(--surface); }
.hz-b .t3 { margin-bottom: 5px; }

.pn { position: absolute; bottom: 14px; right: 40px; font-size: 11px; color: var(--text3); }
.fn { font-size: 11px; color: var(--text3); margin-top: 8px; }
"""


# ---------------------------------------------------------------------------
# Slide templates
# ---------------------------------------------------------------------------
def slide(num, total, header, body, footer=""):
    return f"""<div class="slide">
  <div class="slide-header">{header}</div>
  <div class="slide-body">{body}</div>
  <div class="slide-footer">{footer}</div>
  <div class="pn">{num} / {total}</div>
</div>
"""


def build(charts):
    total = 10
    slides = []

    # SLIDE 1
    slides.append(slide(1, total,
        header="""
        <div class="tag">GP L90D analysis</div>
        <h1 style="font-size:30px;">Revolut GP L90D: root causes and path to £4M</h1>
        <div class="sub">The team tracks GP L90D as its primary metric. The objective is a £4M increase in 6 to 12 months. This analysis identifies what is driving the decline and sizes eight interventions to close the gap.</div>
        """,
        body=f"""
        <div class="stats" style="margin-bottom:16px;">
          <div class="stat"><div class="n">£7.67M</div><div class="l">GP last 90 days</div><div class="d">191,412 users, May to Jul 2024</div></div>
          <div class="stat"><div class="n" style="color:var(--red);">−£403K</div><div class="l">Three-month decline</div><div class="d">Accelerating: −£77K, then −£326K</div></div>
          <div class="stat"><div class="n">8</div><div class="l">Interventions sized</div><div class="d">£1.95M to £3.15M total</div></div>
          <div class="stat"><div class="n" style="color:var(--blue);">£4M</div><div class="l">Target</div><div class="d">Achievable across three horizons</div></div>
        </div>
        <div class="t4" style="text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">Three moves that capture 70% of the total</div>
        <div class="pill"><div class="pill-n">1</div><div class="t3"><strong>Restructure the vending machine campaign</strong> to fix its reward economics. Largest cost at £2.8M per L90D. Worth £800K to £1.2M.</div></div>
        <div class="pill"><div class="pill-n">2</div><div class="t3"><strong>Complete the card payment vendor migration.</strong> Already delivering £331K in savings, with more to come. Worth £350K to £550K.</div></div>
        <div class="pill"><div class="pill-n">3</div><div class="t3"><strong>Scale eSIM distribution.</strong> Revenue grew 8.5x in three months on minimal spend. Worth £250K to £450K.</div></div>
        """))

    # SLIDE 2
    slides.append(slide(2, total,
        header="""
        <h1>GP fell £403K in three months, with the decline accelerating in July</h1>
        <div class="sub">Interest income and FX revenue account for most of the drop, partially offset by lifestyle growth and lower card processing costs.</div>
        """,
        body=f'<div class="chart-container">{charts["bridge"]}</div>',
        footer='<div class="fn">Source: 196,187 user-level P&L records. Amounts converted from £1,000s per documentation. April excluded (partial month, 7 days).</div>'))

    # SLIDE 3
    slides.append(slide(3, total,
        header="""
        <h1>Restructuring the vending machine campaign can recover £800K to £1.2M</h1>
        <div class="sub">Initiative 6 cost £2.8M over 90 days. 6,455 users incurred card production and onboarding costs without ever activating.</div>
        """,
        body=f"""
        <div class="row" style="flex:1;">
          <div class="col" style="justify-content:center;">{charts["nap"]}</div>
          <div class="col" style="gap:8px;">
            <div class="card bl" style="flex:1;">
              <div class="t2 blue">Excluding the reward, non-activated users generate £81 per user</div>
              <div class="t3">Higher than the £57 from activated users. The reward structure creates the loss. Costs hit before activation, so users who never spend £20 represent sunk cost.</div>
            </div>
            <div class="card bl" style="flex:1;">
              <div class="t2 blue">What to do</div>
              <div class="t3">Introduce a qualification gate before dispatching physical cards. Cap monthly spend at £500K (trending there naturally). Track activation rates by channel.</div>
              <div class="t2 blue" style="margin-top:8px;">£800K to £1.2M improvement</div>
            </div>
          </div>
        </div>"""))

    # SLIDE 4
    slides.append(slide(4, total,
        header="""
        <h1>Completing the card vendor migration adds £350K to £550K. Savings are already flowing.</h1>
        <div class="sub">Initiative 8 introduced new cost structures. The data confirms material savings, with the transition still incomplete.</div>
        """,
        body=f"""
        <div class="row" style="flex:1;">
          <div class="col" style="justify-content:center;">{charts["card_costs"]}</div>
          <div class="col" style="gap:8px;">
            <div class="card bl" style="flex:1;">
              <div class="t2 blue">£331K saved in 90 days</div>
              <div class="t3">Top-up processing: <strong>+£269K</strong> | ATM: <strong>+£59K</strong> | POS: <strong>+£3K</strong></div>
              <div class="t3" style="margin-top:6px;">Costs still declining month over month. More savings ahead as remaining volume shifts to new pricing.</div>
            </div>
            <div class="card rl" style="flex:1;">
              <div class="t2 red">Card production costs are moving the wrong way</div>
              <div class="t3">The new single vendor (Initiative 9) increased costs from −£99K to −£137K per month. This £38K increase needs an immediate commercial review.</div>
              <div class="t2 red" style="margin-top:6px;">Recovery target: £100K to £150K</div>
            </div>
          </div>
        </div>"""))

    # SLIDE 5
    slides.append(slide(5, total,
        header="""
        <h1>Scaling eSIMs and RevPoints targets £350K to £630K, with strong early signals</h1>
        <div class="sub">Two lifestyle products show enough momentum to warrant deliberate investment.</div>
        """,
        body=f"""
        <div class="row" style="flex:1;">
          <div class="col" style="gap:8px;">
            <div style="display:flex; gap:8px; flex:1; align-items:center;">
              <div style="flex:1;">{charts["esim"]}</div>
              <div style="flex:1;">{charts["revpoints"]}</div>
            </div>
          </div>
          <div class="col" style="gap:8px;">
            <div class="card bl" style="flex:1;">
              <div class="t2 blue">eSIMs: £12K to £105K in three months</div>
              <div class="t3">8.5x growth. Only 9 transactions in the dataset, so this is very early. Expanding to business travellers and targeting peak travel could generate <strong style="color:var(--blue);">£250K to £450K</strong>.</div>
            </div>
            <div class="card bl" style="flex:1;">
              <div class="t2 blue">RevPoints: £37K to £132K, no promotional spend</div>
              <div class="t3">3.6x organic growth. Expanding merchant partnerships is the natural next step. <strong style="color:var(--blue);">Target: £100K to £180K.</strong></div>
            </div>
            <div class="card">
              <div class="t4">Stays (Initiative 4): launched in July with £15K. The 30% cashback reduction should improve unit economics. Too early to size.</div>
            </div>
          </div>
        </div>"""))

    # SLIDE 6
    slides.append(slide(6, total,
        header="""
        <h1>FX spread pricing review could recover £200K to £350K of the steepest revenue decline</h1>
        <div class="sub">Three revenue lines declined a combined £713K. FX spread is the most controllable.</div>
        """,
        body=f"""
        <div class="row" style="flex:1;">
          <div class="col" style="justify-content:center;">{charts["fx"]}</div>
          <div class="col" style="gap:8px;">
            <div class="card rl" style="flex:1;">
              <div class="t2 red">FX spread: down 57%, from £398K to £173K</div>
              <div class="t3">Steepest structural decline in the dataset. Likely competitive pricing pressure or a shift in currency mix. A review by currency pair and plan tier is the next step. <strong>Recoverable: £200K to £350K.</strong></div>
            </div>
            <div class="card rl" style="flex:1;">
              <div class="t2 red">Interest income on cash: down £373K</div>
              <div class="t3">Cash at banks fell £215K, other financial assets fell £176K. Largely driven by external rate conditions. Balance optimisation could offset some of the decline.</div>
            </div>
            <div class="card">
              <div class="t4">Interchange fees: down £210K. Seasonal or structural. Worth monitoring but lower controllability.</div>
            </div>
          </div>
        </div>"""))

    # SLIDE 7
    slides.append(slide(7, total,
        header="""
        <h1>Three smaller interventions add £250K to £420K</h1>
        <div class="sub">Credit repricing, card production fix, and subscription upgrades each contribute meaningfully to the total.</div>
        """,
        body="""
        <div class="row" style="flex:1; gap:16px;">
          <div class="card" style="flex:1; display:flex; flex-direction:column;">
            <div class="t2 blue">Selective credit repricing: £80K to £150K</div>
            <div class="t3" style="flex:1;">Rate cuts (Initiative 1) reduced loan income in Romania (−£13K), Germany (−£7K), and Lithuania (−£11K). Germany further impacted by doubled provisions (Initiative 16, 5% to 10%). Not all cuts need to persist. Some markets may support higher rates without volume loss.</div>
          </div>
          <div class="card" style="flex:1; display:flex; flex-direction:column;">
            <div class="t2 red">Fix card production costs: £100K to £150K</div>
            <div class="t3" style="flex:1;">The new single vendor (Initiative 9) was supposed to reduce costs through consolidation. Instead, costs rose from −£99K to −£137K per month. Either renegotiate or consider reverting for part of the volume.</div>
          </div>
          <div class="card" style="flex:1; display:flex; flex-direction:column;">
            <div class="t2 blue">Subscription upgrades: £70K to £120K</div>
            <div class="t3" style="flex:1;">Ultra users generate £232 GP/user. Standard users generate £15. Converting 5% of Standard to Plus (roughly 5,600 users) adds £28/user = £155K at zero acquisition cost. Business users at £913 GP/user are even more valuable but the base is small (2,348 users).</div>
          </div>
        </div>"""))

    # SLIDE 8
    slides.append(slide(8, total,
        header="""
        <h1>Eight interventions total £1.95M to £3.15M. Supplementary plays close the gap to £4M.</h1>
        """,
        body=f"""
        <div class="chart-container" style="flex:1;">{charts["sizing"]}</div>
        <div class="card" style="padding:10px 18px;">
          <div class="t3">To reach <strong>£4M</strong>: execute all eight at the high end, plus grow the business segment (Scale plan has 172 users at £2,961 GP each), improve geographic ARPU in core EU markets (France, Romania, Poland at £18 to £32/user vs UK at £90), and refine bank payments pricing.</div>
        </div>"""))

    # SLIDE 9
    slides.append(slide(9, total,
        header='<h1>The first £1.5M can be captured within 90 days through four immediate actions</h1>',
        body="""
        <div class="row" style="gap:12px; flex:1; align-items:stretch;">
          <div class="hz"><div class="hz-h" style="background:var(--blue);">Now: four immediate actions, ~£1.5M</div><div class="hz-b">
            <div class="t3">Restructure vending machine eligibility and cap spend</div>
            <div class="t3">Complete card vendor cost migration across all card types</div>
            <div class="t3">Open commercial review with card production vendor</div>
            <div class="t3">Run FX spread pricing review by currency pair and plan</div>
          </div></div>
          <div class="hz"><div class="hz-h" style="background:#3B5BDB;">3 to 6 months: scale and convert, ~£1.0M</div><div class="hz-b">
            <div class="t3">Scale eSIM distribution with travel-season marketing</div>
            <div class="t3">Expand RevPoints merchant partnerships</div>
            <div class="t3">Run Standard-to-Plus subscription upgrade campaign</div>
          </div></div>
          <div class="hz"><div class="hz-h" style="background:#1864AB;">6 to 12 months: structural, ~£1.5M+</div><div class="hz-b">
            <div class="t3">Credit repricing by market based on competitive analysis</div>
            <div class="t3">Grow business segment via Scale plan and terminal rollout</div>
            <div class="t3">Localised pricing in top EU markets to close the ARPU gap</div>
          </div></div>
        </div>
        <div class="card" style="text-align:center; margin-top:12px; padding:14px;">
          <div class="t2" style="color:var(--text);">The first horizon captures roughly 40% of the £4M target. The highest-confidence interventions require no new investment, just operational decisions.</div>
        </div>"""))

    # SLIDE 10
    slides.append(slide(10, total,
        header="""
        <div class="tag" style="color:var(--text3);">Appendix</div>
        <h1>Assumptions and initiative mapping</h1>
        """,
        body="""
        <div class="row" style="flex:1; gap:16px;">
          <div class="card" style="flex:1;">
            <div class="t4" style="text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Key assumptions</div>
            <div class="t3" style="margin-bottom:5px;">amount_gbp is denominated in thousands as stated in the documentation</div>
            <div class="t3" style="margin-bottom:5px;">April covers only 7 days (24th to 30th) and is excluded from trend analysis</div>
            <div class="t3" style="margin-bottom:5px;">NAP status represents the final activation outcome during the 90-day window</div>
            <div class="t3" style="margin-bottom:5px;">All figures derived exclusively from the provided dataset</div>
            <div class="t3" style="margin-bottom:5px;">Recommendations assume current product mix and no major regulatory changes</div>
            <div class="t3">Vending machine savings assume partial restructuring, not full wind-down</div>
          </div>
          <div class="card" style="flex:1;">
            <div class="t4" style="text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Initiative mapping</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#1</strong> Credit rate cuts (RO, DE, LT): loan interest decline, slide 7</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#3</strong> eSIM launch: 8.5x revenue growth, slide 5</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#4</strong> Stays cashback reduction: £15K first month, slide 5</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#6</strong> Vending machine campaign: £2.8M cost, slide 3</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#8</strong> Card vendor cost changes: £331K savings, slide 4</div>
            <div class="t3" style="margin-bottom:4px;"><strong>#9</strong> New card production vendor: £38K cost increase, slide 4</div>
            <div class="t3"><strong>#16</strong> German loan provisions 5% to 10%: compounds credit decline, slide 7</div>
          </div>
        </div>"""))

    # Assemble
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{CSS}</style></head>
<body>{''.join(slides)}</body>
</html>"""

    OUTPUT_HTML.write_text(html)
    print(f"Slides written to {OUTPUT_HTML}")
    print(f"Total slides: {len(slides)}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    df = load_data()
    charts = generate_charts(df)
    build(charts)
