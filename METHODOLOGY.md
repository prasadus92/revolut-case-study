# Methodology

## Analytical approach

The analysis follows a standard profitability root cause framework: decompose, attribute, size, prioritise.

### 1. Decompose the P&L

GP L90D was broken down using the four-level account hierarchy (account_level_1 through account_level_4). The waterfall bridge compares May to July monthly GP by account_level_2 to identify the largest movers. April was excluded from trend analysis because it contains only 7 days of data (24th to 30th).

### 2. Attribute changes to initiatives

Each of the 17 recent initiatives was mapped to the P&L categories it affects. Where the data shows a material change in a category that an initiative targets, the change is attributed to that initiative. Where multiple factors could explain a change (e.g., FX spread decline could be competitive pressure or Initiative 5 pricing), this is noted explicitly.

10 of 17 initiatives show measurable P&L impact in the dataset. The remaining 7 are either too early to measure, have no direct P&L line (e.g., UX improvements), or affect future periods.

### 3. Size interventions

Each intervention is sized using a conservative-to-moderate range derived from the observed data:

- **Cost levers** (vending machine, card production): sized by calculating the avoidable cost using actual monthly trends and user-level economics
- **Revenue recovery** (FX spread, bank payments): sized as 25-50% recovery of the observed decline, not full reversal
- **Growth plays** (eSIM, RevPoints, subscriptions): sized by extrapolating the observed growth trajectory, with scenarios for active scaling
- **Business growth**: sized using the observed GP/user differential between business and personal segments, multiplied by achievable user growth

No range assumes full reversal of any decline. All ranges are derived from the dataset, not external benchmarks.

### 4. Prioritise by confidence and controllability

Interventions are classified into three horizons based on two dimensions:

- **Controllability**: Is the lever within the team's direct operational control, or does it depend on external factors (market rates, competitive dynamics)?
- **Confidence**: Is the sizing based on a clear, observed trend, or does it require assumptions about user behaviour or market response?

High-confidence, high-controllability levers (vending machine restructuring, card cost migration, FX pricing review) are placed in the first 90-day horizon. Market-dependent levers (credit repricing, geographic expansion) are placed in the 6-12 month horizon.

## Tools

- **Python** (pandas, numpy, matplotlib) for data analysis and chart generation
- **HTML/CSS** for slide layout, rendered to PDF via Puppeteer
- **Jupyter notebook** for interactive analysis and methodology documentation

## Data notes

- 196,187 user-level P&L records across May, June, and July 2024
- amount_gbp is denominated in thousands as stated in the documentation
- All figures derived exclusively from the provided dataset
- NAP (New Active Person) status represents the final activation outcome during the 90-day window
