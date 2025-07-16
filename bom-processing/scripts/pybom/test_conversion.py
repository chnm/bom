#!/usr/bin/env python3
"""
Simple test to verify the Python conversion works.
"""

import pandas as pd
import numpy as np
from bomr.helpers import process_bodleian_data, month_to_number
from bomr.data_processing import tidy_parish_data


def test_basic_functionality():
    """Test basic functionality of the converted functions."""

    print("Testing month_to_number function...")
    assert month_to_number("January") == "01"
    assert month_to_number("December") == "12"
    assert month_to_number("Invalid") == "00"
    print("✓ month_to_number works correctly")

    print("\nTesting process_bodleian_data with missing columns...")

    # Create sample data without is_illegible and is_missing columns
    sample_data = pd.DataFrame(
        {
            "Year": [1665, 1665, 1665],
            "Week": [1, 2, 3],
            "UniqueID": ["A001", "A002", "A003"],
            "Start Day": [1, 8, 15],
            "Start Month": ["January", "January", "January"],
            "End Day": [7, 14, 21],
            "End Month": ["January", "January", "January"],
            "St. Alphage": [5, 3, 2],
            "St. Andrew Holborn": [8, 6, 4],
            "St. Bartholomew": [2, 1, 3],
        }
    )

    result = process_bodleian_data(sample_data, "test_source")

    # Check that result has the expected columns
    expected_columns = [
        "Year",
        "Week",
        "UniqueID",
        "Start Day",
        "Start Month",
        "End Day",
        "End Month",
        "parish_name",
        "count",
        "illegible",
        "missing",
        "source",
    ]

    for col in expected_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Check that illegible and missing columns are False by default
    assert result["illegible"].all() == False
    assert result["missing"].all() == False

    print("✓ process_bodleian_data handles missing flag columns correctly")

    print("\nTesting tidy_parish_data...")

    # Create sample data with parish-type format
    sample_tidy_data = pd.DataFrame(
        {
            "parish_name": [
                "St. Alphage-Buried",
                "St. Andrew-Christened",
                "St. Bartholomew-Plague",
            ],
            "count": [5, 3, 2],
            "year": [1665, 1665, 1665],
        }
    )

    tidied = tidy_parish_data(sample_tidy_data)

    assert "count_type" in tidied.columns
    assert tidied.loc[0, "parish_name"] == "St. Alphage"
    assert tidied.loc[0, "count_type"] == "Buried"
    assert tidied.loc[1, "count_type"] == "Christened"

    print("✓ tidy_parish_data works correctly")

    print("\n🎉 All tests passed! The Python conversion is working correctly.")


if __name__ == "__main__":
    test_basic_functionality()
