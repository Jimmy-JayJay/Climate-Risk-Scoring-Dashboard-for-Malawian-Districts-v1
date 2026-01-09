"""
Data collection functions for climate and socioeconomic data
Fetches data from NASA POWER API, CHIRPS, GADM, and other sources
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
from config import NASA_POWER_API, CLIMATE_PARAMS


def fetch_nasa_power_data(lat: float, 
                          lon: float, 
                          start_year: int = 2000, 
                          end_year: int = 2024,
                          parameters: List[str] = None) -> pd.DataFrame:
    """
    Fetch climate data from NASA POWER API for a specific location
    
    Args:
        lat: Latitude
        lon: Longitude
        start_year: Start year for data
        end_year: End year for data
        parameters: List of parameters to fetch (default: from config)
    
    Returns:
        DataFrame with climate data
    """
    if parameters is None:
        parameters = CLIMATE_PARAMS['nasa_power_params']
    
    # Format parameters for API
    params_str = ','.join(parameters)
    
    # Construct API URL
    url = f"{NASA_POWER_API}?parameters={params_str}&community=AG&longitude={lon}&latitude={lat}&start={start_year}0101&end={end_year}1231&format=JSON"
    
    try:
        print(f"Fetching NASA POWER data for ({lat}, {lon})...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract parameters data
        df_dict = {'date': []}
        for param in parameters:
            df_dict[param] = []
        
        # Parse the nested JSON structure
        if 'properties' in data and 'parameter' in data['properties']:
            for param in parameters:
                if param in data['properties']['parameter']:
                    param_data = data['properties']['parameter'][param]
                    
                    # Get dates and values
                    for date_str, value in param_data.items():
                        if date_str not in df_dict['date']:
                            df_dict['date'].append(date_str)
                        
                        # Handle missing values
                        if value == -999 or value is None:
                            df_dict[param].append(np.nan)
                        else:
                            df_dict[param].append(value)
        
        # Create DataFrame
        df = pd.DataFrame(df_dict)
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        # Rename columns for clarity
        column_mapping = {
            'T2M': 'temperature_mean',
            'T2M_MAX': 'temperature_max',
            'T2M_MIN': 'temperature_min',
            'PRECTOTCORR': 'rainfall'
        }
        df = df.rename(columns=column_mapping)
        
        print(f"Successfully fetched {len(df)} days of data")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA POWER data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing NASA POWER data: {e}")
        return pd.DataFrame()


def fetch_multiple_districts_nasa(districts: Dict[str, Dict],
                                  start_year: int = 2000,
                                  end_year: int = 2024,
                                  delay: float = 1.0) -> pd.DataFrame:
    """
    Fetch NASA POWER data for multiple districts with rate limiting
    
    Args:
        districts: Dictionary of districts with lat/lon
        start_year: Start year
        end_year: End year
        delay: Delay between requests in seconds
    
    Returns:
        Combined DataFrame with all districts
    """
    all_data = []
    
    for district_name, coords in districts.items():
        print(f"\nProcessing {district_name}...")
        
        df = fetch_nasa_power_data(
            lat=coords['lat'],
            lon=coords['lon'],
            start_year=start_year,
            end_year=end_year
        )
        
        if not df.empty:
            df['district'] = district_name
            all_data.append(df)
        
        # Rate limiting
        time.sleep(delay)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal records collected: {len(combined_df)}")
        return combined_df
    else:
        return pd.DataFrame()


def create_sample_socioeconomic_data(districts: List[str]) -> pd.DataFrame:
    """
    Create sample socioeconomic data for MVP testing
    In production, this would fetch from NSO/World Bank sources
    
    Args:
        districts: List of district names
    
    Returns:
        DataFrame with socioeconomic indicators
    """
    # Sample data based on known patterns for Malawi districts
    # These are approximate values for demonstration
    sample_data = {
        'Nsanje': {
            'population': 285000,
            'population_density': 150,
            'poverty_rate': 68,  # High poverty
            'literacy_rate': 58,  # Lower literacy
            'agricultural_dependence': 85,  # Very high
            'health_facility_access': 45,  # Lower access
            'water_access': 52,
            'road_density': 0.15  # km per sq km
        },
        'Lilongwe': {
            'population': 2600000,
            'population_density': 450,
            'poverty_rate': 35,  # Lower poverty (urban)
            'literacy_rate': 82,  # Higher literacy
            'agricultural_dependence': 45,  # Lower (urban)
            'health_facility_access': 78,  # Better access
            'water_access': 85,
            'road_density': 0.45
        },
        'Zomba': {
            'population': 750000,
            'population_density': 280,
            'poverty_rate': 52,  # Medium poverty
            'literacy_rate': 72,  # Medium literacy
            'agricultural_dependence': 65,  # Medium
            'health_facility_access': 62,  # Medium access
            'water_access': 68,
            'road_density': 0.28
        }
    }
    
    # Create DataFrame
    data_list = []
    for district in districts:
        if district in sample_data:
            row = {'district': district}
            row.update(sample_data[district])
            data_list.append(row)
    
    df = pd.DataFrame(data_list)
    
    return df


def create_sample_disaster_data(districts: List[str]) -> pd.DataFrame:
    """
    Create sample historical disaster data for MVP
    In production, this would fetch from EM-DAT
    
    Args:
        districts: List of district names
    
    Returns:
        DataFrame with disaster events
    """
    # Sample disaster events based on known history
    disasters = [
        {'district': 'Nsanje', 'year': 2015, 'type': 'flood', 'severity': 'high', 'affected': 120000},
        {'district': 'Nsanje', 'year': 2019, 'type': 'flood', 'severity': 'high', 'affected': 95000},
        {'district': 'Nsanje', 'year': 2022, 'type': 'flood', 'severity': 'medium', 'affected': 45000},
        {'district': 'Nsanje', 'year': 2023, 'type': 'cyclone', 'severity': 'high', 'affected': 85000},
        {'district': 'Zomba', 'year': 2019, 'type': 'cyclone', 'severity': 'medium', 'affected': 35000},
        {'district': 'Zomba', 'year': 2021, 'type': 'flood', 'severity': 'low', 'affected': 12000},
        {'district': 'Lilongwe', 'year': 2020, 'type': 'drought', 'severity': 'medium', 'affected': 25000},
    ]
    
    df = pd.DataFrame(disasters)
    df = df[df['district'].isin(districts)]
    
    return df


def calculate_cyclone_exposure(district: str, 
                               latitude: float) -> float:
    """
    Calculate cyclone exposure based on geographic location
    Southern districts closer to Mozambique coast have higher exposure
    
    Args:
        district: District name
        latitude: District latitude
    
    Returns:
        Cyclone exposure score (0-100)
    """
    # Southern districts (latitude < -14) have higher cyclone exposure
    # Exposure decreases as you move north
    
    if latitude < -15.5:  # Very southern (Nsanje, Chikwawa, Thyolo, Mulanje, Phalombe)
        return 85
    elif latitude < -14.5:  # Southern (Zomba, Blantyre, Chiradzulu)
        return 60
    elif latitude < -13:  # Central
        return 30
    else:  # Northern
        return 10


def download_gadm_boundaries(country: str = 'MWI', 
                            admin_level: int = 2,
                            output_path: str = 'data/raw/') -> str:
    """
    Download district boundaries from GADM
    Note: This is a placeholder - actual implementation would download shapefiles
    
    Args:
        country: ISO country code (MWI for Malawi)
        admin_level: Administrative level (2 for districts)
        output_path: Path to save the file
    
    Returns:
        Path to downloaded file
    """
    # GADM URL format
    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{country}_shp.zip"
    
    print(f"To download GADM boundaries, visit: {url}")
    print(f"Extract the level {admin_level} shapefile to: {output_path}")
    
    # In production, this would actually download and extract the file
    # For MVP, we'll use sample data or manual download
    
    return f"{output_path}gadm41_{country}_{admin_level}.shp"


def save_data_to_csv(df: pd.DataFrame, 
                     filename: str, 
                     output_dir: str = 'data/processed/') -> str:
    """
    Save DataFrame to CSV file
    
    Args:
        df: DataFrame to save
        filename: Output filename
        output_dir: Output directory
    
    Returns:
        Full path to saved file
    """
    import os
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    
    print(f"Data saved to: {filepath}")
    return filepath


def load_data_from_csv(filepath: str) -> pd.DataFrame:
    """
    Load data from CSV file
    
    Args:
        filepath: Path to CSV file
    
    Returns:
        DataFrame with loaded data
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} rows from {filepath}")
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()
