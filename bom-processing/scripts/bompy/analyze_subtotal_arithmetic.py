#!/usr/bin/env python3
"""
Analyze internal arithmetic of Bills of Mortality by comparing
weekly bill subtotals to general bill (annual) totals.

The sum of weekly subtotals for a geographic area for a year
should approximately match the general bill subtotal for that area.
"""

import pandas as pd
from pathlib import Path


def main():
    # Load subtotals
    data_path = Path(__file__).parent / "data" / "subtotals.csv"

    if not data_path.exists():
        print(f"Error: {data_path} not found. Run process_all_data.py first.")
        return

    df = pd.read_csv(data_path)

    print("=" * 60)
    print("BILLS OF MORTALITY - SUBTOTAL ARITHMETIC VALIDATION")
    print("=" * 60)

    # Basic stats
    print(f"\nTotal subtotal records: {len(df):,}")
    print(f"Bill types: {df['bill_type'].value_counts().to_dict()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")
    print(f"Categories: {df['subtotal_category'].unique().tolist()}")

    # Separate by bill type
    weekly = df[df["bill_type"] == "weekly"].copy()
    general = df[df["bill_type"] == "general"].copy()

    print(f"\nWeekly subtotal records: {len(weekly):,}")
    print(f"General bill subtotal records: {len(general):,}")

    # Find overlapping years
    weekly_years = set(weekly["year"].unique())
    general_years = set(general["year"].unique())
    overlap_years = sorted(weekly_years & general_years)

    print(f"\nYears with weekly data: {len(weekly_years)}")
    print(f"Years with general data: {len(general_years)}")
    print(f"Overlapping years: {len(overlap_years)}")

    if not overlap_years:
        print("\nNo overlapping years found - cannot compare!")
        return

    print(f"Overlap range: {min(overlap_years)} - {max(overlap_years)}")

    # Check week coverage for overlapping years
    print("\n" + "-" * 60)
    print("WEEK COVERAGE FOR OVERLAPPING YEARS")
    print("-" * 60)

    weekly_overlap = weekly[weekly["year"].isin(overlap_years)]
    week_counts = weekly_overlap.groupby("year")["joinid"].nunique().sort_index()

    # Identify years with complete coverage (50+ weeks)
    complete_years = [y for y in overlap_years if week_counts.get(y, 0) >= 50]
    incomplete_years = [y for y in overlap_years if week_counts.get(y, 0) < 50]

    print(f"\nYears with complete coverage (≥50 weeks): {len(complete_years)}")
    print(f"Years with incomplete coverage (<50 weeks): {len(incomplete_years)}")

    if complete_years:
        print(f"\nComplete years: {min(complete_years)} - {max(complete_years)}")
        print("Week counts for complete years:")
        for year in sorted(complete_years)[:15]:
            count = week_counts.get(year, 0)
            print(f"  {year}: {count} weeks")
        if len(complete_years) > 15:
            print(f"  ... and {len(complete_years) - 15} more years")

    # Aggregate weekly subtotals by (category, count_type, year)
    # First, handle potential duplicates by taking max count per unique week
    weekly_deduped = (
        weekly.groupby(["subtotal_category", "count_type", "year", "joinid"])["count"]
        .max()
        .reset_index()
    )

    weekly_sums = (
        weekly_deduped.groupby(["subtotal_category", "count_type", "year"])["count"]
        .sum()
        .reset_index()
    )
    weekly_sums.rename(columns={"count": "weekly_sum"}, inplace=True)

    # General bills - aggregate in case of duplicates
    general_totals = (
        general.groupby(["subtotal_category", "count_type", "year"])["count"]
        .sum()
        .reset_index()
    )
    general_totals.rename(columns={"count": "general_total"}, inplace=True)

    # Merge to compare
    comparison = pd.merge(
        weekly_sums,
        general_totals,
        on=["subtotal_category", "count_type", "year"],
        how="outer",
    )

    # Calculate differences
    comparison["difference"] = comparison["weekly_sum"] - comparison["general_total"]
    comparison["pct_diff"] = (
        comparison["difference"] / comparison["general_total"] * 100
    ).round(2)

    # Filter to rows with both values
    both_available = comparison.dropna(subset=["weekly_sum", "general_total"])

    # FOCUS ON COMPLETE YEARS ONLY
    if not complete_years:
        print("\nNo years with complete coverage found!")
        return

    both_available = both_available[both_available["year"].isin(complete_years)]

    print("\n" + "-" * 60)
    print("COMPARISON RESULTS (COMPLETE YEARS ONLY)")
    print("-" * 60)

    print(f"\nAnalyzing {len(complete_years)} years with ≥50 weeks of data")
    print(f"Comparisons possible: {len(both_available)}")

    if len(both_available) == 0:
        print("No comparisons possible - data doesn't overlap properly")
        return

    # Summary stats
    exact_matches = both_available[both_available["difference"] == 0]
    close_matches = both_available[both_available["pct_diff"].abs() <= 5]
    large_discrepancies = both_available[both_available["pct_diff"].abs() > 10]

    print(
        f"Exact matches (diff = 0): {len(exact_matches)} ({len(exact_matches) / len(both_available) * 100:.1f}%)"
    )
    print(
        f"Close matches (±5%): {len(close_matches)} ({len(close_matches) / len(both_available) * 100:.1f}%)"
    )
    print(
        f"Large discrepancies (>10%): {len(large_discrepancies)} ({len(large_discrepancies) / len(both_available) * 100:.1f}%)"
    )

    # Per-year breakdown
    print("\n" + "-" * 60)
    print("PER-YEAR BREAKDOWN")
    print("-" * 60)

    year_summary = (
        both_available.groupby("year")
        .agg(
            {
                "difference": "mean",
                "pct_diff": "mean",
                "subtotal_category": "count",  # number of comparisons
            }
        )
        .rename(columns={"subtotal_category": "n_comparisons"})
    )
    year_summary["mean_diff"] = year_summary["difference"].round(0)
    year_summary["mean_pct"] = year_summary["pct_diff"].round(2)

    print("\nYear | Comparisons | Mean Diff | Mean % Diff")
    print("-" * 45)
    for year in sorted(complete_years):
        if year in year_summary.index:
            row = year_summary.loc[year]
            print(
                f"{year} |     {int(row['n_comparisons']):2d}      | {row['mean_diff']:8.0f} | {row['mean_pct']:8.2f}%"
            )

    # Show some examples
    print("\n" + "-" * 60)
    print("SAMPLE COMPARISONS (sorted by % difference)")
    print("-" * 60)

    # Best matches
    print("\nBest matches (smallest % difference):")
    best = both_available.nsmallest(5, "pct_diff", keep="first")[
        [
            "year",
            "subtotal_category",
            "count_type",
            "weekly_sum",
            "general_total",
            "difference",
            "pct_diff",
        ]
    ]
    print(best.to_string(index=False))

    # Worst discrepancies
    if len(large_discrepancies) > 0:
        print("\nLargest discrepancies:")
        worst = both_available.nlargest(10, "pct_diff", keep="first")[
            [
                "year",
                "subtotal_category",
                "count_type",
                "weekly_sum",
                "general_total",
                "difference",
                "pct_diff",
            ]
        ]
        print(worst.to_string(index=False))

    # By category summary
    print("\n" + "-" * 60)
    print("SUMMARY BY CATEGORY")
    print("-" * 60)

    category_summary = (
        both_available.groupby("subtotal_category")
        .agg({"difference": ["mean", "std"], "pct_diff": ["mean", "std", "min", "max"]})
        .round(2)
    )
    print(category_summary)

    # By count type summary
    print("\n" + "-" * 60)
    print("SUMMARY BY COUNT TYPE")
    print("-" * 60)

    type_summary = (
        both_available.groupby("count_type")
        .agg({"difference": ["mean", "std"], "pct_diff": ["mean", "std", "min", "max"]})
        .round(2)
    )
    print(type_summary)

    # Export detailed comparison for further analysis
    output_path = Path(__file__).parent / "data" / "subtotal_comparison.csv"
    comparison.to_csv(output_path, index=False)
    print(f"\nDetailed comparison exported to: {output_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
