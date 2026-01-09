"""
Enhance sample data with real World Bank national statistics
Since the GADM shapefile is incomplete, we'll use the generated sample data
but calibrate it based on real World Bank national indicators.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import ALL_DISTRICTS

def extract_world_bank_indicators():
    """Extract key national indicators from World Bank data"""
    print("Extracting World Bank national indicators...")
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    wb_file = os.path.join(data_dir, 'API_MWI_DS2_en_csv_v2_10259.csv')
    wb_data = pd.read_csv(wb_file, skiprows=4)
    
    # Extract most recent values for key indicators
    indicators = {
        'SI.POV.DDAY': 'poverty_rate',
        'SE.ADT.LITR.ZS': 'literacy_rate',
        'SL.AGR.EMPL.ZS': 'agricultural_dependence',
        'SH.H2O.BASW.ZS': 'water_access',
    }
    
    national_stats = {}
    for code, name in indicators.items():
        row = wb_data[wb_data['Indicator Code'] == code]
        if not row.empty:
            year_cols = [col for col in wb_data.columns if col.isdigit()]
            values = row[year_cols].values[0]
            non_null = [v for v in values if pd.notna(v)]
            if non_null:
                national_stats[name] = non_null[-1]
    
    return national_stats

def enhance_sample_data_with_real_stats(national_stats):
    """
    Load generated sample data and recalibrate it based on real national statistics
    """
    print("\nEnhancing sample data with real statistics...")
    
    # Load generated sample data
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    sample_file = os.path.join(data_dir, 'socioeconomic_data_all_districts.csv')
    
    df = pd.read_csv(sample_file)
    
    print(f"Loaded sample data for {len(df)} districts")
    
    # Recalibrate based on real national averages
    if 'poverty_rate' in national_stats:
        current_avg = df['poverty_rate'].mean()
        target_avg = national_stats['poverty_rate']
        adjustment = target_avg - current_avg
        df['poverty_rate'] = np.clip(df['poverty_rate'] + adjustment, 20, 95)
        print(f"  Poverty rate: adjusted from {current_avg:.1f}% to {df['poverty_rate'].mean():.1f}% (target: {target_avg:.1f}%)")
    
    if 'literacy_rate' in national_stats:
        current_avg = df['literacy_rate'].mean()
        target_avg = national_stats['literacy_rate']
        adjustment = target_avg - current_avg
        df['literacy_rate'] = np.clip(df['literacy_rate'] + adjustment, 40, 95)
        print(f"  Literacy rate: adjusted from {current_avg:.1f}% to {df['literacy_rate'].mean():.1f}% (target: {target_avg:.1f}%)")
    
    if 'agricultural_dependence' in national_stats:
        current_avg = df['agricultural_dependence'].mean()
        target_avg = national_stats['agricultural_dependence']
        adjustment = target_avg - current_avg
        df['agricultural_dependence'] = np.clip(df['agricultural_dependence'] + adjustment, 30, 95)
        print(f"  Ag dependency: adjusted from {current_avg:.1f}% to {df['agricultural_dependence'].mean():.1f}% (target: {target_avg:.1f}%)")
    
    if 'water_access' in national_stats:
        current_avg = df['water_access'].mean()
        target_avg = national_stats['water_access']
        adjustment = target_avg - current_avg
        df['water_access'] = np.clip(df['water_access'] + adjustment, 30, 95)
        print(f"  Water access: adjusted from {current_avg:.1f}% to {df['water_access'].mean():.1f}% (target: {target_avg:.1f}%)")
    
    return df

def main():
    print("="*70)
    print("Enhancing Sample Data with Real World Bank Statistics")
    print("="*70)
    
    # Extract real national statistics
    national_stats = extract_world_bank_indicators()
    
    print("\nReal National Statistics from World Bank:")
    for key, value in national_stats.items():
        print(f"  {key}: {value:.2f}")
    
    # Enhance sample data
    enhanced_df = enhance_sample_data_with_real_stats(national_stats)
    
    # Save enhanced data
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    output_file = os.path.join(output_dir, 'socioeconomic_data_enhanced.csv')
    enhanced_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*70}")
    print(f"SUCCESS! Enhanced data saved to:")
    print(f"  {output_file}")
    print(f"{'='*70}")
    
    print(f"\nSummary of Enhanced Data:")
    print(f"  Districts: {len(enhanced_df)}")
    print(f"  Avg Poverty Rate: {enhanced_df['poverty_rate'].mean():.1f}%")
    print(f"  Avg Literacy Rate: {enhanced_df['literacy_rate'].mean():.1f}%")
    print(f"  Avg Ag Dependency: {enhanced_df['agricultural_dependence'].mean():.1f}%")
    print(f"  Avg Water Access: {enhanced_df['water_access'].mean():.1f}%")
    
    print(f"\nThis data now reflects real World Bank national statistics!")
    print(f"\nNext steps:")
    print(f"  1. Update dashboard to use: socioeconomic_data_enhanced.csv")
    print(f"  2. Fetch real climate data using NASA POWER API")
    print(f"  3. Run the dashboard with enhanced data")
    
    return enhanced_df

if __name__ == '__main__':
    df = main()
