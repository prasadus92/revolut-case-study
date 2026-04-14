# Revolut GP L90D: root cause analysis and path to £4M

Analysis of 196,187 user-level P&L records to assess whether recent initiatives are impacting GP L90D, and to size interventions that achieve a £4M GP improvement within 6–12 months.

## Key findings

1. **GP L90D is £8.34M across the L90D window provided** (Apr 24 – Jul 23 2024, 91 days inclusive). April has 7 days and July has 23 days of data; May and June are complete. Month-over-month comparisons use daily run rates to correct for the partial end-months.

2. **Daily run rate is actually improving +15%** from May to July (+£13K/day, equivalent to +£390K/month). Raw monthly totals would show a false "£403K decline" because July has 8 fewer days than May. On an apples-to-apples daily basis, GP is trajectory-positive.

3. **The vending machine campaign is the largest controllable cost lever.** Initiative 6 cost £2.8M across the 91-day window. Non-activated users drove 76% of that cost. Excluding rewards, they generate £115 GP/user vs £57 from activated users — the reward structure creates the loss, not the users.

4. **Four growth categories are adding ~£740K/month of run rate**: Lifestyle (+£9.1K/day, driven by eSIMs and RevPoints), Card Payments (+£9.1K/day, driven by Interchange fees), Subscriptions (+£4.1K/day), and Savings (+£2.3K/day).

5. **Three structural declines are taking ~£290K/month of run rate away**: FX (−£5.2K/day, mainly spread), Interest Income (−£2.6K/day, concentrated in Other Financial Assets), and Bank Payments (−£1.8K/day, led by UK and Romania).

6. **Card production costs are the clearest hurting initiative** — up 39% monthly total, +87% on a daily run rate basis (£3.2K → £6.0K/day). Initiative 9 added ~£83K/month of extra cost.

7. **Eight interventions total £1.5M to £2.9M.** Supplementary plays (business growth, geographic ARPU, balance management) close the gap to £4M.

## Methodology

- Dataset represents the L90D window provided by Revolut (Apr 24 – Jul 23 2024; 91 days inclusive), extracted on Jul 23
- April has 7 days and July has 23 days of data — both partial ends of the window
- Month-over-month comparisons use **daily run rates** (total GP ÷ days in month) to correct for July being 8 days shorter than May
- Segment economics (plan ARPU, country ARPU, user type) use the full 91-day dataset
- L90D totals use all 91 days; £8.34M is the correct total (the £7.67M figure that appears in some cells of earlier drafts excluded April's 7 days)
- 17 initiatives mapped to P&L categories; 11 show measurable impact
- Intervention sizing uses conservative-to-moderate ranges from observed data — no range assumes full reversal of any decline

## Repository structure

```
├── notebook.ipynb              # Full analysis (start here)
├── problem_statement.md        # Case brief
├── dataset.csv                 # Source data (196,187 rows)
├── src/
│   ├── build_html.py           # Slide builder (HTML/CSS)
│   ├── charts.py               # Chart generation (matplotlib, 300 DPI) + load_data()
│   ├── design.py               # Design system (colours, typography, layout)
│   ├── render_pdf.js           # Puppeteer PDF renderer
│   └── test_analysis.py        # Data validation tests (93 tests)
├── output/
│   └── revolut_gp_analysis.pdf # Final deliverable (10-slide PDF)
├── METHODOLOGY.md              # Analytical framework and approach
├── requirements.txt
├── package.json                # Node deps (puppeteer)
└── .github/workflows/          # CI: tests + notebook execution
```

## Running the analysis

```bash
pip install -r requirements.txt
npm install                        # puppeteer for PDF rendering
jupyter notebook notebook.ipynb    # interactive analysis
```

To rebuild the presentation:
```bash
python src/build_html.py           # generate HTML slides + charts
node src/render_pdf.js             # render to PDF via puppeteer
```

To run tests:
```bash
python -m pytest src/test_analysis.py -v
```

---

*This repository is a case-study submission for Revolut's Entrepreneur in Residence role. The dataset is provided by Revolut and is not licensed for reuse.*
