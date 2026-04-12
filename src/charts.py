"""
Chart generation for the Revolut GP L90D presentation.

All charts render at 300 DPI with consistent styling.
Charts are saved as PNG and embedded into HTML slides via base64.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from design import (
    WHITE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY, BORDER,
    C_BLUE, C_BLUE2, C_BLUE3, C_RED, C_RED2, C_GREEN,
)

# ─────────────────────────────────────────────────────────────────────────
# MATPLOTLIB DEFAULTS
# ─────────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": WHITE,
    "axes.facecolor": WHITE,
    "axes.edgecolor": BORDER,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.alpha": 0.4,
    "grid.color": BORDER,
    "grid.linewidth": 0.6,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "sans-serif"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlecolor": TEXT_PRIMARY,
    "axes.labelsize": 10,
    "axes.labelcolor": TEXT_SECONDARY,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
    "xtick.labelsize": 10,
    "ytick.labelsize": 9,
    "text.color": TEXT_PRIMARY,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.facecolor": WHITE,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})


def fmt(val, decimals=0):
    """Format a currency value for chart labels."""
    sign = "\u2212" if val < 0 else ""
    av = abs(val)
    if av >= 1_000_000:
        return f"{sign}\u00a3{av / 1_000_000:.{max(decimals, 1)}f}M"
    if av >= 1_000:
        return f"{sign}\u00a3{av / 1_000:.{decimals}f}K"
    return f"{sign}\u00a3{av:.{decimals}f}"


# ─────────────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────

def waterfall(df, out_dir: Path):
    """GP bridge from May to July by account_level_2."""
    may = df[df.pnl_month == "2024-05"]
    jul = df[df.pnl_month == "2024-07"]
    may_l2 = may.groupby("account_level_2").amount_gbp.sum()
    jul_l2 = jul.groupby("account_level_2").amount_gbp.sum()
    changes = (jul_l2 - may_l2).dropna()
    changes = changes[changes.abs() > 10000].sort_values()

    names = {
        "Interest Income": "Interest\nincome", "FX": "FX\nrevenue",
        "Subscriptions": "Subs", "Bank Payments": "Bank\npayments",
        "Credit": "Credit", "Market Making PnL": "Mkt\nmaking",
        "Other": "Campaigns &\nonboarding", "Savings": "Savings",
        "Card Payments": "Card\npayments", "Lifestyle": "Lifestyle",
        "Treasury Services": "Treasury",
    }

    may_t = may.amount_gbp.sum()
    jul_t = jul.amount_gbp.sum()
    labels = ["May GP"] + [names.get(c, c) for c in changes.index] + ["Jul GP"]
    deltas = [may_t] + list(changes.values) + [jul_t]
    n = len(labels)

    fig, ax = plt.subplots(figsize=(12.5, 4.2))
    x = np.arange(n)
    running = 0

    for i in range(n):
        if i == 0 or i == n - 1:
            ax.bar(x[i], deltas[i], color=C_BLUE, width=0.52, zorder=3)
            ax.text(x[i], deltas[i] + 30000, fmt(deltas[i]),
                    ha="center", fontweight="bold", fontsize=11, color=TEXT_PRIMARY)
            if i == 0:
                running = deltas[i]
        else:
            d = deltas[i]
            colour = C_GREEN if d > 0 else C_RED
            bottom = running + d if d < 0 else running
            ax.bar(x[i], abs(d), bottom=bottom, color=colour, width=0.52,
                   zorder=3, alpha=0.85)
            sign = "+" if d > 0 else ""
            txt = f"{sign}{fmt(d)}"
            if abs(d) > 90000:
                ax.text(x[i], bottom + abs(d) / 2, txt, ha="center",
                        va="center", fontweight="bold", fontsize=9,
                        color=WHITE)
            else:
                y = (bottom + abs(d) + 22000) if d > 0 else (bottom - 22000)
                va = "bottom" if d > 0 else "top"
                ax.text(x[i], y, txt, ha="center", va=va,
                        fontweight="bold", fontsize=8,
                        color=C_GREEN if d > 0 else C_RED)
            ax.plot([x[i - 1] + 0.28, x[i] - 0.28],
                    [running, running], color=BORDER, lw=0.7, ls=":", zorder=2)
            running += d

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.set_ylim(0, may_t * 1.12)
    ax.set_ylabel("")
    fig.savefig(out_dir / "waterfall.png")
    plt.close()


def nap_economics(df, out_dir: Path):
    """GP per user for NAP analysis (slide 3)."""
    nap_gp = df.groupby("is_nap").amount_gbp.sum()
    nap_u = df.groupby("is_nap").user_id.nunique()
    nv = df[~df.account_level_4.str.contains("Vending Machine", case=False, na=False)]
    nv_gp = nv.groupby("is_nap").amount_gbp.sum()
    nv_u = nv.groupby("is_nap").user_id.nunique()

    cats = ["Activated\n(incl. reward)", "Activated\n(excl. reward)",
            "Not activated\n(excl. reward)"]
    vals = [nap_gp["Napped"] / nap_u["Napped"],
            nv_gp["Napped"] / nv_u["Napped"],
            nv_gp["Not Napped"] / nv_u["Not Napped"]]

    fig, ax = plt.subplots(figsize=(5.5, 4.0))
    bars = ax.bar(cats, vals, color=[C_BLUE, C_BLUE2, C_BLUE3],
                  width=0.55, zorder=3, edgecolor=WHITE, linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 3,
                f"\u00a3{v:.0f}", ha="center", va="bottom",
                fontweight="bold", fontsize=15, color=TEXT_PRIMARY)
    ax.set_ylim(0, max(vals) * 1.22)
    ax.set_ylabel("GP per user (L90D)", fontsize=10, color=TEXT_SECONDARY)
    fig.savefig(out_dir / "nap.png")
    plt.close()
    return vals


def fx_components(df, out_dir: Path):
    """FX revenue by component, monthly (slide 4)."""
    months = ["2024-05", "2024-06", "2024-07"]
    fx = df[df.account_level_2 == "FX"]
    fx_l3 = fx.groupby(["pnl_month", "account_level_3"]).amount_gbp.sum().unstack().fillna(0)

    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    x = np.arange(3)
    w = 0.24
    for i, (cat, colour) in enumerate([
        ("FX Spread", C_BLUE), ("FX Fees", C_BLUE2), ("FX Mark-up", C_BLUE3)
    ]):
        if cat in fx_l3.columns:
            vals = [fx_l3.loc[m, cat] if m in fx_l3.index else 0 for m in months]
            bars = ax.bar(x + i * w, vals, w, label=cat.replace("FX ", ""),
                          color=colour, zorder=3)
            for bar, v in zip(bars, vals):
                if v > 50000:
                    ax.text(bar.get_x() + bar.get_width() / 2, v + 8000,
                            fmt(v), ha="center", fontsize=8, color=TEXT_SECONDARY)
    ax.set_xticks(x + w)
    ax.set_xticklabels(["May", "Jun", "Jul"], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.legend(fontsize=9, framealpha=0.95, edgecolor=BORDER,
              loc="upper right", borderpad=0.5)
    ax.set_ylabel("")
    fig.savefig(out_dir / "fx.png")
    plt.close()


def card_costs(df, out_dir: Path):
    """Card payment costs by L3, monthly (slide 5)."""
    months = ["2024-05", "2024-06", "2024-07"]
    cd = df[df.account_level_2 == "Card Payments"]
    cl3 = cd.groupby(["pnl_month", "account_level_3"]).amount_gbp.sum().unstack().fillna(0)

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    x = np.arange(3)
    w = 0.19
    for i, (cat, colour) in enumerate([
        ("Top-ups", C_RED), ("ATM", C_RED2),
        ("Interchange Fees", C_BLUE), ("POS Charges", C_BLUE2)
    ]):
        if cat in cl3.columns:
            vals = [cl3.loc[m, cat] if m in cl3.index else 0 for m in months]
            bars = ax.bar(x + i * w, vals, w, label=cat, color=colour,
                          zorder=3, alpha=0.9)
            # Add value labels on positive bars only (negative labels overlap)
            for bar, v in zip(bars, vals):
                if v > 80000:
                    ax.text(bar.get_x() + bar.get_width() / 2, v + 20000,
                            fmt(v), ha="center", fontsize=7,
                            color=TEXT_SECONDARY, fontweight="bold")
    ax.set_xticks(x + w * 1.5)
    ax.set_xticklabels(["May", "Jun", "Jul"], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.axhline(0, color=TEXT_PRIMARY, lw=0.5)
    # Legend placed outside chart at top-left, horizontal
    ax.legend(fontsize=8, framealpha=0.95, edgecolor=BORDER,
              loc="upper left", ncol=2, borderpad=0.5,
              bbox_to_anchor=(0.0, 1.15))
    ax.set_ylabel("")
    fig.subplots_adjust(top=0.85)
    fig.savefig(out_dir / "card_costs.png")
    plt.close()


def card_production(df, out_dir: Path):
    """Card production cost trend (slide 5)."""
    cp = df[df.account_level_4.str.contains("Card Production", case=False, na=False)]
    months = ["2024-05", "2024-06", "2024-07"]
    cpm = cp.groupby("pnl_month").amount_gbp.sum().reindex(months).fillna(0)

    fig, ax = plt.subplots(figsize=(4.5, 3.4))
    vals = [abs(v) for v in cpm.values]
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=C_RED,
                  width=0.48, zorder=3, alpha=0.85)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2500, fmt(v),
                ha="center", fontsize=11, fontweight="bold", color=TEXT_PRIMARY)
    ax.set_ylim(0, max(vals) * 1.2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.set_ylabel("Monthly cost", fontsize=10, color=TEXT_SECONDARY)
    fig.savefig(out_dir / "card_prod.png")
    plt.close()


def esim_revpoints(df, out_dir: Path):
    """eSIM and RevPoints growth - both combined AND separate charts."""
    months = ["2024-05", "2024-06", "2024-07"]
    esim = df[df.account_level_4.str.contains("eSIM|eSim", case=False, na=False)]
    em = esim.groupby("pnl_month").amount_gbp.sum().reindex(months).fillna(0)
    rp = df[df.account_level_3 == "RevPoints"]
    rm = rp.groupby("pnl_month").amount_gbp.sum().reindex(months).fillna(0)

    # Combined (kept for backward compat)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 4.0))
    for ax, vals, title, colour in [
        (a1, em.values, "eSIM revenue", C_BLUE),
        (a2, rm.values, "RevPoints revenue", C_BLUE2),
    ]:
        bars = ax.bar(["May", "Jun", "Jul"], vals, color=colour,
                      width=0.52, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + max(vals) * 0.03,
                    fmt(v), ha="center", fontweight="bold",
                    fontsize=12, color=TEXT_PRIMARY)
        ax.set_title(title, fontsize=13, fontweight="bold",
                     color=TEXT_PRIMARY, pad=10)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
        ax.set_ylim(0, max(vals) * 1.22)
    fig.tight_layout(w_pad=3)
    fig.savefig(out_dir / "esim_revpoints.png")
    plt.close()

    # Separate eSIM chart (compact for left column in slide 6)
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    vals = em.values
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=C_BLUE, width=0.52, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(vals) * 0.03,
                fmt(v), ha="center", fontweight="bold", fontsize=12, color=TEXT_PRIMARY)
    ax.set_title("eSIM revenue", fontsize=13, fontweight="bold", color=TEXT_PRIMARY, pad=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.set_ylim(0, max(vals) * 1.22)
    fig.savefig(out_dir / "esim.png")
    plt.close()

    # Separate RevPoints chart (compact for left column in slide 6)
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    vals = rm.values
    bars = ax.bar(["May", "Jun", "Jul"], vals, color=C_BLUE2, width=0.52, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(vals) * 0.03,
                fmt(v), ha="center", fontweight="bold", fontsize=12, color=TEXT_PRIMARY)
    ax.set_title("RevPoints revenue", fontsize=13, fontweight="bold", color=TEXT_PRIMARY, pad=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.set_ylim(0, max(vals) * 1.22)
    fig.savefig(out_dir / "revpoints.png")
    plt.close()


def sizing(df, out_dir: Path):
    """Intervention sizing horizontal bar chart (slide 8)."""
    levers = [
        ("Restructure vending\nmachine campaign", 800, 1300),
        ("Scale eSIM\ndistribution", 190, 500),
        ("Recover FX spread\npricing", 170, 340),
        ("Complete card vendor\nmigration", 100, 200),
        ("Optimise bank\npayment pricing", 90, 180),
        ("Fix card production\ncosts", 80, 115),
        ("Subscription upgrade\ncampaign", 31, 156),
        ("Selective credit\nrepricing", 45, 70),
    ]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    y = np.arange(len(levers))
    lows = [l[1] for l in levers]
    highs = [l[2] for l in levers]
    mids = [(l[1] + l[2]) / 2 for l in levers]

    ax.barh(y, mids, color=C_BLUE, height=0.48, zorder=3, alpha=0.85)
    for i in range(len(levers)):
        ax.plot([lows[i], highs[i]], [y[i], y[i]], color=TEXT_PRIMARY,
                lw=2, zorder=4)
        ax.plot([lows[i]], [y[i]], "|", color=TEXT_PRIMARY,
                markersize=8, zorder=4)
        ax.plot([highs[i]], [y[i]], "|", color=TEXT_PRIMARY,
                markersize=8, zorder=4)
        lo_str = f"\u00a3{lows[i]}K" if lows[i] < 1000 else f"\u00a3{lows[i] / 1000:.1f}M"
        hi_str = f"\u00a3{highs[i]}K" if highs[i] < 1000 else f"\u00a3{highs[i] / 1000:.1f}M"
        ax.text(highs[i] + 25, y[i],
                f"{lo_str}\u2013{hi_str}",
                ha="left", va="center", fontweight="bold",
                fontsize=10, color=TEXT_PRIMARY)

    # £4M target line with label at top
    ax.axvline(4000, color=C_RED, lw=2.5, ls="--", zorder=5, alpha=0.8)
    ax.annotate("\u00a34M target", xy=(4000, -0.5), fontsize=10,
                fontweight="bold", color=C_RED, ha="center", va="bottom")

    ax.set_yticks(y)
    ax.set_yticklabels([l[0] for l in levers], fontsize=10)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"\u00a3{v / 1000:.1f}M" if v >= 1000 else f"\u00a3{v:.0f}K"))
    ax.set_xlim(0, 4500)
    ax.set_ylim(len(levers) - 0.5, -0.8)
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out_dir / "sizing.png")
    plt.close()


def generate_all(df, out_dir: Path):
    """Generate all charts and return any computed values needed by slides."""
    out_dir.mkdir(parents=True, exist_ok=True)
    print("  waterfall...")
    waterfall(df, out_dir)
    print("  nap_economics...")
    nap_vals = nap_economics(df, out_dir)
    print("  fx_components...")
    fx_components(df, out_dir)
    print("  card_costs...")
    card_costs(df, out_dir)
    print("  card_production...")
    card_production(df, out_dir)
    print("  esim_revpoints...")
    esim_revpoints(df, out_dir)
    print("  sizing...")
    sizing(df, out_dir)
    print(f"  All charts saved to {out_dir}")
    return {"nap_vals": nap_vals}
