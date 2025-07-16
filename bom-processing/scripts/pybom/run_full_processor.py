#!/usr/bin/env python3
"""
Simple script to run the full BOMProcessor without Typer complications.
"""

import sys
from pathlib import Path
from bomr.main import BOMProcessor

def main():
    """Run the full BOM processing pipeline."""
    
    print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Bills of Mortality Data Processor")
    print("Python conversion of R scripts for Death by Numbers project\n")
    
    # Set up paths
    data_dir = "../../../bom-data/data-csvs"
    output_dir = "data"
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Create processor
    processor = BOMProcessor(data_dir, output_dir)
    
    try:
        # Run full pipeline
        print("Loading CSV files...")
        processor.load_csv_files()
        
        print("Processing causes of death...")
        processor.process_causes_data()
        
        print("Processing weekly bills...")
        weekly_bills = processor.process_weekly_bills_data()
        
        print("Processing general bills...")
        general_bills = processor.process_general_bills_data()
        
        print("Saving all results...")
        processor.save_results(weekly_bills, general_bills)
        
        print("✅ Processing completed successfully!")
        
        # Show summary
        output_path = Path(output_dir)
        if output_path.exists():
            csv_files = list(output_path.glob("*.csv"))
            print(f"\n📊 Generated {len(csv_files)} output files:")
            for file in sorted(csv_files):
                print(f"  - {file.name}")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()