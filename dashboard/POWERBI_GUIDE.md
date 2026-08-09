# Power BI Dashboard — Build Guide

This folder contains the two CSVs you need — `powerbi_dataset.csv` (main dataset) and
`model_comparison_results.csv` (model accuracy by season) — plus the steps to rebuild the
dashboard in Power BI Desktop. Budget ~45–60 minutes.

## 1. Import data
1. Power BI Desktop → **Get Data → Text/CSV** → select `powerbi_dataset.csv`. Click **Load**.
2. Repeat for `model_comparison_results.csv`.
3. In **Power Query Editor**, set `date` to type **Date**, and `season` to type **Text**
   (categorical). Close & Apply.

## 2. Build the season sort order (so charts don't sort alphabetically)
1. New Table (DAX): `SeasonOrder = {("Spring",1),("Summer",2),("Autumn",3),("Winter",4)}`
2. On `powerbi_dataset`, add a calculated column linking to this order, or simpler: **Sort by
   Column** → set `season` to sort by a new `season_rank` column (Spring=1, Summer=2, Autumn=3, Winter=4).

## 3. Pages & visuals

### Page 1 — Overview
- **Card visuals**: average chlorophyll-a, average turbidity, average suspended solids
- **Line chart**: `date` (axis) × `chlorophyll_a_ugL`, `turbidity_ntu`, `suspended_solids_mgL` (values) — shows the 5-year trend
- **Slicer**: `year` (2013–2017)

### Page 2 — Seasonality
- **Clustered column chart**: `season` (axis) × average of the 3 water-quality variables
- **Scatter chart**: `band3_green` (x) vs `chlorophyll_a_ugL` (y), colored by `season` — shows the reflectance relationship visually, the core insight of the project

### Page 3 — Model accuracy (from `model_comparison_results.csv`)
- **Clustered bar chart**: `variable` (axis) × `relative_error` (value), split by `model` — reproduces the model-comparison chart from the notebook
- **Table**: `variable`, `season`, `model`, `mse`, `relative_error` — full detail for anyone who wants to dig in
- **Callout card**: best model per variable (pull from `summary_metrics.json` in `/data`)

## 4. Formatting tips for a portfolio-ready look
- Use a consistent color per water-quality variable across every page (e.g. green = chlorophyll-a, brown = turbidity, grey = suspended solids)
- Add a text box on Page 1: *"Synthetic dataset reproducing real seasonal patterns and error ranges from PhD research; satellite-based model for reservoir monitoring, Cefni Reservoir, Anglesey, UK."* — this is important for transparency with recruiters
- Publish to **Power BI Service** (Publish → My Workspace) and use **File → Embed report → Publish to web** (or share the `.pbix` link) so recruiters can open it without installing anything
- Add the published link to your GitHub README and LinkedIn featured section

## 5. Where to link it from your portfolio
- GitHub README → badge/link to the published Power BI report
- LinkedIn "Featured" section → screenshot + link
- CV → one line under this project: *"Built an interactive Power BI dashboard translating model outputs into an operational monitoring view."*
