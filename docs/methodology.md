# Climate Risk Scoring Methodology

## Overview

This document provides a comprehensive explanation of the climate risk scoring methodology used in the Climate Risk Scoring Dashboard for Malawian Districts. The methodology is based on the IPCC AR5 vulnerability framework and implements a transparent, reproducible approach to assessing climate risk at the district level.

---

## Conceptual Framework

### IPCC AR5 Vulnerability Framework

The methodology follows the Intergovernmental Panel on Climate Change (IPCC) Fifth Assessment Report (AR5) definition of risk:

```
Risk = f(Hazard, Exposure, Vulnerability)

Where: Vulnerability = f(Sensitivity, Adaptive Capacity)
```

For this dashboard, we simplify to:

```
Risk = f(Hazard, Exposure, Adaptive Capacity)
```

**Definitions:**

- **Hazard**: The potential occurrence of climate-related physical events that may cause adverse effects
- **Exposure**: The presence of people, livelihoods, infrastructure, or assets in places that could be adversely affected
- **Adaptive Capacity**: The ability of systems, institutions, humans, and other organisms to adjust to potential damage, to take advantage of opportunities, or to respond to consequences
- **Vulnerability**: The propensity or predisposition to be adversely affected (inverse of adaptive capacity)

---

## Composite Risk Score Formula

### Main Formula

```
Risk Score = (Hazard × 0.40) + (Exposure × 0.30) + (Vulnerability × 0.30)

Where:
  Vulnerability = 100 - Adaptive Capacity
  All scores are on a 0-100 scale
```

### Rationale for Weights

- **Hazard (40%)**: Climate hazards are the primary driver of risk and are increasing due to climate change
- **Exposure (30%)**: Exposure determines who and what is at risk
- **Adaptive Capacity (30%)**: Capacity to adapt can significantly reduce risk even with high hazards

These weights are based on:

1. IPCC AR5 framework recommendations
2. Literature review of vulnerability assessments in Sub-Saharan Africa
3. Expert consultation with climate scientists and policymakers

---

## Component Scoring

### 1. Hazard Component (40% weight)

The hazard component aggregates five climate-related hazards relevant to Malawi:

```
Hazard Score = (RV × 0.20) + (DF × 0.20) + (FR × 0.25) + (TE × 0.20) + (CE × 0.15)

Where:
  RV = Rainfall Variability
  DF = Drought Frequency
  FR = Flood Risk
  TE = Temperature Extremes
  CE = Cyclone Exposure
```

#### 1.1 Rainfall Variability (20%)

**Indicator**: Coefficient of Variation (CV) of annual rainfall

**Calculation**:

```python
CV = (σ / μ) × 100

Where:
  σ = Standard deviation of annual rainfall (2000-2024)
  μ = Mean annual rainfall (2000-2024)
```

**Data Source**: NASA POWER API, CHIRPS

**Interpretation**: Higher CV indicates more unpredictable rainfall, increasing agricultural risk

#### 1.2 Drought Frequency (20%)

**Indicator**: Percentage of time in drought conditions

**Calculation**:

```python
Drought Frequency = (Months with SPI < -1.0) / (Total Months) × 100

Where:
  SPI = Standardized Precipitation Index (3-month accumulation)
```

**Data Source**: CHIRPS rainfall data

**Interpretation**: Higher frequency indicates more persistent drought conditions

#### 1.3 Flood Risk (25%)

**Indicator**: Historical flood event frequency and severity

**Calculation**:

```python
Flood Risk = Normalized(Event Count × Severity Weight)

Severity Weights:
  - High severity: 3.0
  - Medium severity: 2.0
  - Low severity: 1.0
```

**Data Source**: EM-DAT International Disaster Database, Dartmouth Flood Observatory

**Interpretation**: Districts with more frequent and severe floods score higher

#### 1.4 Temperature Extremes (20%)

**Indicator**: Number of heat wave days (temperature > 35°C)

**Calculation**:

```python
Heat Days = Count(Daily Tmax > 35°C) over 2000-2024
```

**Data Source**: NASA POWER API

**Interpretation**: More heat days indicate higher heat stress risk for humans and crops

#### 1.5 Cyclone Exposure (15%)

**Indicator**: Geographic exposure to tropical cyclones

**Calculation**:

```python
Cyclone Exposure = f(Latitude, Distance to Coast)

Scoring:
  - Latitude < -15.5° (Very South): 85
  - Latitude -15.5° to -14.5° (South): 60
  - Latitude -14.5° to -13.0° (Central): 30
  - Latitude > -13.0° (North): 10
```

**Data Source**: Geographic coordinates, historical cyclone tracks

**Interpretation**: Southern districts closer to Mozambique coast have higher exposure

---

### 2. Exposure Component (30% weight)

The exposure component measures the extent to which people and assets are exposed to climate hazards:

```
Exposure Score = (EP × 0.35) + (AD × 0.35) + (ID × 0.20) + (CE × 0.10)

Where:
  EP = Exposed Population
  AD = Agricultural Dependence
  ID = Infrastructure Deficit
  CE = Cropland Exposure
```

#### 2.1 Exposed Population (35%)

**Indicator**: Population density in hazard-prone areas

**Calculation**:

```python
Exposed Population = Normalized(Population Density)
```

**Data Source**: WorldPop, Malawi Population Census 2018

**Interpretation**: Higher density means more people exposed to climate hazards

#### 2.2 Agricultural Dependence (35%)

**Indicator**: Percentage of population dependent on agriculture

**Calculation**:

```python
Agricultural Dependence = (Agricultural Population / Total Population) × 100
```

**Data Source**: Malawi NSO Integrated Household Survey, World Bank

**Interpretation**: Higher dependence increases vulnerability to climate-related crop failures

#### 2.3 Infrastructure Deficit (20%)

**Indicator**: Lack of climate-resilient infrastructure (inverted)

**Calculation**:

```python
Infrastructure Deficit = 100 - Normalized(Road Density + Health Facility Density)
```

**Data Source**: OpenStreetMap, Malawi NSO

**Interpretation**: Lower infrastructure means less capacity to respond to disasters

#### 2.4 Cropland Exposure (10%)

**Indicator**: Cropland area per capita

**Calculation**:

```python
Cropland Exposure = Normalized(Cropland Area / Population)
```

**Data Source**: FAO, Malawi Ministry of Agriculture

**Interpretation**: More cropland per capita increases exposure to agricultural losses

---

### 3. Adaptive Capacity Component (30% weight)

The adaptive capacity component measures the ability to cope with and adapt to climate risks:

```
Adaptive Capacity = ((100 - PR) × 0.35) + (EL × 0.25) + (SA × 0.25) + (LC × 0.15)

Where:
  PR = Poverty Rate (inverted)
  EL = Education Level
  SA = Service Access
  LC = Local Capacity
```

**Note**: Higher adaptive capacity leads to LOWER vulnerability and thus LOWER risk.

#### 3.1 Poverty Rate (35%, inverted)

**Indicator**: Percentage of population below poverty line

**Calculation**:

```python
Poverty Component = (100 - Poverty Rate) × 0.35
```

**Data Source**: Malawi NSO Integrated Household Survey

**Interpretation**: Higher poverty reduces capacity to adapt (inverted in formula)

#### 3.2 Education Level (25%)

**Indicator**: Literacy rate

**Calculation**:

```python
Education Level = Literacy Rate (%)
```

**Data Source**: Malawi NSO Education Statistics

**Interpretation**: Higher education enables better understanding and adoption of adaptation strategies

#### 3.3 Service Access (25%)

**Indicator**: Average access to health and water services

**Calculation**:

```python
Service Access = (Health Facility Access + Clean Water Access) / 2
```

**Data Source**: Malawi NSO, UNICEF/WHO

**Interpretation**: Better service access improves resilience and recovery capacity

#### 3.4 Local Capacity (15%)

**Indicator**: Proxy for local government and community capacity

**Calculation**:

```python
Local Capacity = f(District Budget per Capita, Climate Finance Received)
```

**Data Source**: Malawi Ministry of Finance, Climate finance databases

**Interpretation**: Higher local capacity enables better planning and implementation of adaptation

---

## Normalization Procedure

All indicators are normalized to a 0-100 scale to ensure comparability.

### Robust Normalization (Default Method)

```python
def robust_normalize(values):
    p5 = percentile(values, 5)
    p95 = percentile(values, 95)

    normalized = ((values - p5) / (p95 - p5)) × 100
    normalized = clip(normalized, 0, 100)

    return normalized
```

**Advantages**:

- Handles outliers effectively
- More stable than min-max normalization
- Reduces impact of extreme values

**Alternative**: Min-max normalization available for comparison

---

## Sensitivity Analysis

To test the robustness of the risk scores, we implement sensitivity analysis with four weighting scenarios:

### Scenario 1: Baseline (Default)

- Hazard: 40%
- Exposure: 30%
- Adaptive Capacity: 30%

### Scenario 2: Hazard-Focused

- Hazard: 50%
- Exposure: 25%
- Adaptive Capacity: 25%

### Scenario 3: Equity-Focused

- Hazard: 30%
- Exposure: 30%
- Adaptive Capacity: 40%

### Scenario 4: Equal Weights

- Hazard: 33.3%
- Exposure: 33.3%
- Adaptive Capacity: 33.3%

**Analysis**: Districts that rank in the top 10 across all scenarios are considered robustly high-risk.

---

## Risk Categorization

Risk scores are categorized into five levels:

| Category  | Score Range | Color Code  | Interpretation                      |
| --------- | ----------- | ----------- | ----------------------------------- |
| Very High | 75-100      | Red         | Immediate intervention needed       |
| High      | 60-74       | Orange      | Priority for adaptation investments |
| Medium    | 40-59       | Yellow      | Moderate attention required         |
| Low       | 25-39       | Light Green | Lower priority                      |
| Very Low  | 0-24        | Dark Green  | Minimal climate risk                |

---

## Data Sources Summary

| Data Type      | Source         | Years     | Resolution      | Access              |
| -------------- | -------------- | --------- | --------------- | ------------------- |
| Temperature    | NASA POWER     | 2000-2024 | 0.5° × 0.625°   | Free API            |
| Rainfall       | CHIRPS         | 1981-2024 | 0.05° (~5km)    | Free download       |
| Population     | WorldPop       | 2020      | 100m            | Free download       |
| Boundaries     | GADM v4.1      | 2024      | District level  | Free download       |
| Poverty        | Malawi NSO IHS | 2019-2020 | District level  | Public reports      |
| Education      | Malawi NSO     | 2018      | District level  | Public reports      |
| Disasters      | EM-DAT         | 1900-2024 | Event level     | Free (registration) |
| Infrastructure | OpenStreetMap  | Current   | Point/line data | Free API            |

---

## Validation Approach

### Face Validity

- Compare results with known high-risk districts (e.g., Nsanje, Chikwawa)
- Verify that flood-prone areas score high on flood risk
- Check that urban areas have higher adaptive capacity

### Expert Validation

- Review by climate scientists (DCCMS, LUANAR)
- Feedback from NGOs working in climate adaptation
- Consultation with district-level officials

### Cross-Validation

- Compare with INFORM Risk Index (if available)
- Compare with ND-GAIN vulnerability scores
- Compare with MVAC vulnerability classifications

### Statistical Validation

- Spearman rank correlation with existing indices (target: >0.6)
- Sensitivity analysis (rank stability across scenarios)
- Uncertainty quantification (confidence intervals)

---

## Limitations and Caveats

### Data Limitations

1. **Temporal Mismatch**: Different indicators from different years (2018-2024)
2. **Spatial Resolution**: Some data aggregated from gridded to district level
3. **Data Gaps**: Some districts have incomplete socioeconomic data
4. **Proxy Indicators**: Local capacity uses proxy measures

### Methodological Limitations

1. **Additive Model**: Assumes components are independent (alternative: multiplicative)
2. **Static Weights**: Weights don't change over time or by context
3. **Historical Bias**: Based on past data, may not capture future risks
4. **Aggregation**: District-level masks within-district variation

### Scope Limitations

1. **Climate Hazards Only**: Doesn't include non-climate risks (conflict, disease)
2. **No Future Projections**: Based on historical data, not climate models
3. **Malawi-Specific**: Weights may not apply to other countries
4. **District Level**: Not suitable for sub-district planning

---

## Uncertainty Quantification

### Data Quality Scores

Each district receives a data quality score (0-100) based on:

- Completeness of data (% of indicators available)
- Recency of data (years since collection)
- Source reliability (primary vs. secondary sources)

### Confidence Intervals

Monte Carlo simulation (1000 iterations) varying:

- Indicator weights (±10%)
- Normalization parameters (±5%)

Results reported as: **Risk Score ± Standard Deviation**

---

## Reproducibility

All code and data are available in the project repository:

- `src/scoring_engine.py` - Risk calculation implementation
- `src/config.py` - All weights and parameters
- `tests/test_scoring.py` - Validation tests
- `notebooks/` - Step-by-step calculations

To reproduce results:

```bash
git clone https://github.com/yourusername/climate-risk-malawi.git
cd climate-risk-malawi
pip install -r requirements.txt
streamlit run src/app.py
```

---

## References

1. IPCC (2014). Climate Change 2014: Impacts, Adaptation, and Vulnerability. Fifth Assessment Report.

2. Brooks, N., Adger, W. N., & Kelly, P. M. (2005). The determinants of vulnerability and adaptive capacity at the national level and the implications for adaptation. Global Environmental Change, 15(2), 151-163.

3. Füssel, H. M., & Klein, R. J. (2006). Climate change vulnerability assessments: an evolution of conceptual thinking. Climatic Change, 75(3), 301-329.

4. Government of Malawi (2020). Malawi Integrated Household Survey 2019-2020. National Statistical Office.

5. NASA POWER Project (2024). Prediction of Worldwide Energy Resources. https://power.larc.nasa.gov/

6. Funk, C., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. Scientific Data, 2, 150066.

---

## Version History

- **v1.0** (January 2026): Initial MVP with 3 districts
- **v2.0** (Planned): Full implementation with all 28 districts

---

## Contact

For questions about this methodology:

- **Technical**: Review code in `src/scoring_engine.py`
- **Conceptual**: See IPCC AR5 Chapter 19
- **Data**: Refer to data sources table above

---

**Last Updated**: January 9, 2026
