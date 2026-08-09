# 🛰️ Predicting Water Quality from Satellite Imagery — Cefni Reservoir, UK

**Estimating chlorophyll-a, turbidity, and suspended solids from Landsat-8 reflectance, as an early-warning alternative to manual field sampling.**

[![Python](https://img.shields.io/badge/Python-3.11-blue)]() [![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)]() [![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)]()

## 📌 Overview

Water utilities need continuous visibility into reservoir water quality to manage algal blooms,
turbidity, and sediment — but manual field sampling is slow and expensive. This project shows an
end-to-end analytics workflow that estimates three key water-quality indicators directly from
free satellite imagery of the **Cefni Reservoir** (Anglesey, Wales, UK):

- 🌿 **Chlorophyll-a** (algal bloom indicator)
- 💧 **Turbidity**
- 🧪 **Suspended solids**

This is a portfolio rebuild of the remote-sensing + machine-learning methodology from my PhD
research (University of Rome "La Sapienza"), reconstructed with an open-source Python stack and
a business-facing Power BI dashboard.

## 🗂️ Repository structure

```
├── data/
│   ├── generate_dataset.py           # synthetic data generator (see note below)
│   ├── cefni_reservoir_synthetic.csv # analysis-ready dataset
│   ├── model_comparison_results.csv  # model errors per season/variable
│   └── summary_metrics.json
├── notebooks/
│   ├── analysis.py                   # full pipeline as a plain script
│   └── cefni_water_quality_analysis.ipynb   # narrated notebook with charts
├── assets/                           # exported chart images
├── dashboard/
│   └── POWERBI_GUIDE.md              # step-by-step to rebuild the Power BI dashboard
└── README.md
```

## ⚠️ A note on the data

The original research used real water-quality measurements supplied by **Welsh Water /
Hamdden Ltd** (2013–2017), which are proprietary and cannot be published. The dataset in this
repository is **synthetic**: generated to reproduce the same variables, seasonal patterns, and
error magnitudes reported in the original study, so the complete pipeline can be shared publicly
and safely. See `data/generate_dataset.py` for the full generation logic.

## 🔬 Methodology

1. **Pre-processing** — Haar wavelet decomposition of the spectral signal
2. **Exploratory analysis** — seasonal patterns, correlation between reflectance bands and water-quality parameters
3. **Dimensionality reduction** — PCA on Landsat-8 bands (Blue, Green, Red)
4. **Model comparison** — Linear Regression (LSE), SVR with RBF kernel, and a small Neural
   Network (MLP), trained per season and evaluated with MSE and Relative Error

| Original thesis method | Open-source equivalent used here |
|---|---|
| LSE (Least Squares) | `LinearRegression` |
| RBF Network | `SVR(kernel="rbf")` |
| WANN / ANFIS (Neural Network family) | `MLPRegressor` |

## 📊 Key result

A satellite-driven model can flag rising chlorophyll-a levels — an early sign of algal blooms —
without waiting for the next scheduled field sample, giving reservoir management teams an
early-warning layer at near-zero marginal cost.

## 📈 Dashboard

A companion **Power BI dashboard** translates these results into a stakeholder-facing view
(trend by season, model accuracy comparison, alert thresholds). See [`dashboard/POWERBI_GUIDE.md`](dashboard/POWERBI_GUIDE.md).

## 🛠️ Tech stack

`Python` · `pandas` · `scikit-learn` · `matplotlib` · `Power BI`

## ▶️ Run it yourself

```bash
pip install -r requirements.txt
python data/generate_dataset.py
python notebooks/analysis.py
```

## 🎓 Background

Adapted from my PhD thesis *"Estimating the Concentration of Physico-Chemical Parameters in
Hydroelectric Power Plant Reservoirs"* (University of Rome "La Sapienza", 2018), which applied
remote sensing and wavelet neural networks to reservoirs in Brazil and the UK.
