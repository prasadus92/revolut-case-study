"""
Revolut EIR case study: chart generation v3
Strict 2-colour palette: blue (#0075EB) + red (#EF4444)
All backgrounds: #0A0A0A. All text: white or #9A9A9A.
No purple, no green, no amber, no teal.
No emdashes in any text.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = Path(__file__).resolve().parent.parent / "dataset.csv"
CHART_DIR = Path(__file__).resolve().parent.parent / "charts" / "final"
CHART_DIR.mkdir(parents=True, exist_ok=True)

SCALE = 1_000
BG = "#0A0A0A"
BLUE = "#0075EB"
BLUE_LIGHT = "#3B9AFF"
RED = "#EF4444"
RED_LIGHT = "#F87171"
TEXT = "#FFFFFF"
MUTED = "#9A9A9A"
GRID = "#1E1E1E"
BORDER = "#2A2A2A"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "axes.edgecolor": BORDER, "axes.grid": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.alpha": 0.25, "grid.color": "#2A2A2A",
    "font.family": "sans-serif", "font.size": 13,
    "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.titlecolor": TEXT, "axes.labelsize": 12,
    "axes.labelcolor": MUTED, "xtick.color": MUTED,
    "ytick.color": MUTED, "text.color": TEXT,
    "figure.dpi": 200, "savefig.facecolor": BG,
})


def fmt(val, decimals=0):
    if abs(val) >= 1_000_000:
        return f"\u00a3{val/1_000_000:.{max(decimals,1)}f}M"
    if abs(val) >= 1_000:
        return f"\u00a3{val/1_000:.{decimals}f}K"
    return f"\u00a3{val:.{decimals}f}"


def load():
    df = pd.read_csv(DATA_PATH)
    if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
        df = df.drop(columns=[df.columns[0]])
    df["amount_gbp"] = pd.to_numeric(df["amount_gbp"], errors="coerce") * SCALE
    return df


def chart_monthly(df):
    """Slide 1: Monthly GP bars."""
    m = df.groupby("pnl_month")["amount_gbp"].sum()
    vals = [m["2024-05"], m["2024-06"], m["2024-07"]]

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=BLUE, width=0.42, zorder=3)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 25_000, fmt(h),
                ha="center", va="bottom", fontweight="bold", fontsize=14, color=TEXT)
    ax.annotate(f"\u2212\u00a3{abs(vals[2]-vals[0])/1000:.0f}K",
                xy=(2, vals[2]), xytext=(1.5, vals[0]*0.82),
                fontsize=16, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=2))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_ylim(0, max(vals) * 1.2)
    ax.set_ylabel("")
    fig.tight_layout(pad=1.0)
    fig.savefig(CHART_DIR / "monthly_gp.png", bbox_inches="tight")
    plt.close()
    print("  monthly_gp")


def chart_bridge(df):
    """Slide 2: May to July waterfall bridge by L2 category."""
    months_may = df[df["pnl_month"] == "2024-05"]
    months_jul = df[df["pnl_month"] == "2024-07"]

    items = []
    name_map = {
        "Interest Income": "Interest\nincome",
        "FX": "FX\nrevenue",
        "Card Payments": "Card\npayments",
        "Subscriptions": "Subscriptions",
        "Other": "Onboarding\n& campaigns",
        "Lifestyle": "Lifestyle",
        "Bank Payments": "Bank\npayments",
        "Credit": "Credit",
        "Savings": "Savings",
    }
    for l2 in df["account_level_2"].unique():
        may_v = months_may[months_may["account_level_2"] == l2]["amount_gbp"].sum()
        jul_v = months_jul[months_jul["account_level_2"] == l2]["amount_gbp"].sum()
        delta = jul_v - may_v
        if abs(delta) > 15000:
            items.append((name_map.get(l2, l2), delta))
    items.sort(key=lambda x: x[1])

    may_total = months_may["amount_gbp"].sum()
    jul_total = months_jul["amount_gbp"].sum()

    labels = ["May\nGP"] + [n for n, _ in items] + ["Jul\nGP"]
    deltas = [may_total] + [d for _, d in items] + [jul_total]

    n = len(labels)
    fig, ax = plt.subplots(figsize=(12.5, 4.8))
    x = np.arange(n)

    running = 0
    for i in range(n):
        if i == 0:
            ax.bar(x[i], deltas[i], color=BLUE, width=0.52, zorder=3)
            ax.text(x[i], deltas[i] + 25000, fmt(deltas[i]),
                    ha="center", fontweight="bold", fontsize=12, color=TEXT)
            running = deltas[i]
        elif i == n - 1:
            ax.bar(x[i], deltas[i], color=BLUE, width=0.52, zorder=3)
            ax.text(x[i], deltas[i] + 25000, fmt(deltas[i]),
                    ha="center", fontweight="bold", fontsize=12, color=TEXT)
        else:
            d = deltas[i]
            color = BLUE_LIGHT if d > 0 else RED
            bottom = running + d if d < 0 else running
            ax.bar(x[i], abs(d), bottom=bottom, color=color, width=0.52, zorder=3, alpha=1.0)

            sign = "+" if d > 0 else ""
            label_text = f"{sign}{fmt(d)}"
            if abs(d) > 80000:
                ax.text(x[i], bottom + abs(d)/2, label_text,
                        ha="center", va="center", fontweight="bold", fontsize=9, color=TEXT)
            else:
                y_pos = (bottom + abs(d) + 18000) if d > 0 else (bottom - 18000)
                va = "bottom" if d > 0 else "top"
                ax.text(x[i], y_pos, label_text, ha="center", va=va,
                        fontweight="bold", fontsize=8, color=BLUE_LIGHT if d > 0 else RED_LIGHT)

            # Connector line from previous bar
            ax.plot([x[i-1] + 0.28, x[i] - 0.28],
                    [running, running], color=BORDER, linewidth=0.8, zorder=2, linestyle=":")
            running += d

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_ylim(0, may_total * 1.14)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "bridge.png", bbox_inches="tight")
    plt.close()
    print("  bridge")


def chart_vending_cost(df):
    """Slide 3: Vending machine monthly cost (bars shown as positive for readability)."""
    vm = df[df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
    vm_m = vm.groupby("pnl_month")["amount_gbp"].sum()
    vals = [abs(vm_m.get("2024-05", 0)), abs(vm_m.get("2024-06", 0)), abs(vm_m.get("2024-07", 0))]

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=RED, width=0.42, zorder=3, alpha=1.0)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 12000, fmt(v),
                ha="center", fontweight="bold", fontsize=12, color=TEXT)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_ylim(0, max(vals) * 1.18)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "vending_cost.png", bbox_inches="tight")
    plt.close()
    print("  vending_cost")


def chart_nap_economics(df):
    """Slide 3: GP per user, three scenarios."""
    nap_gp = df.groupby("is_nap")["amount_gbp"].sum()
    nap_users = df.groupby("is_nap")["user_id"].nunique()
    non_vm = df[~df["account_level_4"].str.contains("Vending Machine", case=False, na=False)]
    nap_gp_clean = non_vm.groupby("is_nap")["amount_gbp"].sum()

    cats = ["Activated\n(with reward cost)", "Activated\n(excl. reward)", "Not activated\n(excl. reward)"]
    gp_per = [
        nap_gp["Napped"] / nap_users["Napped"],
        nap_gp_clean["Napped"] / nap_users["Napped"],
        nap_gp_clean["Not Napped"] / nap_users["Not Napped"],
    ]
    colors = [BLUE, BLUE_LIGHT, BLUE_LIGHT]

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    bars = ax.bar(cats, gp_per, color=colors, width=0.48, zorder=3, alpha=1.0)
    for bar, v in zip(bars, gp_per):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2,
                f"\u00a3{v:.0f}", ha="center", va="bottom",
                fontweight="bold", fontsize=14, color=TEXT)
    ax.axhline(0, color=BORDER, linewidth=0.5)
    ax.set_ylabel("")
    ax.set_ylim(0, max(gp_per) * 1.2)
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "nap_economics.png", bbox_inches="tight")
    plt.close()
    print("  nap_economics")


def chart_fx(df):
    """Slide 4: FX revenue by component, monthly."""
    fx = df[df["account_level_2"] == "FX"]
    months = ["2024-05", "2024-06", "2024-07"]
    fx_l3 = fx.groupby(["pnl_month", "account_level_3"])["amount_gbp"].sum().unstack().fillna(0)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    x = np.arange(3)
    w = 0.22
    # Use blue at different opacities instead of different colours
    items = [("FX Spread", BLUE, 1.0), ("FX Fees", BLUE, 0.6), ("FX Mark-up", BLUE, 0.35)]

    for i, (cat, color, alpha) in enumerate(items):
        if cat in fx_l3.columns:
            vals = [fx_l3.loc[m, cat] if m in fx_l3.index else 0 for m in months]
            bars = ax.bar(x + i*w, vals, w, label=cat.replace("FX ", ""),
                          color=color, zorder=3, alpha=alpha)
            for bar, v in zip(bars, vals):
                if v > 40000:
                    ax.text(bar.get_x() + bar.get_width()/2, v + 5000,
                            fmt(v), ha="center", fontsize=7, color=MUTED)

    ax.set_xticks(x + w)
    ax.set_xticklabels(["May", "Jun", "Jul"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.legend(fontsize=9, framealpha=0, labelcolor=MUTED)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "fx_decline.png", bbox_inches="tight")
    plt.close()
    print("  fx_decline")


def chart_card_costs(df):
    """Slide 5: Card payment costs by L3, monthly. Costs shown as negative."""
    card = df[df["account_level_2"] == "Card Payments"]
    months = ["2024-05", "2024-06", "2024-07"]
    card_l3 = card.groupby(["pnl_month", "account_level_3"])["amount_gbp"].sum().unstack().fillna(0)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    x = np.arange(3)
    w = 0.2

    items = [
        ("Top-ups", RED, 1.0),
        ("ATM", RED, 0.6),
        ("Interchange Fees", BLUE, 0.85),
        ("POS Charges", BLUE, 0.4),
    ]
    for i, (cat, color, alpha) in enumerate(items):
        if cat in card_l3.columns:
            vals = [card_l3.loc[m, cat] if m in card_l3.index else 0 for m in months]
            ax.bar(x + i*w, vals, w, label=cat, color=color, zorder=3, alpha=alpha)

    ax.set_xticks(x + w * 1.5)
    ax.set_xticklabels(["May", "Jun", "Jul"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.axhline(0, color=BORDER, linewidth=0.5)
    ax.legend(fontsize=8, framealpha=0, labelcolor=MUTED, loc="lower left")
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "card_costs.png", bbox_inches="tight")
    plt.close()
    print("  card_costs")


def chart_card_prod(df):
    """Slide 5: Card production costs worsening."""
    cp = df[df["account_level_4"].str.contains("Card Production", case=False, na=False)]
    months = ["2024-05", "2024-06", "2024-07"]
    cp_m = cp.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)

    fig, ax = plt.subplots(figsize=(4.5, 2.8))
    vals = [abs(v) for v in cp_m.values]
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=RED, width=0.42, zorder=3, alpha=1.0)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2500, fmt(v),
                ha="center", fontsize=10, fontweight="bold", color=TEXT)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_ylim(0, max(vals) * 1.2)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "card_prod.png", bbox_inches="tight")
    plt.close()
    print("  card_prod")


def chart_credit(df):
    """Slide 6: Credit GP by country, monthly. Blue at different opacities."""
    months = ["2024-05", "2024-06", "2024-07"]
    countries = [("Romania", 1.0), ("Germany", 0.6), ("Lithuania", 0.35)]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    x = np.arange(3)
    w = 0.22
    for i, (country, alpha) in enumerate(countries):
        cr = df[(df["account_level_2"] == "Credit") & (df["user_country"] == country)]
        cr_m = cr.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)
        ax.bar(x + i*w, cr_m.values, w, label=country, color=BLUE, zorder=3, alpha=alpha)

    ax.set_xticks(x + w)
    ax.set_xticklabels(["May", "Jun", "Jul"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.legend(fontsize=9, framealpha=0, labelcolor=MUTED)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "credit.png", bbox_inches="tight")
    plt.close()
    print("  credit")


def chart_esim(df):
    """Slide 7: eSIM revenue growth."""
    esim = df[df["account_level_4"].str.contains("eSIM|eSim", case=False, na=False)]
    months = ["2024-05", "2024-06", "2024-07"]
    esim_m = esim.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)

    fig, ax = plt.subplots(figsize=(5, 3.2))
    vals = esim_m.values
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=BLUE, width=0.42, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2000,
                fmt(v), ha="center", fontweight="bold", fontsize=12, color=TEXT)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    mv = max(vals)
    ax.set_ylim(0, mv + mv * 0.22 if mv > 0 else 1000)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "esim.png", bbox_inches="tight")
    plt.close()
    print("  esim")


def chart_revpoints(df):
    """Slide 7: RevPoints growth."""
    rp = df[df["account_level_3"] == "RevPoints"]
    months = ["2024-05", "2024-06", "2024-07"]
    rp_m = rp.groupby("pnl_month")["amount_gbp"].sum().reindex(months).fillna(0)

    fig, ax = plt.subplots(figsize=(5, 3.2))
    vals = rp_m.values
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=BLUE, width=0.42, zorder=3, alpha=1.0)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2000,
                fmt(v), ha="center", fontweight="bold", fontsize=11, color=TEXT)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_ylim(0, max(vals) * 1.22)
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "revpoints.png", bbox_inches="tight")
    plt.close()
    print("  revpoints")


def chart_plans(df):
    """Slide 8: GP per user by plan, horizontal bars."""
    plans = ["STANDARD", "PLUS", "PREMIUM", "METAL", "ULTRA"]
    gp = df[df["user_plan"].isin(plans)].groupby("user_plan")["amount_gbp"].sum()
    users = df[df["user_plan"].isin(plans)].groupby("user_plan")["user_id"].nunique()
    per_user = (gp / users).reindex(plans)

    fig, ax = plt.subplots(figsize=(6, 3.2))
    y_labels = ["Standard", "Plus", "Premium", "Metal", "Ultra"]
    bars = ax.barh(y_labels, per_user.values, color=BLUE, height=0.45, zorder=3)
    for bar, v in zip(bars, per_user.values):
        ax.text(bar.get_width() + 4, bar.get_y() + bar.get_height()/2,
                f"\u00a3{v:.0f}", ha="left", va="center",
                fontweight="bold", fontsize=12, color=TEXT)
    ax.set_xlim(0, per_user.max() * 1.2)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"\u00a3{x:.0f}"))
    ax.set_ylabel("")
    fig.tight_layout(pad=0.8)
    fig.savefig(CHART_DIR / "plan_gp.png", bbox_inches="tight")
    plt.close()
    print("  plan_gp")


def chart_sizing(df):
    """Slide 9: Opportunity sizing with horizontal bars and ranges."""
    levers = [
        ("Restructure vending\nmachine campaign", 800, 1200),
        ("Complete card\nvendor migration", 350, 550),
        ("Scale eSIM\ndistribution", 250, 450),
        ("Recover FX\nspread pricing", 200, 350),
        ("Grow RevPoints\nand lifestyle", 100, 180),
        ("Fix card\nproduction costs", 100, 150),
        ("Reprice credit\nproducts", 80, 150),
        ("Subscription\nupgrade campaign", 70, 120),
    ]

    fig, ax = plt.subplots(figsize=(11, 5.2))
    y = np.arange(len(levers))
    names = [l[0] for l in levers]
    mids = [(l[1] + l[2]) / 2 for l in levers]
    lows = [l[1] for l in levers]
    highs = [l[2] for l in levers]

    ax.barh(y, mids, color=BLUE, height=0.5, zorder=3, alpha=1.0)

    for i in range(len(levers)):
        ax.plot([lows[i], highs[i]], [y[i], y[i]], color=TEXT, linewidth=2.5, zorder=4)
        ax.plot([lows[i]], [y[i]], "|", color=TEXT, markersize=10, zorder=4)
        ax.plot([highs[i]], [y[i]], "|", color=TEXT, markersize=10, zorder=4)
        ax.text(highs[i] + 30, y[i], f"\u00a3{mids[i]/1000:.1f}M",
                ha="left", va="center", fontweight="bold", fontsize=10, color=TEXT)

    ax.axvline(4000, color=RED, linewidth=2.5, linestyle="--", zorder=5)
    ax.text(4020, -0.7, "\u00a34M target", color=RED, fontweight="bold", fontsize=12)

    total_mid = sum(mids)
    total_low = sum(lows)
    total_high = sum(highs)
    ax.text(total_mid + 30, len(levers) + 0.1,
            f"Total: \u00a3{total_mid/1000:.1f}M  (range \u00a3{total_low/1000:.1f}M \u2013 \u00a3{total_high/1000:.1f}M)",
            fontsize=11, fontweight="bold", color=MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"\u00a3{x/1000:.1f}M" if x >= 1000 else f"\u00a3{x:.0f}K"))
    ax.set_xlim(0, 4600)
    ax.set_ylabel("")
    fig.tight_layout(pad=1.0)
    fig.savefig(CHART_DIR / "sizing.png", bbox_inches="tight")
    plt.close()
    print("  sizing")


def main():
    df = load()
    print("Generating v3 charts (strict 2-colour palette)...")
    chart_monthly(df)
    chart_bridge(df)
    chart_vending_cost(df)
    chart_nap_economics(df)
    chart_fx(df)
    chart_card_costs(df)
    chart_card_prod(df)
    chart_credit(df)
    chart_esim(df)
    chart_revpoints(df)
    chart_plans(df)
    chart_sizing(df)
    print(f"All saved to {CHART_DIR}")


if __name__ == "__main__":
    main()
