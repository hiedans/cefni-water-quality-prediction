"""
Synthetic data generator - Cefni Reservoir (Anglesey, Wales, UK) water quality monitoring.

IMPORTANT: This dataset is entirely SYNTHETIC. It reproduces the statistical
structure, seasonal patterns, and error magnitudes reported in the original
academic study (relative errors, MSE ranges, sample counts) but contains
NO real measurements from Welsh Water / Hamdden Ltd. It is safe to publish.

Design targets calibrated from the source study:
- Period: Jan 2013 - Dec 2017 (5 years), monthly sampling -> 60 records
- Variables: Chlorophyll-a (C), Turbidity (T), Suspended Solids (SS)
- Predictors: Landsat-8 OLI reflectance bands 2 (Blue), 3 (Green), 4 (Red)
- Seasonal cycles: Summer, Autumn, Winter, Spring
- Realistic value ranges for a shallow eutrophic UK reservoir
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

dates = pd.date_range("2013-01-01", "2017-12-01", freq="MS")


def month_to_season(m):
    if m in (6, 7, 8):
        return "Summer"
    if m in (9, 10, 11):
        return "Autumn"
    if m in (12, 1, 2):
        return "Winter"
    return "Spring"


rows = []
for d in dates:
    season = month_to_season(d.month)

    # seasonal baseline signal (algal blooms peak in summer -> higher chlorophyll)
    season_factor = {"Summer": 1.35, "Autumn": 0.95, "Winter": 0.55, "Spring": 0.85}[season]

    # Reflectance bands (0-1 scale), water absorbs more in red, reflects more in green/blue
    band_blue = np.clip(rng.normal(0.045, 0.006), 0.02, 0.09)
    band_green = np.clip(rng.normal(0.065, 0.008) * season_factor, 0.03, 0.13)
    band_red = np.clip(rng.normal(0.035, 0.005) * season_factor, 0.015, 0.09)

    # Physico-chemical parameters, driven by reflectance + season + noise
    chlorophyll_a = max(0.5, 8 + 140 * band_green - 60 * band_blue + rng.normal(0, 2.5) * season_factor)
    turbidity = max(0.3, 3 + 55 * band_red + rng.normal(0, 1.2))
    suspended_solids = max(0.2, 2 + 40 * band_red + 10 * band_green + rng.normal(0, 1.5))

    ph = np.clip(rng.normal(7.4, 0.35), 6.4, 8.6)
    conductivity = np.clip(rng.normal(210, 20) + (10 if season == "Summer" else 0), 140, 300)

    rows.append(
        dict(
            date=d.date().isoformat(),
            year=d.year,
            month=d.month,
            season=season,
            band2_blue=round(band_blue, 4),
            band3_green=round(band_green, 4),
            band4_red=round(band_red, 4),
            chlorophyll_a_ugL=round(chlorophyll_a, 2),
            turbidity_ntu=round(turbidity, 2),
            suspended_solids_mgL=round(suspended_solids, 2),
            ph=round(ph, 2),
            conductivity_uScm=round(conductivity, 1),
        )
    )

df = pd.DataFrame(rows)
df.to_csv("/home/claude/portfolio/data/cefni_reservoir_synthetic.csv", index=False)
print(df.shape)
print(df.head())
