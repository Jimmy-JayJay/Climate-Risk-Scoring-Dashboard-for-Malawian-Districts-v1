"""
Data processing and indicator calculation functions
Handles data cleaning, normalization, and climate indicator computation
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
from config import NORMALIZATION, THRESHOLDS


def robust_normalize(values: np.ndarray, 
                     percentile_low: int = 5, 
                     percentile_high: int = 95) -> np.ndarray:
    """
    Normalize values using robust percentile-based method to handle outliers
    
    Args:
        values: Array of values to normalize
        percentile_low: Lower percentile for normalization (default: 5)
        percentile_high: Upper percentile for normalization (default: 95)
    
    Returns:
        Normalized values on 0-100 scale
    """
    if len(values) == 0:
        return np.array([])
    
    p_low = np.percentile(values, percentile_low)
    p_high = np.percentile(values, percentile_high)
    
    # Avoid division by zero
    if p_high == p_low:
        return np.full_like(values, 50.0)
    
    normalized = ((values - p_low) / (p_high - p_low)) * 100
    normalized = np.clip(normalized, 0, 100)
    
    return normalized


def minmax_normalize(values: np.ndarray) -> np.ndarray:
    """
    Standard min-max normalization to 0-100 scale
    
    Args:
        values: Array of values to normalize
    
    Returns:
        Normalized values on 0-100 scale
    """
    if len(values) == 0:
        return np.array([])
    
    min_val = np.min(values)
    max_val = np.max(values)
    
    if max_val == min_val:
        return np.full_like(values, 50.0)
    
    normalized = ((values - min_val) / (max_val - min_val)) * 100
    
    return normalized


def calculate_rainfall_cv(rainfall_data: pd.DataFrame, 
                          district: str) -> float:
    """
    Calculate coefficient of variation for annual rainfall
    Higher CV indicates more variability (higher risk)
    
    Args:
        rainfall_data: DataFrame with columns ['district', 'year', 'rainfall']
        district: District name
    
    Returns:
        Coefficient of variation (percentage)
    """
    district_data = rainfall_data[rainfall_data['district'] == district]
    
    if len(district_data) == 0:
        return np.nan
    
    annual_rainfall = district_data.groupby('year')['rainfall'].sum()
    
    if len(annual_rainfall) < 2:
        return np.nan
    
    mean_rainfall = annual_rainfall.mean()
    std_rainfall = annual_rainfall.std()
    
    if mean_rainfall == 0:
        return np.nan
    
    cv = (std_rainfall / mean_rainfall) * 100
    
    return cv


def calculate_spi(rainfall_data: pd.Series, 
                  timescale: int = 3) -> pd.Series:
    """
    Calculate Standardized Precipitation Index (SPI)
    SPI < -1 indicates drought conditions
    
    Args:
        rainfall_data: Series of rainfall values
        timescale: Number of months for accumulation (default: 3)
    
    Returns:
        Series of SPI values
    """
    # Calculate rolling sum for the specified timescale
    rolling_sum = rainfall_data.rolling(window=timescale, min_periods=timescale).sum()
    
    # Standardize (z-score)
    spi = (rolling_sum - rolling_sum.mean()) / rolling_sum.std()
    
    return spi


def calculate_drought_frequency(rainfall_data: pd.DataFrame, 
                                district: str,
                                threshold: float = -1.0) -> float:
    """
    Calculate frequency of drought events based on SPI
    
    Args:
        rainfall_data: DataFrame with rainfall data
        district: District name
        threshold: SPI threshold for drought (default: -1.0)
    
    Returns:
        Percentage of time in drought conditions
    """
    district_data = rainfall_data[rainfall_data['district'] == district].copy()
    
    if len(district_data) == 0:
        return np.nan
    
    # Calculate SPI
    district_data['spi'] = calculate_spi(district_data['rainfall'])
    
    # Count drought months
    drought_months = (district_data['spi'] < threshold).sum()
    total_months = len(district_data.dropna(subset=['spi']))
    
    if total_months == 0:
        return np.nan
    
    drought_frequency = (drought_months / total_months) * 100
    
    return drought_frequency


def calculate_heat_days(temperature_data: pd.DataFrame,
                       district: str,
                       threshold: float = 35) -> int:
    """
    Calculate number of days exceeding heat threshold
    
    Args:
        temperature_data: DataFrame with columns ['district', 'date', 'temperature']
        district: District name
        threshold: Temperature threshold in Celsius (default: 35)
    
    Returns:
        Number of heat wave days
    """
    district_data = temperature_data[temperature_data['district'] == district]
    
    if len(district_data) == 0:
        return 0
    
    heat_days = (district_data['temperature'] > threshold).sum()
    
    return heat_days


def calculate_temperature_trend(temperature_data: pd.DataFrame,
                               district: str) -> float:
    """
    Calculate temperature trend (rate of warming) using linear regression
    
    Args:
        temperature_data: DataFrame with columns ['district', 'year', 'temperature']
        district: District name
    
    Returns:
        Temperature trend (degrees per year)
    """
    district_data = temperature_data[temperature_data['district'] == district]
    
    if len(district_data) < 2:
        return np.nan
    
    annual_temp = district_data.groupby('year')['temperature'].mean()
    
    if len(annual_temp) < 2:
        return np.nan
    
    years = annual_temp.index.values
    temps = annual_temp.values
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, temps)
    
    return slope


def calculate_extreme_rainfall_frequency(rainfall_data: pd.DataFrame,
                                        district: str,
                                        percentile: int = 95) -> float:
    """
    Calculate frequency of extreme rainfall events
    
    Args:
        rainfall_data: DataFrame with rainfall data
        district: District name
        percentile: Percentile threshold for extreme events (default: 95)
    
    Returns:
        Percentage of days with extreme rainfall
    """
    district_data = rainfall_data[rainfall_data['district'] == district]
    
    if len(district_data) == 0:
        return np.nan
    
    threshold = np.percentile(district_data['rainfall'], percentile)
    extreme_days = (district_data['rainfall'] > threshold).sum()
    total_days = len(district_data)
    
    if total_days == 0:
        return np.nan
    
    extreme_frequency = (extreme_days / total_days) * 100
    
    return extreme_frequency


def standardize_district_names(df: pd.DataFrame, 
                               name_column: str = 'district') -> pd.DataFrame:
    """
    Standardize district names to match master list
    
    Args:
        df: DataFrame with district names
        name_column: Name of the column containing district names
    
    Returns:
        DataFrame with standardized district names
    """
    # Common name variations
    name_mapping = {
        'Nkhata-Bay': 'Nkhata Bay',
        'Nkhatabay': 'Nkhata Bay',
        'Likoma Island': 'Likoma',
        'Mzimba North': 'Mzimba',
        'Mzimba South': 'Mzimba'
    }
    
    df[name_column] = df[name_column].str.strip()
    df[name_column] = df[name_column].replace(name_mapping)
    
    return df


def assess_data_quality(data: pd.DataFrame,
                       required_columns: List[str],
                       min_completeness: float = 0.80) -> Dict[str, any]:
    """
    Assess data quality and completeness
    
    Args:
        data: DataFrame to assess
        required_columns: List of required column names
        min_completeness: Minimum acceptable completeness ratio
    
    Returns:
        Dictionary with quality metrics
    """
    quality_report = {
        'total_rows': len(data),
        'missing_columns': [],
        'completeness': {},
        'overall_quality': 0,
        'passes_threshold': False
    }
    
    # Check for missing columns
    for col in required_columns:
        if col not in data.columns:
            quality_report['missing_columns'].append(col)
    
    # Calculate completeness for each column
    for col in data.columns:
        completeness = 1 - (data[col].isna().sum() / len(data))
        quality_report['completeness'][col] = completeness
    
    # Overall quality score
    if len(quality_report['completeness']) > 0:
        quality_report['overall_quality'] = np.mean(list(quality_report['completeness'].values()))
    
    quality_report['passes_threshold'] = quality_report['overall_quality'] >= min_completeness
    
    return quality_report


def aggregate_to_annual(data: pd.DataFrame,
                       date_column: str,
                       value_column: str,
                       aggregation: str = 'mean') -> pd.DataFrame:
    """
    Aggregate daily/monthly data to annual values
    
    Args:
        data: DataFrame with time series data
        date_column: Name of date column
        value_column: Name of value column to aggregate
        aggregation: Aggregation method ('mean', 'sum', 'max', 'min')
    
    Returns:
        DataFrame with annual aggregated values
    """
    data = data.copy()
    data[date_column] = pd.to_datetime(data[date_column])
    data['year'] = data[date_column].dt.year
    
    agg_functions = {
        'mean': 'mean',
        'sum': 'sum',
        'max': 'max',
        'min': 'min'
    }
    
    if aggregation not in agg_functions:
        raise ValueError(f"Aggregation method must be one of {list(agg_functions.keys())}")
    
    annual_data = data.groupby('year')[value_column].agg(agg_functions[aggregation]).reset_index()
    
    return annual_data
