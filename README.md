# Revolut GP L90D: root cause analysis and path to £4M

Analysis of 196,187 user-level P&L records to identify what is driving the decline in gross profit and size interventions to achieve a £4M GP improvement within 6 to 12 months.

## Key findings

1. **GP L90D is £7.67M and declining.** Monthly GP fell from £2.72M (May) to £2.31M (Jul), with the decline accelerating: £77K in June, £326K in July.

2. **The vending machine campaign is the largest cost lever.** Initiative 6 cost £2.6M per L90D. Non-activated users (6,455) drove 89% of that cost. Excluding rewards, they generate £115 GP/user vs £57 from activated users. The reward structure creates the loss, not the users.

3. **Card vendor migration is delivering real savings.** Processing costs fell £331K between May and July, with the transition still incomplete. Card production costs moved in the wrong direction (+£38K/month from Initiative 9).

4. **eSIMs grew 8.5x in three months** on 9 users. RevPoints grew 3.6x with no promotional spend. Both are high-ROI growth opportunities.

5. **FX spread collapsed 57%** (£398K to £173K), the steepest structural revenue decline. Romania FX dropped 61%, possibly linked to Initiative 5. Interest income fell £373K, partly driven by Initiative 2 increasing savings rates.

6. **Eight interventions total £1.5M to £2.8M.** Supplementary plays (business growth, geographic ARPU, balance optimisation) close the gap to £4M.

## Methodology

- P&L decomposed using the four-level account hierarchy (account_level_1 to account_level_4)
- Monthly trends compared May to July; April excluded (7 days only)
- Each intervention sized using observed data trends, extrapolated conservatively
- 17 initiatives from the brief mapped to measurable P&L impact; 10 show impact in the dataset
- All figures derived exclusively from the provided dataset

## Repository structure

```
├── notebook.ipynb              # Full analysis (start here)
├── problem_statement.md        # Case brief
├── dataset.csv                 # Source data (196,187 rows)
├── src/
│   ├── build_html.py           # Slide builder (HTML/CSS)
│   ├── charts.py               # Chart generation (matplotlib, 300 DPI)
│   ├── design.py               # Design system (colours, typography, layout)
│   ├── render_pdf.js           # Puppeteer PDF renderer
│   └── test_analysis.py        # Data validation tests
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
