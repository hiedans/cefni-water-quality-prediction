"""
Predicting Water Quality Parameters from Satellite Reflectance
Cefni Reservoir, Anglesey, Wales, UK -- Portfolio re-implementation

Methodology adapted from a PhD thesis (Estimating the Concentration of
Physico-Chemical Parameters in Hydroelectric Power Plant Reservoirs) into a
business-facing data analytics project. Original models (WANN/ANFIS) are
re-implemented here with scikit-learn equivalents for a lean, reproducible,
open-source stack: Linear Regression (LSE), Support Vector Regression with
RBF kernel (RBF), a small Neural Network (MLP, ANN), and a simple
autoregressive baseline (AR).
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

plt.rcParams["figure.dpi"] = 110
ASSETS = "/home/claude/portfolio/assets"

df = pd.read_csv("/home/claude/portfolio/data/cefni_reservoir_synthetic.csv", parse_dates=["date"])

# ---------------------------------------------------------------
# 1. Simple Haar wavelet decomposition of the reflectance signal
#    (mirrors the wavelet pre-processing step used in the original study)
# ---------------------------------------------------------------
def haar_transform(signal):
    signal = np.asarray(signal, dtype=float)
    if len(signal) % 2 != 0:
        signal = np.append(signal, signal[-1])
    approx = (signal[0::2] + signal[1::2]) / np.sqrt(2)
    detail = (signal[0::2] - signal[1::2]) / np.sqrt(2)
    return approx, detail

approx_g, detail_g = haar_transform(df["band3_green"].values)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].plot(df["date"], df["band3_green"], color="#2E7D32")
ax[0].set_title("Green band reflectance (raw)")
ax[0].tick_params(axis="x", rotation=45)
ax[1].plot(approx_g, label="Approximation", color="#1565C0")
ax[1].plot(detail_g, label="Detail", color="#C62828")
ax[1].set_title("Haar wavelet decomposition")
ax[1].legend()
plt.tight_layout()
plt.savefig(f"{ASSETS}/01_wavelet_decomposition.png")
plt.close()

# ---------------------------------------------------------------
# 2. Exploratory analysis: seasonal pattern + correlation with bands
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
targets = ["chlorophyll_a_ugL", "turbidity_ntu", "suspended_solids_mgL"]
labels = ["Chlorophyll-a (µg/L)", "Turbidity (NTU)", "Suspended Solids (mg/L)"]
for ax, t, lab in zip(axes, targets, labels):
    df.boxplot(column=t, by="season", ax=ax,
               positions=[0, 1, 2, 3])
    ax.set_title(lab)
    ax.set_xlabel("")
plt.suptitle("")
plt.tight_layout()
plt.savefig(f"{ASSETS}/02_seasonal_boxplots.png")
plt.close()

corr = df[["band2_blue", "band3_green", "band4_red"] + targets].corr()
fig, ax = plt.subplots(figsize=(5.5, 4.5))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha="right")
ax.set_yticklabels(corr.columns)
for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
fig.colorbar(im)
plt.title("Correlation: satellite bands vs. water quality")
plt.tight_layout()
plt.savefig(f"{ASSETS}/03_correlation_heatmap.png")
plt.close()

# ---------------------------------------------------------------
# 3. PCA on the spectral bands (mirrors the factor analysis / PCA
#    step used in the original study to reduce band redundancy)
# ---------------------------------------------------------------
X_bands = df[["band2_blue", "band3_green", "band4_red"]].values
X_scaled = StandardScaler().fit_transform(X_bands)
pca = PCA(n_components=3).fit(X_scaled)
explained = pca.explained_variance_ratio_

fig, ax = plt.subplots(figsize=(5, 3.5))
ax.bar(range(1, 4), explained * 100, color="#455A64")
ax.set_xticks([1, 2, 3])
ax.set_xlabel("Principal Component")
ax.set_ylabel("Variance explained (%)")
ax.set_title("PCA - spectral band variance explained")
plt.tight_layout()
plt.savefig(f"{ASSETS}/04_pca_variance.png")
plt.close()

# ---------------------------------------------------------------
# 4. Model comparison per season: LSE (Linear), RBF (SVR), ANN (MLP)
#    Metrics: MSE and Relative Error, same formulas as the source study
# ---------------------------------------------------------------
results = []
predictions_store = {}

features = ["band2_blue", "band3_green", "band4_red"]
seasons = ["Summer", "Autumn", "Winter", "Spring"]

models = {
    "LSE": lambda: LinearRegression(),
    "RBF": lambda: SVR(kernel="rbf", C=10, gamma="scale"),
    "ANN": lambda: MLPRegressor(hidden_layer_sizes=(16, 8), max_iter=3000, random_state=42),
}

for target in targets:
    for season in seasons:
        sub = df[df["season"] == season]
        X = sub[features].values
        y = sub[target].values
        if len(X) < 6:
            continue
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
        for name, make_model in models.items():
            model = make_model()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rel_err = np.mean(np.abs(y_pred - y_test) / np.maximum(np.abs(y_test), 1e-6))
            results.append(dict(variable=target, season=season, model=name,
                                 mse=mse, relative_error=rel_err, n_test=len(y_test)))

results_df = pd.DataFrame(results)
results_df.to_csv("/home/claude/portfolio/data/model_comparison_results.csv", index=False)

# Summary chart: relative error by model, averaged across seasons, per variable
summary = results_df.groupby(["variable", "model"])["relative_error"].mean().unstack()
fig, ax = plt.subplots(figsize=(7, 4))
summary.plot(kind="bar", ax=ax, color=["#1565C0", "#EF6C00", "#2E7D32"])
ax.set_ylabel("Mean relative error")
ax.set_title("Model comparison - mean relative error by variable")
ax.set_xticklabels(["Chlorophyll-a", "Turbidity", "Suspended Solids"], rotation=0)
plt.tight_layout()
plt.savefig(f"{ASSETS}/05_model_comparison.png")
plt.close()

# Best model per variable
best_model = results_df.groupby(["variable", "model"])["relative_error"].mean().reset_index()
best_model = best_model.loc[best_model.groupby("variable")["relative_error"].idxmin()]

summary_json = {
    "n_samples": int(len(df)),
    "date_range": [df["date"].min().strftime("%Y-%m"), df["date"].max().strftime("%Y-%m")],
    "pca_variance_explained": [round(float(v) * 100, 1) for v in explained],
    "best_model_per_variable": best_model.to_dict(orient="records"),
    "overall_mean_relative_error": round(float(results_df["relative_error"].mean()), 4),
}
with open("/home/claude/portfolio/data/summary_metrics.json", "w") as f:
    json.dump(summary_json, f, indent=2)

print(json.dumps(summary_json, indent=2))
print("\nAssets written to:", ASSETS)
