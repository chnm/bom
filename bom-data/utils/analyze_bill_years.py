#!/usr/bin/env python3

import csv
import glob


def categorize_bills():
    """Categorize bills by type"""

    # Get all CSV files in current directory (excluding subdirectories)
    csv_files = glob.glob("*.csv")

    weekly_bills = []
    general_bills = []
    other_bills = []

    for filename in csv_files:
        filename_lower = filename.lower()

        if "weekly" in filename_lower:
            weekly_bills.append(filename)
        elif "general" in filename_lower:
            general_bills.append(filename)
        else:
            other_bills.append(filename)

    return weekly_bills, general_bills, other_bills


def extract_years_from_csv(filename, bill_type):
    """Extract years from CSV data based on bill type"""
    years = set()

    try:
        with open(filename, "r", encoding="utf-8") as csvfile:
            # Try to read with different encodings if UTF-8 fails
            reader = csv.DictReader(csvfile)

            for row in reader:
                if bill_type == "weekly":
                    # Weekly bills typically have 'Year' column
                    if "Year" in row and row["Year"]:
                        try:
                            year = int(row["Year"])
                            if 1500 <= year <= 2100:  # Reasonable year range
                                years.add(year)
                        except ValueError:
                            pass

                elif bill_type == "general":
                    # General bills have 'Start year' and 'End year'
                    for col in ["Start year", "End year"]:
                        if col in row and row[col]:
                            try:
                                year = int(row[col])
                                if 1500 <= year <= 2100:
                                    years.add(year)
                            except ValueError:
                                pass

                else:  # other bills
                    # Other bills typically have 'Year' column
                    if "Year" in row and row["Year"]:
                        try:
                            year = int(row["Year"])
                            if 1500 <= year <= 2100:
                                years.add(year)
                        except ValueError:
                            pass

    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return set()

    return years


def analyze_year_ranges(bill_list, bill_type):
    """Extract and analyze year ranges for a list of bills"""
    all_years = set()
    bill_info = []

    for filename in bill_list:
        years = extract_years_from_csv(filename, bill_type.lower())
        if years:
            all_years.update(years)
            bill_info.append((filename, sorted(years)))

    if all_years:
        unique_years = sorted(all_years)
        min_year = min(unique_years)
        max_year = max(unique_years)

        print(f"\n{bill_type.upper()} BILLS:")
        print(f"Total files: {len(bill_list)}")
        print(f"Historical year range: {min_year} - {max_year}")
        print(f"Unique years: {unique_years}")
        print("\nFiles with data:")

        for filename, years in bill_info:
            if years:
                print(f"  {filename}: {years}")

        # Files without year data
        files_without_years = [
            f for f in bill_list if not extract_years_from_csv(f, bill_type.lower())
        ]
        if files_without_years:
            print("\nFiles without readable year data:")
            for filename in files_without_years:
                print(f"  {filename}")
    else:
        print(f"\n{bill_type.upper()} BILLS:")
        print(f"Total files: {len(bill_list)}")
        print("No year data found in CSV files")


def get_all_unique_years(bill_list, bill_type):
    """Get all unique years from a list of bills"""
    all_years = set()

    for filename in bill_list:
        years = extract_years_from_csv(filename, bill_type.lower())
        all_years.update(years)

    return sorted(all_years)


def write_results_to_file(weekly_bills, general_bills, other_bills):
    """Write results to a text file"""
    output_file = "bill_years_analysis.txt"

    weekly_years = get_all_unique_years(weekly_bills, "Weekly")
    general_years = get_all_unique_years(general_bills, "General")
    other_years = get_all_unique_years(other_bills, "Other")

    with open(output_file, "w") as f:
        f.write("BILLS OF MORTALITY - HISTORICAL YEAR RANGE ANALYSIS\n")
        f.write("=" * 60 + "\n")
        f.write("(Analyzing actual year data from CSV contents, not filenames)\n\n")

        # Weekly Bills
        f.write("WEEKLY BILLS:\n")
        f.write(f"Total files: {len(weekly_bills)}\n")
        if weekly_years:
            f.write(f"Year range: {min(weekly_years)} - {max(weekly_years)}\n")
            f.write(f"Total unique years: {len(weekly_years)}\n")
            f.write("All available years:\n")

            # Format years in rows of 10 for readability
            for i in range(0, len(weekly_years), 10):
                year_chunk = weekly_years[i : i + 10]
                f.write("  " + ", ".join(map(str, year_chunk)) + "\n")
        else:
            f.write("No year data found\n")

        f.write("\n" + "-" * 50 + "\n\n")

        # General Bills
        f.write("GENERAL BILLS:\n")
        f.write(f"Total files: {len(general_bills)}\n")
        if general_years:
            f.write(f"Year range: {min(general_years)} - {max(general_years)}\n")
            f.write(f"Total unique years: {len(general_years)}\n")
            f.write("All available years:\n")

            # Format years in rows of 10 for readability
            for i in range(0, len(general_years), 10):
                year_chunk = general_years[i : i + 10]
                f.write("  " + ", ".join(map(str, year_chunk)) + "\n")
        else:
            f.write("No year data found\n")

        f.write("\n" + "-" * 50 + "\n\n")

        # Other Bills
        f.write("OTHER BILLS:\n")
        f.write(f"Total files: {len(other_bills)}\n")
        if other_years:
            f.write(f"Year range: {min(other_years)} - {max(other_years)}\n")
            f.write(f"Total unique years: {len(other_years)}\n")
            f.write("All available years:\n")

            # Format years in rows of 10 for readability
            for i in range(0, len(other_years), 10):
                year_chunk = other_years[i : i + 10]
                f.write("  " + ", ".join(map(str, year_chunk)) + "\n")
        else:
            f.write("No year data found\n")

        f.write("\n" + "=" * 60 + "\n\n")

        # Summary
        f.write("SUMMARY:\n")
        f.write(
            f"Weekly bills: {len(weekly_bills)} files ({len(weekly_years)} unique years)\n"
        )
        f.write(
            f"General bills: {len(general_bills)} files ({len(general_years)} unique years)\n"
        )
        f.write(
            f"Other bills: {len(other_bills)} files ({len(other_years)} unique years)\n"
        )
        f.write(
            f"Total: {len(weekly_bills) + len(general_bills) + len(other_bills)} files\n"
        )

        # Combined year coverage
        all_combined_years = sorted(set(weekly_years + general_years + other_years))
        if all_combined_years:
            f.write(
                f"\nCombined coverage: {min(all_combined_years)} - {max(all_combined_years)} ({len(all_combined_years)} unique years total)\n"
            )

    return output_file, weekly_years, general_years, other_years


def main():
    print("BILLS OF MORTALITY - HISTORICAL YEAR RANGE ANALYSIS")
    print("=" * 60)
    print("(Analyzing actual year data from CSV contents, not filenames)")

    weekly_bills, general_bills, other_bills = categorize_bills()

    # Write detailed results to file
    output_file, weekly_years, general_years, other_years = write_results_to_file(
        weekly_bills, general_bills, other_bills
    )

    # Print summary to console
    print("\nSUMMARY:")
    print(f"Weekly bills: {len(weekly_bills)} files ({len(weekly_years)} unique years)")
    if weekly_years:
        print(f"  Year range: {min(weekly_years)} - {max(weekly_years)}")

    print(
        f"General bills: {len(general_bills)} files ({len(general_years)} unique years)"
    )
    if general_years:
        print(f"  Year range: {min(general_years)} - {max(general_years)}")

    print(f"Other bills: {len(other_bills)} files ({len(other_years)} unique years)")
    if other_years:
        print(f"  Year range: {min(other_years)} - {max(other_years)}")

    # Combined coverage
    all_combined_years = sorted(set(weekly_years + general_years + other_years))
    if all_combined_years:
        print(
            f"\nCombined coverage: {min(all_combined_years)} - {max(all_combined_years)} ({len(all_combined_years)} unique years total)"
        )

    print(f"\nDetailed results written to: {output_file}")
    print(
        "This file contains the complete list of all available years for each bill type."
    )


if __name__ == "__main__":
    main()
