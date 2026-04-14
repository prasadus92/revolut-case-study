"""
Revolut GP L90D - final HTML slide deck v5.
1280x720px slides. Rendered to PDF via Puppeteer.

Design principles:
- 16px base body text. 18px card titles. 28px slide titles.
- Two card semantics: INSIGHT (what data shows) vs ACTION (what to do)
- Colour: blue=actionable, green=growth, red=risk, gray=monitor
- Logical grouping with consistent vertical centering
- 40px padding on all sides

Usage: python3 src/build_html.py && node src/render_pdf.js
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "output" / "charts_final"
OUTPUT = ROOT / "output" / "slides.html"

def img(n):
    return f"data:image/png;base64,{base64.b64encode((CHARTS/n).read_bytes()).decode()}"

# ── Icons (Lucide-style SVG, 18x18) ────────────────────────────────────
def ico(path, color="currentColor", size=18):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0">{path}</svg>'

ICO_DOWN = ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>')
ICO_UP = ico('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>')
ICO_ALERT = ico('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>')
ICO_CHECK = ico('<polyline points="20 6 9 17 4 12"/>')
ICO_TARGET = ico('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>')
ICO_TOOL = ico('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>')
ICO_USERS = ico('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>')
ICO_DOLLAR = ico('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>')
ICO_GLOBE = ico('<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>')
ICO_ZAP = ico('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>')
ICO_SHIELD = ico('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>')


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg:#FFF;--text:#1A1A2E;--text2:#4A5568;--text3:#94A3B8;
  --blue:#0B84F6;--blue-bg:#EBF5FF;
  --red:#DC2626;--red-bg:#FEF2F2;
  --green:#059669;--green-bg:#ECFDF5;
  --gray-bg:#F7F8FA;--border:#E2E8F0;
  --shadow:0 1px 3px rgba(0,0,0,0.06);
  --r:8px;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;}

/* Slide frame with 40px padding all sides */
.slide{width:1280px;height:720px;position:relative;overflow:hidden;background:var(--bg);padding:40px;display:flex;flex-direction:column;page-break-after:always;}
.slide::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--blue);}
.slide:last-child{page-break-after:auto;}

/* Typography - 16px base */
.tag{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--blue);margin-bottom:2px;}
h1{font-size:28px;font-weight:700;line-height:1.22;color:var(--text);letter-spacing:-0.3px;}
.sub{font-size:15px;line-height:1.5;color:var(--text2);margin-top:4px;}
.fn{position:absolute;bottom:10px;left:40px;right:80px;font-size:9px;line-height:1.3;color:var(--text3);}
.pn{position:absolute;bottom:10px;right:40px;font-size:9px;color:var(--text3);}

/* Layout */
.row{display:flex;gap:14px;}
.col{display:flex;flex-direction:column;gap:10px;}
.fill{flex:1;}
.vc{justify-content:center;}
.mt{margin-top:10px;}
.section-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--text2);margin-bottom:6px;}

/* Stat cards */
.stats{display:grid;gap:20px;margin:14px 0 8px;}
.stats-4{grid-template-columns:repeat(4,1fr);}
.stats-2x2{grid-template-columns:repeat(2,1fr);}
.stat{padding:14px 18px 12px;background:var(--gray-bg);border-radius:var(--r);border-top:3px solid var(--text);box-shadow:var(--shadow);}
.stat-val{font-size:36px;font-weight:800;letter-spacing:-1px;line-height:1.1;}
.stat-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);margin-top:6px;}
.stat-detail{font-size:10px;color:var(--text3);margin-top:3px;}

/* INSIGHT card (what data shows) - solid left border */
.card{background:var(--blue-bg);border:1px solid var(--border);border-left:4px solid var(--blue);border-radius:var(--r);padding:12px 16px;box-shadow:var(--shadow);}
.card.red{background:var(--red-bg);border-left-color:var(--red);}
.card.green{background:var(--green-bg);border-left-color:var(--green);}
.card.gray{background:var(--gray-bg);border-left-color:var(--text3);}

/* ACTION card (what to do) - dashed left border + slightly different bg */
.card.action{border-left-style:dashed;border-left-width:4px;background:#F0F7FF;}
.card.action.green{background:#E6FAF0;}

.card-h{font-size:18px;font-weight:700;color:var(--blue);margin-bottom:5px;line-height:1.3;display:flex;align-items:center;gap:8px;}
.card.red .card-h{color:var(--red);}
.card.green .card-h{color:var(--green);}
.card.gray .card-h{color:var(--text2);}
.card-b{font-size:15px;line-height:1.5;color:var(--text2);}
.card-b strong{color:var(--text);}
.hl{color:var(--blue);font-weight:600;}
.neg{color:var(--red);font-weight:600;}
.pos{color:var(--green);font-weight:600;}

/* Callout */
.callout{background:var(--blue);color:white;padding:12px 22px;border-radius:var(--r);font-size:16px;font-weight:700;}

/* Numbered bullets */
.bullet{display:flex;gap:14px;align-items:flex-start;}
.bullet-n{width:32px;height:32px;border-radius:50%;background:var(--blue);color:white;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;flex-shrink:0;}
.bullet-t{font-size:15px;line-height:1.55;color:var(--text2);}
.bullet-t strong{color:var(--text);font-weight:600;}

/* Chart */
.chart{display:flex;align-items:center;justify-content:center;}
.chart img{max-width:100%;height:auto;}

/* Horizons */
.hz{flex:1;border-radius:var(--r);overflow:hidden;border:1px solid var(--border);box-shadow:var(--shadow);display:flex;flex-direction:column;}
.hz-badge{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;}
.hz-body{padding:16px;background:white;font-size:16px;line-height:1.55;color:var(--text);}
.hz-body li{margin-bottom:10px;margin-left:16px;list-style:disc;}
.hz-body li strong{font-weight:600;}

/* Summary bar - flows with content */
.summary{background:var(--gray-bg);border:1px solid var(--border);border-radius:var(--r);padding:12px 18px;font-size:15px;line-height:1.5;color:var(--text);margin-top:12px;}
.summary.blue{background:var(--blue-bg);border-color:var(--blue);}
.summary strong{font-weight:600;}

/* Bottom bar - fixed position above footnote, consistent across slides */
.bottom-bar{position:absolute;bottom:32px;left:40px;right:40px;border-radius:var(--r);padding:12px 20px;font-size:15px;line-height:1.5;box-shadow:var(--shadow);}
.bottom-bar.accent{background:var(--blue);color:white;}
.bottom-bar.accent strong{color:white;}
.bottom-bar.blue-bg{background:var(--blue-bg);border:1px solid var(--blue);color:var(--text);}
.bottom-bar.gray-bg{background:var(--gray-bg);border:1px solid var(--border);color:var(--text);}
.bottom-bar strong{font-weight:600;}

/* Horizon headers match card title size */
.hz-head{padding:12px 16px;font-size:18px;font-weight:700;color:white;display:flex;justify-content:space-between;align-items:center;}
"""

N = 10

def legend(*types):
    """Build a tailored colour legend for the footnote. Only include colours used on this slide."""
    parts = []
    mapping = {
        'action': '<span style="color:#0B84F6">\u25cf</span> Actionable',
        'growth': '<span style="color:#059669">\u25cf</span> Growth opportunity',
        'risk': '<span style="color:#DC2626">\u25cf</span> Risk / decline',
        'monitor': '<span style="color:#94A3B8">\u25cf</span> Monitor',
        'dashed': 'Dashed border = recommendation',
    }
    for t in types:
        if t in mapping:
            parts.append(mapping[t])
    return 'Colour coding: ' + ' &nbsp; '.join(parts) + '.'

def S(num, content, fn=""):
    f = f'<div class="fn">{fn}</div>' if fn else ""
    return f'<div class="slide">{content}{f}<div class="pn">{num}/{N}</div></div>\n'


def s01():
    return S(1, f"""
<div class="tag">Executive summary</div>
<h1>GP L90D is \u00a38.3M with growth masking structural pressure. Eight interventions capture \u00a31.5M\u2013\u00a32.9M toward the \u00a34M target.</h1>
<div class="sub">Of 17 recent initiatives, 11 show measurable P&L impact: <strong>net positive on portfolio</strong>, with card production vendor (#9) as the clearest drag. Lifestyle, Card Payments, Subscriptions and Savings drive ~\u00a3740K/month of run-rate growth; FX, Interest Income and Bank Payments drive ~\u00a3290K/month of decline. Net of all categories: <strong>+\u00a3390K/month</strong>.</div>

<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:24px;">
  <div class="stats stats-2x2" style="gap:24px;">
    <div class="stat" style="border-top-color:var(--text)"><div class="stat-val">\u00a38.34M</div><div class="stat-label">GP L90D</div><div class="stat-detail">L90D window, Apr 24\u2013Jul 23 (91 days inclusive)</div></div>
    <div class="stat" style="border-top-color:var(--green)"><div class="stat-val" style="color:var(--green)">+\u00a3390K/mo</div><div class="stat-label">Run-rate trajectory</div><div class="stat-detail">Day-normalised, May to July (+15%)</div></div>
    <div class="stat" style="border-top-color:var(--text)"><div class="stat-val">8</div><div class="stat-label">Interventions sized</div><div class="stat-detail">\u00a31.5M to \u00a32.9M from data</div></div>
    <div class="stat" style="border-top-color:var(--blue)"><div class="stat-val" style="color:var(--blue)">\u00a34M</div><div class="stat-label">Target</div><div class="stat-detail">+48% L90D over 6\u201312 months</div></div>
  </div>

  <div>
    <div class="section-label">Three moves that drive ~75% of sized recovery</div>
    <div style="display:flex;flex-direction:column;gap:14px;margin-top:8px;">
      <div class="bullet"><div class="bullet-n">1</div><div class="bullet-t"><strong>Restructure the vending machine campaign.</strong> Largest controllable cost at \u00a32.8M across 91 days; 76% goes to users who never activate. Qualification gate + spend cap recovers <span class="hl">\u00a3800K\u2013\u00a31.3M</span>.</div></div>
      <div class="bullet"><div class="bullet-n">2</div><div class="bullet-t"><strong>Launch eSIM travel campaign</strong> targeting business-traveller corridors. Daily revenue grew 11.5x from May to July on 9 users. Worth <span class="hl">\u00a3190K\u2013\u00a3500K</span> at scale.</div></div>
      <div class="bullet"><div class="bullet-n">3</div><div class="bullet-t"><strong>Review FX spread pricing</strong> by currency pair and plan tier, starting with Romania. Daily run rate fell 41% from May to July; recovering 25\u201350% adds <span class="hl">\u00a3170K\u2013\u00a3340K</span>.</div></div>
    </div>
  </div>
</div>
""", 'Source: 196,187 user-level P&L records, Apr 24\u2013Jul 23 2024 (L90D window provided in the dataset; 91 days inclusive). Amounts in \u00a31,000s per documentation. Month comparisons use daily run rates (May 31 days, Jun 30, Jul 23).')


def s02():
    return S(2, f"""
<div class="tag">Root cause analysis</div>
<h1>Daily run rate grew +\u00a313K/day (+15%) from May to July, driven by four growth categories offsetting three structural declines.</h1>
<div class="sub">Growth: Lifestyle (+\u00a39.1K/day), Card Payments (+\u00a39.1K/day), Subscriptions (+\u00a34.1K/day), Savings (+\u00a32.3K/day). Decline: FX (\u2212\u00a35.2K/day), Interest Income (\u2212\u00a32.6K/day), Bank Payments (\u2212\u00a31.8K/day). Net impact at 30-day run rate: +\u00a3390K/month.</div>
<div class="chart fill mt"><img src="{img('waterfall.png')}" style="width:100%;"></div>
""", "Daily run rate bridge: May GP\u00f731 days vs Jul GP\u00f723 days. Day-normalised to correct for July\u2019s 23-day window (data extracted Jul 23). Categories with change below \u00a3100/day excluded.")


def s03():
    return S(3, f"""
<div class="tag">Deep dive: largest cost lever</div>
<h1>The vending machine campaign cost \u00a32.8M across the L90D window. 76% went to users who never activated.</h1>
<div class="sub">Stripping the reward, each non-activated user generates \u00a3115 in GP vs \u00a357 for activated ones. The reward structure, not the user base, drives the cost.</div>

<div class="row fill mt" style="gap:18px;">
  <div class="chart" style="flex:0 0 42%;"><img src="{img('nap.png')}" style="width:100%;"></div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card">
      <div class="card-h">{ICO_USERS} \u00a3115 GP/user without the reward vs \u00a357 with it</div>
      <div class="card-b">Without the reward, non-activated users generate 2x the GP of activated ones. The cost sits in the reward structure and card dispatch process, not in user quality.</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_TOOL} Qualification gate + spend cap</div>
      <div class="card-b">
        <strong>1.</strong> Require digital activation before dispatching physical cards.<br>
        <strong>2.</strong> Cap daily spend at \u00a316K (May and July run rate: \u00a332K and \u00a331K/day).<br>
        <strong>3.</strong> Track activation rate by channel to optimise allocation.
      </div>
    </div>
  </div>
</div>

<div class="bottom-bar accent">Recovery: \u00a3800K to \u00a31.3M per L90D &nbsp;\u2502&nbsp; Largest single intervention</div>
""", "GP/user = total GP / unique users per NAP segment across all 91 days. Vending Machine Rewards isolated via account_level_4. "
    + legend('action', 'dashed'))


def s04():
    return S(4, f"""
<div class="tag">Deep dive: structural revenue pressure</div>
<h1>Three revenue lines are losing ~\u00a3290K/month of run rate. FX spread and bank payments are the most actionable.</h1>
<div class="sub">Ordered by controllability. All figures are daily run rates (May\u00f731, Jul\u00f723). FX and bank payments respond to pricing review. Interest income is a mix story. Subscriptions are actually recovering.</div>

<div class="row fill mt" style="gap:16px;">
  <div class="chart" style="flex:0 0 44%;" ><img src="{img('fx.png')}" style="width:100%;"></div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card red">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--red)')} FX spread: \u00a312.8K\u2192\u00a37.5K/day (\u221241%)</div>
      <div class="card-b">Steepest structural decline; FX overall is \u2212\u00a35.2K/day. Romania FX Spread fell 66% daily. Review by currency pair and plan tier. <strong>Recoverable: <span class="hl">\u00a3170K to \u00a3340K</span></strong></div>
    </div>
    <div class="card red">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--red)')} Bank payments: \u00a37.2K\u2192\u00a35.4K/day (\u221225%)</div>
      <div class="card-b">UK (\u2212\u00a3918/day) and Romania (\u2212\u00a3466/day) led the decline. Init. 5 explains Romania (HUF/RON free for Premium); UK warrants separate investigation. <strong>Recoverable: <span class="hl">\u00a390K to \u00a3180K</span></strong></div>
    </div>
    <div class="card gray">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--text3)')} Interest income: \u22127% daily (asset mix)</div>
      <div class="card-b">Cash at banks is actually <span class="pos">+3% daily</span>; the decline sits in Other Financial Assets (\u221234% daily). Balance optimisation may offset <span class="hl">\u00a350K to \u00a3100K</span>.</div>
    </div>
    <div class="card green">
      <div class="card-h">{ICO_UP} Subscriptions: \u00a328.0K\u2192\u00a332.1K/day (+15%)</div>
      <div class="card-b">Plan Fees recovered to \u00a329.2K/day in Jul after a \u00a320.2K/day June trough. Initiative 7 benefits appear to be driving re-engagement.</div>
    </div>
  </div>
</div>
""", "Daily run rates by account_level_3 (May\u00f731 days, Jun\u00f730, Jul\u00f723). Ordered by controllability. "
    + legend('risk', 'monitor', 'growth'))


def s05():
    return S(5, f"""
<div class="tag">Deep dive: card payments</div>
<h1>Card payments is a +\u00a3273K/month run-rate growth engine, but card production costs are rising 87% daily.</h1>
<div class="sub">Two card initiatives with opposite outcomes. Card payments revenue is accelerating (Initiative 8 + volume growth). Card production cost is the clearest hurting initiative in the portfolio.</div>

<div class="row fill mt" style="gap:16px;">
  <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center;">
    <div class="chart"><img src="{img('card_costs.png')}" style="width:100%;"></div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center;">
    <div class="chart"><img src="{img('card_prod.png')}" style="width:100%;"></div>
  </div>
</div>
<div class="row" style="gap:16px;margin-top:10px;">
  <div class="card green" style="flex:1;">
    <div class="card-h">{ICO_UP} Interchange fees up <span class="pos">+\u00a37.5K/day (+16%)</span></div>
    <div class="card-b">Net card payments GP: \u00a311K\u2192\u00a320K/day. ATM costs improved <span class="pos">+29%</span> daily (Init. 8 vendor change). Completing the migration recovers <span class="hl">\u00a3100K\u2013\u00a3200K</span>.</div>
  </div>
  <div class="card red" style="flex:1;">
    <div class="card-h">{ICO_ALERT} Card production: +87% daily (\u00a33.2K\u2192\u00a36.0K/day)</div>
    <div class="card-b">Initiative 9 added <span class="neg">\u00a383K/month</span> extra cost. Commercial review with the new vendor is urgent. <strong>Recovery: <span class="hl">\u00a380K to \u00a3115K per L90D</span></strong></div>
  </div>
</div>
""", "Card payments by account_level_3 (daily run rate). Top-ups/ATM/POS charges are costs. Interchange fees are revenue. "
    + legend('growth', 'risk'))


def s06():
    return S(6, f"""
<div class="tag">Deep dive: growth engines</div>
<h1>Lifestyle daily run rate grew 3.5x from May to July. eSIMs and RevPoints deserve deliberate investment.</h1>
<div class="sub">Two products grew organically with minimal spend. Scaling them is the highest-ROI growth play.</div>

<div class="row fill mt" style="gap:18px;">
  <div style="flex:0 0 34%;display:flex;flex-direction:column;gap:6px;justify-content:center;">
    <div class="chart"><img src="{img('esim.png')}" style="width:100%;"></div>
    <div class="chart"><img src="{img('revpoints.png')}" style="width:100%;"></div>
  </div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card action green">
      <div class="card-h">{ICO_UP} eSIMs: add <span class="pos">\u00a3190K\u2013\u00a3500K</span> per L90D</div>
      <div class="card-b">11.5x daily growth (\u00a30.4K\u2192\u00a34.6K/day) on just 9 users. Initiative 3 is at the start of its adoption curve. Target business travellers and peak travel (Q3/Q4).</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_UP} RevPoints: add <span class="hl">\u00a3100K\u2013\u00a3180K</span> per L90D</div>
      <div class="card-b">4.8x daily growth (\u00a31.2K\u2192\u00a35.7K/day), zero promotional spend. Expand merchant partnerships.</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_DOLLAR} Subscription upgrades: <span class="hl">+\u00a328 GP/user</span></div>
      <div class="card-b">111,167 Standard users at \u00a315 vs Plus at \u00a343, Ultra at \u00a3232. Converting 1\u20135% to Plus adds <span class="hl">\u00a331K\u2013\u00a3156K</span>.</div>
    </div>
    <div class="card gray">
      <div class="card-h">{ICO_GLOBE} Stays: \u00a315K in Jul (too early to size)</div>
      <div class="card-b">Initiative 4 launched July with 30% lower cashback.</div>
    </div>
  </div>
</div>
""", "Lifestyle by account_level_4. eSIM and RevPoints isolated from account hierarchy. Daily run rates (May\u00f731, Jul\u00f723). "
    + legend('growth', 'action', 'monitor', 'dashed'))


def s07():
    return S(7, f"""
<div class="tag">Deep dive: additional levers</div>
<h1>Three operational levers add \u00a3157K to \u00a3272K. Business growth closes the gap.</h1>
<div class="sub">Each requires an operational decision, not new capital.</div>

<div style="display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:18px 22px;margin-top:14px;align-content:center;flex:1;padding-bottom:60px;">
  <div class="card action" style="padding:16px 18px;">
    <div class="card-h">{ICO_DOLLAR} Credit repricing: <span class="hl">\u00a345K\u2013\u00a370K</span></div>
    <div class="card-b">Loan daily decline: Poland <span class="neg">\u2212\u00a3417/day</span>, Lithuania <span class="neg">\u2212\u00a3329/day</span>, Romania <span class="neg">\u2212\u00a3208/day</span>, Germany <span class="neg">\u2212\u00a3126/day</span> (Init. 1 + 16), Ireland flat. Partially offset: Credit Cards turned positive and BNPL grew <span class="pos">8.9x daily</span>.</div>
  </div>
  <div class="card action" style="padding:16px 18px;">
    <div class="card-h">{ICO_DOLLAR} Bank payment pricing: <span class="hl">\u00a390K\u2013\u00a3180K</span></div>
    <div class="card-b">Total bank payments down <span class="neg">\u2212\u00a31.8K/day (\u221225%)</span>. UK leads the decline at <span class="neg">\u2212\u00a3918/day</span>, Romania at <span class="neg">\u2212\u00a3466/day</span>. Init. 5 explains Romania; UK warrants separate investigation.</div>
  </div>
  <div class="card gray" style="padding:16px 18px;">
    <div class="card-h">{ICO_TOOL} SMS and operational: ~\u00a322K per L90D</div>
    <div class="card-b">In-house SMS cut costs <span class="pos">\u221260%</span>. Legal streamlining halved approval time. Faster refunds improve UX. Youth segment (3,153 users) runs at <span class="neg">\u2212\u00a358/user</span>, but daily run rate is recovering (May \u2212\u00a32.4K/day to Jul \u2212\u00a31.6K/day).</div>
  </div>
  <div class="card action green" style="padding:16px 18px;">
    <div class="card-h">{ICO_USERS} Business segment: <span class="pos">27x GP/user</span></div>
    <div class="card-b">2,348 business users at <strong>\u00a3913 GP/user</strong> vs 185,894 personal at \u00a334. Growing by 500 users via Scale plan + terminal rollout adds <span class="pos">\u00a3300K\u2013\u00a3600K</span>.</div>
  </div>
</div>

<div class="bottom-bar gray-bg">
  {ICO_GLOBE}
  <strong style="margin-left:6px;">Geographic ARPU gap:</strong> UK <strong>\u00a390</strong>/user vs France \u00a323, Romania \u00a317, Poland \u00a331. Localised pricing could recover <span class="hl">\u00a3200K\u2013\u00a3400K</span> per L90D.
</div>
""", "Initiatives 1, 5, 10, 11, 13, 16, 17 mapped to levers above. "
    + legend('action', 'growth', 'monitor', 'dashed'))


def s08():
    return S(8, f"""
<div class="tag">Intervention sizing</div>
<h1>Eight interventions total \u00a31.5M to \u00a32.9M. Supplementary plays close the gap to \u00a34M.</h1>
<div class="sub">Ranges derived from observed daily run rates (no full reversal assumed). Current daily trajectory of +\u00a3390K/month, if sustained, adds headroom; eight interventions plus supplementary plays drive the case toward the \u00a312.3M L90D target.</div>

<div class="chart mt" style="margin-bottom:14px;"><img src="{img('sizing.png')}" style="width:100%;max-height:440px;"></div>

<div class="bottom-bar gray-bg">
  {ICO_TARGET}
  <strong style="margin-left:6px;">Closing the gap to \u00a34M:</strong> Execute all eight at the high end (\u00a32.9M), then add business segment growth (+\u00a3300K\u2013\u00a3600K), geographic ARPU optimisation (+\u00a3200K\u2013\u00a3400K), and balance management (+\u00a350K\u2013\u00a3100K). <strong>Full range: \u00a32.1M to \u00a34.0M.</strong>
</div>
""")


def s09():
    return S(9, f"""
<div class="tag">Roadmap</div>
<h1>Four immediate actions capture ~\u00a31.0M in 90 days. Full \u00a34M is a 12-month execution.</h1>

<div style="flex:1;display:flex;align-items:center;margin-top:10px;">
  <div class="row" style="gap:14px;width:100%;align-items:stretch;">
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#0B84F6,#0070E0);">Now: 0\u201390 days &nbsp; ~\u00a31.0M <span class="hz-badge">High confidence</span></div><div class="hz-body"><ul>
      <li><strong>Ship qualification gate</strong> for vending machine; cap daily spend at <strong>\u00a316K</strong></li>
      <li><strong>Review FX spread pricing</strong> by currency pair and plan tier, starting with Romania</li>
      <li><strong>Renegotiate card production contract</strong> with a volume-tied fee structure</li>
      <li><strong>Migrate 100%</strong> of new cards onto the new vendor pricing</li>
    </ul></div></div>
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#3B5BDB,#2B4BC9);">3\u20136 months &nbsp; ~\u00a31.0M <span class="hz-badge">Medium confidence</span></div><div class="hz-body"><ul>
      <li><strong>Launch eSIM travel-season campaign</strong> in top business-traveller corridors</li>
      <li><strong>Sign RevPoints partners</strong> in top travel and retail categories</li>
      <li><strong>Launch Standard\u2192Plus upgrade campaign</strong> targeting high-engagement users</li>
      <li><strong>Reprice bank payments</strong> in UK and high-volume currencies</li>
    </ul></div></div>
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#1E3A5F,#162D4A);">6\u201312 months &nbsp; ~\u00a32.0M <span class="hz-badge">Market-dependent</span></div><div class="hz-body"><ul>
      <li><strong>Diagnose loan decline</strong> in PL and LT; test selective repricing if pricing-driven</li>
      <li><strong>Grow business segment</strong> via Scale plan and POS terminal rollout</li>
      <li><strong>Pilot localised pricing</strong> in top EU markets to narrow the UK\u2013EU ARPU gap</li>
      <li><strong>Partner with treasury</strong> on rebalancing case: OFA \u221234% vs Cash at Banks flat</li>
    </ul></div></div>
  </div>
</div>

<div class="bottom-bar blue-bg">
  {ICO_SHIELD}
  <strong style="margin-left:6px;">First horizon = decisions you can make in week one, no new headcount, no new budget.</strong> Vending machine restructuring, card vendor renegotiation, and FX pricing review are all within direct team control.
</div>
""")


def s10():
    return S(10, f"""
<div class="tag" style="color:var(--text3);">Appendix</div>
<h1>Data methodology, assumptions, and initiative mapping</h1>

<div class="row" style="gap:14px;margin-top:14px;flex:1;">
  <div style="flex:0 0 42%;background:var(--gray-bg);border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;">
    <div class="section-label">Data methodology</div>
    <div style="font-size:14px;line-height:1.6;color:var(--text2);margin-bottom:12px;">
      <strong>L90D window:</strong> 91 days, Apr 24\u2013Jul 23 2024. Data extracted on Jul 23.<br>
      <strong>April:</strong> 7 days (partial start of window).<br>
      <strong>July:</strong> 23 days (partial end of window).<br>
      <strong>Daily run rate:</strong> Month comparisons use total GP \u00f7 days in month (31/30/23). Raw monthly totals would under-represent July by 8 days and produce a false decline signal.<br>
      <strong>L90D total:</strong> \u00a38.34M across all 91 days.
    </div>
    <div class="section-label" style="margin-top:6px;">Key assumptions</div>
    <div style="font-size:13px;line-height:1.55;color:var(--text2);">
      \u2022 amount_gbp denominated in thousands per documentation<br>
      \u2022 NAP segments grouped by per-record status (captures GP generated during each phase)<br>
      \u2022 Segment economics (plan/country/user type) use full dataset<br>
      \u2022 Sizing uses conservative\u2013moderate ranges from observed trends<br>
      \u2022 No range assumes full reversal of any decline<br>
      \u2022 FX spread: 25\u201350% addressable through pricing<br>
      \u2022 2024 cohort \u00a314/user vs \u00a349 for pre-2024 cohorts<br>
      \u2022 Current product mix assumed; no regulatory changes beyond Init. 16
    </div>
  </div>
  <div style="flex:1;background:var(--gray-bg);border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;">
    <div class="section-label">Initiative mapping</div>
    <div style="font-size:13px;line-height:1.6;color:var(--text2);">
      <strong>#1</strong> Credit rate cuts (RO, DE, LT): loan daily run rate \u2212\u00a3329\u2013\u00a3126/day by market \u2192 slide 7<br>
      <strong>#2</strong> Savings rate increase (Metal/Ultra): Instant Access daily <span class="pos">+84%</span> (volume offset higher rate cost) \u2192 slide 4<br>
      <strong>#3</strong> eSIM launch: <span class="pos">11.5x</span> daily growth on 9 users \u2192 slide 6<br>
      <strong>#4</strong> Stays cashback reduction: \u00a315K first month \u2192 slide 6<br>
      <strong>#5</strong> Bank payment HUF/RON free: Romania \u2212\u00a3466/day \u2192 slides 4, 7<br>
      <strong>#6</strong> Vending machine campaign: \u00a32.8M L90D cost \u2192 slide 3<br>
      <strong>#7</strong> Subscription benefits (Plus/Ultra): Plan Fees recovered Jun\u2192Jul \u2192 slides 4, 6<br>
      <strong>#8</strong> Card vendor cost changes: ATM <span class="pos">+29%</span> daily \u2192 slide 5<br>
      <strong>#9</strong> Card production vendor: <span class="neg">+87%</span> daily cost \u2192 slide 5<br>
      <strong>#10</strong> Simplified business onboarding: no direct P&L signal \u2192 slide 7<br>
      <strong>#11</strong> New terminal for offline payments: Merchant Acquiring still small \u2192 slide 7<br>
      <strong>#12</strong> Money Market Funds: Treasury Services growing from tiny base<br>
      <strong>#13</strong> Scale plan: 187 users at \u00a32,768 GP/user \u2192 slide 7<br>
      <strong>#14</strong> Faster refund settlement: UX, no direct P&L line<br>
      <strong>#15</strong> Legal streamlining: process efficiency, no P&L line<br>
      <strong>#16</strong> German loan provisions 5%\u219210%: compounds Init. 1 in Germany<br>
      <strong>#17</strong> In-house SMS: <span class="pos">\u221260%</span>, ~\u00a322K/L90D \u2192 slide 7
    </div>
  </div>
</div>
""", "Analysis in Python (pandas, numpy, matplotlib). P&L decomposed via four-level account hierarchy. 17 initiatives mapped; 11 show measurable P&L impact.")


def main():
    print("Building HTML slides v5...")
    slides = [s01(), s02(), s03(), s04(), s05(), s06(), s07(), s08(), s09(), s10()]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Revolut GP L90D Analysis</title>
<style>{CSS}</style></head>
<body>{''.join(slides)}</body>
</html>"""
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Written: {OUTPUT}  ({len(slides)} slides)")

if __name__ == "__main__":
    main()
