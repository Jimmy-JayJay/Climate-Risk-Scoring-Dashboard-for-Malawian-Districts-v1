# Climate Risk Scoring Dashboard for Malawian Districts

A comprehensive, data-driven dashboard for assessing climate resilience across Malawi's 28 districts. This tool integrates NASA POWER climate data, World Bank socioeconomic indicators, and geospatial analysis to calculate risk scores aligned with the IPCC AR5 vulnerability framework.

## Project Overview

Malawi faces increasing climate risks, including floods, droughts, and cyclones. This dashboard empowers policymakers, NGOs, and researchers to:

- Identify high-risk districts using scientific data.
- Visualize vulnerability through interactive maps.
- Analyze risk components: Hazard, Exposure, and Vulnerability.
- Plan targeted adaptation interventions.

## Key Features

- **Real Climate Data**: Uses NASA POWER API for daily temperature and rainfall data (2020-2024).
- **Socioeconomic Context**: Integrates official World Bank development indicators (Poverty, Literacy, etc.).
- **Geospatial Precision**: Uses GADM Level 1 administrative boundaries and WorldPop population data.
- **IPCC Agnostic**: Risk scoring methodology aligned with the IPCC AR5 framework.
- **Interactive Visualization**: Filter by risk components and drill down into specific districts.

## Data Sources

| Component         | Source     | Details                                        |
| ----------------- | ---------- | ---------------------------------------------- |
| **Climate**       | NASA POWER | Daily temperature & rainfall (2020-2024)       |
| **Socioeconomic** | World Bank | Poverty, Literacy, Ag Dependency, Water Access |
| **Population**    | WorldPop   | 2020 UN-adjusted population counts             |
| **Boundaries**    | GADM v4.1  | Official administrative boundaries             |

## Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/malawi-climate-risk-dashboard.git
   cd malawi-climate-risk-dashboard
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

## Methodology

The dashboard strictly implements the **IPCC AR5 Multiplicative Risk Framework**.

**Formula:**
$$ Risk = \sqrt[3]{Hazard \times Exposure \times Vulnerability} $$

This multiplicative approach ensures that:

- **Zero-handling**: If any component (e.g., Exposure) is zero, the total Risk is zero.
- **Interaction**: High hazard combined with high vulnerability produces disproportionately higher risk scores.

**Components:**

- **Hazard**: Rainfall Variability (25%), Drought Frequency (25%), Flood Risk (25%), Heat Extremes (25%).
- **Exposure**: Population Density, Agricultural Dependence, Infrastructure Deficit.
- **Vulnerability**: Poverty Rate, Education Levels, Access to Services (Water/Health).

All indicators are normalized to a 0-100 scale using robust percentile clipping (5th-95th) to handle outliers.

## Project Structure

```
├── data/
│   ├── processed/      # Cleaned data used by the app
│   └── raw/            # Raw source data
├── docs/               # Methodology and guides
├── notebooks/          # Analysis notebooks
├── scripts/            # Data collection scripts
├── src/                # Source code
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Future Enhancements

- Expand analysis to sub-district level
- Integrate real-time NASA POWER API
- Add time-series trend analysis
- Incorporate climate model projections

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Developer**: [Jimmy Matewere](https://github.com/Jimmy-JayJay)
**Project Link**: [https://github.com/Jimmy-JayJay/Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1](https://github.com/Jimmy-JayJay/Climate-Risk-Scoring-Dashboard-for-Malawian-Districts-v1)

## Acknowledgments

- IPCC AR5 framework
- NASA POWER Project
- World Bank Open Data
- Malawi National Statistical Office
