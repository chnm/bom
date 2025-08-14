#!/usr/bin/env python3
"""
Data Coverage Analysis for Bills of Mortality
Identifies missing years by parish and generates coverage visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
from typing import Dict, List, Tuple

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the processed BOM data."""
    data_dir = Path('data')
    
    # Load main bills data
    bills_path = data_dir / 'all_bills.csv'
    if not bills_path.exists():
        raise FileNotFoundError(f"Bills data not found at {bills_path}")
    
    bills = pd.read_csv(bills_path)
    print(f"Loaded {len(bills):,} bill records")
    
    # Load parish lookup
    parishes_path = data_dir / 'parishes.csv'
    if not parishes_path.exists():
        print("Warning: parishes.csv not found, using parish IDs")
        parishes = None
    else:
        parishes = pd.read_csv(parishes_path)
        print(f"Loaded {len(parishes)} parish records")
    
    return bills, parishes

def analyze_coverage_by_parish(bills: pd.DataFrame, parishes: pd.DataFrame = None) -> pd.DataFrame:
    """Analyze data coverage by parish across years."""
    
    # Get parish name mapping
    parish_names = {}
    if parishes is not None:
        parish_names = dict(zip(parishes['id'], parishes['parish_name']))
    
    # Get coverage by parish and year
    coverage_data = []
    
    for parish_id in bills['parish_id'].unique():
        parish_data = bills[bills['parish_id'] == parish_id]
        parish_name = parish_names.get(parish_id, f'Parish {parish_id}')
        
        years_with_data = sorted(parish_data['year'].unique())
        if not years_with_data:
            continue
            
        year_min, year_max = min(years_with_data), max(years_with_data)
        years_expected = set(range(year_min, year_max + 1))
        years_missing = years_expected - set(years_with_data)
        
        # Count by bill type
        weekly_years = set(parish_data[parish_data['bill_type'] == 'weekly']['year'].unique())
        general_years = set(parish_data[parish_data['bill_type'] == 'general']['year'].unique())
        
        coverage_data.append({
            'parish_id': parish_id,
            'parish_name': parish_name,
            'year_min': year_min,
            'year_max': year_max,
            'years_span': year_max - year_min + 1,
            'years_with_data': len(years_with_data),
            'years_missing': len(years_missing),
            'coverage_rate': len(years_with_data) / len(years_expected) if years_expected else 0,
            'missing_years': sorted(list(years_missing)),
            'weekly_years': len(weekly_years),
            'general_years': len(general_years),
            'total_records': len(parish_data)
        })
    
    return pd.DataFrame(coverage_data)

def identify_bill_type_gaps(bills: pd.DataFrame) -> Dict[str, List[int]]:
    """Identify years missing for each bill type."""
    gaps = {}
    
    for bill_type in bills['bill_type'].unique():
        type_data = bills[bills['bill_type'] == bill_type]
        years_with_data = set(type_data['year'].unique())
        
        if years_with_data:
            year_min, year_max = min(years_with_data), max(years_with_data)
            years_expected = set(range(year_min, year_max + 1))
            missing_years = sorted(list(years_expected - years_with_data))
            gaps[bill_type] = missing_years
    
    return gaps

def create_coverage_heatmap(bills: pd.DataFrame, parishes: pd.DataFrame = None, save_path: str = None):
    """Create a heatmap showing data coverage by parish and year."""
    
    # Prepare data for heatmap
    parish_names = {}
    if parishes is not None:
        parish_names = dict(zip(parishes['id'], parishes['parish_name']))
    
    # Create pivot table: parishes vs years
    parish_year_counts = bills.groupby(['parish_id', 'year']).size().reset_index(name='record_count')
    
    # Add parish names
    parish_year_counts['parish_name'] = parish_year_counts['parish_id'].map(
        lambda x: parish_names.get(x, f'Parish {x}')
    )
    
    # Create pivot table
    heatmap_data = parish_year_counts.pivot(
        index='parish_name', 
        columns='year', 
        values='record_count'
    ).fillna(0)
    
    # Sort by first year of data for each parish
    first_year_by_parish = parish_year_counts.groupby('parish_name')['year'].min().sort_values()
    heatmap_data = heatmap_data.reindex(first_year_by_parish.index)
    
    # Create the heatmap
    plt.figure(figsize=(20, 12))
    
    # Use binary colormap for presence/absence
    binary_data = (heatmap_data > 0).astype(int)
    
    sns.heatmap(
        binary_data, 
        cmap='RdYlGn', 
        cbar_kws={'label': 'Has Data'}, 
        yticklabels=True,
        xticklabels=5,  # Show every 5th year
        linewidths=0.1
    )
    
    plt.title('Bills of Mortality Data Coverage by Parish and Year', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Parish', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to {save_path}")
    
    plt.show()

def create_bill_type_timeline(bills: pd.DataFrame, save_path: str = None):
    """Create timeline showing availability of weekly vs general bills."""
    
    # Count records by year and bill type
    yearly_counts = bills.groupby(['year', 'bill_type']).size().unstack(fill_value=0)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    
    # Plot record counts
    if 'weekly' in yearly_counts.columns:
        ax1.bar(yearly_counts.index, yearly_counts['weekly'], 
               alpha=0.7, label='Weekly Bills', color='skyblue', width=0.8)
    if 'general' in yearly_counts.columns:
        ax1.bar(yearly_counts.index, yearly_counts['general'], 
               alpha=0.7, label='General Bills', color='orange', 
               bottom=yearly_counts.get('weekly', 0), width=0.8)
    
    ax1.set_ylabel('Number of Records')
    ax1.set_title('Bills of Mortality Record Counts by Year and Type', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot presence/absence
    presence_data = (yearly_counts > 0).astype(int)
    bottom_vals = np.zeros(len(yearly_counts))
    
    if 'weekly' in presence_data.columns:
        ax2.bar(presence_data.index, presence_data['weekly'], 
               alpha=0.7, label='Weekly Bills Available', color='skyblue', width=0.8)
        bottom_vals = presence_data['weekly']
    
    if 'general' in presence_data.columns:
        ax2.bar(presence_data.index, presence_data['general'], 
               alpha=0.7, label='General Bills Available', color='orange', 
               bottom=bottom_vals, width=0.8)
    
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Data Available')
    ax2.set_title('Data Availability by Bill Type', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(['None', 'One Type', 'Both Types'])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Timeline saved to {save_path}")
    
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze Bills of Mortality data coverage')
    parser.add_argument('--save-plots', action='store_true', 
                       help='Save plots to files')
    parser.add_argument('--output-dir', default='analysis_output',
                       help='Directory to save plots')
    
    args = parser.parse_args()
    
    if args.save_plots:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
    
    print("🔍 Bills of Mortality - Data Coverage Analysis")
    print("=" * 50)
    
    # Load data
    try:
        bills, parishes = load_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Basic coverage statistics
    print(f"\n📊 Basic Coverage Statistics:")
    print(f"Total records: {len(bills):,}")
    print(f"Years covered: {bills['year'].min()} - {bills['year'].max()}")
    print(f"Number of years with data: {bills['year'].nunique()}")
    print(f"Number of parishes: {bills['parish_id'].nunique()}")
    
    # Bill type breakdown
    bill_type_counts = bills['bill_type'].value_counts()
    print(f"\nBill Types:")
    for bill_type, count in bill_type_counts.items():
        print(f"  {bill_type.title()}: {count:,} records")
    
    # Coverage by parish analysis
    print(f"\n🏛️ Analyzing coverage by parish...")
    coverage_df = analyze_coverage_by_parish(bills, parishes)
    
    # Parish coverage summary
    print(f"\nParish Coverage Summary:")
    print(f"  Average coverage rate: {coverage_df['coverage_rate'].mean():.2%}")
    print(f"  Parishes with 100% coverage: {(coverage_df['coverage_rate'] == 1.0).sum()}")
    print(f"  Parishes with <50% coverage: {(coverage_df['coverage_rate'] < 0.5).sum()}")
    
    # Parishes with most missing years
    worst_coverage = coverage_df.nlargest(10, 'years_missing')
    if len(worst_coverage) > 0:
        print(f"\nParishes with most missing years:")
        for _, parish in worst_coverage.iterrows():
            if parish['years_missing'] > 0:
                print(f"  {parish['parish_name'][:35]:35} - {parish['years_missing']:2d} missing ({parish['year_min']}-{parish['year_max']})")
    
    # Bill type gaps
    print(f"\n📅 Identifying bill type gaps...")
    bill_gaps = identify_bill_type_gaps(bills)
    
    for bill_type, missing_years in bill_gaps.items():
        if missing_years:
            print(f"\n{bill_type.title()} Bills missing for years:")
            # Group consecutive years
            groups = []
            current_group = [missing_years[0]]
            
            for year in missing_years[1:]:
                if year == current_group[-1] + 1:
                    current_group.append(year)
                else:
                    groups.append(current_group)
                    current_group = [year]
            groups.append(current_group)
            
            for group in groups:
                if len(group) == 1:
                    print(f"  {group[0]}")
                else:
                    print(f"  {group[0]}-{group[-1]} ({len(group)} years)")
    
    # Create visualizations
    print(f"\n📊 Creating visualizations...")
    
    heatmap_path = output_dir / 'coverage_heatmap.png' if args.save_plots else None
    create_coverage_heatmap(bills, parishes, heatmap_path)
    
    timeline_path = output_dir / 'bill_type_timeline.png' if args.save_plots else None
    create_bill_type_timeline(bills, timeline_path)
    
    # Export detailed coverage data
    if args.save_plots:
        coverage_csv_path = output_dir / 'parish_coverage_analysis.csv'
        coverage_df.to_csv(coverage_csv_path, index=False)
        print(f"Coverage analysis saved to {coverage_csv_path}")
    
    print(f"\n✅ Analysis complete!")
    
    # Key findings summary
    print(f"\n🔍 Key Findings:")
    
    # General vs Weekly bill gaps
    general_gaps = bill_gaps.get('general', [])
    weekly_gaps = bill_gaps.get('weekly', [])
    
    if general_gaps:
        recent_general_gaps = [y for y in general_gaps if y >= 1660]
        early_general_gaps = [y for y in general_gaps if y < 1660]
        
        if recent_general_gaps:
            print(f"  🔴 General Bills missing for recent years: {recent_general_gaps}")
        if early_general_gaps:
            print(f"  🟡 General Bills missing for early years: {early_general_gaps}")
    
    if weekly_gaps:
        recent_weekly_gaps = [y for y in weekly_gaps if y >= 1660]
        early_weekly_gaps = [y for y in weekly_gaps if y < 1660]
        
        if early_weekly_gaps:
            print(f"  🔴 Weekly Bills missing for early years: {early_weekly_gaps[:10]}{'...' if len(early_weekly_gaps) > 10 else ''}")
        if recent_weekly_gaps:
            print(f"  🟡 Weekly Bills missing for recent years: {recent_weekly_gaps}")
    
    # Coverage completeness
    poor_coverage_parishes = coverage_df[coverage_df['coverage_rate'] < 0.5]
    if len(poor_coverage_parishes) > 0:
        print(f"  ⚠️ {len(poor_coverage_parishes)} parishes have <50% coverage")

if __name__ == "__main__":
    main()