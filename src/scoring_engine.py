"""
Risk scoring engine for climate vulnerability assessment
Implements the IPCC-aligned risk scoring methodology
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import (
    WEIGHTS, HAZARD_WEIGHTS, EXPOSURE_WEIGHTS, 
    ADAPTIVE_CAPACITY_WEIGHTS, WEIGHTING_SCENARIOS
)
from data_processing import robust_normalize


class RiskScorer:
    """
    Climate risk scoring engine implementing IPCC vulnerability framework
    Risk = f(Hazard, Exposure, Adaptive Capacity)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the risk scorer
        
        Args:
            weights: Custom weights for components (default: from config)
        """
        self.weights = weights if weights is not None else WEIGHTS
        self.hazard_weights = HAZARD_WEIGHTS
        self.exposure_weights = EXPOSURE_WEIGHTS
        self.adaptive_capacity_weights = ADAPTIVE_CAPACITY_WEIGHTS
    
    def calculate_hazard_score(self, indicators: Dict[str, float]) -> float:
        """
        Calculate hazard component score
        
        Args:
            indicators: Dictionary with hazard indicators
                - rainfall_variability: CV of annual rainfall
                - drought_frequency: % of time in drought
                - flood_risk: Historical flood events score
                - temperature_extremes: Heat wave days
                - cyclone_exposure: Geographic cyclone risk
        
        Returns:
            Hazard score (0-100, higher = more hazardous)
        """
        score = 0.0
        
        # Rainfall variability
        if 'rainfall_variability' in indicators:
            score += indicators['rainfall_variability'] * self.hazard_weights['rainfall_variability']
        
        # Drought frequency
        if 'drought_frequency' in indicators:
            score += indicators['drought_frequency'] * self.hazard_weights['drought_frequency']
        
        # Flood risk
        if 'flood_risk' in indicators:
            score += indicators['flood_risk'] * self.hazard_weights['flood_risk']
        
        # Temperature extremes
        if 'temperature_extremes' in indicators:
            score += indicators['temperature_extremes'] * self.hazard_weights['temperature_extremes']
        
        return score
    
    def calculate_exposure_score(self, indicators: Dict[str, float]) -> float:
        """
        Calculate exposure component score
        
        Args:
            indicators: Dictionary with exposure indicators
                - exposed_population: Population in hazard zones
                - agricultural_dependence: % dependent on agriculture
                - infrastructure_deficit: Lack of infrastructure (inverted)
                - cropland_exposure: Cropland area at risk
        
        Returns:
            Exposure score (0-100, higher = more exposed)
        """
        score = 0.0
        
        # Exposed population
        if 'exposed_population' in indicators:
            score += indicators['exposed_population'] * self.exposure_weights['exposed_population']
        
        # Agricultural dependence
        if 'agricultural_dependence' in indicators:
            score += indicators['agricultural_dependence'] * self.exposure_weights['agricultural_dependence']
        
        # Infrastructure deficit (inverted - low infrastructure = high exposure)
        if 'infrastructure_deficit' in indicators:
            score += indicators['infrastructure_deficit'] * self.exposure_weights['infrastructure_deficit']
        
        # Cropland exposure
        if 'cropland_exposure' in indicators:
            score += indicators['cropland_exposure'] * self.exposure_weights['cropland_exposure']
        
        return score
    
    def calculate_adaptive_capacity_score(self, indicators: Dict[str, float]) -> float:
        """
        Calculate adaptive capacity component score
        Higher adaptive capacity = lower vulnerability
        
        Args:
            indicators: Dictionary with adaptive capacity indicators
                - poverty_rate: % below poverty line (inverted)
                - education_level: Literacy rate
                - service_access: Access to health/water services
                - local_capacity: Local government capacity
        
        Returns:
            Adaptive capacity score (0-100, higher = better capacity)
        """
        score = 0.0
        
        # Poverty rate (inverted - higher poverty = lower capacity)
        if 'poverty_rate' in indicators:
            inverted_poverty = 100 - indicators['poverty_rate']
            score += inverted_poverty * self.adaptive_capacity_weights['poverty_rate']
        
        # Education level (higher = better capacity)
        if 'education_level' in indicators:
            score += indicators['education_level'] * self.adaptive_capacity_weights['education_level']
        
        # Service access (higher = better capacity)
        if 'service_access' in indicators:
            score += indicators['service_access'] * self.adaptive_capacity_weights['service_access']
        
        # Local capacity (higher = better capacity)
        if 'local_capacity' in indicators:
            score += indicators['local_capacity'] * self.adaptive_capacity_weights['local_capacity']
        
        return score
    
    def calculate_risk_score(self, 
                            hazard: float, 
                            exposure: float, 
                            adaptive_capacity: float) -> float:
        """
        Calculate composite risk score using IPCC AR5 multiplicative framework
        
        IPCC AR5 Framework: Risk = f(Hazard, Exposure, Vulnerability)
        This implementation uses: Risk = Hazard × Exposure × Vulnerability
        
        The multiplicative relationship ensures:
        - If any component is zero, risk is zero (you can't have risk without
          all three components present)
        - High hazard with zero exposure = zero risk (reflects reality)
        - Components interact rather than being independent
        
        Args:
            hazard: Hazard component score (0-100)
            exposure: Exposure component score (0-100)
            adaptive_capacity: Adaptive capacity score (0-100)
        
        Returns:
            Composite risk score (0-100, higher = higher risk)
        """
        # Convert adaptive capacity to vulnerability (inverse relationship)
        vulnerability = 100 - adaptive_capacity
        
        # Normalize components to 0-1 scale for multiplication
        h_norm = hazard / 100.0
        e_norm = exposure / 100.0
        v_norm = vulnerability / 100.0
        
        # IPCC AR5 Multiplicative Model: Risk = H × E × V
        # Using geometric mean to maintain 0-100 scale interpretability
        # Risk = (H × E × V)^(1/3) × 100
        # This preserves the multiplicative interaction while keeping scores interpretable
        raw_product = h_norm * e_norm * v_norm
        
        # Geometric mean normalization: cube root to maintain scale
        # When all components are 100, result is 100
        # When any component is 0, result is 0
        risk_score = (raw_product ** (1/3)) * 100
        
        # Ensure score is within bounds
        risk_score = np.clip(risk_score, 0, 100)
        
        return risk_score
    
    def calculate_all_scores(self, 
                            hazard_indicators: Dict[str, float],
                            exposure_indicators: Dict[str, float],
                            adaptive_capacity_indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate all component and composite scores
        
        Args:
            hazard_indicators: Hazard indicator values
            exposure_indicators: Exposure indicator values
            adaptive_capacity_indicators: Adaptive capacity indicator values
        
        Returns:
            Dictionary with all scores
        """
        hazard_score = self.calculate_hazard_score(hazard_indicators)
        exposure_score = self.calculate_exposure_score(exposure_indicators)
        adaptive_capacity_score = self.calculate_adaptive_capacity_score(adaptive_capacity_indicators)
        risk_score = self.calculate_risk_score(hazard_score, exposure_score, adaptive_capacity_score)
        
        return {
            'hazard': hazard_score,
            'exposure': exposure_score,
            'adaptive_capacity': adaptive_capacity_score,
            'vulnerability': 100 - adaptive_capacity_score,
            'risk': risk_score
        }
    
    def sensitivity_analysis(self, 
                            data: pd.DataFrame,
                            scenarios: Dict[str, Dict] = None) -> pd.DataFrame:
        """
        Perform sensitivity analysis with different weighting schemes
        
        Args:
            data: DataFrame with all indicators and scores
            scenarios: Dictionary of weighting scenarios (default: from config)
        
        Returns:
            DataFrame with risk scores for each scenario
        """
        if scenarios is None:
            scenarios = WEIGHTING_SCENARIOS
        
        results = []
        
        for scenario_name, scenario_weights in scenarios.items():
            # Create scorer with scenario weights
            scorer = RiskScorer(weights=scenario_weights)
            
            # Calculate risk scores for each district
            for _, row in data.iterrows():
                risk_score = scorer.calculate_risk_score(
                    hazard=row['hazard'],
                    exposure=row['exposure'],
                    adaptive_capacity=row['adaptive_capacity']
                )
                
                results.append({
                    'district': row['district'],
                    'scenario': scenario_name,
                    'risk_score': risk_score
                })
        
        return pd.DataFrame(results)
    
    def rank_districts(self, data: pd.DataFrame, 
                      score_column: str = 'risk') -> pd.DataFrame:
        """
        Rank districts by risk score
        
        Args:
            data: DataFrame with district scores
            score_column: Column to rank by
        
        Returns:
            DataFrame sorted by rank
        """
        ranked = data.copy()
        ranked['rank'] = ranked[score_column].rank(ascending=False, method='min')
        ranked = ranked.sort_values('rank')
        
        return ranked
    
    def categorize_risk(self, risk_score: float) -> str:
        """
        Categorize risk score into risk levels
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            Risk category string
        """
        if risk_score >= 75:
            return 'Very High'
        elif risk_score >= 60:
            return 'High'
        elif risk_score >= 40:
            return 'Medium'
        elif risk_score >= 25:
            return 'Low'
        else:
            return 'Very Low'


def normalize_indicators(data: pd.DataFrame, 
                        indicator_columns: List[str],
                        method: str = 'robust') -> pd.DataFrame:
    """
    Normalize all indicators to 0-100 scale
    
    Args:
        data: DataFrame with raw indicators
        indicator_columns: List of columns to normalize
        method: Normalization method ('robust' or 'minmax')
    
    Returns:
        DataFrame with normalized indicators
    """
    normalized_data = data.copy()
    
    for col in indicator_columns:
        if col in data.columns:
            values = data[col].values
            
            if method == 'robust':
                normalized_values = robust_normalize(values)
            else:
                # Min-max normalization
                min_val = values.min()
                max_val = values.max()
                if max_val > min_val:
                    normalized_values = ((values - min_val) / (max_val - min_val)) * 100
                else:
                    normalized_values = np.full_like(values, 50.0)
            
            normalized_data[col] = normalized_values
    
    return normalized_data


def calculate_district_scores(data: pd.DataFrame,
                             hazard_cols: List[str],
                             exposure_cols: List[str],
                             adaptive_capacity_cols: List[str]) -> pd.DataFrame:
    """
    Calculate risk scores for all districts
    
    Args:
        data: DataFrame with normalized indicators
        hazard_cols: List of hazard indicator columns
        exposure_cols: List of exposure indicator columns
        adaptive_capacity_cols: List of adaptive capacity indicator columns
    
    Returns:
        DataFrame with all scores
    """
    scorer = RiskScorer()
    results = []
    
    for _, row in data.iterrows():
        # Extract indicators
        hazard_indicators = {col: row[col] for col in hazard_cols if col in row}
        exposure_indicators = {col: row[col] for col in exposure_cols if col in row}
        adaptive_capacity_indicators = {col: row[col] for col in adaptive_capacity_cols if col in row}
        
        # Calculate scores
        scores = scorer.calculate_all_scores(
            hazard_indicators,
            exposure_indicators,
            adaptive_capacity_indicators
        )
        
        # Add district name
        scores['district'] = row['district']
        
        # Add risk category
        scores['risk_category'] = scorer.categorize_risk(scores['risk'])
        
        results.append(scores)
    
    return pd.DataFrame(results)
