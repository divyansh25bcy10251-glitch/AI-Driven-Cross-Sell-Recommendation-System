"""
eda.py  ·  Bank Marketing Dataset — Exploratory Data Analysis
VITB AI Innovators Hub · Data Analyst Track

Run this standalone to reproduce all findings shown in the dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── styling ───────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#adbac7",
    "text.color":       "#adbac7",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "grid.color":       "#21262d",
    "axes.grid":        True,
    "axes.titlecolor":  "#f0f6fc",
    "axes.titlesize":   13,
    "font.family":      "sans-serif",
})
GREEN  = "#3fb950"
BLUE   = "#58a6ff"
RED    = "#f78166"

# ── 0. Load & first look ──────────────────────────────────────────────────────
print("=" * 60)
print("STEP 0  ·  Loading Data")
print("=" * 60)

df = pd.read_csv("bank-full.csv", sep=";")
print(f"Shape     : {df.shape}")
print(f"Columns   : {list(df.columns)}")
print(f"\nData types:\n{df.dtypes.to_string()}")
print(f"\nNull values:\n{df.isnull().sum().to_string()}")
print(f"\nClass balance:\n{df['y'].value_counts().to_string()}")
print(f"  → Subscription rate: {(df['y']=='yes').mean()*100:.2f}%")

# ── Feature engineering ───────────────────────────────────────────────────────
df["subscribed"] = (df["y"] == "yes").astype(int)
bins   = [17, 30, 45, 60, 100]
labels = ["18–30", "31–45", "46–60", "60+"]
df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels)

# ── 1. Which job types have the highest subscription rate? ────────────────────
print("\n" + "="*60)
print("Q1  ·  Subscription Rate by Job Type")
print("="*60)

job_stats = (
    df.groupby("job")["subscribed"]
    .agg(["mean","count"])
    .rename(columns={"mean":"sub_rate","count":"n"})
    .sort_values("sub_rate", ascending=False)
)
job_stats["sub_pct"] = job_stats["sub_rate"] * 100
print(job_stats.to_string())

fig, ax = plt.subplots(figsize=(9, 5))
job_sorted = job_stats.sort_values("sub_pct", ascending=True)
colors = [GREEN if r >= job_stats["sub_rate"].median() else BLUE
          for r in job_sorted["sub_rate"]]
ax.barh(job_sorted.index, job_sorted["sub_pct"], color=colors)
for i, (_, row) in enumerate(job_sorted.iterrows()):
    ax.text(row["sub_pct"] + 0.2, i, f"{row['sub_pct']:.1f}%",
            va="center", fontsize=9, color="#adbac7")
ax.set_xlabel("Subscription Rate (%)")
ax.set_title("Subscription Rate by Job Type\n(green = above median)", pad=12)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
plt.savefig("q1_job_subscription.png", dpi=150, bbox_inches="tight")
plt.close()
print("→ Saved: q1_job_subscription.png")

# ── 2. Balance vs subscription ────────────────────────────────────────────────
print("\n" + "="*60)
print("Q2  ·  Account Balance vs Subscription Likelihood")
print("="*60)

bal_bins   = [-10000, 0, 500, 1500, 3000, 6000, 15000, 200000]
bal_labels = ["<0","0–500","500–1.5k","1.5k–3k","3k–6k","6k–15k","15k+"]
df["bal_bracket"] = pd.cut(df["balance"], bins=bal_bins, labels=bal_labels)

bal_stats = (
    df.groupby("bal_bracket", observed=True)["subscribed"]
    .agg(["mean","count"])
    .rename(columns={"mean":"sub_rate","count":"n"})
    .reset_index()
)
bal_stats["sub_pct"] = bal_stats["sub_rate"] * 100
print(bal_stats.to_string())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Bar chart
ax = axes[0]
ax.bar(bal_stats["bal_bracket"].astype(str), bal_stats["sub_pct"],
       color=BLUE, alpha=0.8)
ax.plot(range(len(bal_stats)), bal_stats["sub_pct"],
        color=GREEN, lw=2, marker="o", ms=5)
ax.set_ylabel("Subscription Rate (%)")
ax.set_title("Sub Rate by Balance Bracket")
ax.tick_params(axis="x", rotation=30)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

# Box plot
ax2 = axes[1]
data_yes = df[df["y"]=="yes"]["balance"].clip(-5000, 20000)
data_no  = df[df["y"]=="no"]["balance"].clip(-5000, 20000)
bp = ax2.boxplot([data_yes, data_no],
                 patch_artist=True,
                 labels=["Subscribed","Not Subscribed"],
                 medianprops=dict(color="white", lw=2))
bp["boxes"][0].set_facecolor(GREEN + "80")
bp["boxes"][1].set_facecolor(RED   + "80")
ax2.set_ylabel("Balance (€, capped at 20k)")
ax2.set_title("Balance Distribution by Outcome")

plt.tight_layout()
plt.savefig("q2_balance_subscription.png", dpi=150, bbox_inches="tight")
plt.close()
print("→ Saved: q2_balance_subscription.png")

# ── 3. Age group subscription rate ───────────────────────────────────────────
print("\n" + "="*60)
print("Q3  ·  Subscription Rate by Age Group")
print("="*60)

age_stats = (
    df.groupby("age_group", observed=True)["subscribed"]
    .agg(["mean","count"])
    .rename(columns={"mean":"sub_rate","count":"n"})
    .reset_index()
)
age_stats["sub_pct"] = age_stats["sub_rate"] * 100
print(age_stats.to_string())

fig, ax = plt.subplots(figsize=(7, 4))
ax2b = ax.twinx()
x = range(len(age_stats))
ax.bar(x, age_stats["n"], color="#21262d", label="# Customers")
ax2b.plot(x, age_stats["sub_pct"], color=GREEN, lw=3,
          marker="o", ms=9, label="Sub rate %")
ax.set_xticks(x)
ax.set_xticklabels(age_stats["age_group"].astype(str))
ax.set_ylabel("# Customers", color="#8b949e")
ax2b.set_ylabel("Subscription Rate (%)", color=GREEN)
ax2b.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("Subscription Rate by Age Group\n(U-shaped pattern)")
ax.tick_params(axis="y", colors="#8b949e")
ax2b.tick_params(axis="y", colors=GREEN)
plt.tight_layout()
plt.savefig("q3_age_subscription.png", dpi=150, bbox_inches="tight")
plt.close()
print("→ Saved: q3_age_subscription.png")

# ── 4. Housing loan effect ────────────────────────────────────────────────────
print("\n" + "="*60)
print("Q4  ·  Housing Loan vs Subscription Rate")
print("="*60)

h_stats = df.groupby("housing")["subscribed"].mean() * 100
print(h_stats)
diff = h_stats["no"] - h_stats["yes"]
print(f"  → Penalty of having a housing loan: -{diff:.1f} pp")

# by age group too
ha_stats = (
    df.groupby(["housing","age_group"], observed=True)["subscribed"]
    .mean().reset_index()
)
ha_stats["sub_pct"] = ha_stats["subscribed"] * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

ax = axes[0]
ax.bar(["Has Housing Loan","No Housing Loan"],
       [h_stats["yes"], h_stats["no"]],
       color=[RED, GREEN], width=0.4)
for i, (label, val) in enumerate(zip(["yes","no"], [h_stats["yes"], h_stats["no"]])):
    ax.text(i, val+0.3, f"{val:.1f}%", ha="center", fontsize=12, color="white", fontweight="bold")
ax.set_ylabel("Subscription Rate (%)")
ax.set_title("Overall Housing Loan Effect")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

ax2 = axes[1]
age_groups = age_stats["age_group"].astype(str).tolist()
x = np.arange(len(age_groups))
w = 0.35
for i, (hval, color, lbl) in enumerate(
        [("yes", RED, "Has Housing Loan"), ("no", GREEN, "No Housing Loan")]):
    subset = ha_stats[ha_stats["housing"]==hval].sort_values("age_group")
    ax2.bar(x + i*w, subset["sub_pct"], width=w, color=color, label=lbl, alpha=0.85)
ax2.set_xticks(x + w/2)
ax2.set_xticklabels(age_groups)
ax2.set_ylabel("Subscription Rate (%)")
ax2.set_title("Housing Loan Effect by Age Group")
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.legend()

plt.tight_layout()
plt.savefig("q4_housing_subscription.png", dpi=150, bbox_inches="tight")
plt.close()
print("→ Saved: q4_housing_subscription.png")

# ── 5. Summary ────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY  ·  Key Findings for Relationship Managers")
print("="*60)
top_job = job_stats.index[0]
top_rate = job_stats["sub_pct"].iloc[0]
print(f"\n1. JOB:     Top segment is '{top_job}' at {top_rate:.1f}% subscription rate.")
print(f"2. BALANCE: Customers with >€6k balance convert at higher rates.")
print(f"3. AGE:     18–30 and 60+ groups show the highest receptivity (U-curve).")
print(f"4. HOUSING: Housing loan holders convert at {h_stats['yes']:.1f}% vs {h_stats['no']:.1f}% — "
      f"a {diff:.1f}pp drag.")
print("\n✅ EDA complete. Run `streamlit run app.py` to launch the dashboard.")
