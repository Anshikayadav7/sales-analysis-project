"""Sales Data Analysis: cleaning, insights and charts for the Superstore dataset.

Usage (from the project folder):
    python sales_analysis.py
    python sales_analysis.py --input "path/to/other_superstore_file.csv"

Outputs:
    data/processed/sales_clean.csv   cleaned data (load this into Power BI)
    outputs/insights.md              insights calculated from the data
    outputs/charts/*.png             charts
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE / "data" / "raw" / "Sample - Superstore.csv"
CLEAN_PATH = BASE / "data" / "processed" / "sales_clean.csv"
CHART_DIR = BASE / "outputs" / "charts"
INSIGHTS_PATH = BASE / "outputs" / "insights.md"

REQUIRED = ["Order ID", "Order Date", "Ship Date", "Segment", "Region", "Category",
            "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit"]
BANDS = ["No discount", "1-20%", "21-40%", "Over 40%"]
GREEN, AMBER, RED = "#1f6f5c", "#e0a030", "#c0392b"


def money(x):
    sign = "-" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x/1e6:.2f}M" if x >= 1e6 else f"{sign}${x:,.0f}"


def load_and_clean(path):
    if not path.exists():
        sys.exit(f"Input file not found: {path}\nPut the Superstore CSV in data/raw/ or use --input.")
    try:
        df = pd.read_csv(path)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        sys.exit(f"The CSV is missing required columns: {missing}\nFound: {list(df.columns)}")

    print(f"Raw shape: {df.shape} | nulls: {int(df.isna().sum().sum())} | duplicates: {int(df.duplicated().sum())}")
    df = df.drop_duplicates().copy()
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    for c in ["order_date", "ship_date"]:
        df[c] = pd.to_datetime(df[c], format="mixed")
    for c in ["region", "category", "sub_category", "segment", "ship_mode"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().str.title()
    for c in ["sales", "quantity", "discount", "profit"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["order_date", "sales", "quantity", "discount", "profit"])
    if len(df) < before:
        print(f"Dropped {before - len(df)} rows with unusable values.")
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    df["ship_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["profit_margin"] = np.where(df["sales"] > 0, df["profit"] / df["sales"] * 100, 0.0).round(2)
    df["discount_band"] = pd.cut(df["discount"], [-0.01, 0, 0.2, 0.4, 1.0], labels=BANDS).astype(str)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Clean shape: {df.shape} | period: {df.order_date.min().date()} to {df.order_date.max().date()}")
    return df


def summarise(df, key):
    g = df.groupby(key)[["sales", "profit"]].sum()
    g["margin"] = g["profit"] / g["sales"] * 100
    return g


def build_insights(df):
    out = []
    S, P = df.sales.sum(), df.profit.sum()
    out.append(f"**Overview:** {money(S)} in sales and {money(P)} in profit ({P/S*100:.1f}% margin) from "
               f"{df.order_id.nunique():,} orders and {df.customer_id.nunique():,} customers, "
               f"{df.order_date.min():%b %Y} to {df.order_date.max():%b %Y}.")

    yr = summarise(df, "year")
    growth = yr["sales"].pct_change() * 100
    parts = [f"{y}: {money(r.sales)}" + ("" if np.isnan(growth[y]) else f" ({growth[y]:+.1f}%)") for y, r in yr.iterrows()]
    out.append("**Yearly sales (growth vs previous year):** " + "; ".join(parts) + ".")

    m = df.groupby("month")["sales"].sum()
    q4 = df[df.order_date.dt.month >= 10].sales.sum() / S * 100
    out.append(f"**Seasonality:** best month was {m.idxmax():%b %Y} ({money(m.max())}), weakest was "
               f"{m.idxmin():%b %Y} ({money(m.min())}). October to December brings {q4:.0f}% of all sales.")

    c = summarise(df, "category").sort_values("sales", ascending=False)
    out.append("**Categories:** " + "; ".join(f"{k} {money(r.sales)} sales, {r.margin:.1f}% margin" for k, r in c.iterrows()) + ".")
    low = c["margin"].idxmin()
    out.append(f"**Weakest category by margin:** {low} at {c.margin.min():.1f}%, against {c.margin.max():.1f}% for {c.margin.idxmax()}.")

    r = summarise(df, "region").sort_values("sales", ascending=False)
    out.append("**Regions:** " + "; ".join(f"{k} {money(x.sales)} sales, {x.margin:.1f}% margin" for k, x in r.iterrows()) + ".")

    sg = summarise(df, "segment").sort_values("sales", ascending=False)
    out.append("**Segments:** " + "; ".join(f"{k} {money(x.sales)} sales, {x.margin:.1f}% margin" for k, x in sg.iterrows()) + ".")

    sub = summarise(df, "sub_category").sort_values("profit")
    loss = sub[sub.profit < 0]
    if len(loss):
        out.append("**Loss-making sub-categories:** " + "; ".join(f"{k} ({money(x.profit)} profit on {money(x.sales)} sales)" for k, x in loss.iterrows()) + ".")
    top_sub = sub.sort_values("profit", ascending=False).head(3)
    out.append("**Most profitable sub-categories:** " + "; ".join(f"{k} ({money(x.profit)})" for k, x in top_sub.iterrows()) + ".")

    d = summarise(df, "discount_band").reindex(BANDS)
    out.append("**Profit margin by discount level:** " + "; ".join(f"{k}: {x.margin:.1f}%" for k, x in d.iterrows()) + ".")
    heavy = df[df.discount > 0.2]
    out.append(f"**Heavy discounting:** {len(heavy)/len(df)*100:.1f}% of order lines were discounted by more than 20%, "
               f"and together they made {money(heavy.profit.sum())} in profit on {money(heavy.sales.sum())} in sales.")

    p = df.groupby("product_name")[["sales", "profit"]].sum()
    out.append("**Top 5 products by sales:** " + "; ".join(f"{k} ({money(x.sales)})" for k, x in p.nlargest(5, "sales").iterrows()) + ".")
    out.append("**Top 5 products by profit:** " + "; ".join(f"{k} ({money(x.profit)})" for k, x in p.nlargest(5, "profit").iterrows()) + ".")
    out.append("**5 biggest loss-making products:** " + "; ".join(f"{k} ({money(x.profit)})" for k, x in p.nsmallest(5, "profit").iterrows()) + ".")
    neg = (p.profit < 0).sum()
    out.append(f"**Product breadth:** {neg} of {len(p):,} products lost money overall.")
    return out


def style():
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 120,
                         "axes.titleweight": "bold"})


def k_fmt(ax, axis="y"):
    f = matplotlib.ticker.FuncFormatter(lambda v, _: f"${v/1e3:,.0f}K")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def short(s, n=38):
    return s if len(s) <= n else s[: n - 1] + "…"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHART_DIR / name)
    plt.close(fig)


def make_charts(df):
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    style()

    # Revenue by year
    yr = summarise(df, "year")
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(yr.index.astype(str), yr.sales, color=GREEN)
    ax.bar_label(bars, labels=[money(v) for v in yr.sales], padding=3)
    ax.set_title("Revenue by year"); k_fmt(ax)
    save(fig, "01_revenue_by_year.png")

    # Monthly trend
    m = df.groupby("month")["sales"].sum()
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(m.index, m.values, color=GREEN, lw=2, label="Monthly sales")
    ax.plot(m.index, m.rolling(3).mean(), color=AMBER, ls="--", lw=2, label="3-month average")
    ax.set_title("Monthly sales trend"); ax.legend(); k_fmt(ax)
    save(fig, "02_monthly_sales_trend.png")

    # Seasonality: each year's months on the same axis
    t = df.assign(mon=df.order_date.dt.month).groupby(["year", "mon"])["sales"].sum().unstack(0)
    fig, ax = plt.subplots(figsize=(9, 4))
    t.plot(ax=ax, marker="o", lw=2)
    ax.set_xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_xlabel(""); ax.set_title("Monthly sales by year (seasonality)"); ax.legend(title="Year"); k_fmt(ax)
    save(fig, "03_seasonality_by_year.png")

    # Category and region: sales vs profit
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, k in zip(axs, ["category", "region"]):
        g = summarise(df, k).sort_values("sales", ascending=False)
        g[["sales", "profit"]].plot.bar(ax=ax, color=[GREEN, AMBER], rot=0)
        ax.set_title(f"Sales and profit by {k}"); ax.set_xlabel(""); k_fmt(ax)
    save(fig, "04_sales_profit_category_region.png")

    # Top 10 products by sales and by profit
    p = df.groupby("product_name")[["sales", "profit"]].sum()
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    for ax, col, color in [(axs[0], "sales", GREEN), (axs[1], "profit", AMBER)]:
        top = p.nlargest(10, col).sort_values(col)
        ax.barh([short(i) for i in top.index], top[col], color=color)
        ax.set_title(f"Top 10 products by {col}"); k_fmt(ax, "x")
    save(fig, "05_top_products.png")

    # Sub-category profit
    sub = summarise(df, "sub_category").sort_values("profit")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh(sub.index, sub.profit, color=np.where(sub.profit < 0, RED, GREEN))
    ax.set_title("Profit by sub-category (red = loss)"); k_fmt(ax, "x")
    save(fig, "06_profit_by_subcategory.png")

    # Discount vs margin
    d = summarise(df, "discount_band").reindex(BANDS)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(d.index, d.margin, color=np.where(d.margin < 0, RED, GREEN))
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in d.margin], padding=3)
    ax.axhline(0, color="black", lw=.8); ax.set_title("Profit margin by discount level")
    ax.set_ylabel("Profit margin (%)")
    save(fig, "07_discount_vs_margin.png")

    # Region x category profit heatmap
    pv = df.pivot_table(index="region", columns="category", values="profit", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(7, 4))
    lim = np.abs(pv.values).max()
    im = ax.imshow(pv, cmap="RdYlGn", vmin=-lim, vmax=lim)
    ax.set_xticks(range(pv.shape[1]), pv.columns); ax.set_yticks(range(pv.shape[0]), pv.index)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            ax.text(j, i, money(pv.iat[i, j]), ha="center", va="center", fontsize=9)
    ax.set_title("Profit by region and category"); fig.colorbar(im)
    save(fig, "08_profit_heatmap.png")


def main():
    ap = argparse.ArgumentParser(description="Superstore sales analysis")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="path to the raw Superstore CSV")
    args = ap.parse_args()

    df = load_and_clean(args.input)
    insights = build_insights(df)
    INSIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    INSIGHTS_PATH.write_text("# Sales insights\n\nAll figures are calculated from the CSV by `sales_analysis.py`.\n\n"
                             + "\n".join(f"- {i}" for i in insights) + "\n", encoding="utf-8")
    print("\n=== INSIGHTS ===")
    for i in insights:
        print("-", i.replace("**", ""))
    make_charts(df)
    print(f"\nSaved: {CLEAN_PATH.relative_to(BASE)}, {INSIGHTS_PATH.relative_to(BASE)}, {CHART_DIR.relative_to(BASE)}/")


if __name__ == "__main__":
    main()
