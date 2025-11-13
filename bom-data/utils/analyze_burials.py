#!/usr/bin/env python3

import pandas as pd


def analyze_burial_data(csv_file):
    """
    Analyze burial data from the Bills of Mortality CSV file.
    Extracts all '- Buried' columns and sums them by year and week.
    """

    # Read the CSV file
    print(f"Reading data from {csv_file}...")
    df = pd.read_csv(csv_file)

    # Get all columns that contain '- Buried'
    burial_columns = [col for col in df.columns if "- Buried" in col]

    print(f"Found {len(burial_columns)} burial columns")

    # Select relevant columns: Year, Week, and all burial columns
    analysis_columns = ["Year", "Week"] + burial_columns
    analysis_df = df[analysis_columns].copy()

    # Convert burial columns to numeric, replacing empty strings and non-numeric values with 0
    for col in burial_columns:
        analysis_df[col] = pd.to_numeric(analysis_df[col], errors="coerce").fillna(0)

    # Calculate total burials for each row (year/week combination)
    analysis_df["Total_Burials"] = analysis_df[burial_columns].sum(axis=1)

    # Group by Year and Week, summing the burials (in case there are duplicate year/week entries)
    summary = (
        analysis_df.groupby(["Year", "Week"])
        .agg({"Total_Burials": "sum", **{col: "sum" for col in burial_columns}})
        .reset_index()
    )

    # Sort by Year and Week
    summary = summary.sort_values(["Year", "Week"])

    return summary, burial_columns


def print_summary_stats(summary_df):
    """Print basic statistics about the burial data"""
    print("\n=== BURIAL DATA SUMMARY ===")
    print(f"Total records: {len(summary_df)}")
    print(f"Years covered: {summary_df['Year'].min()} - {summary_df['Year'].max()}")
    print(f"Total weeks: {summary_df['Week'].nunique()}")
    print(f"Average burials per week: {summary_df['Total_Burials'].mean():.1f}")
    print(f"Maximum burials in a week: {summary_df['Total_Burials'].max()}")
    print(f"Minimum burials in a week: {summary_df['Total_Burials'].min()}")
    print()


def display_top_burial_weeks(summary_df, n=10):
    """Display the weeks with the highest burial counts"""
    top_weeks = summary_df.nlargest(n, "Total_Burials")
    print(f"=== TOP {n} WEEKS BY BURIAL COUNT ===")
    for _, row in top_weeks.iterrows():
        print(f"Year {row['Year']}, Week {row['Week']}: {row['Total_Burials']} burials")
    print()


def display_yearly_totals(summary_df):
    """Display total burials by year"""
    yearly_totals = (
        summary_df.groupby("Year")["Total_Burials"].sum().sort_values(ascending=False)
    )
    print("=== BURIALS BY YEAR ===")
    for year, total in yearly_totals.items():
        print(f"{year}: {total} burials")
    print()


def export_results(summary_df, burial_columns, output_file):
    """Export the analyzed data to a new CSV file"""
    # Create a simplified output with just the key information
    output_columns = ["Year", "Week", "Total_Burials"] + burial_columns
    output_df = summary_df[output_columns]

    output_df.to_csv(output_file, index=False)
    print(f"Results exported to: {output_file}")


def main():
    csv_file = "2025-10-27-Laxton-combineddata-weeklybills-parishes.csv"
    output_file = "burial_analysis_results.csv"

    try:
        # Analyze the data
        summary_df, burial_columns = analyze_burial_data(csv_file)

        # Print statistics
        print_summary_stats(summary_df)
        display_yearly_totals(summary_df)
        display_top_burial_weeks(summary_df, 15)

        # Show sample of the data
        print("=== SAMPLE DATA (First 10 records) ===")
        print(
            summary_df[["Year", "Week", "Total_Burials"]]
            .head(10)
            .to_string(index=False)
        )
        print()

        # Export results
        export_results(summary_df, burial_columns, output_file)

        print(
            f"\nAnalysis complete! Found {len(burial_columns)} burial columns across {len(summary_df)} year/week combinations."
        )

    except FileNotFoundError:
        print(f"Error: Could not find the file '{csv_file}'")
        print("Please make sure the CSV file is in the current directory.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")


if __name__ == "__main__":
    main()
