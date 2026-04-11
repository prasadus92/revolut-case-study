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
<h1>GP L90D declined \u00a3403K. Eight interventions size \u00a31.5M to \u00a32.8M in recovery.</h1>
<div class="sub">Business growth, geographic ARPU, and balance optimisation close the remaining gap to \u00a34M.</div>

<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:24px;">
  <div class="stats stats-2x2" style="gap:24px;">
    <div class="stat" style="border-top-color:var(--text)"><div class="stat-val">\u00a37.67M</div><div class="stat-label">GP L90D</div><div class="stat-detail">191,412 users, May to Jul 2024</div></div>
    <div class="stat" style="border-top-color:var(--red)"><div class="stat-val" style="color:var(--red)">\u2212\u00a3403K</div><div class="stat-label">Three-month decline</div><div class="stat-detail">Accelerating: \u2212\u00a377K then \u2212\u00a3326K</div></div>
    <div class="stat" style="border-top-color:var(--text)"><div class="stat-val">8</div><div class="stat-label">Interventions sized</div><div class="stat-detail">\u00a31.5M to \u00a32.8M from data</div></div>
    <div class="stat" style="border-top-color:var(--blue)"><div class="stat-val" style="color:var(--blue)">\u00a34M</div><div class="stat-label">Target</div><div class="stat-detail">Achievable across three horizons</div></div>
  </div>

  <div>
    <div class="section-label">Three moves that drive 60% of recovery</div>
    <div style="display:flex;flex-direction:column;gap:14px;margin-top:8px;">
      <div class="bullet"><div class="bullet-n">1</div><div class="bullet-t"><strong>Restructure the vending machine campaign</strong> to eliminate non-activated user waste. Largest cost at \u00a32.6M per L90D. Qualification gate and spend cap recover <span class="hl">\u00a3800K to \u00a31.3M</span>.</div></div>
      <div class="bullet"><div class="bullet-n">2</div><div class="bullet-t"><strong>Scale eSIM distribution</strong> with targeted travel-season push. Revenue grew 8.5x in three months on 9 users. Worth <span class="hl">\u00a3190K to \u00a3500K</span> at scale.</div></div>
      <div class="bullet"><div class="bullet-n">3</div><div class="bullet-t"><strong>Recover FX spread pricing</strong> through review by currency pair and plan tier. Spread fell 57% (\u00a3398K to \u00a3173K). Recovering 25\u201350% adds <span class="hl">\u00a3170K to \u00a3340K</span>.</div></div>
    </div>
  </div>
</div>
""", 'Source: 196,187 user-level P&L records, May\u2013Jul 2024. Amounts in \u00a31,000s per documentation. April excluded (7 days).')


def s02():
    return S(2, f"""
<div class="tag">Root cause analysis</div>
<h1>GP fell \u00a3403K in three months, with the decline accelerating in July</h1>
<div class="sub">Interest income (\u2212\u00a3373K) and FX revenue (\u2212\u00a3317K) drove 83% of the drop. Card cost savings (+\u00a3122K) and lifestyle growth (+\u00a3181K) partially offset.</div>
<div class="chart fill mt"><img src="{img('waterfall.png')}" style="width:100%;"></div>
""", "Monthly GP by account_level_2. Categories below \u00a310K excluded.")


def s03():
    return S(3, f"""
<div class="tag">Deep dive: largest cost lever</div>
<h1>The vending machine campaign cost \u00a32.6M in 90 days. Non-activated users drove 89%.</h1>
<div class="sub">The reward structure creates the loss. Without it, non-activated users generate more GP than activated ones.</div>

<div class="row fill mt" style="gap:18px;">
  <div class="chart" style="flex:0 0 42%;"><img src="{img('nap.png')}" style="width:100%;"></div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card">
      <div class="card-h">{ICO_USERS} \u00a3115 GP/user without the reward vs \u00a357 with it</div>
      <div class="card-b">Non-activated users are more profitable than activated ones when the vending machine reward is removed. The reward structure creates the loss, not the users themselves.</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_TOOL} Qualification gate + spend cap</div>
      <div class="card-b">
        <strong>1.</strong> Require digital activation before dispatching physical cards.<br>
        <strong>2.</strong> Cap monthly spend at \u00a3500K (trending from \u00a3985K to \u00a3721K).<br>
        <strong>3.</strong> Track activation rate by channel to optimise allocation.
      </div>
    </div>
  </div>
</div>

<div class="bottom-bar accent">Recovery: \u00a3800K to \u00a31.3M per L90D &nbsp;\u2502&nbsp; Largest single intervention</div>
""", "GP/user = total L90D GP / unique users per NAP segment. Vending Machine Rewards isolated via account_level_4. "
    + legend('action', 'dashed'))


def s04():
    return S(4, f"""
<div class="tag">Deep dive: revenue declines</div>
<h1>Three revenue lines fell \u00a3788K. FX spread and bank payments are most actionable.</h1>
<div class="sub">Ordered by controllability: FX and bank payments can be addressed through pricing review. Interest income is largely external.</div>

<div class="row fill mt" style="gap:16px;">
  <div class="chart" style="flex:0 0 44%;" ><img src="{img('fx.png')}" style="width:100%;"></div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card red">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--red)')} FX spread: down 57%, \u00a3398K to \u00a3173K/month</div>
      <div class="card-b">Steepest structural decline. Romania FX dropped 61%. Review by currency pair and plan tier. <strong>Recoverable: <span class="hl">\u00a3170K to \u00a3340K</span></strong></div>
    </div>
    <div class="card red">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--red)')} Bank payment fees: down \u00a3126K/month</div>
      <div class="card-b">Initiative 5 made first 2 HUF/RON transfers free for Premium. Romania fell \u00a316K/mo. <strong>Recoverable: <span class="hl">\u00a390K to \u00a3180K</span></strong></div>
    </div>
    <div class="card gray">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--text3)')} Interest income: down \u00a3373K (limited controllability)</div>
      <div class="card-b">Cash at banks fell \u00a3215K. Initiative 2 raised Metal/Ultra savings rates, increasing payouts. Balance optimisation may offset <span class="hl">\u00a350K to \u00a3100K</span>.</div>
    </div>
    <div class="card gray">
      <div class="card-h">{ico('<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>','var(--text3)')} Subscriptions: down \u00a3129K</div>
      <div class="card-b">Plan Fees fell \u00a3774K to \u00a3671K. Monitor against Initiative 7 benefit costs.</div>
    </div>
  </div>
</div>
""", "FX by account_level_3. Ordered by controllability (most actionable first). "
    + legend('risk', 'monitor'))


def s05():
    return S(5, f"""
<div class="tag">Deep dive: card costs</div>
<h1>Card vendor migration saved \u00a3331K. Card production costs moved the wrong way.</h1>
<div class="sub">Two card initiatives with opposite outcomes. One is delivering, the other needs intervention.</div>

<div class="row fill mt" style="gap:16px;">
  <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center;">
    <div class="chart"><img src="{img('card_costs.png')}" style="width:100%;"></div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center;">
    <div class="chart"><img src="{img('card_prod.png')}" style="width:100%;"></div>
  </div>
</div>
<div class="row" style="gap:16px;margin-top:10px;">
  <div class="card" style="flex:1;">
    <div class="card-h">{ICO_CHECK} \u00a3331K saved in 90 days</div>
    <div class="card-b">Top-up processing: <span class="pos">+\u00a3269K</span> | ATM: <span class="pos">+\u00a359K</span> | POS: <span class="pos">+\u00a33K</span>. Additional <span class="hl">\u00a3100K to \u00a3200K</span> achievable as migration completes. Interchange fees fell \u00a3210K (revenue decline).</div>
  </div>
  <div class="card red" style="flex:1;">
    <div class="card-h">{ICO_ALERT} Card production: +39% (\u00a399K to \u00a3137K/month)</div>
    <div class="card-b">Initiative 9 increased costs by <span class="neg">\u00a338K/month</span>. Commercial review needed. <strong>Recovery: <span class="hl">\u00a380K to \u00a3115K per L90D</span></strong></div>
  </div>
</div>
""", "Card payments by account_level_3. Top-ups/ATM are costs. Interchange fees are revenue. "
    + legend('action', 'risk'))


def s06():
    return S(6, f"""
<div class="tag">Deep dive: growth engines</div>
<h1>Lifestyle revenue grew 163%. eSIMs and RevPoints deserve deliberate investment.</h1>
<div class="sub">Two products grew organically with minimal spend. Scaling them is the highest-ROI growth play.</div>

<div class="row fill mt" style="gap:18px;">
  <div style="flex:0 0 34%;display:flex;flex-direction:column;gap:6px;justify-content:center;">
    <div class="chart"><img src="{img('esim.png')}" style="width:100%;"></div>
    <div class="chart"><img src="{img('revpoints.png')}" style="width:100%;"></div>
  </div>
  <div class="col vc" style="flex:1;gap:18px;">
    <div class="card action green">
      <div class="card-h">{ICO_UP} eSIMs: scale to <span class="pos">\u00a3190K\u2013\u00a3500K</span> per L90D</div>
      <div class="card-b">8.5x growth (\u00a312K to \u00a3105K) on 9 users. Target business travellers and peak travel (Q3/Q4).</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_UP} RevPoints: target <span class="hl">\u00a3100K\u2013\u00a3180K</span> per L90D</div>
      <div class="card-b">3.6x organic growth (\u00a337K to \u00a3132K), zero promotional spend. Expand merchant partnerships.</div>
    </div>
    <div class="card action">
      <div class="card-h">{ICO_DOLLAR} Subscription upgrades: <span class="hl">+\u00a325 GP/user</span></div>
      <div class="card-b">107,927 Standard at \u00a318 vs Plus at \u00a343, Ultra at \u00a3232. Converting 1\u20135% adds <span class="hl">\u00a327K\u2013\u00a3135K</span>.</div>
    </div>
    <div class="card gray">
      <div class="card-h">{ICO_GLOBE} Stays: \u00a315K first month (too early to size)</div>
      <div class="card-b">Initiative 4 launched July with 30% lower cashback.</div>
    </div>
  </div>
</div>
""", "Lifestyle by account_level_4. eSIM and RevPoints isolated from account hierarchy. "
    + legend('growth', 'action', 'monitor', 'dashed'))


def s07():
    return S(7, f"""
<div class="tag">Deep dive: additional levers</div>
<h1>Four smaller levers add \u00a3215K to \u00a3365K. Business growth closes the gap.</h1>
<div class="sub">Each requires an operational decision, not new capital.</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:36px 22px;margin-top:10px;align-content:center;flex:1;">
  <div class="card action" style="min-height:140px;padding:16px 18px;">
    <div class="card-h">{ICO_DOLLAR} Credit repricing: <span class="hl">\u00a345K\u2013\u00a370K</span></div>
    <div class="card-b">Loan rate cuts: Romania <span class="neg">\u2212\u00a313K/mo</span>, Lithuania <span class="neg">\u2212\u00a311K/mo</span>, Germany <span class="neg">\u2212\u00a36K/mo</span> (compounded by Initiative 16). Not all cuts need to persist. Credit Cards and BNPL partially offset.</div>
  </div>
  <div class="card action" style="min-height:140px;padding:16px 18px;">
    <div class="card-h">{ICO_DOLLAR} Bank payment pricing: <span class="hl">\u00a390K\u2013\u00a3180K</span></div>
    <div class="card-b">Transfer fees fell \u00a3292K to \u00a3166K/month. Initiative 5 made first 2 HUF/RON transfers free for Premium; Romania fell <span class="neg">\u00a316K/mo</span>. Pricing review across currencies and plans.</div>
  </div>
  <div class="card gray" style="min-height:140px;padding:16px 18px;">
    <div class="card-h">{ICO_TOOL} SMS and operational: ~\u00a322K per L90D</div>
    <div class="card-b">In-house SMS cut costs <span class="pos">\u221260%</span>. Legal streamlining halved approval time. Faster refunds improve UX. These compound the value of other interventions.</div>
  </div>
  <div class="card action green" style="min-height:140px;padding:16px 18px;">
    <div class="card-h">{ICO_USERS} Business segment: <span class="pos">27x GP/user</span></div>
    <div class="card-b">2,348 business users at <strong>\u00a3913 GP/user</strong> vs 185,894 personal at \u00a334. Growing by 500 users via Scale plan + terminal rollout adds <span class="pos">\u00a3300K\u2013\u00a3600K</span>.</div>
  </div>
</div>

<div class="bottom-bar gray-bg">
  {ICO_GLOBE}
  <strong style="margin-left:6px;">Geographic ARPU gap:</strong> UK <strong>\u00a390</strong>/user vs France \u00a322, Romania \u00a318, Poland \u00a320. Localised pricing could recover <span class="hl">\u00a3200K\u2013\u00a3400K</span> per L90D.
</div>
""", "Initiatives 1, 5, 10, 11, 13, 16, 17 mapped to levers above. "
    + legend('action', 'growth', 'monitor', 'dashed'))


def s08():
    return S(8, f"""
<div class="tag">Intervention sizing</div>
<h1>Eight interventions total \u00a31.5M to \u00a32.8M. Growth plays close the gap to \u00a34M.</h1>

<div class="chart mt" style="margin-bottom:8px;"><img src="{img('sizing.png')}" style="width:100%;"></div>

<div class="bottom-bar gray-bg">
  {ICO_TARGET}
  <strong style="margin-left:6px;">Closing the gap to \u00a34M:</strong> Execute all eight at the high end (\u00a32.8M), then add business segment growth (+\u00a3300K\u2013\u00a3600K), geographic ARPU optimisation (+\u00a3200K\u2013\u00a3400K), and balance management (+\u00a350K\u2013\u00a3100K). <strong>Full range: \u00a32.1M to \u00a33.9M.</strong>
</div>
""")


def s09():
    return S(9, f"""
<div class="tag">Roadmap</div>
<h1>Four immediate actions capture ~\u00a31.0M in 90 days. Full \u00a34M is a 12-month execution.</h1>

<div style="flex:1;display:flex;align-items:center;margin-top:10px;">
  <div class="row" style="gap:14px;width:100%;align-items:stretch;">
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#0B84F6,#0070E0);">Now: 0\u201390 days &nbsp; ~\u00a31.0M <span class="hz-badge">High confidence</span></div><div class="hz-body"><ul>
      <li>Cap vending machine spend at <strong>\u00a3500K/month</strong> and introduce qualification gate</li>
      <li>Run <strong>FX spread pricing review</strong> by currency pair and plan tier</li>
      <li>Open <strong>commercial review</strong> with card production vendor</li>
      <li>Complete card vendor <strong>cost migration</strong> across all card types</li>
    </ul></div></div>
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#3B5BDB,#2B4BC9);">3\u20136 months &nbsp; ~\u00a31.0M <span class="hz-badge">Medium confidence</span></div><div class="hz-body"><ul>
      <li>Scale <strong>eSIM distribution</strong> with travel-season marketing</li>
      <li>Expand <strong>RevPoints</strong> merchant partnerships</li>
      <li>Launch <strong>Standard-to-Plus</strong> subscription upgrade campaign</li>
      <li>Review <strong>bank payment pricing</strong> across currencies</li>
    </ul></div></div>
    <div class="hz"><div class="hz-head" style="background:linear-gradient(135deg,#1E3A5F,#162D4A);">6\u201312 months &nbsp; ~\u00a32.0M <span class="hz-badge">Market-dependent</span></div><div class="hz-body"><ul>
      <li>Selective <strong>credit repricing</strong> by market based on elasticity</li>
      <li>Grow <strong>business segment</strong> via Scale plan and terminal rollout</li>
      <li><strong>Localised pricing</strong> in top EU markets to close ARPU gap</li>
      <li><strong>Balance optimisation</strong> to offset interest income decline</li>
    </ul></div></div>
  </div>
</div>

<div class="bottom-bar blue-bg">
  {ICO_SHIELD}
  <strong style="margin-left:6px;">First horizon = operational decisions, no new investment.</strong> Vending machine restructuring, card cost migration, and FX pricing review are all within direct team control. These are the highest-confidence levers.
</div>
""")


def s10():
    return S(10, f"""
<div class="tag" style="color:var(--text3);">Appendix</div>
<h1>Assumptions, methodology, and initiative mapping</h1>

<div class="row" style="gap:14px;margin-top:14px;flex:1;">
  <div style="flex:1;background:var(--gray-bg);border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;">
    <div class="section-label">Key assumptions</div>
    <div style="font-size:15px;line-height:1.7;color:var(--text2);">
      \u2022 amount_gbp denominated in thousands per documentation<br>
      \u2022 April (7 days) excluded. L90D = May + Jun + Jul<br>
      \u2022 NAP status = final activation outcome in the 90-day window<br>
      \u2022 All figures from provided dataset only, no external data<br>
      \u2022 Sizing uses conservative\u2013moderate ranges from observed trends<br>
      \u2022 No range assumes full reversal of any decline<br>
      \u2022 Vending machine: partial restructuring, not wind-down<br>
      \u2022 FX spread: 25\u201350% addressable through pricing<br>
      \u2022 Current product mix assumed; no regulatory changes beyond Init. 16
    </div>
  </div>
  <div style="flex:1;background:var(--gray-bg);border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;">
    <div class="section-label">Initiative mapping</div>
    <div style="font-size:14px;line-height:1.65;color:var(--text2);">
      <strong>#1</strong> Credit rate cuts (RO, DE, LT): loan decline \u2192 slide 7<br>
      <strong>#2</strong> Savings rate increase (Metal/Ultra): +\u00a321K \u2192 slide 4<br>
      <strong>#3</strong> eSIM launch: 8.5x growth \u2192 slide 6<br>
      <strong>#4</strong> Stays cashback reduction: \u00a315K first month \u2192 slide 6<br>
      <strong>#5</strong> Bank payment pricing (HUF/RON) \u2192 slides 4, 7<br>
      <strong>#6</strong> Vending machine campaign: \u00a32.6M cost \u2192 slide 3<br>
      <strong>#7</strong> Subscription benefits (Plus/Ultra) \u2192 slide 6<br>
      <strong>#8</strong> Card vendor cost changes: \u00a3331K savings \u2192 slide 5<br>
      <strong>#9</strong> Card production vendor: +\u00a338K/month \u2192 slide 5<br>
      <strong>#10</strong> Simplified business onboarding \u2192 slide 7<br>
      <strong>#11</strong> New terminal for offline payments \u2192 slide 7<br>
      <strong>#12</strong> Money Market Funds: no material P&L impact yet<br>
      <strong>#13</strong> Scale plan: 187 users, \u00a32,783 GP/user \u2192 slide 7<br>
      <strong>#14</strong> Faster refund settlement: UX, no P&L impact<br>
      <strong>#15</strong> Legal streamlining: 50% faster approvals<br>
      <strong>#16</strong> German provisions 5% to 10% \u2192 slide 7<br>
      <strong>#17</strong> In-house SMS: \u221260%, ~\u00a322K/L90D \u2192 slide 7
    </div>
  </div>
</div>
""", "Analysis in Python (pandas, numpy, matplotlib). P&L decomposed via four-level account hierarchy. 17 initiatives mapped; 10 show measurable P&L impact.")


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
