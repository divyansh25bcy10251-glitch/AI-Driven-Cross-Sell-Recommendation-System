# EXPLANATION.md

## Bank Cross-Sell Intelligence — Data Analyst Track  
**VITB AI Innovators Hub · Screening Task Submission**

---

## What I built

A two-part deliverable:

1. **`eda.py`** — A standalone Python script that loads the UCI Bank Marketing Dataset, performs structured EDA, and outputs four business-question charts as `.png` files. Running it is the equivalent of walking through a Jupyter notebook but without the cell overhead.

2. **`app.py`** — A Streamlit dashboard with five interactive sections, a sidebar filter panel (job type, education, balance range, housing loan, personal loan), and live-computed KPIs. Every chart in the dashboard is built with Plotly so filters immediately rerender the graphs.

---

## How the data works

The dataset has **45,211 rows and 17 columns**. Each row is one customer from a Portuguese bank's telemarketing campaign. The target column `y` (renamed `subscribed` in the code) tells us whether that customer agreed to a term deposit.

The class imbalance is real: only **13.4% of customers subscribed**. That matters a lot when you later build an ML model — a dumb classifier that always predicts "no" would be 86.6% accurate, which is why accuracy alone is a poor metric for this problem. For the EDA layer though, we're not predicting yet — we're segmenting.

Feature types I worked with:

| Type | Columns |
|---|---|
| Demographic | age, job, marital, education |
| Financial | balance, housing, loan, default |
| Campaign metadata | duration, campaign, pdays, previous, poutcome |
| Target | y |

---

## The four business questions — what I found and why it makes sense

### Q1: Which job types have the highest subscription rate?

**Students (33.1%) and Retired (25.3%)** are the highest converters. Blue-collar workers (8.6%) and services staff (8.8%) are at the bottom.

*Why this makes sense:* Students and retirees have simpler financial lives — fewer competing obligations. A student getting their first financial product, or a retiree consolidating savings, is more receptive than a 38-year-old blue-collar worker managing a mortgage, car payment, and school fees.

**RM implication:** Don't cold-pitch blue-collar workers with generic product offers. If you do call them, lead with a pain point they actually have (cost reduction, emergency buffer) rather than investment growth.

---

### Q2: Balance vs subscription likelihood

Subscription rate increases monotonically with balance bracket. Customers with negative balances convert at ~9%; customers with €6k+ convert at ~19%.

*Why this makes sense:* Higher balance = more financial slack = more openness to adding new products. People who are overdrawn are in survival mode, not growth mode.

The box plot reinforces this: the median balance of subscribers is visibly higher than non-subscribers.

**RM implication:** Balance is a *pre-call filter*. Sort your outreach list by balance descending before you start dialing.

---

### Q3: Age group subscription rates

This produces a **U-shaped curve**: 18–30 (16.9%) and 60+ (22.3%) outperform the middle segments (31–45 at 12.7%, 46–60 at 11.6%).

*Why this makes sense:* The mid-career cohort carries the heaviest financial load (mortgage, kids, car). Young adults and seniors have different but shared trait — more financial headroom. Seniors may also be reinvesting pensions; young adults may be starting to save.

The chart uses a dual-axis design (bar for volume, line for rate) because the two measures operate on completely different scales. Showing them together lets an RM see *both* how many customers exist in each segment and how likely they are to convert.

---

### Q4: Housing loan effect

Customers **without** a housing loan subscribe at 16.8% vs 10.8% for those who have one — a **6 percentage point suppression**.

This holds across every age group when broken down by both variables. It's not an artifact of one cohort.

*Why this makes sense:* An existing mortgage is a major psychological and financial commitment. Taking on another product feels riskier when you're already locked into a large monthly payment.

**RM implication:** For housing loan holders, pitch low-commitment add-ons (credit card with cashback, small life insurance) rather than more debt. Frame it as protection, not expansion.

---

## Dashboard design decisions

**Sidebar filters are global.** Every chart respects the active filters. This is intentional — an RM might want to look only at middle-aged management-level customers with balances between €2k–€10k. All four charts update simultaneously.

**KPI cards at the top** give an at-a-glance sanity check so the RM knows how many customers their current filter covers and what the baseline conversion rate looks like before diving into the breakdowns.

**Insight callouts** below each chart translate the visual into a concrete action — not "here's a chart" but "here's what you do with this."

**The correlation heatmap (section 5)** is a bonus section. It highlights that `duration` has the strongest correlation with subscription, but duration is only known *after* the call ends. You can't use it to decide *who to call*. This is a classic data leakage trap in this dataset that often trips up people new to it. The actionable predictors pre-call are `balance` and `previous` (number of prior contacts).

---

## What I'd do next (if selected)

- **Feature engineering for the ML model**: encode categorical variables (job, education, marital) using target encoding rather than one-hot to avoid dimensionality explosion.
- **Handle class imbalance**: SMOTE or class weights in the classifier — the 86/14 split will skew a vanilla logistic regression.
- **Add a propensity score output** to the dashboard: instead of segment rates, show a per-customer predicted probability that an RM can sort by.
- **Connect to a live data source**: swap the CSV read for a database query so the dashboard reflects current customer state rather than a static export.

---

*Dataset: UCI Bank Marketing Dataset (bank-full.csv) — ~45k records, Portuguese bank telemarketing campaign.*  
*Stack: Python 3, Pandas, NumPy, Plotly, Streamlit, Matplotlib, Seaborn.*
