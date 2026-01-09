"""
Fetch real climate data from NASA POWER API for all 28 Malawian districts
This will take 30-60 minutes due to API rate limits
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection import fetch_multiple_districts_nasa
from config import ALL_DISTRICTS

def main():
    print("="*70)
    print("Fetching Real Climate Data from NASA POWER API")
    print("="*70)
    print(f"\nThis will fetch data for {len(ALL_DISTRICTS)} districts")
    print("Time period: 2020-2024")
    print("Estimated time: 30-60 minutes (2 second delay between requests)")
    print("\nData includes:")
    print("  - Daily temperature (min, max, mean)")
    print("  - Daily rainfall")
    print("  - Solar radiation")
    print("  - Relative humidity")
    print("\n" + "="*70)
    
    # Fetch data for all districts
    climate_data = fetch_multiple_districts_nasa(
        districts=ALL_DISTRICTS,
        start_year=2020,
        end_year=2024,
        delay=2.0  # 2 second delay to respect API limits
    )
    
    # Save to processed directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'climate_data_nasa_power.csv')
    climate_data.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("SUCCESS! Real climate data fetched and saved")
    print("="*70)
    print(f"\nFile: {output_file}")
    print(f"Records: {len(climate_data):,}")
    print(f"Districts: {climate_data['district'].nunique()}")
    print(f"Date range: {climate_data['date'].min()} to {climate_data['date'].max()}")
    
    print("\nSample data:")
    print(climate_data.head())
    
    print("\nData summary:")
    print(climate_data.describe())
    
    return climate_data

if __name__ == '__main__':
    df = main()
