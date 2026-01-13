# Climate Risk Scoring Methodology

## Overview

This document provides a comprehensive explanation of the climate risk scoring methodology used in the Climate Risk Scoring Dashboard for Malawian Districts. The methodology is strictly aligned with the **IPCC AR5 vulnerability framework** and implements a transparent, reproducible approach to assessing climate risk at the district level.

---

## Conceptual Framework

### IPCC AR5 Vulnerability Framework

The methodology follows the Intergovernmental Panel on Climate Change (IPCC) Fifth Assessment Report (AR5) definition of risk, which emphasizes the interaction of three distinct components:

```
Risk = f(Hazard, Exposure, Vulnerability)
```

**Definitions:**

- **Hazard**: The potential occurrence of climate-related physical events (e.g., floods, droughts).
- **Exposure**: The presence of people, livelihoods, infrastructure, or assets in places that could be adversely affected.
- **Vulnerability**: The propensity or predisposition to be adversely affected (approximated here as _100 - Adaptive Capacity_).

---

## Composite Risk Score Formula

### Multiplicative Risk Model

This dashboard calculates the final risk score using a **geometric mean** of the three components. This is a critical methodological choice that reflects the physical reality of risk.

```
Risk Score = ∛(Hazard × Exposure × Vulnerability)

Where:
  Vulnerability = 100 - Adaptive Capacity
  All scores are normalized to a 0-100 scale
```

### Why Multiplicative?

1.  **Zero-Handling**: If any component is zero, the total risk is zero.
    - _Example:_ A desert with high heat hazard but zero population (Exposure) has zero human risk.
    - _Example:_ A city with high exposure but zero hazard occurrence has zero risk.
2.  **Interaction Effects**: High hazard combined with high exposure creates disproportionately higher risk than their sum would suggest.
3.  **IPCC Alignment**: Strictly adheres to the conceptual framework where risk is the intersection of H, E, and V.

---

## Component Scoring

Each component is calculated as a weighted composite of its sub-indicators.

### 1. Hazard Component

aggregated from four key climate hazards:

| Sub-indicator            | Weight | Description                                             | Data Source         |
| :----------------------- | :----- | :------------------------------------------------------ | :------------------ |
| **Rainfall Variability** | 25%    | Coefficient of Variation (CV) of annual rainfall        | NASA POWER / CHIRPS |
| **Drought Frequency**    | 25%    | % of months with SPI < -1.0                             | CHIRPS              |
| **Flood Risk**           | 25%    | Frequency of extreme rainfall events (>95th percentile) | NASA POWER          |
| **Heat Stress**          | 25%    | Frequency of days with Tmax > 35°C                      | NASA POWER          |

_Note: The breakdown uses equal weighting (25%) to avoid overfitting to specific hazard types in the absence of granular hyper-local loss data._

---

### 2. Exposure Component

Measures who and what is in harm's way:

| Sub-indicator          | Weight | Description                                   | Data Source      |
| :--------------------- | :----- | :-------------------------------------------- | :--------------- |
| **Exposed Population** | 35%    | Population density in the district            | WorldPop         |
| **Agri. Dependence**   | 35%    | % Population dependent on subsistence farming | World Bank / NSO |
| **Infrastructure Gap** | 20%    | Inverse of road & facility density            | OpenStreetMap    |
| **Cropland Density**   | 10%    | Cropland area per capita                      | FAO / Land Cover |

---

### 3. Vulnerability (Adaptive Capacity) Component

Measures the systemic fragility or lack of coping capacity.
_Calculated as (100 - Adaptive Capacity)._

| Sub-indicator      | Weight | Description                                | Data Source         |
| :----------------- | :----- | :----------------------------------------- | :------------------ |
| **Poverty Rate**   | 35%    | % Population below poverty line (Inverted) | World Bank / NSO    |
| **Education**      | 25%    | Adult literacy rate                        | NSO                 |
| **Service Access** | 25%    | Access to improved water & sanitation      | UNICEF / WHO        |
| **Local Capacity** | 15%    | Fiscal/Institutional capacity proxy        | Ministry of Finance |

---

## Normalization Procedure

All raw indicators are normalized to a **0-100 scale** to ensure comparability across different units (e.g., mm of rain vs. % poverty).

### Robust Percentile Clipping (5th-95th)

Instead of standard Min-Max normalization, we use **robust clipping**:

```python
normalized = ((value - p5) / (p95 - p5)) * 100
constrained = clip(normalized, 0, 100)
```

**Why?**
Climate and socioeconomic data often contains extreme outliers (e.g., a massive flood event in one year). Standard min-max normalization would compress the variance for all other districts. Robust clipping ensures the distribution remains meaningful for the majority of cases.

---

## Risk Categorization

| Score Range  | Category  | Action Level                            |
| :----------- | :-------- | :-------------------------------------- |
| **75 - 100** | Very High | Urgent Priority for Adaptation Finance  |
| **60 - 74**  | High      | Significant Intervention Required       |
| **40 - 59**  | Medium    | Periodic Monitoring & Capacity Building |
| **25 - 39**  | Low       | Standard Development Planning           |
| **0 - 24**   | Very Low  | Minimal Climate-Specific Risk           |

---

## Data Sources Summary

| Data Type             | Source           | Resolution           | Update Frequency            |
| :-------------------- | :--------------- | :------------------- | :-------------------------- |
| **Meteorological**    | NASA POWER API   | Daily (0.5° grid)    | Real-time (Latency ~2 days) |
| **Rainfall Historic** | CHIRPS           | Monthly (0.05° grid) | Monthly                     |
| **Population**        | WorldPop         | 100m Grid            | Annual                      |
| **Socioeconomic**     | World Bank / NSO | District Level       | Annual / Periodic Surveys   |
| **Boundaries**        | GADM v4.1        | Admin Level 1        | Static                      |

---

## Limitations

1.  **Proxy Indicators**: Flood risk is modeled via extreme rainfall probability, not hydraulic flow modeling.
2.  **Resolution**: District-level aggregation may mask village-level hotspots.
3.  **Data Gaps**: Socioeconomic data relies on periodic census/survey intervals (3-5 years).

---

## Contact & Citation

**Developer:** Jimmy Matewere
**Repository:** [GitHub](https://github.com/Jimmy-JayJay/Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1)

_Please cite as:_

> "Climate Risk Scoring Dashboard for Malawian Districts (2026). Developed using IPCC AR5 multiplicative vulnerability framework."
