# Methodology

## Analytical approach

The analysis follows a standard profitability root cause framework: decompose, attribute, size, prioritise.

### 1. Data window and normalisation

The dataset spans the L90D window provided by Revolut, extracted on Jul 23 2024. The window covers Apr 24 – Jul 23 2024 — 91 days when both endpoints are counted inclusively, which is how the dataset was supplied. This structure means:

- **April**: 7 days (24th–30th) — partial start of the window
- **May**: 31 days — complete
- **June**: 30 days — complete
- **July**: 23 days (1st–23rd) — partial end of the window

Any month-over-month comparison must correct for the fact that May has 31 days of data while July only has 23. I use **daily run rates** (total GP ÷ days in month) for all month-to-month comparisons throughout the analysis. Raw monthly totals would understate July by 8 days and produce a false "£403K decline" signal when the business is actually running slightly ahead on a daily basis.

The L90D total (£8.34M) uses all 91 days of data; it is the correct aggregate figure for the metric the brief defines as "total gross profit in the last 90 days."

### 2. Decompose the P&L

GP L90D was broken down using the four-level account hierarchy (account_level_1 through account_level_4). The waterfall bridge compares May daily run rate to July daily run rate by account_level_2 to identify the largest movers. Categories with daily rate change below £100/day are excluded as noise.

### 3. Attribute changes to initiatives

Each of the 17 recent initiatives was mapped to the P&L categories it affects. Where the data shows a material change in a category that an initiative targets, the change is attributed to that initiative. Where multiple factors could explain a change (e.g., FX spread decline could be competitive pressure or Initiative 5 pricing), this is noted explicitly.

11 of 17 initiatives show measurable P&L impact in the dataset. The remaining 6 are either too early to measure, have no direct P&L line (e.g., UX improvements), or affect future periods.

### 4. Size interventions

Each intervention is sized using a conservative-to-moderate range derived from the observed data:

- **Cost levers** (vending machine, card production): sized by calculating the avoidable cost using actual daily run rates and user-level economics
- **Revenue recovery** (FX spread, bank payments): sized as 25-50% recovery of the observed daily rate decline, not full reversal
- **Growth plays** (eSIM, RevPoints, subscriptions): sized by extrapolating the observed daily growth trajectory, with scenarios for active scaling
- **Business growth**: sized using the observed GP/user differential between business and personal segments, multiplied by achievable user growth

No range assumes full reversal of any decline. All ranges are derived from the dataset, not external benchmarks.

### 5. Prioritise by confidence and controllability

Interventions are classified into three horizons based on two dimensions:

- **Controllability**: Is the lever within the team's direct operational control, or does it depend on external factors (market rates, competitive dynamics)?
- **Confidence**: Is the sizing based on a clear, observed trend, or does it require assumptions about user behaviour or market response?

High-confidence, high-controllability levers (vending machine restructuring, card cost migration, FX pricing review) are placed in the first 90-day horizon. Market-dependent levers (credit repricing, geographic expansion) are placed in the 6-12 month horizon.

## Tools

- **Python** (pandas, numpy, matplotlib) for data analysis and chart generation
- **HTML/CSS** for slide layout, rendered to PDF via Puppeteer
- **Jupyter notebook** for interactive analysis and methodology documentation
- **pytest** test suite (93 tests) validates every numeric claim in the presentation against the dataset

## Data notes

- 196,187 user-level P&L records across the L90D window provided by Revolut (Apr 24 – Jul 23 2024; 91 days inclusive)
- 191,412 unique users total; segment economics use the full dataset
- 2024 cohort users generate £14/user vs £49 for pre-2024 cohorts
- amount_gbp is denominated in thousands as stated in the documentation — converted to actual pounds in `charts.load_data()`
- All figures derived exclusively from the provided dataset
- NAP (New Active Person) segments are grouped by per-record status, so GP captures contribution during each phase. 2,324 users transitioned from 'Not Napped' to 'Napped' during the period and contribute to both segments accordingly
