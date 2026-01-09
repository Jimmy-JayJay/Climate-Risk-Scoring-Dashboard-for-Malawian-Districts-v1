"""
Process GADM Level 1 data (28 main districts) with WorldPop population
This will give us exact population counts for the 28 districts used in the dashboard
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import ALL_DISTRICTS

def process_gadm_level1_with_worldpop():
    """Process GADM Level 1 boundaries with WorldPop population data"""
    print("="*70)
    print("Processing GADM Level 1 (28 Main Districts) with WorldPop")
    print("="*70)
    
    # Load GADM Level 1 shapefile
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'gadm')
    shp_file = os.path.join(data_dir, 'gadm41_MWI_1.shp')
    
    print(f"\nLoading GADM Level 1 shapefile...")
    gdf = gpd.read_file(shp_file)
    
    print(f"Loaded {len(gdf)} districts")
    print(f"\nDistrict names from GADM:")
    for name in sorted(gdf['NAME_1'].unique()):
        print(f"  - {name}")
    
    # Load WorldPop raster
    worldpop_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'worldpop')
    raster_path = os.path.join(worldpop_dir, 'mwi_ppp_2020_UNadj_constrained.tif')
    
    print(f"\n{'='*70}")
    print("Extracting Population from WorldPop Raster")
    print("="*70)
    
    district_data = []
    
    with rasterio.open(raster_path) as src:
        for idx, row in gdf.iterrows():
            district_name = row['NAME_1']
            geometry = [mapping(row['geometry'])]
            
            try:
                # Mask raster with district polygon
                out_image, out_transform = mask(src, geometry, crop=True, nodata=0)
                # Sum all pixel values (population count)
                population = float(out_image.sum())
                
                # Calculate area and density
                area_sqkm = row['geometry'].area / 1e6  # Convert to sq km
                pop_density = population / area_sqkm if area_sqkm > 0 else 0
                
                print(f"  {district_name:20s}: {population:>12,.0f} people ({pop_density:>6.1f} per km²)")
                
                district_data.append({
                    'district': district_name,
                    'population': population,
                    'area_sqkm': area_sqkm,
                    'population_density': pop_density
                })
                
            except Exception as e:
                print(f"  Error processing {district_name}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(district_data)
    
    print(f"\n{'='*70}")
    print("Summary Statistics")
    print("="*70)
    print(f"Total Districts: {len(df)}")
    print(f"Total Population: {df['population'].sum():,.0f}")
    print(f"Average Population: {df['population'].mean():,.0f}")
    print(f"Median Population: {df['population'].median():,.0f}")
    print(f"Min Population: {df['population'].min():,.0f} ({df.loc[df['population'].idxmin(), 'district']})")
    print(f"Max Population: {df['population'].max():,.0f} ({df.loc[df['population'].idxmax(), 'district']})")
    
    # Save to CSV
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'population_gadm_level1.csv')
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*70}")
    print(f"SUCCESS! Population data saved to:")
    print(f"  {output_file}")
    print("="*70)
    
    # Check name matching with config
    print(f"\n{'='*70}")
    print("Checking Name Matching with Dashboard Config")
    print("="*70)
    
    gadm_names = set(df['district'].str.upper())
    config_names = set([d.upper() for d in ALL_DISTRICTS.keys()])
    
    matched = gadm_names & config_names
    gadm_only = gadm_names - config_names
    config_only = config_names - gadm_names
    
    print(f"\nMatched ({len(matched)} districts):")
    for name in sorted(matched):
        print(f"  [OK] {name}")
    
    if gadm_only:
        print(f"\nIn GADM but not in config ({len(gadm_only)}):")
        for name in sorted(gadm_only):
            print(f"  [?] {name}")
    
    if config_only:
        print(f"\nIn config but not in GADM ({len(config_only)}):")
        for name in sorted(config_only):
            print(f"  [?] {name}")
    
    print(f"\nMatch rate: {len(matched)}/{len(config_names)} ({100*len(matched)/len(config_names):.1f}%)")
    
    return df

if __name__ == '__main__':
    df = process_gadm_level1_with_worldpop()
    print("\nFirst 10 districts:")
    print(df.head(10).to_string())
