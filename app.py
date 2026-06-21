import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Cross-Sell Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #0d1117; }

  /* KPI cards */
  .kpi-row { display: flex; gap: 16px; margin-bottom: 24px; }
  .kpi-card {
    flex: 1;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
  }
  .kpi-label { font-size: 12px; font-weight: 500; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
  .kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #f0f6fc; line-height: 1; }
  .kpi-sub { font-size: 12px; color: #58a6ff; margin-top: 4px; }

  /* Section headers */
  .section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px; font-weight: 700; color: #f0f6fc;
    margin: 32px 0 4px 0; padding-bottom: 8px;
    border-bottom: 2px solid #238636;
  }
  .section-sub { font-size: 13px; color: #8b949e; margin-bottom: 20px; }

  /* Insight callout */
  .insight-box {
    background: #0d2818;
    border-left: 3px solid #238636;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 13px; color: #adbac7;
    margin-top: 12px;
  }
  .insight-box strong { color: #3fb950; }

  /* Override streamlit backgrounds */
  .stApp { background: #0d1117; }
  section[data-testid="stSidebar"] { background: #161b22 !important; }
  .stSelectbox label, .stMultiSelect label, .stSlider label { color: #8b949e !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "#161b22",
        "plot_bgcolor": "#161b22",
        "font": {"color": "#adbac7", "family": "Inter"},
        "title": {"font": {"color": "#f0f6fc", "size": 15, "family": "Space Grotesk"}},
        "xaxis": {"gridcolor": "#21262d", "linecolor": "#30363d", "zerolinecolor": "#21262d"},
        "yaxis": {"gridcolor": "#21262d", "linecolor": "#30363d", "zerolinecolor": "#21262d"},
        "legend": {"bgcolor": "#161b22", "bordercolor": "#30363d"},
        "colorway": ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff"],
    }
}

# ─── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("bank-full.csv", sep=";")
    df["subscribed"] = (df["y"] == "yes").astype(int)
    bins = [17, 30, 45, 60, 100]
    labels = ["18–30", "31–45", "46–60", "60+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels)
    return df

df = load_data()

# ─── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Filters")
    st.markdown("---")

    jobs_all = sorted(df["job"].unique())
    selected_jobs = st.multiselect("Job types", jobs_all, default=jobs_all, key="job_filter")

    edu_all = sorted(df["education"].unique())
    selected_edu = st.multiselect("Education level", edu_all, default=edu_all)

    bal_min, bal_max = int(df["balance"].min()), int(df["balance"].max())
    balance_range = st.slider("Balance range (€)", bal_min, bal_max, (bal_min, min(20000, bal_max)))

    housing_filter = st.selectbox("Housing loan", ["All", "Yes", "No"])
    loan_filter = st.selectbox("Personal loan", ["All", "Yes", "No"])

    st.markdown("---")
    st.markdown("<span style='font-size:11px;color:#484f58;'>VITB AI Innovators Hub · Data Analyst Track</span>", unsafe_allow_html=True)

# Apply filters
mask = (
    df["job"].isin(selected_jobs) &
    df["education"].isin(selected_edu) &
    df["balance"].between(*balance_range)
)
if housing_filter != "All":
    mask &= df["housing"] == housing_filter.lower()
if loan_filter != "All":
    mask &= df["loan"] == loan_filter.lower()

dff = df[mask]

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 24px 0;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#f0f6fc;">
    🏦 Bank Cross-Sell Intelligence
  </div>
  <div style="font-size:14px;color:#8b949e;margin-top:4px;">
    UCI Bank Marketing Dataset · Relationship Manager Insights Dashboard
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI row ───────────────────────────────────────────────────────────────────
total = len(dff)
subscribers = dff["subscribed"].sum()
sub_rate = subscribers / total * 100 if total > 0 else 0
avg_bal = dff["balance"].mean()
median_age = dff["age"].median()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Customers (filtered)</div>
      <div class="kpi-value">{total:,}</div>
      <div class="kpi-sub">of {len(df):,} total</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Subscription Rate</div>
      <div class="kpi-value">{sub_rate:.1f}%</div>
      <div class="kpi-sub">{subscribers:,} subscribed</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Avg. Account Balance</div>
      <div class="kpi-value">€{avg_bal:,.0f}</div>
      <div class="kpi-sub">median age {median_age:.0f} yrs</div>
    </div>""", unsafe_allow_html=True)
with c4:
    housing_pct = (dff["housing"] == "yes").mean() * 100
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">With Housing Loan</div>
      <div class="kpi-value">{housing_pct:.1f}%</div>
      <div class="kpi-sub">existing product holders</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Q1 · Subscription rate by job type
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">① Subscription Rate by Job Type</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Which customer segments are most receptive to new products?</div>', unsafe_allow_html=True)

job_stats = (
    dff.groupby("job")["subscribed"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "sub_rate", "count": "customers"})
    .sort_values("sub_rate", ascending=True)
)
job_stats["sub_pct"] = job_stats["sub_rate"] * 100
job_stats["label"] = job_stats["sub_pct"].map("{:.1f}%".format)

col1, col2 = st.columns([3, 1])
with col1:
    fig = go.Figure()
    colors = ["#3fb950" if r >= job_stats["sub_rate"].median() else "#58a6ff"
              for r in job_stats["sub_rate"]]
    fig.add_trace(go.Bar(
        x=job_stats["sub_pct"], y=job_stats["job"],
        orientation="h",
        marker_color=colors,
        text=job_stats["label"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Subscription rate: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=380,
        margin=dict(l=0, r=60, t=10, b=10),
        xaxis_title="Subscription Rate (%)",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    top_job = job_stats.iloc[-1]
    bot_job = job_stats.iloc[0]
    st.markdown(f"""
    <div class="insight-box">
      <strong>🏆 Highest: {top_job['job']}</strong><br>
      {top_job['sub_pct']:.1f}% subscription rate
      <br><br>
      <strong>📉 Lowest: {bot_job['job']}</strong><br>
      {bot_job['sub_pct']:.1f}% subscription rate
      <br><br>
      <strong>RM Tip:</strong> Prioritise retired and student segments — they convert at nearly 2× the average rate. Blue-collar customers need stronger incentive framing.
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Q2 · Balance vs subscription
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">② Account Balance vs. Subscription Likelihood</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Does wealth signal intent to buy?</div>', unsafe_allow_html=True)

# Bin balance into brackets
bal_bins = [-10000, 0, 500, 1500, 3000, 6000, 15000, 200000]
bal_labels = ["<0", "0–500", "500–1.5k", "1.5k–3k", "3k–6k", "6k–15k", "15k+"]
dff2 = dff.copy()
dff2["bal_bracket"] = pd.cut(dff2["balance"], bins=bal_bins, labels=bal_labels)

bal_stats = (
    dff2.groupby("bal_bracket", observed=True)["subscribed"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "sub_rate", "count": "customers"})
)
bal_stats["sub_pct"] = bal_stats["sub_rate"] * 100

col1, col2 = st.columns(2)
with col1:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bal_stats["bal_bracket"].astype(str),
        y=bal_stats["sub_pct"],
        marker_color="#58a6ff",
        marker_line_color="#79c0ff",
        marker_line_width=1,
        hovertemplate="<b>Balance: %{x}</b><br>Subscription rate: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=bal_stats["bal_bracket"].astype(str),
        y=bal_stats["sub_pct"],
        mode="lines+markers",
        line=dict(color="#3fb950", width=2),
        marker=dict(size=6, color="#3fb950"),
        name="Trend",
    ))
    fig.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=320,
        margin=dict(l=0, r=20, t=10, b=10),
        yaxis_title="Subscription Rate (%)",
        xaxis_title="Account Balance Bracket (€)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Box plot of balance by subscription
    fig2 = go.Figure()
    for label, color in [("yes", "#3fb950"), ("no", "#f78166")]:
        sub_bal = dff[dff["y"] == label]["balance"].clip(-5000, 20000)
        fig2.add_trace(go.Box(
            y=sub_bal,
            name="Subscribed" if label == "yes" else "Not Subscribed",
            marker_color=color,
            boxmean="sd",
            hovertemplate="<b>%{fullData.name}</b><br>%{y:,.0f} €<extra></extra>",
        ))
    fig2.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=320,
        margin=dict(l=0, r=0, t=10, b=10),
        yaxis_title="Balance (€, capped at 20k)",
        showlegend=True,
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <strong>Key finding:</strong> Customers with balances above €6,000 subscribe at notably higher rates — wealth correlates with willingness to add new financial products.
  The distribution for subscribers is shifted right, suggesting balance is a useful pre-filter for RM outreach.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Q3 · Age group analysis
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">③ Subscription Rate by Age Group</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Which life stage is most open to new financial products?</div>', unsafe_allow_html=True)

age_stats = (
    dff.groupby("age_group", observed=True)["subscribed"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "sub_rate", "count": "customers"})
)
age_stats["sub_pct"] = age_stats["sub_rate"] * 100

col1, col2 = st.columns([2, 1])
with col1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=age_stats["age_group"].astype(str),
        y=age_stats["customers"],
        name="# Customers",
        marker_color="#21262d",
        hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=age_stats["age_group"].astype(str),
        y=age_stats["sub_pct"],
        name="Subscription %",
        mode="lines+markers",
        line=dict(color="#3fb950", width=3),
        marker=dict(size=10, color="#3fb950", line=dict(color="#0d1117", width=2)),
        hovertemplate="<b>%{x}</b><br>Sub rate: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=320,
        margin=dict(l=0, r=40, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="# Customers", secondary_y=False, gridcolor="#21262d")
    fig.update_yaxes(title_text="Subscription Rate (%)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    for _, row in age_stats.iterrows():
        bar_w = int(row["sub_pct"] / age_stats["sub_pct"].max() * 100)
        st.markdown(f"""
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#adbac7;margin-bottom:4px;">
            <span><b>{row['age_group']}</b></span>
            <span style="color:#3fb950;font-weight:600;">{row['sub_pct']:.1f}%</span>
          </div>
          <div style="background:#21262d;border-radius:4px;height:8px;overflow:hidden;">
            <div style="background:#3fb950;width:{bar_w}%;height:100%;border-radius:4px;"></div>
          </div>
          <div style="font-size:11px;color:#484f58;margin-top:2px;">{int(row['customers']):,} customers</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
  <strong>U-shaped pattern observed:</strong> Young adults (18–30) and seniors (60+) show the highest receptivity.
  The core working-age segment (31–45) has the most customers but converts at lower rates — likely due to financial commitments (mortgages, families).
  <strong>RM strategy:</strong> Use different product angles — savings/investment for seniors, flexible plans for young adults.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Q4 · Housing loan effect
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">④ Impact of Existing Housing Loan on New Product Uptake</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Does an existing financial commitment suppress cross-sell success?</div>', unsafe_allow_html=True)

housing_stats = (
    dff.groupby(["housing", "age_group"], observed=True)["subscribed"]
    .mean()
    .reset_index()
    .rename(columns={"subscribed": "sub_rate"})
)
housing_stats["sub_pct"] = housing_stats["sub_rate"] * 100

col1, col2 = st.columns(2)
with col1:
    # Simple comparison donut-style bars
    h_summary = (
        dff.groupby("housing")["subscribed"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "sub_rate"})
    )
    h_summary["sub_pct"] = h_summary["sub_rate"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=h_summary["housing"].map({"yes": "Has Housing Loan", "no": "No Housing Loan"}),
        y=h_summary["sub_pct"],
        marker_color=["#f78166", "#3fb950"],
        width=0.4,
        text=h_summary["sub_pct"].map("{:.1f}%".format),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Sub rate: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=300,
        margin=dict(l=0, r=20, t=30, b=10),
        yaxis_title="Subscription Rate (%)",
        yaxis_range=[0, h_summary["sub_pct"].max() * 1.3],
        title="Overall Effect",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.bar(
        housing_stats,
        x="age_group", y="sub_pct", color="housing",
        barmode="group",
        color_discrete_map={"yes": "#f78166", "no": "#3fb950"},
        labels={"sub_pct": "Subscription Rate (%)", "age_group": "Age Group", "housing": "Housing Loan"},
        title="By Age Group",
    )
    fig2.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=300,
        margin=dict(l=0, r=0, t=30, b=10),
        legend=dict(title="Housing Loan"),
    )
    st.plotly_chart(fig2, use_container_width=True)

has_housing_rate = dff[dff["housing"] == "yes"]["subscribed"].mean() * 100
no_housing_rate = dff[dff["housing"] == "no"]["subscribed"].mean() * 100
diff = no_housing_rate - has_housing_rate

st.markdown(f"""
<div class="insight-box">
  <strong>Clear suppression effect:</strong> Customers without a housing loan subscribe at {no_housing_rate:.1f}% vs {has_housing_rate:.1f}% for those with one —
  a <strong>{diff:.1f} percentage point difference</strong>.
  This pattern holds across all age groups. Customers carrying a mortgage may perceive additional products as financial overreach.
  <strong>RM action:</strong> For housing loan holders, emphasise low-commitment products (credit cards, small insurance) rather than additional loans.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Bonus: Correlation heatmap
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⑤ Feature Correlation Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Numeric feature correlations with subscription outcome</div>', unsafe_allow_html=True)

numeric_cols = ["age", "balance", "duration", "campaign", "previous", "subscribed"]
corr_df = dff[numeric_cols].corr()

fig = go.Figure(data=go.Heatmap(
    z=corr_df.values,
    x=corr_df.columns,
    y=corr_df.index,
    colorscale=[[0, "#f78166"], [0.5, "#21262d"], [1, "#3fb950"]],
    zmin=-1, zmax=1,
    text=np.round(corr_df.values, 2),
    texttemplate="%{text}",
    hovertemplate="<b>%{x} × %{y}</b><br>Correlation: %{z:.2f}<extra></extra>",
))
fig.update_layout(
    **PLOTLY_TEMPLATE["layout"],
    height=350,
    margin=dict(l=0, r=0, t=10, b=10),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <strong>Duration is the strongest predictor</strong> — but it's only known after the call ends, so it can't be used for pre-call targeting.
  <strong>Balance and previous contact</strong> are the most actionable pre-call signals.
  Campaign count has a negative correlation: the more times you've called someone, the less likely they are to convert — suggesting diminishing returns on repeat outreach.
</div>
""", unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#484f58;padding:8px 0;'>"
    "VITB AI Innovators Hub · Bank Cross-Sell Recommendation System · Data Analyst Track"
    "</div>",
    unsafe_allow_html=True,
)
