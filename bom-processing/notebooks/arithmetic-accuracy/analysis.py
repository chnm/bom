"""Reproducible analysis for the arithmetic-accuracy reviewer revisions.

The source notebooks are preserved as historical records. This module supplies a
single, tested data preparation path for the revised figures and diagnostics.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import warnings
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA


DATA_REF = "9d0614c6c6ca134c734472b7a56fb4a14f4f8be0"
DATA_RELATIVE_DIR = Path(
    "bom-processing/scripts/bompy/data/2025-11-ArchivalCopyofArticleData"
)
DATA_FILES = {
    "all_bills.csv": (
        134_914_826,
        "a8d05f062104934698dc297a29b050c95e769498dad0ae729eaf983836d16a4f",
    ),
    "weeks.csv": (
        516_681,
        "0bb1a649584ab07bb8a4df9bae3ce277ade783f8fe9f2303e61acb20b3360c8d",
    ),
    "parishes.csv": (
        10_851,
        "ca71b254a6966438a2b625b9e9196cfaab4321f26150f0843649b43c1f46525b",
    ),
    "subtotals.csv": (
        8_849_190,
        "9724a7b0fea370b5a44e4ee4a53e0f28f589ca32b538f063c36a3fd322a6382a",
    ),
    "duplicate_bills_removable.csv": (
        29_509,
        "f5afbc898d8fdc49c62608422136081f67022efeddc8d912654e2deecf686542",
    ),
}


@dataclass(frozen=True)
class DataBundle:
    """Article data and the resolved source paths used to load it."""

    all_bills: pd.DataFrame
    weeks: pd.DataFrame
    parishes: pd.DataFrame
    subtotals: pd.DataFrame
    duplicate_bills_removable: pd.DataFrame
    paths: dict[str, Path]


@dataclass(frozen=True)
class PreparedData:
    """Clean weekly inputs shared by every revised analysis."""

    bills: pd.DataFrame
    subtotals: pd.DataFrame
    calendar: pd.DataFrame
    illegible_joinids: frozenset[int]
    legibility_by_year: pd.DataFrame


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_lfs_pointer(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size > 1024:
        return False
    with path.open("rb") as source:
        return source.read(200).startswith(
            b"version https://git-lfs.github.com/spec/v1"
        )


def _is_verified(path: Path, expected_size: int, expected_sha256: str) -> bool:
    return (
        path.is_file()
        and not _is_lfs_pointer(path)
        and path.stat().st_size == expected_size
        and _sha256(path) == expected_sha256
    )


def find_repository_root(start: Path | None = None) -> Path | None:
    """Find a checkout containing the archived article-data directory."""

    candidates = [Path(start or Path.cwd()).resolve(), Path(__file__).resolve().parent]
    for initial in candidates:
        for candidate in (initial, *initial.parents):
            if (candidate / DATA_RELATIVE_DIR).is_dir():
                return candidate
    return None


def resolve_data_paths(
    cache_dir: Path | None = None,
    data_ref: str | None = None,
) -> dict[str, Path]:
    """Resolve local CSVs or download and verify immutable Git LFS objects."""

    explicit_dir = os.environ.get("BOM_DATA_DIR")
    repository_root = find_repository_root()
    local_dir = Path(explicit_dir).expanduser() if explicit_dir else None
    if local_dir is None and repository_root is not None:
        local_dir = repository_root / DATA_RELATIVE_DIR

    cache = Path(
        cache_dir
        or os.environ.get("BOM_DATA_CACHE", Path(__file__).resolve().parent / "data-cache")
    ).expanduser()
    cache.mkdir(parents=True, exist_ok=True)
    ref = data_ref or os.environ.get("BOM_DATA_REF", DATA_REF)

    paths: dict[str, Path] = {}
    for name, (expected_size, expected_sha256) in DATA_FILES.items():
        local_path = local_dir / name if local_dir is not None else None
        if local_path is not None and _is_verified(
            local_path, expected_size, expected_sha256
        ):
            paths[name] = local_path
            continue

        cached_path = cache / name
        if not _is_verified(cached_path, expected_size, expected_sha256):
            relative = (DATA_RELATIVE_DIR / name).as_posix()
            url = (
                "https://media.githubusercontent.com/media/chnm/bom/"
                f"{ref}/{relative}"
            )
            temporary = cached_path.with_suffix(cached_path.suffix + ".part")
            temporary.unlink(missing_ok=True)
            print(f"Downloading {name} from the archived article dataset...")
            try:
                with urlopen(url) as response, temporary.open("wb") as target:
                    shutil.copyfileobj(response, target, length=1024 * 1024)
                if not _is_verified(temporary, expected_size, expected_sha256):
                    raise RuntimeError(
                        f"Downloaded {name} failed size or SHA-256 verification"
                    )
                temporary.replace(cached_path)
            finally:
                temporary.unlink(missing_ok=True)
        paths[name] = cached_path

    return paths


def load_data(cache_dir: Path | None = None) -> DataBundle:
    """Load the checksum-verified archived article dataset."""

    paths = resolve_data_paths(cache_dir=cache_dir)
    return DataBundle(
        all_bills=pd.read_csv(paths["all_bills.csv"], low_memory=False),
        weeks=pd.read_csv(paths["weeks.csv"], low_memory=False),
        parishes=pd.read_csv(paths["parishes.csv"], low_memory=False),
        subtotals=pd.read_csv(paths["subtotals.csv"], low_memory=False),
        duplicate_bills_removable=pd.read_csv(
            paths["duplicate_bills_removable.csv"], low_memory=False
        ),
        paths=paths,
    )


def _boolean(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def prepare_data(bundle: DataBundle) -> PreparedData:
    """Create comparable weekly parish sums, subtotals, and legibility flags."""

    required_week_columns = ["joinid", "year", "week_number"]
    missing = set(required_week_columns) - set(bundle.weeks.columns)
    if missing:
        raise ValueError(f"weeks.csv is missing required columns: {sorted(missing)}")

    optional_week_columns = [
        column
        for column in [
            "year_range",
            "start_day",
            "start_month",
            "end_day",
            "end_month",
        ]
        if column in bundle.weeks.columns
    ]
    week_lookup = bundle.weeks[
        required_week_columns + optional_week_columns
    ].drop_duplicates("joinid")

    bills = bundle.all_bills.copy()
    merge_columns = [
        column
        for column in week_lookup.columns
        if column not in bills.columns or column == "joinid"
    ]
    bills = bills.merge(week_lookup[merge_columns], on="joinid", how="left")
    bills["count"] = pd.to_numeric(bills["count"], errors="coerce")
    bills["illegible_flag"] = _boolean(bills["illegible"])
    bills = bills[bills["week_number"].between(1, 55, inclusive="both")]
    if "bill_type" in bills.columns:
        bills = bills[bills["bill_type"].eq("weekly")]
    bills = bills[bills["count_type"].isin(["buried", "plague"])]
    bills = bills[bills["parish_id"].ne(19)]

    subtotals = bundle.subtotals.copy()
    merge_columns = [
        column
        for column in week_lookup.columns
        if column not in subtotals.columns or column == "joinid"
    ]
    subtotals = subtotals.merge(week_lookup[merge_columns], on="joinid", how="left")
    subtotals["count"] = pd.to_numeric(subtotals["count"], errors="coerce")
    subtotals["illegible_flag"] = _boolean(subtotals["illegible"])
    subtotals = subtotals[
        subtotals["week_number"].between(1, 55, inclusive="both")
    ]
    if "bill_type" in subtotals.columns:
        subtotals = subtotals[subtotals["bill_type"].eq("weekly")]
    subtotals = subtotals[subtotals["count_type"].isin(["buried", "plague"])]

    illegible_joinids = frozenset(
        pd.concat(
            [
                bills.loc[bills["illegible_flag"], "joinid"],
                subtotals.loc[subtotals["illegible_flag"], "joinid"],
            ]
        )
        .dropna()
        .astype("int64")
        .unique()
        .tolist()
    )

    observed_weeks = bills[["joinid", "year", "week_number"]].drop_duplicates()
    observed_weeks["illegible_week"] = observed_weeks["joinid"].isin(
        illegible_joinids
    )
    legibility_by_year = (
        observed_weeks.groupby("year", as_index=False)
        .agg(
            total_weeks=("joinid", "nunique"),
            illegible_weeks=("illegible_week", "sum"),
        )
        .sort_values("year")
    )
    legibility_by_year["legible_weeks"] = (
        legibility_by_year["total_weeks"] - legibility_by_year["illegible_weeks"]
    )
    legibility_by_year["percent_legible"] = (
        100 * legibility_by_year["legible_weeks"] / legibility_by_year["total_weeks"]
    )
    legibility_by_year["fully_legible"] = legibility_by_year[
        "illegible_weeks"
    ].eq(0)

    calendar = (
        week_lookup[week_lookup["week_number"].between(1, 55, inclusive="both")][
            ["year", "week_number"]
        ]
        .drop_duplicates()
        .sort_values(["year", "week_number"])
        .reset_index(drop=True)
    )
    calendar["time_index"] = np.arange(len(calendar))

    return PreparedData(
        bills=bills,
        subtotals=subtotals,
        calendar=calendar,
        illegible_joinids=illegible_joinids,
        legibility_by_year=legibility_by_year,
    )


def build_comparison(prepared: PreparedData, legible_only: bool = False) -> pd.DataFrame:
    """Compare printed subtotals with parish sums for numerically comparable weeks."""

    bills = prepared.bills
    subtotals = prepared.subtotals
    if legible_only:
        bills = bills[~bills["joinid"].isin(prepared.illegible_joinids)]
        subtotals = subtotals[~subtotals["joinid"].isin(prepared.illegible_joinids)]

    keys = ["year", "week_number", "count_type"]
    parish_sums = (
        bills.groupby(keys, as_index=False)["count"]
        .sum(min_count=1)
        .rename(columns={"count": "parish_sum"})
    )
    printed_subtotals = (
        subtotals.groupby(keys, as_index=False)["count"]
        .sum(min_count=1)
        .rename(columns={"count": "subtotal_sum"})
    )
    comparison = printed_subtotals.merge(parish_sums, on=keys, how="inner")
    comparison = comparison.dropna(subset=["subtotal_sum", "parish_sum"]).copy()
    comparison["difference"] = comparison["subtotal_sum"] - comparison["parish_sum"]
    comparison["absolute_difference"] = comparison["difference"].abs()
    comparison["arithmetic_error"] = comparison["difference"].ne(0)
    comparison["legible_only"] = legible_only
    return comparison.sort_values(keys).reset_index(drop=True)


def _save_figure(fig: plt.Figure, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")


def _year_ticks(calendar: pd.DataFrame) -> tuple[list[int], list[str]]:
    starts = calendar.drop_duplicates("year", keep="first")
    starts = starts[
        starts["year"].eq(starts["year"].min()) | starts["year"].mod(5).eq(0)
    ]
    return starts["time_index"].tolist(), starts["year"].astype(int).astype(str).tolist()


def plot_weekly_differences(
    comparison: pd.DataFrame,
    prepared: PreparedData,
    output_base: Path,
    title: str,
) -> plt.Figure:
    """Create a large landscape replacement for Figure 4 or Figure 5."""

    plt.rcParams.update(
        {
            "font.size": 13,
            "axes.titlesize": 16,
            "axes.labelsize": 14,
            "xtick.labelsize": 11,
            "ytick.labelsize": 12,
            "legend.fontsize": 12,
        }
    )
    fig, axes = plt.subplots(2, 1, figsize=(16, 9), sharex=True)
    positive_color = "#C44E35"
    negative_color = "#087E8B"
    ticks, labels = _year_ticks(prepared.calendar)

    for ax, count_type, panel_title in zip(
        axes,
        ["buried", "plague"],
        ["Burial counts", "Plague counts"],
        strict=True,
    ):
        panel = prepared.calendar.merge(
            comparison.loc[
                comparison["count_type"].eq(count_type),
                ["year", "week_number", "difference"],
            ],
            on=["year", "week_number"],
            how="left",
        )
        observed = panel.dropna(subset=["difference"])
        nonzero = observed[observed["difference"].ne(0)]
        nonzero_colors = np.where(
            nonzero["difference"].gt(0), positive_color, negative_color
        )
        ax.vlines(
            nonzero["time_index"],
            0,
            nonzero["difference"],
            color=nonzero_colors,
            linewidth=0.7,
            alpha=0.8,
        )
        ax.axhline(0, color="#222222", linewidth=1)
        ax.set_yscale("symlog", linthresh=5)
        ax.set_title(panel_title, loc="left")
        ax.set_ylabel("Printed subtotal minus\nparish-summed count")
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.text(
            0.995,
            0.03,
            f"{len(observed):,} comparable weeks · symmetric log scale",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=11,
            color="#444444",
        )

    axes[-1].set_xticks(ticks, labels, rotation=45, ha="right")
    axes[-1].set_xlabel("Year")
    fig.suptitle(title, fontsize=19, y=0.99)
    fig.legend(
        handles=[
            Patch(facecolor=positive_color, label="Printed subtotal is larger"),
            Patch(facecolor=negative_color, label="Parish sum is larger"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.955),
        ncol=2,
        frameon=False,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    _save_figure(fig, output_base)
    return fig


def annual_comparison(
    all_data: pd.DataFrame,
    legible_data: pd.DataFrame,
    prepared: PreparedData,
) -> pd.DataFrame:
    keys = ["year", "count_type"]
    annual_all = all_data.groupby(keys, as_index=False).agg(
        all_mean_absolute_difference=("absolute_difference", "mean"),
        all_comparable_weeks=("difference", "size"),
    )
    annual_legible = legible_data.groupby(keys, as_index=False).agg(
        legible_mean_absolute_difference=("absolute_difference", "mean"),
        legible_comparable_weeks=("difference", "size"),
    )
    return (
        annual_all.merge(annual_legible, on=keys, how="inner")
        .merge(prepared.legibility_by_year, on="year", how="left")
        .sort_values(keys)
        .reset_index(drop=True)
    )


def plot_annual_comparison(data: pd.DataFrame, output_base: Path) -> plt.Figure:
    """Plot reviewer-requested paired all-data versus legible-only annual errors."""

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    for ax, count_type, panel_title in zip(
        axes,
        ["buried", "plague"],
        ["Burial counts", "Plague counts"],
        strict=True,
    ):
        panel = data[data["count_type"].eq(count_type)].dropna(
            subset=["legible_mean_absolute_difference", "all_mean_absolute_difference"]
        )
        ordinary = panel[~panel["fully_legible"]]
        fully = panel[panel["fully_legible"]]
        ax.scatter(
            ordinary["legible_mean_absolute_difference"],
            ordinary["all_mean_absolute_difference"],
            s=48,
            color="#087E8B",
            alpha=0.8,
            label="Some illegible weeks",
        )
        ax.scatter(
            fully["legible_mean_absolute_difference"],
            fully["all_mean_absolute_difference"],
            s=62,
            facecolors="none",
            edgecolors="#C44E35",
            linewidths=1.5,
            label="Every observed week legible",
        )
        maximum = max(
            panel["legible_mean_absolute_difference"].max(),
            panel["all_mean_absolute_difference"].max(),
        )
        ax.plot([0, maximum], [0, maximum], "--", color="#333333", linewidth=1)
        if len(panel) >= 3:
            result = stats.pearsonr(
                panel["legible_mean_absolute_difference"],
                panel["all_mean_absolute_difference"],
            )
            annotation = f"n = {len(panel)} years; Pearson r = {result.statistic:.2f}"
        else:
            annotation = f"n = {len(panel)} years"
        largest = panel.assign(
            gap=(
                panel["all_mean_absolute_difference"]
                - panel["legible_mean_absolute_difference"]
            ).abs()
        ).nlargest(4, "gap")
        offsets = [(6, 8), (6, -14), (6, 18), (6, -24)]
        for row, offset in zip(largest.itertuples(), offsets, strict=False):
            ax.annotate(
                str(int(row.year)),
                (row.legible_mean_absolute_difference, row.all_mean_absolute_difference),
                xytext=offset,
                textcoords="offset points",
                fontsize=9,
            )
        ax.text(0.03, 0.96, annotation, transform=ax.transAxes, va="top")
        ax.set_title(panel_title)
        ax.set_xlabel("Mean absolute arithmetic difference\nlegible weeks only")
        ax.set_ylabel("Mean absolute arithmetic difference\nall comparable weeks")
        ax.grid(color="#E0E0E0", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.91),
        ncol=2,
        frameon=False,
    )
    fig.suptitle(
        "Annual arithmetic differences in all and legible-only bills",
        fontsize=19,
        y=0.985,
    )
    fig.subplots_adjust(top=0.78, bottom=0.18, left=0.09, right=0.98, wspace=0.28)
    _save_figure(fig, output_base)
    return fig


def figure_9_data(all_data: pd.DataFrame, prepared: PreparedData) -> pd.DataFrame:
    """Calculate the annual variables requested for the replacement Figure 9."""

    # Retain the manuscript's post-1663 window, when annual coverage is close to
    # complete, so sparse early years do not dominate the relationship.
    buried = all_data[
        all_data["count_type"].eq("buried") & all_data["year"].ge(1663)
    ]
    annual_errors = buried.groupby("year", as_index=False).agg(
        comparable_weeks=("arithmetic_error", "size"),
        arithmetic_errors=("arithmetic_error", "sum"),
    )
    annual_errors["arithmetic_error_rate"] = (
        100
        * annual_errors["arithmetic_errors"]
        / annual_errors["comparable_weeks"]
    )
    return annual_errors.merge(
        prepared.legibility_by_year, on="year", how="inner"
    ).sort_values("year")


def figure_9_regression(
    data: pd.DataFrame,
) -> tuple[stats.LinregressResult, bool, pd.DataFrame]:
    """Calculate the Figure 9 linear fit and mean-response confidence interval."""

    model_data = data.dropna(subset=["percent_legible", "arithmetic_error_rate"])
    regression = stats.linregress(
        model_data["percent_legible"], model_data["arithmetic_error_rate"]
    )
    supported = len(model_data) >= 10 and regression.pvalue < 0.05
    fit = pd.DataFrame(columns=["percent_legible", "fitted", "lower", "upper"])
    if supported:
        x = model_data["percent_legible"].to_numpy()
        y = model_data["arithmetic_error_rate"].to_numpy()
        grid = np.linspace(x.min(), x.max(), 200)
        fitted = regression.intercept + regression.slope * grid
        residuals = y - (regression.intercept + regression.slope * x)
        dof = len(x) - 2
        residual_sd = np.sqrt(np.sum(residuals**2) / dof)
        denominator = np.sum((x - x.mean()) ** 2)
        se_mean = residual_sd * np.sqrt(
            1 / len(x) + (grid - x.mean()) ** 2 / denominator
        )
        critical = stats.t.ppf(0.975, dof)
        fit = pd.DataFrame(
            {
                "percent_legible": grid,
                "fitted": fitted,
                "lower": fitted - critical * se_mean,
                "upper": fitted + critical * se_mean,
            }
        )
    return regression, supported, fit


def plot_figure_9(data: pd.DataFrame, output_base: Path) -> tuple[plt.Figure, dict]:
    """Create the reviewer-requested legibility/error-rate scatterplot."""

    model_data = data.dropna(subset=["percent_legible", "arithmetic_error_rate"])
    regression, supported, fit = figure_9_regression(model_data)

    fig, ax = plt.subplots(figsize=(11, 8), constrained_layout=True)
    ax.scatter(
        model_data["percent_legible"],
        model_data["arithmetic_error_rate"],
        s=58,
        color="#087E8B",
        alpha=0.82,
        edgecolor="white",
        linewidth=0.5,
    )
    if supported:
        ax.plot(
            fit["percent_legible"],
            fit["fitted"],
            color="#C44E35",
            linewidth=2,
            label="Linear fit",
        )
        ax.fill_between(
            fit["percent_legible"],
            fit["lower"],
            fit["upper"],
            color="#C44E35",
            alpha=0.16,
            label="95% confidence interval",
        )
        ax.legend(frameon=False)

    predictions = regression.intercept + regression.slope * model_data["percent_legible"]
    labels = model_data.assign(
        residual=(model_data["arithmetic_error_rate"] - predictions).abs()
    ).nlargest(5, "residual")
    for row in labels.itertuples():
        ax.annotate(
            str(int(row.year)),
            (row.percent_legible, row.arithmetic_error_rate),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=10,
        )

    ax.set_title("Arithmetic-error rate and legibility of weekly burial bills", fontsize=18)
    ax.set_xlabel("Legible weekly bills (%)", fontsize=15)
    ax.set_ylabel("Comparable weeks with an arithmetic error (%)", fontsize=15)
    ax.tick_params(labelsize=12)
    ax.grid(color="#E0E0E0", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0.03,
        0.97,
        (
            f"n = {len(model_data)} years; r = {regression.rvalue:.2f}; "
            f"p = {regression.pvalue:.3g}"
        ),
        transform=ax.transAxes,
        va="top",
        fontsize=12,
    )
    _save_figure(fig, output_base)
    return fig, {
        "n": len(model_data),
        "slope": regression.slope,
        "intercept": regression.intercept,
        "r": regression.rvalue,
        "p": regression.pvalue,
        "fit_plotted": supported,
    }


def _json_records(data: pd.DataFrame, columns: list[str]) -> list[dict]:
    """Return deterministic, JSON-safe records for the website export."""

    return json.loads(
        data.loc[:, columns].to_json(orient="records", double_precision=10)
    )


def _json_scalar(value: object) -> object:
    """Convert NumPy scalar values to their JSON-native equivalents."""

    return value.item() if isinstance(value, np.generic) else value


def export_website_data(results: dict[str, object], output: Path) -> None:
    """Export a compact, versioned snapshot for the standalone web explorer."""

    all_data = results["all_data"]
    legible_data = results["legible_data"]
    annual = results["annual_comparison"]
    replacement = results["figure_9_data"]
    diagnostics = results["diagnostics"]
    figure_9_stats = results["figure_9_stats"]
    if not all(
        isinstance(frame, pd.DataFrame)
        for frame in [all_data, legible_data, annual, replacement, diagnostics]
    ):
        raise TypeError("Analysis result frames are not available for website export")

    keys = ["year", "week_number", "count_type"]
    legible_keys = legible_data[keys].drop_duplicates().assign(legible=True)
    weekly = all_data.merge(legible_keys, on=keys, how="left")
    weekly["legible"] = weekly["legible"].eq(True)

    comparison_stats = {}
    for count_type in ["buried", "plague"]:
        panel = annual[annual["count_type"].eq(count_type)]
        x = panel["legible_mean_absolute_difference"]
        y = panel["all_mean_absolute_difference"]
        if len(panel) >= 2 and x.nunique() > 1 and y.nunique() > 1:
            correlation = stats.pearsonr(x, y)
            correlation_r = correlation.statistic
            correlation_p = correlation.pvalue
        else:
            correlation_r = None
            correlation_p = None
        comparison_stats[count_type] = {
            "n": len(panel),
            "r": _json_scalar(correlation_r),
            "p": _json_scalar(correlation_p),
            "fully_legible_years": int(panel["fully_legible"].sum()),
        }

    _, _, figure_9_fit = figure_9_regression(replacement)
    payload = {
        "metadata": {
            "title": "Arithmetic Accuracy Explorer",
            "dataset_ref": DATA_REF,
            "dataset": "2025-11-ArchivalCopyofArticleData",
            "year_min": int(weekly["year"].min()),
            "year_max": int(weekly["year"].max()),
            "definitions": {
                "difference": "Printed subtotal minus the sum of parish counts.",
                "arithmetic_error": "A comparable week whose difference is not zero.",
                "legible": "No parish count or printed subtotal in the week is marked illegible.",
            },
            "files": {
                name: {"bytes": size, "sha256": checksum}
                for name, (size, checksum) in DATA_FILES.items()
            },
        },
        "weekly": _json_records(
            weekly,
            [
                "year",
                "week_number",
                "count_type",
                "subtotal_sum",
                "parish_sum",
                "difference",
                "absolute_difference",
                "arithmetic_error",
                "legible",
            ],
        ),
        "annual_comparison": _json_records(
            annual,
            [
                "year",
                "count_type",
                "all_mean_absolute_difference",
                "legible_mean_absolute_difference",
                "all_comparable_weeks",
                "legible_comparable_weeks",
                "percent_legible",
                "fully_legible",
            ],
        ),
        "figure_9": _json_records(
            replacement,
            [
                "year",
                "comparable_weeks",
                "arithmetic_errors",
                "arithmetic_error_rate",
                "percent_legible",
            ],
        ),
        "figure_9_fit": _json_records(
            figure_9_fit,
            ["percent_legible", "fitted", "lower", "upper"],
        ),
        "statistics": {
            "annual_comparison": comparison_stats,
            "figure_9": {
                key: _json_scalar(value) for key, value in figure_9_stats.items()
            },
        },
        "diagnostics": _json_records(
            diagnostics,
            [
                "count_type",
                "metric",
                "expected_weeks",
                "observed_weeks",
                "coverage_percent",
                "longest_contiguous_run",
                "spearman_time_rho",
                "spearman_time_p",
                "ljung_box_lag",
                "ljung_box_p",
                "seasonal_acf_lag_52",
                "selected_model",
                "model_aic",
                "residual_ljung_box_p",
                "model_adequate",
            ],
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    weekly.to_csv(output.parent / "weekly-differences.csv", index=False)
    annual.to_csv(output.parent / "annual-comparison.csv", index=False)
    replacement.to_csv(output.parent / "legibility-error-rate.csv", index=False)


def _longest_observed_run(series: pd.Series) -> pd.Series:
    present = series.notna()
    groups = present.ne(present.shift(fill_value=False)).cumsum()
    runs = []
    for _, group in series.groupby(groups):
        if group.notna().all():
            runs.append(group)
    return max(runs, key=len) if runs else pd.Series(dtype=float)


def time_series_diagnostics(
    all_data: pd.DataFrame, prepared: PreparedData
) -> pd.DataFrame:
    """Test ordering, coverage, trend, autocorrelation, and conditional ARMA fits."""

    rows: list[dict] = []
    for count_type in ["buried", "plague"]:
        base = prepared.calendar.merge(
            all_data.loc[
                all_data["count_type"].eq(count_type),
                ["year", "week_number", "difference"],
            ],
            on=["year", "week_number"],
            how="left",
        ).set_index("time_index")
        for metric in ["signed_difference", "absolute_difference"]:
            series = base["difference"]
            if metric == "absolute_difference":
                series = series.abs()
            observed = series.dropna()
            run = _longest_observed_run(series).astype(float)
            trend = stats.spearmanr(observed.index, observed.values)
            lag = min(10, max(1, len(run) // 5))
            if len(run) >= 20:
                ljung_box_p = float(
                    acorr_ljungbox(run, lags=[lag], return_df=True)[
                        "lb_pvalue"
                    ].iloc[0]
                )
            else:
                ljung_box_p = np.nan
            seasonal_acf_52 = float(run.autocorr(lag=52)) if len(run) > 104 else np.nan

            best_result = None
            best_order = None
            if len(run) >= 30 and pd.notna(ljung_box_p) and ljung_box_p < 0.05:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    for p in range(3):
                        for q in range(3):
                            if p == 0 and q == 0:
                                continue
                            try:
                                result = ARIMA(run, order=(p, 0, q), trend="c").fit()
                            except (ValueError, np.linalg.LinAlgError):
                                continue
                            if best_result is None or result.aic < best_result.aic:
                                best_result = result
                                best_order = (p, 0, q)

            if best_result is not None:
                residual_lag = min(10, max(1, len(best_result.resid) // 5))
                residual_ljung_box_p = float(
                    acorr_ljungbox(
                        best_result.resid,
                        lags=[residual_lag],
                        return_df=True,
                    )["lb_pvalue"].iloc[0]
                )
                selected_model = f"ARIMA{best_order}"
                model_aic = float(best_result.aic)
                model_adequate = residual_ljung_box_p >= 0.05
            else:
                residual_ljung_box_p = np.nan
                selected_model = "not fitted"
                model_aic = np.nan
                model_adequate = np.nan

            rows.append(
                {
                    "count_type": count_type,
                    "metric": metric,
                    "expected_weeks": len(series),
                    "observed_weeks": len(observed),
                    "coverage_percent": 100 * len(observed) / len(series),
                    "longest_contiguous_run": len(run),
                    "spearman_time_rho": trend.statistic,
                    "spearman_time_p": trend.pvalue,
                    "ljung_box_lag": lag,
                    "ljung_box_p": ljung_box_p,
                    "seasonal_acf_lag_52": seasonal_acf_52,
                    "selected_model": selected_model,
                    "model_aic": model_aic,
                    "residual_ljung_box_p": residual_ljung_box_p,
                    "model_adequate": model_adequate,
                }
            )
    return pd.DataFrame(rows)


def _write_results_summary(
    output: Path,
    annual: pd.DataFrame,
    figure_9_stats: dict,
    diagnostics: pd.DataFrame,
) -> None:
    lines = [
        "# Revision analysis results",
        "",
        "## Figures 4 and 5 annual comparison",
        "",
    ]
    for count_type in ["buried", "plague"]:
        panel = annual[annual["count_type"].eq(count_type)]
        result = stats.pearsonr(
            panel["legible_mean_absolute_difference"],
            panel["all_mean_absolute_difference"],
        )
        lines.append(
            f"- {count_type.title()}: {len(panel)} paired years; Pearson "
            f"r = {result.statistic:.3f}, p = {result.pvalue:.3g}; "
            f"{int(panel['fully_legible'].sum())} fully legible years."
        )
    lines.extend(
        [
            "",
            "## Figure 9 replacement",
            "",
            (
                f"- {figure_9_stats['n']} annual observations; linear slope = "
                f"{figure_9_stats['slope']:.3f}; Pearson r = "
                f"{figure_9_stats['r']:.3f}; p = {figure_9_stats['p']:.3g}."
            ),
            (
                "- A fitted line and 95% confidence interval were plotted."
                if figure_9_stats["fit_plotted"]
                else "- The relationship did not meet the prespecified p < 0.05 threshold, so no fitted line was plotted."
            ),
            "",
            "## Figure 4 time-series diagnostics",
            "",
        ]
    )
    for row in diagnostics.itertuples():
        lb = (
            "not tested"
            if pd.isna(row.ljung_box_p)
            else f"p = {row.ljung_box_p:.3g}"
        )
        if row.selected_model == "not fitted":
            model_note = "no ARMA-family model fitted"
        elif bool(row.model_adequate):
            model_note = f"{row.selected_model} passed the residual white-noise check"
        else:
            model_note = (
                f"{row.selected_model} candidate was inadequate because residual "
                f"autocorrelation remained (p = {row.residual_ljung_box_p:.3g})"
            )
        lines.append(
            f"- {row.count_type}, {row.metric}: {row.observed_weeks}/"
            f"{row.expected_weeks} weeks observed ({row.coverage_percent:.1f}%); "
            f"longest contiguous run {row.longest_contiguous_run}; Ljung-Box {lb}; "
            f"{model_note}."
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_analysis(output_dir: Path | None = None) -> dict[str, object]:
    """Run all confirmed reviewer revisions and write their artifacts."""

    base = Path(output_dir or Path(__file__).resolve().parent)
    figures = base / "figures"
    tables = base / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    bundle = load_data()
    prepared = prepare_data(bundle)
    all_data = build_comparison(prepared, legible_only=False)
    legible_data = build_comparison(prepared, legible_only=True)

    figure_4 = plot_weekly_differences(
        all_data,
        prepared,
        figures / "figure_4_all_bills",
        "Weekly arithmetic differences in all comparable bills",
    )
    figure_5 = plot_weekly_differences(
        legible_data,
        prepared,
        figures / "figure_5_legible_bills",
        "Weekly arithmetic differences after excluding illegible weeks",
    )
    annual = annual_comparison(all_data, legible_data, prepared)
    comparison_figure = plot_annual_comparison(
        annual, figures / "figure_4_5_annual_comparison"
    )
    annual.to_csv(tables / "figure_4_5_annual_comparison.csv", index=False)

    replacement_data = figure_9_data(all_data, prepared)
    figure_9, figure_9_stats = plot_figure_9(
        replacement_data, figures / "figure_9_legibility_error_rate"
    )
    replacement_data.to_csv(tables / "figure_9_annual_data.csv", index=False)

    diagnostics = time_series_diagnostics(all_data, prepared)
    diagnostics.to_csv(tables / "time_series_diagnostics.csv", index=False)
    _write_results_summary(
        tables / "revision_results.md", annual, figure_9_stats, diagnostics
    )

    return {
        "bundle": bundle,
        "prepared": prepared,
        "all_data": all_data,
        "legible_data": legible_data,
        "annual_comparison": annual,
        "figure_9_data": replacement_data,
        "diagnostics": diagnostics,
        "figure_9_stats": figure_9_stats,
        "figures": [figure_4, figure_5, comparison_figure, figure_9],
    }


if __name__ == "__main__":
    results = run_analysis()
    print("Revision artifacts written to figures/ and tables/.")
    repository_root = find_repository_root()
    if repository_root is not None and (repository_root / "bom-website/static").is_dir():
        website_data = (
            repository_root
            / "bom-website/static/data/arithmetic-accuracy/data.json"
        )
        export_website_data(results, website_data)
        thumbnail = (
            repository_root
            / "bom-website/static/images/viz/arithmetic-accuracy.png"
        )
        thumbnail.parent.mkdir(parents=True, exist_ok=True)
        results["figures"][-1].savefig(
            thumbnail, dpi=140, bbox_inches="tight", facecolor="white"
        )
        print(f"Website data written to {website_data}.")
    print(results["diagnostics"].to_string(index=False))
