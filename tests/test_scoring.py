"""
Unit tests for the risk scoring engine
Tests normalization, score calculation, and adaptive capacity inversion
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scoring_engine import RiskScorer, normalize_indicators
from data_processing import robust_normalize, minmax_normalize


class TestNormalization:
    """Test normalization functions"""
    
    def test_robust_normalize(self):
        """Test robust normalization handles outliers correctly"""
        values = np.array([10, 20, 30, 40, 50, 100])  # 100 is outlier
        normalized = robust_normalize(values)
        
        assert len(normalized) == len(values)
        assert normalized.min() >= 0
        assert normalized.max() <= 100
        assert not np.isnan(normalized).any()
    
    def test_minmax_normalize(self):
        """Test min-max normalization"""
        values = np.array([0, 25, 50, 75, 100])
        normalized = minmax_normalize(values)
        
        assert normalized.min() == 0
        assert normalized.max() == 100
        assert normalized[2] == 50  # Middle value
    
    def test_normalize_empty_array(self):
        """Test normalization with empty array"""
        values = np.array([])
        normalized = robust_normalize(values)
        
        assert len(normalized) == 0
    
    def test_normalize_constant_values(self):
        """Test normalization when all values are the same"""
        values = np.array([50, 50, 50, 50])
        normalized = robust_normalize(values)
        
        assert np.all(normalized == 50.0)


class TestRiskScorer:
    """Test risk scoring engine"""
    
    def test_risk_score_bounds(self):
        """Test that risk scores are within 0-100 bounds"""
        scorer = RiskScorer()
        
        risk = scorer.calculate_risk_score(hazard=80, exposure=60, adaptive_capacity=40)
        
        assert 0 <= risk <= 100
    
    def test_adaptive_capacity_inversion(self):
        """Test that higher adaptive capacity reduces risk"""
        scorer = RiskScorer()
        
        # Same hazard and exposure, different adaptive capacity
        risk_high_capacity = scorer.calculate_risk_score(
            hazard=80, 
            exposure=60, 
            adaptive_capacity=80  # High capacity
        )
        risk_low_capacity = scorer.calculate_risk_score(
            hazard=80, 
            exposure=60, 
            adaptive_capacity=20  # Low capacity
        )
        
        # Higher adaptive capacity should result in lower risk
        assert risk_high_capacity < risk_low_capacity
    
    def test_hazard_score_calculation(self):
        """Test hazard component score calculation"""
        scorer = RiskScorer()
        
        indicators = {
            'rainfall_variability': 70,
            'drought_frequency': 60,
            'flood_risk': 80,
            'temperature_extremes': 50,
            'cyclone_exposure': 40
        }
        
        hazard_score = scorer.calculate_hazard_score(indicators)
        
        assert 0 <= hazard_score <= 100
        # Should be weighted average
        expected = (70*0.20 + 60*0.20 + 80*0.25 + 50*0.20 + 40*0.15)
        assert abs(hazard_score - expected) < 0.01
    
    def test_exposure_score_calculation(self):
        """Test exposure component score calculation"""
        scorer = RiskScorer()
        
        indicators = {
            'exposed_population': 60,
            'agricultural_dependence': 75,
            'infrastructure_deficit': 50,
            'cropland_exposure': 40
        }
        
        exposure_score = scorer.calculate_exposure_score(indicators)
        
        assert 0 <= exposure_score <= 100
    
    def test_adaptive_capacity_score_calculation(self):
        """Test adaptive capacity component score calculation"""
        scorer = RiskScorer()
        
        indicators = {
            'poverty_rate': 60,  # High poverty
            'education_level': 70,
            'service_access': 65,
            'local_capacity': 50
        }
        
        capacity_score = scorer.calculate_adaptive_capacity_score(indicators)
        
        assert 0 <= capacity_score <= 100
        # Poverty should be inverted
        # Expected: (100-60)*0.35 + 70*0.25 + 65*0.25 + 50*0.15
        expected = 40*0.35 + 70*0.25 + 65*0.25 + 50*0.15
        assert abs(capacity_score - expected) < 0.01
    
    def test_risk_categorization(self):
        """Test risk category assignment"""
        scorer = RiskScorer()
        
        assert scorer.categorize_risk(80) == 'Very High'
        assert scorer.categorize_risk(65) == 'High'
        assert scorer.categorize_risk(50) == 'Medium'
        assert scorer.categorize_risk(30) == 'Low'
        assert scorer.categorize_risk(15) == 'Very Low'
    
    def test_all_scores_calculation(self):
        """Test complete score calculation"""
        scorer = RiskScorer()
        
        hazard_indicators = {
            'rainfall_variability': 70,
            'drought_frequency': 60,
            'flood_risk': 80,
            'temperature_extremes': 50,
            'cyclone_exposure': 40
        }
        
        exposure_indicators = {
            'exposed_population': 60,
            'agricultural_dependence': 75,
            'infrastructure_deficit': 50,
            'cropland_exposure': 40
        }
        
        adaptive_capacity_indicators = {
            'poverty_rate': 60,
            'education_level': 70,
            'service_access': 65,
            'local_capacity': 50
        }
        
        scores = scorer.calculate_all_scores(
            hazard_indicators,
            exposure_indicators,
            adaptive_capacity_indicators
        )
        
        assert 'hazard' in scores
        assert 'exposure' in scores
        assert 'adaptive_capacity' in scores
        assert 'vulnerability' in scores
        assert 'risk' in scores
        
        # Vulnerability should be inverse of adaptive capacity
        assert scores['vulnerability'] == 100 - scores['adaptive_capacity']
    
    def test_district_ranking(self):
        """Test district ranking functionality"""
        scorer = RiskScorer()
        
        data = pd.DataFrame({
            'district': ['A', 'B', 'C'],
            'risk': [75, 50, 90]
        })
        
        ranked = scorer.rank_districts(data, score_column='risk')
        
        assert ranked.iloc[0]['district'] == 'C'  # Highest risk
        assert ranked.iloc[1]['district'] == 'A'
        assert ranked.iloc[2]['district'] == 'B'  # Lowest risk


class TestSensitivityAnalysis:
    """Test sensitivity analysis functionality"""
    
    def test_sensitivity_analysis_scenarios(self):
        """Test that sensitivity analysis produces results for all scenarios"""
        scorer = RiskScorer()
        
        data = pd.DataFrame({
            'district': ['Nsanje', 'Lilongwe'],
            'hazard': [80, 40],
            'exposure': [70, 50],
            'adaptive_capacity': [30, 70]
        })
        
        scenarios = {
            'baseline': {'hazard': 0.4, 'exposure': 0.3, 'adaptive_capacity': 0.3},
            'hazard_focused': {'hazard': 0.5, 'exposure': 0.25, 'adaptive_capacity': 0.25}
        }
        
        results = scorer.sensitivity_analysis(data, scenarios)
        
        assert len(results) == len(data) * len(scenarios)
        assert 'scenario' in results.columns
        assert 'risk_score' in results.columns


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
