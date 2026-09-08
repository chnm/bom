import json
from pathlib import Path

import pandas as pd

from analysis import (
    DataBundle,
    _is_lfs_pointer,
    annual_comparison,
    build_comparison,
    export_website_data,
    figure_9_data,
    figure_9_regression,
    prepare_data,
)


def synthetic_bundle() -> DataBundle:
    weeks = pd.DataFrame(
        {
            "joinid": [1, 2, 3],
            "year": [1700, 1700, 1701],
            "week_number": [1, 2, 1],
            "year_range": ["1699-1700", "1699-1700", "1700-1701"],
        }
    )
    all_bills = pd.DataFrame(
        {
            "joinid": [1, 1, 2, 2, 3, 3],
            "count": [5, 1, 4, 0, 3, 1],
            "count_type": ["buried", "plague"] * 3,
            "illegible": [False, False, True, False, False, False],
            "bill_type": ["weekly"] * 6,
            "parish_id": [1] * 6,
        }
    )
    subtotals = pd.DataFrame(
        {
            "joinid": [1, 1, 2, 2, 3, 3],
            "count": [6, 1, 4, 0, 5, 1],
            "count_type": ["buried", "plague"] * 3,
            "illegible": [False] * 6,
            "bill_type": ["weekly"] * 6,
        }
    )
    return DataBundle(
        all_bills=all_bills,
        weeks=weeks,
        parishes=pd.DataFrame({"id": [1]}),
        subtotals=subtotals,
        duplicate_bills_removable=pd.DataFrame(),
        paths={},
    )


def test_lfs_pointer_detection(tmp_path: Path) -> None:
    pointer = tmp_path / "data.csv"
    pointer.write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        "oid sha256:abc\nsize 1\n",
        encoding="utf-8",
    )
    assert _is_lfs_pointer(pointer)


def test_legible_only_removes_the_entire_flagged_week() -> None:
    prepared = prepare_data(synthetic_bundle())
    all_data = build_comparison(prepared)
    legible = build_comparison(prepared, legible_only=True)

    assert set(all_data["year"]) == {1700, 1701}
    assert not ((legible["year"] == 1700) & (legible["week_number"] == 2)).any()
    assert prepared.legibility_by_year.loc[
        prepared.legibility_by_year["year"].eq(1700), "percent_legible"
    ].item() == 50


def test_error_rate_uses_comparable_burial_weeks() -> None:
    prepared = prepare_data(synthetic_bundle())
    all_data = build_comparison(prepared)
    replacement = figure_9_data(all_data, prepared)

    year_1700 = replacement[replacement["year"].eq(1700)].iloc[0]
    assert year_1700["comparable_weeks"] == 2
    assert year_1700["arithmetic_errors"] == 1
    assert year_1700["arithmetic_error_rate"] == 50


def test_annual_comparison_marks_fully_legible_years() -> None:
    prepared = prepare_data(synthetic_bundle())
    all_data = build_comparison(prepared)
    legible = build_comparison(prepared, legible_only=True)
    annual = annual_comparison(all_data, legible, prepared)

    assert annual.loc[annual["year"].eq(1701), "fully_legible"].all()


def test_figure_9_regression_returns_a_supported_fit() -> None:
    data = pd.DataFrame(
        {
            "percent_legible": range(10, 110, 10),
            "arithmetic_error_rate": range(90, -10, -10),
        }
    )
    regression, supported, fit = figure_9_regression(data)

    assert supported
    assert regression.slope == -1
    assert len(fit) == 200


def test_website_export_is_versioned_and_marks_legible_weeks(
    tmp_path: Path,
) -> None:
    prepared = prepare_data(synthetic_bundle())
    all_data = build_comparison(prepared)
    legible_data = build_comparison(prepared, legible_only=True)
    annual = annual_comparison(all_data, legible_data, prepared)
    replacement = figure_9_data(all_data, prepared)
    output = tmp_path / "data.json"
    diagnostics = pd.DataFrame(
        columns=[
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
        ]
    )
    results = {
        "all_data": all_data,
        "legible_data": legible_data,
        "annual_comparison": annual,
        "figure_9_data": replacement,
        "diagnostics": diagnostics,
        "figure_9_stats": {
            "n": len(replacement),
            "slope": -1,
            "intercept": 100,
            "r": -1,
            "p": 0,
            "fit_plotted": True,
        },
    }
    export_website_data(results, output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["metadata"]["dataset_ref"]
    week_two = next(row for row in payload["weekly"] if row["week_number"] == 2)
    assert week_two["legible"] is False
