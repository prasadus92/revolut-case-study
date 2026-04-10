# Revolut GP L90D: root cause analysis and path to £4M improvement

Analysis of 196,187 user-level P&L records to identify what is driving the decline in gross profit and recommend interventions to achieve a £4M GP improvement within 6-12 months.

## Key findings

1. **GP L90D is declining at an accelerating rate.** May delivered £2.72M, July came in at £2.31M. The June-to-July drop (£326K) was 4x worse than May-to-June (£77K).

2. **The vending machine campaign (Initiative 6) is the single largest cost at £2.8M per L90D.** But non-activated users are not inherently unprofitable. Excluding reward allocation, they generate £81/user vs £57 from activated users. The reward structure creates the loss, not the users.

3. **Card payment vendor migration (Initiative 8) is delivering real savings.** Processing costs fell £331K between May and July, with the transition still incomplete.

4. **eSIMs (Initiative 3) grew 8.5x in three months** on minimal spend, with only 9 transactions in the dataset. This product is at the very start of its adoption curve.

5. **FX spread collapsed 57%** from May to July, the steepest structural revenue decline. A pricing review could recover £200K to £350K.

## Repository structure

```
├── notebook.ipynb            # Full analysis methodology (start here)
├── problem_statement.md      # Case brief converted to markdown
├── dataset.csv               # Source data (196,187 rows)
├── src/
│   └── generate_charts.py    # Chart generation script
├── slides/
│   ├── slides.md             # Slidev presentation source
│   └── charts/               # Charts embedded in slides
├── charts/final/             # All generated charts
├── output/
│   └── revolut_gp_analysis.pdf  # Final deliverable (PDF)
├── requirements.txt
└── .gitignore
```

## Running the analysis

```bash
pip install -r requirements.txt
python src/generate_charts.py    # regenerate all charts
```

To rebuild the slides (requires Node.js):
```bash
cd slides && npx @slidev/cli export --format pdf --dark --output ../output/revolut_gp_analysis.pdf
```
