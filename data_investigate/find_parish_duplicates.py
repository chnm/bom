"""Identify suspected duplicate parish entries in parishes.csv.

Flags entries with empty bills_subunit/foundation_year fields and attempts
to find their canonical counterpart by matching canonical_name or fuzzy
parish_name similarity against entries that DO have full metadata.

Usage:
    python find_parish_duplicates.py
    # or from bom-processing/scripts/bompy/:
    uv run ../../data_investigate/find_parish_duplicates.py
"""

import csv
from pathlib import Path

DATA_DIR = (
    Path(__file__).parent.parent / "bom-processing" / "scripts" / "bompy" / "data"
)
PARISHES_CSV = DATA_DIR / "parishes.csv"
ALL_BILLS_CSV = DATA_DIR / "all_bills.csv"


def load_parishes():
    with open(PARISHES_CSV) as f:
        return list(csv.DictReader(f))


def count_bills_by_parish():
    counts = {}
    with open(ALL_BILLS_CSV) as f:
        for row in csv.DictReader(f):
            pid = int(row["parish_id"])
            counts[pid] = counts.get(pid, 0) + 1
    return counts


def normalize(name: str) -> str:
    """Normalize a parish name for comparison."""
    return name.lower().replace(".", "").replace("'", "").replace("  ", " ").strip()


def extract_core_name(name: str) -> str:
    """Extract core parish name, stripping common prefixes/suffixes and location qualifiers.

    Only strips qualifiers when the remaining name is specific enough to avoid
    false matches (e.g. "St George" alone is too generic).
    """
    n = normalize(name)
    for qualifier in [" in ", " by ", " at ", " near ", " upon "]:
        if qualifier in n:
            core = n.split(qualifier)[0].strip()
            # Don't strip if the remaining core is too generic (< 15 chars)
            # to avoid collapsing distinct "St George ..." parishes
            if len(core) >= 15:
                n = core
    return n.strip()


def find_potential_match(suspect, full_parishes):
    """Try to find a canonical counterpart for a suspect entry."""
    s_canon = normalize(suspect["canonical_name"])
    s_name = normalize(suspect["parish_name"])
    s_core = extract_core_name(suspect["parish_name"])

    for p in full_parishes:
        p_canon = normalize(p["canonical_name"])
        p_name = normalize(p["parish_name"])
        p_core = extract_core_name(p["parish_name"])

        # Exact canonical name match
        if s_canon == p_canon:
            return p

        # One canonical name contains the other
        if s_canon in p_canon or p_canon in s_canon:
            return p

        # Parish name similarity (one is substring of other)
        if len(s_name) > 5 and len(p_name) > 5:
            if s_name in p_name or p_name in s_name:
                return p

        # Core name match (strips location qualifiers)
        if len(s_core) > 5 and s_core == p_core:
            return p

        # Spelling variation: "burg" vs "bury", "all" vs "al" prefix
        if (
            s_core.replace("sburg", "sbury") == p_core
            or p_core.replace("sbury", "sburg") == s_core
        ):
            return p
        if (
            s_core.replace("allhallows", "alhallows") == p_core
            or p_core.replace("alhallows", "allhallows") == s_core
        ):
            return p

    return None


def main():
    parishes = load_parishes()
    bill_counts = count_bills_by_parish()

    # Split into full-metadata and suspect entries
    full = [p for p in parishes if p["bills_subunit"]]
    suspects = [p for p in parishes if not p["bills_subunit"]]

    if not suspects:
        print("No suspected duplicates found.")
        return

    print(f"Found {len(suspects)} parish entries with empty metadata:\n")
    print(
        f"{'ID':>4}  {'Records':>7}  {'Parish Name':<35} {'Canonical Name':<35} {'Suggested Match'}"
    )
    print("-" * 130)

    for s in suspects:
        pid = int(s["id"])
        count = bill_counts.get(pid, 0)
        match = find_potential_match(s, full)

        match_str = ""
        if match:
            match_str = f"→ ID {match['id']} ({match['parish_name']} / {match['canonical_name']})"
        else:
            match_str = "  [no match found — may need manual review]"

        print(
            f"{pid:>4}  {count:>7}  {s['parish_name']:<35} {s['canonical_name']:<35} {match_str}"
        )


if __name__ == "__main__":
    main()
