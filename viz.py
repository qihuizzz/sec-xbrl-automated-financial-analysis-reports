# viz.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _clean_xy(df: pd.DataFrame) -> Tuple[list[int], pd.DataFrame]:
    d = df.copy()
    d = d.sort_values("fy", ascending=True)
    x = d["fy"].astype(int).tolist()
    return x, d


def _beautify_axis(ax) -> None:
    ax.grid(True, axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _annotate_last(ax, x: list[int], y: pd.Series, suffix: str = "") -> None:
    s = pd.to_numeric(y, errors="coerce")
    if s.notna().sum() == 0:
        return
    idx = s.last_valid_index()
    if idx is None:
        return
    last_x = x[list(s.index).index(idx)] if idx in s.index else x[-1]
    last_y = float(s.loc[idx])
    ax.annotate(
        f"{last_y:.1f}{suffix}",
        xy=(last_x, last_y),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
    )


def save_financial_charts(display_df: pd.DataFrame, out_dir: str) -> Dict[str, str]:
    """
    display_df is output of format_financials_for_display
    USD lines are scaled to billions
    margin columns are decimals
    """
    out_path = Path(out_dir)
    _ensure_dir(out_path)

    if display_df is None or display_df.empty:
        return {}

    x, df = _clean_xy(display_df)

    saved: Dict[str, str] = {}

    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 160,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
        }
    )

    billions_fmt = mtick.FormatStrFormatter("%.1f")
    pct_fmt = mtick.PercentFormatter(xmax=1.0, decimals=0)

    def _save(fig, filename: str) -> str:
        fp = out_path / filename
        fig.savefig(fp, bbox_inches="tight")
        plt.close(fig)
        return str(fp).replace("\\", "/")

    # Chart 1 Revenue
    if "revenue" in df.columns and pd.to_numeric(df["revenue"], errors="coerce").notna().any():
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        ax.plot(x, df["revenue"], marker="o", linewidth=2)
        ax.set_title("Revenue")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("USD billions")
        ax.yaxis.set_major_formatter(billions_fmt)
        _beautify_axis(ax)
        _annotate_last(ax, x, df["revenue"], "B")
        saved["revenue"] = _save(fig, "revenue.png")

    # Chart 2 Margins
    margin_cols = [
        ("gross_margin", "Gross margin"),
        ("operating_margin", "Operating margin"),
        ("net_margin", "Net margin"),
        ("fcf_margin", "FCF margin"),
    ]
    have_any = any(c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any() for c, _ in margin_cols)
    if have_any:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        for c, label in margin_cols:
            if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any():
                ax.plot(x, df[c], marker="o", linewidth=2, label=label)
        ax.set_title("Margins")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("Percent")
        ax.yaxis.set_major_formatter(pct_fmt)
        ax.legend(loc="best")
        _beautify_axis(ax)
        saved["margins"] = _save(fig, "margins.png")

    # Chart 3 Cash flow
    cf_cols = [
        ("cfo", "CFO"),
        ("capex", "Capex"),
        ("fcf", "FCF"),
    ]
    have_any = any(c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any() for c, _ in cf_cols)
    if have_any:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        for c, label in cf_cols:
            if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any():
                ax.plot(x, df[c], marker="o", linewidth=2, label=label)
        ax.set_title("Cash flow")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("USD billions")
        ax.yaxis.set_major_formatter(billions_fmt)
        ax.legend(loc="best")
        _beautify_axis(ax)
        saved["cash_flow"] = _save(fig, "cash_flow.png")

    # Chart 4 Revenue YoY
    if "revenue_yoy" in df.columns and pd.to_numeric(df["revenue_yoy"], errors="coerce").notna().any():
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        ax.bar(x, df["revenue_yoy"])
        ax.set_title("Revenue YoY")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("Percent")
        ax.yaxis.set_major_formatter(pct_fmt)
        _beautify_axis(ax)
        saved["revenue_yoy"] = _save(fig, "revenue_yoy.png")

    # New chart 5 Income statement levels
    level_cols = [
        ("revenue", "Revenue"),
        ("gross_profit", "Gross profit"),
        ("operating_income", "Operating income"),
        ("net_income", "Net income"),
    ]
    have_any = any(c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any() for c, _ in level_cols)
    if have_any:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        for c, label in level_cols:
            if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any():
                ax.plot(x, df[c], marker="o", linewidth=2, label=label)
        ax.set_title("Income statement levels")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("USD billions")
        ax.yaxis.set_major_formatter(billions_fmt)
        ax.legend(loc="best")
        _beautify_axis(ax)
        saved["income_statement"] = _save(fig, "income_statement.png")

    # New chart 6 Balance sheet snapshot
    bs_cols = [
        ("cash", "Cash"),
        ("equity", "Equity"),
    ]
    have_any = any(c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any() for c, _ in bs_cols)
    if have_any:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        for c, label in bs_cols:
            if c in df.columns and pd.to_numeric(df[c], errors="coerce").notna().any():
                ax.plot(x, df[c], marker="o", linewidth=2, label=label)
        ax.set_title("Balance sheet snapshot")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("USD billions")
        ax.yaxis.set_major_formatter(billions_fmt)
        ax.legend(loc="best")
        _beautify_axis(ax)
        saved["balance_sheet"] = _save(fig, "balance_sheet.png")

    # New chart 7 Cash flow quality
    if (
        "cfo" in df.columns
        and "net_income" in df.columns
        and pd.to_numeric(df["cfo"], errors="coerce").notna().any()
        and pd.to_numeric(df["net_income"], errors="coerce").notna().any()
    ):
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        diff = pd.to_numeric(df["cfo"], errors="coerce") - pd.to_numeric(df["net_income"], errors="coerce")
        ax.bar(x, diff)
        ax.axhline(0, linewidth=1)
        ax.set_title("Cash flow quality")
        ax.set_xlabel("Fiscal year")
        ax.set_ylabel("CFO minus net income, USD billions")
        ax.yaxis.set_major_formatter(billions_fmt)
        _beautify_axis(ax)
        saved["cash_quality"] = _save(fig, "cash_quality.png")

    return saved