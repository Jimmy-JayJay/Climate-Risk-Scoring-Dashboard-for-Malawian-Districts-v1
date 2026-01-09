"""
Configuration file for Climate Risk Scoring Dashboard
Contains district information, API endpoints, and scoring weights
"""

# NASA POWER API endpoint
NASA_POWER_API = "https://power.larc.nasa.gov/api/temporal/daily/point"

# CHIRPS data sources
CHIRPS_API = "https://data.chc.ucsb.edu/products/CHIRPS-2.0"

# District centroids for MVP (3 districts)
MVP_DISTRICTS = {
    'Nsanje': {'lat': -16.92, 'lon': 35.26, 'expected_risk': 'high'},
    'Lilongwe': {'lat': -13.98, 'lon': 33.78, 'expected_risk': 'low'},
    'Zomba': {'lat': -15.38, 'lon': 35.32, 'expected_risk': 'medium'}
}

# All 28 Malawi districts with centroids
ALL_DISTRICTS = {
    'Balaka': {'lat': -14.98, 'lon': 34.95},
    'Blantyre': {'lat': -15.78, 'lon': 35.00},
    'Chikwawa': {'lat': -16.03, 'lon': 34.78},
    'Chiradzulu': {'lat': -15.68, 'lon': 35.23},
    'Chitipa': {'lat': -9.70, 'lon': 33.27},
    'Dedza': {'lat': -14.38, 'lon': 34.33},
    'Dowa': {'lat': -13.65, 'lon': 33.93},
    'Karonga': {'lat': -9.93, 'lon': 33.93},
    'Kasungu': {'lat': -13.03, 'lon': 33.48},
    'Likoma': {'lat': -12.06, 'lon': 34.73},
    'Lilongwe': {'lat': -13.98, 'lon': 33.78},
    'Machinga': {'lat': -14.97, 'lon': 35.52},
    'Mangochi': {'lat': -14.48, 'lon': 35.26},
    'Mchinji': {'lat': -13.80, 'lon': 32.88},
    'Mulanje': {'lat': -16.03, 'lon': 35.50},
    'Mwanza': {'lat': -15.62, 'lon': 34.52},
    'Mzimba': {'lat': -11.90, 'lon': 33.60},
    'Neno': {'lat': -15.40, 'lon': 34.62},
    'Nkhata Bay': {'lat': -11.61, 'lon': 34.30},
    'Nkhotakota': {'lat': -12.93, 'lon': 34.30},
    'Nsanje': {'lat': -16.92, 'lon': 35.26},
    'Ntcheu': {'lat': -14.82, 'lon': 34.63},
    'Ntchisi': {'lat': -13.50, 'lon': 33.90},
    'Phalombe': {'lat': -15.80, 'lon': 35.65},
    'Rumphi': {'lat': -10.88, 'lon': 33.86},
    'Salima': {'lat': -13.78, 'lon': 34.45},
    'Thyolo': {'lat': -16.07, 'lon': 35.14},
    'Zomba': {'lat': -15.38, 'lon': 35.32}
}

# Scoring weights - baseline scenario
WEIGHTS = {
    'hazard': 0.40,
    'exposure': 0.30,
    'adaptive_capacity': 0.30
}

# Hazard component sub-weights (refined methodology)
HAZARD_WEIGHTS = {
    'rainfall_variability': 0.20,
    'drought_frequency': 0.20,
    'flood_risk': 0.25,
    'temperature_extremes': 0.20,
    'cyclone_exposure': 0.15
}

# Exposure component sub-weights (refined methodology)
EXPOSURE_WEIGHTS = {
    'exposed_population': 0.35,
    'agricultural_dependence': 0.35,
    'infrastructure_deficit': 0.20,
    'cropland_exposure': 0.10
}

# Adaptive Capacity component sub-weights (refined methodology)
ADAPTIVE_CAPACITY_WEIGHTS = {
    'poverty_rate': 0.35,        # Inverted: higher poverty = lower capacity
    'education_level': 0.25,     # Higher education = higher capacity
    'service_access': 0.25,      # Higher access = higher capacity
    'local_capacity': 0.15       # Higher capacity = higher capacity
}

# Alternative weighting scenarios for sensitivity analysis
WEIGHTING_SCENARIOS = {
    'baseline': {
        'hazard': 0.40,
        'exposure': 0.30,
        'adaptive_capacity': 0.30
    },
    'hazard_focused': {
        'hazard': 0.50,
        'exposure': 0.25,
        'adaptive_capacity': 0.25
    },
    'equity_focused': {
        'hazard': 0.30,
        'exposure': 0.30,
        'adaptive_capacity': 0.40
    },
    'equal_weights': {
        'hazard': 0.333,
        'exposure': 0.333,
        'adaptive_capacity': 0.334
    }
}

# Climate data parameters
CLIMATE_PARAMS = {
    'start_year': 2000,
    'end_year': 2024,
    'nasa_power_params': [
        'T2M',          # Temperature at 2 meters
        'T2M_MAX',      # Maximum temperature
        'T2M_MIN',      # Minimum temperature
        'PRECTOTCORR'   # Precipitation corrected
    ]
}

# Thresholds for climate extremes
THRESHOLDS = {
    'heat_wave_temp': 35,        # Celsius
    'heavy_rain_percentile': 95,  # 95th percentile
    'drought_spi_threshold': -1.0 # SPI < -1 indicates drought
}

# Normalization parameters
NORMALIZATION = {
    'method': 'robust',  # 'robust' or 'minmax'
    'percentile_low': 5,
    'percentile_high': 95
}

# Data quality thresholds
DATA_QUALITY = {
    'min_completeness': 0.80,  # 80% of data must be present
    'max_missing_years': 3      # Maximum 3 missing years in time series
}
