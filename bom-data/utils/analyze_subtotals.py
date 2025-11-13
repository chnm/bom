#!/usr/bin/env python3

import pandas as pd


def analyze_subtotal_data(csv_file):
    """
    Analyze geographical subtotal data from the Bills of Mortality CSV file.
    Extracts burial subtotals for different regions and organizes them by year and week.
    """

    # Read the CSV file
    print(f"Reading data from {csv_file}...")
    df = pd.read_csv(csv_file)

    # Define the subtotal columns we're interested in
    subtotal_patterns = [
        "within the walls",
        "without the walls",
        "middlesex and surrey",
        "westminster",
    ]

    # Find all columns containing our patterns, excluding individual parish burials
    subtotal_columns = []
    for col in df.columns:
        col_lower = col.lower()
        # Check if column contains our patterns and is likely a burial subtotal
        for pattern in subtotal_patterns:
            if pattern in col_lower:
                # Exclude individual Westminster parish burials
                if "westminster - buried" not in col_lower:
                    # Focus on burial subtotals (not christened or plague)
                    if (
                        "buried" in col_lower
                        and "christened" not in col_lower
                        and "plague" not in col_lower
                    ):
                        subtotal_columns.append(col)
                        break

    print(f"Found {len(subtotal_columns)} subtotal burial columns:")
    for col in subtotal_columns:
        print(f"  - {col}")
    print()

    # Select relevant columns: Year, Week, and all subtotal columns
    analysis_columns = ["Year", "Week"] + subtotal_columns
    analysis_df = df[analysis_columns].copy()

    # Convert subtotal columns to numeric, replacing empty strings and non-numeric values with 0
    for col in subtotal_columns:
        analysis_df[col] = pd.to_numeric(analysis_df[col], errors="coerce").fillna(0)

    # Calculate total burials for each row (year/week combination)
    analysis_df["Total_Burials"] = analysis_df[subtotal_columns].sum(axis=1)

    # Group by Year and Week, summing the burials (in case there are duplicate year/week entries)
    summary = (
        analysis_df.groupby(["Year", "Week"])
        .agg({"Total_Burials": "sum", **{col: "sum" for col in subtotal_columns}})
        .reset_index()
    )

    # Sort by Year and Week
    summary = summary.sort_values(["Year", "Week"])

    return summary, subtotal_columns


def print_summary_stats(summary_df, subtotal_columns):
    """Print basic statistics about the subtotal burial data"""
    print("=== SUBTOTAL BURIAL DATA SUMMARY ===")
    print(f"Total records: {len(summary_df)}")
    print(f"Years covered: {summary_df['Year'].min()} - {summary_df['Year'].max()}")
    print(f"Total weeks: {summary_df['Week'].nunique()}")
    print(f"Average total burials per week: {summary_df['Total_Burials'].mean():.1f}")
    print(f"Maximum total burials in a week: {summary_df['Total_Burials'].max()}")
    print(f"Minimum total burials in a week: {summary_df['Total_Burials'].min()}")
    print()

    # Show averages for each region
    print("=== AVERAGE BURIALS BY REGION ===")
    for col in subtotal_columns:
        avg_burials = summary_df[col].mean()
        print(f"{col}: {avg_burials:.1f} per week")
    print()


def display_regional_breakdown(summary_df, subtotal_columns, n=10):
    """Display the weeks with highest burials broken down by region"""
    top_weeks = summary_df.nlargest(n, "Total_Burials")
    print(f"=== TOP {n} WEEKS BY TOTAL BURIAL COUNT (Regional Breakdown) ===")
    for _, row in top_weeks.iterrows():
        print(
            f"\nYear {int(row['Year'])}, Week {int(row['Week'])}: {int(row['Total_Burials'])} total burials"
        )
        for col in subtotal_columns:
            if row[col] > 0:
                print(f"  - {col}: {int(row[col])}")


def display_yearly_totals(summary_df, subtotal_columns):
    """Display total burials by year for each region"""
    yearly_totals = summary_df.groupby("Year")[
        ["Total_Burials"] + subtotal_columns
    ].sum()
    yearly_totals = yearly_totals.sort_values("Total_Burials", ascending=False)

    print("=== BURIALS BY YEAR (Top 10) ===")
    for year, row in yearly_totals.head(10).iterrows():
        print(f"\n{int(year)}: {int(row['Total_Burials'])} total burials")
        for col in subtotal_columns:
            if row[col] > 0:
                print(f"  - {col}: {int(row[col])}")


def analyze_regional_trends(summary_df, subtotal_columns):
    """Analyze trends in different regions"""
    print("=== REGIONAL ANALYSIS ===")

    # Calculate total burials by region across all years
    region_totals = {}
    for col in subtotal_columns:
        region_totals[col] = summary_df[col].sum()

    # Sort regions by total burials
    sorted_regions = sorted(region_totals.items(), key=lambda x: x[1], reverse=True)

    print("Total burials by region (entire dataset):")
    for region, total in sorted_regions:
        percentage = (total / sum(region_totals.values())) * 100
        print(f"  {region}: {int(total)} ({percentage:.1f}%)")
    print()


def export_results(summary_df, subtotal_columns, output_file):
    """Export the analyzed data to a new CSV file"""
    output_columns = ["Year", "Week", "Total_Burials"] + subtotal_columns
    output_df = summary_df[output_columns]

    output_df.to_csv(output_file, index=False)
    print(f"Results exported to: {output_file}")


def main():
    csv_file = "2025-10-27-Laxton-combineddata-weeklybills-parishes.csv"
    output_file = "subtotal_analysis_results.csv"

    try:
        # Analyze the data
        summary_df, subtotal_columns = analyze_subtotal_data(csv_file)

        # Print statistics
        print_summary_stats(summary_df, subtotal_columns)
        analyze_regional_trends(summary_df, subtotal_columns)
        display_yearly_totals(summary_df, subtotal_columns)
        display_regional_breakdown(summary_df, subtotal_columns, 10)

        # Show sample of the data
        print("\n=== SAMPLE DATA (First 10 records) ===")
        display_cols = ["Year", "Week", "Total_Burials"] + subtotal_columns
        print(summary_df[display_cols].head(10).to_string(index=False))
        print()

        # Export results
        export_results(summary_df, subtotal_columns, output_file)

        print(
            f"\nAnalysis complete! Found {len(subtotal_columns)} subtotal columns across {len(summary_df)} year/week combinations."
        )

    except FileNotFoundError:
        print(f"Error: Could not find the file '{csv_file}'")
        print("Please make sure the CSV file is in the current directory.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")


if __name__ == "__main__":
    main()
