# Climate Risk Scoring Dashboard for Malawian Districts

🔗 **[Live Dashboard]([https://malawi-climate-risk-dashboard.streamlit.app/])** | [Methodology](src/app.py)

A data-driven dashboard for assessing climate resilience across Malawi's 28 districts. This tool integrates NASA POWER climate data, World Bank socioeconomic indicators, and geospatial analysis to calculate risk scores aligned with the IPCC AR5 vulnerability framework.

## Project Overview

Malawi faces escalating climate risks from floods, droughts, and extreme weather events. Climate adaptation funding often relies on outdated vulnerability assessments that fail to capture current conditions.

This dashboard addresses that gap by providing:

- **Automated risk assessment** across all 28 Malawian districts
- **Scientific methodology** implementing the IPCC AR5 vulnerability framework
- **Real-time data integration** from NASA satellite observations and World Bank indicators
- **Interactive visualization** enabling policymakers to identify high-risk districts and understand why they're vulnerable

Built for policymakers, NGOs, researchers, and climate practitioners working on adaptation planning in Malawi.

## Key Features

- **Satellite-Derived Climate Data**: Uses NASA POWER API for daily temperature and rainfall data (2020-2024).
- **Socioeconomic Context**: Integrates official World Bank development indicators (Poverty, Literacy, etc.).
- **Geospatial Precision**: Uses GADM Level 1 administrative boundaries and WorldPop population data.
- **IPCC Aligned**: Risk scoring methodology aligned with the IPCC AR5 framework.
- **Interactive Visualization**: Filter by risk components and drill down into specific districts.

## Methodology

This dashboard implements the **IPCC AR5 Multiplicative Risk Framework**:

```
Risk Score = ∛(Hazard × Exposure × Vulnerability)
```

**Why multiplicative?**

- If any component is zero, risk is zero (you cannot have risk without hazard, exposure, AND vulnerability).
- Components interact (high hazard + high exposure creates disproportionate risk).
- Reflects physical reality of climate risk.

**Components:**

- **Hazard:** Rainfall variability, drought frequency, flood risk, heat extremes (25% each).
- **Exposure:** Population density (35%), agricultural dependence (35%), infrastructure deficit (20%), cropland exposure (10%).
- **Vulnerability:** Poverty rate (35%), education levels (25%), access to services (25%), local capacity (15%).

All indicators are normalized to a 0-100 scale using robust percentile clipping (5th-95th) to handle outliers.

## Risk Categories

- **Very High (75-100)**: Immediate adaptation priority
- **High (60-74)**: Significant intervention needed
- **Medium (40-59)**: Moderate risk, monitoring required
- **Low (25-39)**: Below-average risk
- **Very Low (0-24)**: Minimal climate risk

## Data Sources

| Component         | Source     | Details                                        |
| ----------------- | ---------- | ---------------------------------------------- |
| **Climate**       | NASA POWER | Daily temperature & rainfall (2020-2024)       |
| **Socioeconomic** | World Bank | Poverty, Literacy, Ag Dependency, Water Access |
| **Population**    | WorldPop   | 2020 UN-adjusted population counts             |
| **Boundaries**    | GADM v4.1  | Official administrative boundaries             |

## Prerequisites

- Python 3.8 or higher
- Git
- 2GB available disk space

## Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Jimmy-JayJay/Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1.git
   cd Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1
   ```

2. **Set up environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure

```
├── data/
│   ├── processed/      # Cleaned indicator datasets
│   └── raw/            # Raw JSON/CSV from APIs
├── docs/               # Methodology documentation
├── notebooks/          # Exploratory Data Analysis (EDA)
├── scripts/            # Data collection and processing scripts
├── src/                # Application source code
│   ├── app.py          # Main Streamlit application
│   ├── config.py       # Configuration and weights
│   └── scoring_engine.py # Risk calculation logic
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Developer:** Jimmy Matewere  
**Email:** jimmymatewere@gmail.com  
**LinkedIn:** [linkedin.com/in/jimmy-matewere](https://linkedin.com/in/jimmy-matewere)  
**Project Link:** [GitHub Repository](https://github.com/Jimmy-JayJay/Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1)

## Acknowledgments

- IPCC AR5 framework
- NASA POWER Project
- World Bank Open Data
