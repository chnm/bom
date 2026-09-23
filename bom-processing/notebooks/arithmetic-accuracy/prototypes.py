"""Print-legibility prototypes for replacing Figures 4 and 5.

Run with ``uv run python prototypes.py``. Output goes to ``figures/prototypes/``.
Each prototype folds the all-data and legible-only views into one figure by
distinguishing weeks that contain an illegible value.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis import (
    PreparedData,
    _save_figure,
    _year_ticks,
    build_comparison,
    load_data,
    prepare_data,
)

POSITIVE = "#C44E35"
NEGATIVE = "#087E8B"
POSITIVE_LIGHT = "#E8B4A8"
NEGATIVE_LIGHT = "#9FCDD2"
INK = "#222222"


def flagged_comparison(prepared: PreparedData) -> pd.DataFrame:
    """All comparable weeks with a ``legible`` flag for the whole weekly bill."""

    data = build_comparison(prepared)
    weeks = prepared.bills[["joinid", "year", "week_number"]].drop_duplicates()
    illegible_weeks = weeks[weeks["joinid"].isin(prepared.illegible_joinids)][
        ["year", "week_number"]
    ].drop_duplicates()
    keys = pd.MultiIndex.from_frame(illegible_weeks)
    data["legible"] = ~pd.MultiIndex.from_frame(data[["year", "week_number"]]).isin(keys)
    return data


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )


# ---------------------------------------------------------------------------
# Option 1: annual diverging bars split by legibility, plus magnitude panel
# ---------------------------------------------------------------------------


def annual_direction_shares(data: pd.DataFrame, count_type: str) -> pd.DataFrame:
    panel = data[data["count_type"].eq(count_type)].assign(
        pos_legible=lambda d: d["difference"].gt(0) & d["legible"],
        pos_illegible=lambda d: d["difference"].gt(0) & ~d["legible"],
        neg_legible=lambda d: d["difference"].lt(0) & d["legible"],
        neg_illegible=lambda d: d["difference"].lt(0) & ~d["legible"],
    )
    grouped = panel.groupby("year")
    out = grouped[["pos_legible", "pos_illegible", "neg_legible", "neg_illegible"]].sum()
    out.insert(0, "weeks", grouped.size())
    errors = panel[panel["difference"].ne(0)].groupby("year")["absolute_difference"]
    out["median_abs_error"] = errors.median()
    out["max_abs_error"] = errors.max()
    for column in ["pos_legible", "pos_illegible", "neg_legible", "neg_illegible"]:
        out[f"{column}_share"] = 100 * out[column] / out["weeks"]
    return out.reset_index()


def plot_option_1(data: pd.DataFrame, count_type: str, output_base: Path) -> None:
    _style()
    annual = annual_direction_shares(data, count_type)
    years = annual["year"].to_numpy()
    fig, (top, bottom) = plt.subplots(
        2,
        1,
        figsize=(10, 6.5),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1.6], "hspace": 0.08},
    )

    top.bar(years, annual["pos_legible_share"], color=POSITIVE, width=0.85)
    top.bar(
        years,
        annual["pos_illegible_share"],
        bottom=annual["pos_legible_share"],
        color=POSITIVE_LIGHT,
        width=0.85,
    )
    top.bar(years, -annual["neg_legible_share"], color=NEGATIVE, width=0.85)
    top.bar(
        years,
        -annual["neg_illegible_share"],
        bottom=-annual["neg_legible_share"],
        color=NEGATIVE_LIGHT,
        width=0.85,
    )
    top.axhline(0, color=INK, linewidth=0.8)
    top.set_ylabel("Weeks with an arithmetic error\n(% of comparable weeks)")
    top.yaxis.set_major_formatter(lambda v, _: f"{abs(v):.0f}")
    top.grid(axis="y", color="#E0E0E0", linewidth=0.6)
    top.spines[["top", "right"]].set_visible(False)
    top.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=POSITIVE, label="Printed subtotal larger, legible week"),
            plt.Rectangle((0, 0), 1, 1, color=POSITIVE_LIGHT, label="Printed subtotal larger, week contains illegible value"),
            plt.Rectangle((0, 0), 1, 1, color=NEGATIVE, label="Parish sum larger, legible week"),
            plt.Rectangle((0, 0), 1, 1, color=NEGATIVE_LIGHT, label="Parish sum larger, week contains illegible value"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22),
        ncol=2,
        frameon=False,
    )

    bottom.vlines(years, annual["median_abs_error"], annual["max_abs_error"], color="#999999", linewidth=1)
    bottom.scatter(years, annual["max_abs_error"], s=10, color="#999999", zorder=3)
    bottom.scatter(years, annual["median_abs_error"], s=16, color=INK, zorder=4)
    bottom.set_yscale("log")
    bottom.set_ylabel("Size of error\n(median · maximum)")
    bottom.set_xlabel("Year")
    bottom.grid(axis="y", color="#E0E0E0", linewidth=0.6)
    bottom.spines[["top", "right"]].set_visible(False)
    bottom.set_xticks(np.arange(1640, years.max() + 1, 10))

    label = "burial" if count_type == "buried" else "plague"
    fig.suptitle(f"Annual arithmetic errors in weekly {label} counts", y=0.995)
    fig.subplots_adjust(top=0.82, bottom=0.09, left=0.11, right=0.98)
    _save_figure(fig, output_base)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Option 2: the over/under form as small multiples by decade
# ---------------------------------------------------------------------------


def plot_option_2(data: pd.DataFrame, prepared: PreparedData, count_type: str, output_base: Path) -> None:
    _style()
    panel = prepared.calendar.merge(
        data.loc[data["count_type"].eq(count_type), ["year", "week_number", "difference", "legible"]],
        on=["year", "week_number"],
        how="left",
    )
    panel = panel[panel["difference"].notna() & panel["difference"].ne(0)]
    decades = sorted(set((panel["year"] // 10) * 10))
    limit = panel["difference"].abs().max()

    fig, axes = plt.subplots(len(decades), 1, figsize=(8.5, 0.72 * len(decades) + 1), sharey=True)
    strip_weeks = 530
    for ax, decade in zip(axes, decades, strict=True):
        strip = panel[(panel["year"] // 10 * 10).eq(decade)]
        cal = prepared.calendar[prepared.calendar["year"].between(decade, decade + 9)]
        colors = np.where(
            strip["difference"].gt(0),
            np.where(strip["legible"], POSITIVE, POSITIVE_LIGHT),
            np.where(strip["legible"], NEGATIVE, NEGATIVE_LIGHT),
        )
        ax.vlines(strip["time_index"], 0, strip["difference"], color=colors, linewidth=1.1)
        ax.axhline(0, color=INK, linewidth=0.6)
        ax.set_yscale("symlog", linthresh=5)
        ax.set_ylim(-limit * 1.5, limit * 1.5)
        ax.set_xlim(cal["time_index"].min() - 2, cal["time_index"].min() + strip_weeks)
        starts = cal.groupby("year", as_index=False).agg(time_index=("time_index", "min"), weeks=("time_index", "size"))
        ax.set_xticks(starts["time_index"], np.where(starts["weeks"] >= 20, starts["year"].astype(str), ""))
        ax.tick_params(axis="x", length=2)
        ax.set_yticks([-100, 0, 100], ["−100", "0", "100"])
        ax.grid(axis="y", color="#E8E8E8", linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.text(0.005, 0.92, f"{decade}s", transform=ax.transAxes, va="top", fontsize=10, fontweight="bold")

    fig.supylabel("Printed subtotal minus parish-summed count (symmetric log scale)", fontsize=11)
    fig.legend(
        handles=[
            plt.Line2D([], [], color=POSITIVE, linewidth=3, label="Printed subtotal larger"),
            plt.Line2D([], [], color=NEGATIVE, linewidth=3, label="Parish sum larger"),
            plt.Line2D([], [], color="#BBBBBB", linewidth=3, label="Lighter: week contains an illegible value"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=3,
        frameon=False,
    )
    label = "burial" if count_type == "buried" else "plague"
    fig.suptitle(f"Weekly arithmetic differences in {label} counts, by decade", y=0.998)
    fig.subplots_adjust(top=0.94, bottom=0.03, left=0.09, right=0.99, hspace=0.7)
    _save_figure(fig, output_base)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Option 4: rolling error rate by direction, with labelled outliers
# ---------------------------------------------------------------------------


def plot_option_4(data: pd.DataFrame, prepared: PreparedData, count_type: str, output_base: Path, top_n: int = 15) -> None:
    _style()
    panel = prepared.calendar.merge(
        data.loc[data["count_type"].eq(count_type), ["year", "week_number", "difference", "legible"]],
        on=["year", "week_number"],
        how="left",
    ).set_index("time_index")
    observed = panel["difference"].notna()
    window, min_periods = 52, 26
    rate = lambda mask: (  # noqa: E731
        100 * mask.astype(float).where(observed).rolling(window, min_periods=min_periods).mean()
    )
    pos_rate = rate(panel["difference"].gt(0))
    neg_rate = rate(panel["difference"].lt(0))
    ticks, labels = _year_ticks(prepared.calendar)

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(12, 6.5), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.6], "hspace": 0.1}
    )
    top.plot(pos_rate.index, pos_rate, color=POSITIVE, linewidth=1.2, label="Printed subtotal larger")
    top.plot(neg_rate.index, neg_rate, color=NEGATIVE, linewidth=1.2, label="Parish sum larger")
    top.set_ylabel("Weeks with an arithmetic error\n(52-week rolling %)")
    top.set_ylim(0, None)
    top.grid(axis="y", color="#E0E0E0", linewidth=0.6)
    top.spines[["top", "right"]].set_visible(False)
    top.legend(loc="upper left", frameon=False, ncol=2)

    outliers = (
        panel.dropna(subset=["difference"])
        .assign(size=lambda d: d["difference"].abs())
        .nlargest(top_n, "size")
        .sort_index()
    )
    colors = np.where(outliers["difference"].gt(0), POSITIVE, NEGATIVE)
    bottom.vlines(outliers.index, 0, outliers["difference"], color=colors, linewidth=1.8)
    bottom.scatter(
        outliers.index,
        outliers["difference"],
        s=34,
        facecolor=np.where(outliers["legible"], colors, "white"),
        edgecolor=colors,
        linewidth=1.3,
        zorder=3,
    )
    bottom.axhline(0, color=INK, linewidth=0.8)
    bottom.set_yscale("symlog", linthresh=10)
    listing = []
    for number, (idx, row) in enumerate(outliers.iterrows(), start=1):
        bottom.annotate(
            str(number),
            (idx, row.difference),
            xytext=(0, 7 if row.difference > 0 else -7),
            textcoords="offset points",
            ha="center",
            va="bottom" if row.difference > 0 else "top",
            fontsize=7.5,
        )
        legibility = "" if row.legible else " *"
        listing.append(f"{number:>2}  {int(row.year)} wk {int(row.week_number):<2} {int(row.difference):>+5}{legibility}")
    fig.text(
        0.80,
        0.40,
        "Largest differences\n" + "\n".join(listing) + "\n\n* week contains an\n  illegible value",
        fontsize=8.5,
        family="monospace",
        va="top",
    )
    bottom.set_ylabel(f"{top_n} largest differences\n(printed minus parish sum)")
    bottom.set_xlabel("Year")
    bottom.set_xticks(ticks, labels, rotation=45, ha="right")
    bottom.grid(axis="y", color="#E0E0E0", linewidth=0.6)
    bottom.spines[["top", "right"]].set_visible(False)

    label = "burial" if count_type == "buried" else "plague"
    fig.suptitle(f"Arithmetic-error rate in weekly {label} counts, with the largest discrepancies", y=0.995)
    fig.subplots_adjust(top=0.92, bottom=0.12, left=0.09, right=0.78)
    _save_figure(fig, output_base)
    plt.close(fig)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = here / "figures" / "prototypes"
    out.mkdir(parents=True, exist_ok=True)
    prepared = prepare_data(load_data())
    data = flagged_comparison(prepared)
    for count_type in ["buried", "plague"]:
        plot_option_1(data, count_type, out / f"option1_annual_bars_{count_type}")
    plot_option_2(data, prepared, "buried", out / "option2_decade_strips_buried")
    plot_option_4(data, prepared, "buried", out / "option4_rolling_rate_buried")
    print(f"Prototypes written to {out}")
