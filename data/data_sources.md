## Primary Data Sources

### 1. Climate Data

#### NASA POWER API

- **Source**: NASA Prediction of Worldwide Energy Resources
- **URL**: https://power.larc.nasa.gov/
- **Data Type**: Gridded climate data
- **Variables**:
  - Daily temperature (minimum, maximum, mean)
  - Daily rainfall
  - Solar radiation
  - Relative humidity
- **Temporal Coverage**: 2020-2024 (5 years)
- **Spatial Resolution**: 0.5° x 0.5° grid
- **Access**: Free, no registration required
- **API Rate Limit**: ~2 seconds between requests
- **Data File**: `data/processed/climate_data_nasa_power.csv`
- **Status**: Real data fetched

---

### 2. Socioeconomic Data

#### World Bank Development Indicators

- **Source**: World Bank Open Data
- **URL**: https://data.worldbank.org/
- **Dataset**: World Development Indicators (WDI)
- **File**: `API_MWI_DS2_en_csv_v2_10259.csv`
- **Last Updated**: December 2025
- **Indicators Used**:
  - **SI.POV.DDAY**: Poverty headcount ratio at $2.15/day (75.4%)
  - **SE.ADT.LITR.ZS**: Adult literacy rate (70.2%)
  - **SL.AGR.EMPL.ZS**: Employment in agriculture (61.7%)
  - **SH.H2O.BASW.ZS**: Access to basic water services (73.1%)
  - **SP.POP.TOTL**: Total population (21.7 million)
- **Temporal Coverage**: 1960-2024
- **Geographic Level**: National (Malawi)
- **Data File**: `data/processed/socioeconomic_data_enhanced.csv`
- **Status**: Real national statistics integrated

**Note**: District-level estimates are calibrated to match real national averages from World Bank data.

---

### 3. Population Data

#### WorldPop

- **Source**: WorldPop Project
- **URL**: https://www.worldpop.org/
- **Dataset**: Population Counts 2020 (UN-adjusted, constrained)
- **File**: `mwi_ppp_2020_UNadj_constrained.tif`
- **Year**: 2020
- **Spatial Resolution**: 100m x 100m
- **Format**: GeoTIFF raster
- **Total Population**: 18.9 million (from raster aggregation)
- **Processing**: Zonal statistics by district using GADM boundaries
- **Data File**: `data/processed/socioeconomic_data_real.csv`
- **Status**: Real population data processed

---

### 4. Administrative Boundaries

#### GADM (Global Administrative Areas)

- **Source**: GADM Database of Global Administrative Areas
- **URL**: https://gadm.org/
- **Version**: 4.1
- **Dataset**: Malawi Administrative Boundaries Level 2
- **File**: `gadm41_MWI_2.shp` (+ .shx, .dbf, .prj, .cpg)
- **Administrative Level**: Level 2 (Districts and sub-districts)
- **Number of Units**: 256 administrative units
- **Main Districts**: 28 districts
- **Format**: ESRI Shapefile
- **Coordinate System**: WGS84 (EPSG:4326)
- **Data File**: `data/raw/gadm/gadm41_MWI_2.*`
- **Status**: Complete shapefile processed

---

### 5. Disaster Data

#### EM-DAT (Emergency Events Database)

- **Source**: Centre for Research on the Epidemiology of Disasters (CRED)
- **URL**: https://www.emdat.be/
- **Coverage**: Historical disaster events in Malawi
- **Event Types**: Floods, droughts, cyclones, storms
- **Temporal Coverage**: 2010-2024
- **Access**: Free registration required
- **Data File**: `data/processed/disaster_data_all_districts.csv`
- **Status**: Sample data (based on known historical patterns)

**Known Major Events**:

- 2015: Floods (Southern Region)
- 2019: Cyclone Idai
- 2022: Tropical Storm Ana
- 2023: Cyclone Freddy

---

## Derived Indicators

### Climate Indicators

#### Rainfall Variability

- **Calculation**: Coefficient of Variation (CV) of annual rainfall
- **Formula**: CV = (σ / μ) × 100
- **Data Source**: NASA POWER daily rainfall
- **Temporal Aggregation**: Annual totals (2020-2024)

#### Drought Frequency

- **Method**: Standardized Precipitation Index (SPI)
- **Threshold**: SPI < -1.0 (moderate drought)
- **Data Source**: NASA POWER daily rainfall
- **Temporal Window**: 3-month rolling average

#### Heat Days

- **Definition**: Days with maximum temperature > 35°C
- **Data Source**: NASA POWER daily temperature
- **Temporal Aggregation**: Annual count

#### Flood Risk

- **Proxy**: Historical disaster frequency
- **Data Source**: EM-DAT disaster database
- **Normalization**: Robust percentile-based (5th-95th percentile)

#### Cyclone Exposure

- **Method**: Latitude-based scoring
- **Formula**: Higher scores for southern districts (< -15° latitude)
- **Rationale**: Southern Malawi more exposed to Indian Ocean cyclones

---

### Socioeconomic Indicators

#### Poverty Rate

- **Source**: World Bank SI.POV.DDAY
- **National Average**: 75.4%
- **District Range**: 60-90% (calibrated estimates)
- **Urban/Rural Adjustment**: Urban districts 20-40% below national average

#### Literacy Rate

- **Source**: World Bank SE.ADT.LITR.ZS
- **National Average**: 70.2%
- **District Range**: 55-90% (calibrated estimates)
- **Urban/Rural Adjustment**: Urban districts 10-20% above national average

#### Agricultural Dependence

- **Source**: World Bank SL.AGR.EMPL.ZS
- **National Average**: 61.7%
- **District Range**: 40-90% (calibrated estimates)
- **Urban/Rural Adjustment**: Urban districts 30-50% below national average

#### Service Access

- **Components**: Health facilities + water access
- **Formula**: (health_access + water_access) / 2
- **Data Sources**: World Bank health and water indicators

---

## Data Processing Methods

### Normalization

- **Method**: Robust percentile-based normalization
- **Range**: 0-100 scale
- **Percentiles**: 5th (minimum) to 95th (maximum)
- **Purpose**: Handle outliers and ensure comparability

### Aggregation

- **Spatial**: Sub-district to district level
- **Temporal**: Daily to annual indicators
- **Method**: Mean, sum, or count depending on indicator

### Quality Control

- **Missing Data**: Handled via interpolation or exclusion
- **Outliers**: Clipped at 5th and 95th percentiles
- **Validation**: Cross-checked against known patterns

---

## Risk Scoring Methodology

### Framework

- **Basis**: IPCC AR5 Vulnerability Framework
- **Formula**: Risk = f(Hazard, Exposure, Adaptive Capacity)

### Component Weights

- **Hazard**: 40%
- **Exposure**: 30%
- **Vulnerability** (100 - Adaptive Capacity): 30%

### Sub-component Weights

**Hazard (40%)**:

- Rainfall Variability: 20%
- Drought Frequency: 20%
- Flood Risk: 25%
- Temperature Extremes: 20%
- Cyclone Exposure: 15%

**Exposure (30%)**:

- Exposed Population: 35%
- Agricultural Dependence: 35%
- Infrastructure Deficit: 20%
- Cropland Exposure: 10%

**Adaptive Capacity (30%)**:

- Poverty Rate: 35% (inverted)
- Education Level: 25%
- Service Access: 25%
- Local Capacity: 15%

---

## Data Quality Assessment

### Climate Data (NASA POWER)

- **Completeness**: >95% (daily data 2020-2024)
- **Accuracy**: Validated against ground stations
- **Reliability**: High (NASA quality-controlled)
- **Limitations**: Gridded data may not capture micro-climates

### Socioeconomic Data (World Bank)

- **Completeness**: 100% for national indicators
- **Accuracy**: Official government statistics
- **Reliability**: High (international standard)
- **Limitations**: National-level only, district estimates are modeled

### Population Data (WorldPop)

- **Completeness**: 100% spatial coverage
- **Accuracy**: ±10-15% (UN-adjusted)
- **Reliability**: High (peer-reviewed methodology)
- **Limitations**: 2020 baseline, may not reflect recent changes

### Disaster Data (EM-DAT)

- **Completeness**: Major events only
- **Accuracy**: Varies by event reporting
- **Reliability**: Medium (depends on local reporting)
- **Limitations**: Under-reporting of small events

---

## Data Update Frequency

| Data Source | Update Frequency | Last Updated | Next Update      |
| ----------- | ---------------- | ------------ | ---------------- |
| NASA POWER  | Daily            | 2024-12-31   | Ongoing          |
| World Bank  | Annual           | 2024-12      | 2025-12          |
| WorldPop    | Annual           | 2020         | 2025 (projected) |
| GADM        | Irregular        | 2024 (v4.1)  | TBD              |
| EM-DAT      | Continuous       | 2024-12      | Ongoing          |

---

## Citations

### Data Sources

**NASA POWER**:

> NASA Prediction of Worldwide Energy Resources (POWER) Project. (2024). NASA POWER Data Access Viewer. Retrieved from https://power.larc.nasa.gov/

**World Bank**:

> World Bank. (2024). World Development Indicators. Retrieved from https://data.worldbank.org/

**WorldPop**:

> WorldPop. (2020). Global High Resolution Population Denominators Project. University of Southampton. doi:10.5258/SOTON/WP00645

**GADM**:

> GADM. (2024). GADM database of Global Administrative Areas, version 4.1. Retrieved from https://gadm.org/

**EM-DAT**:

> Guha-Sapir, D., Below, R., & Hoyois, P. (2024). EM-DAT: The Emergency Events Database. Université catholique de Louvain (UCL) - CRED. Retrieved from https://www.emdat.be/

### Methodology

**IPCC AR5**:

> IPCC. (2014). Climate Change 2014: Impacts, Adaptation, and Vulnerability. Contribution of Working Group II to the Fifth Assessment Report of the Intergovernmental Panel on Climate Change. Cambridge University Press.

---

## Contact & Support

**Data Issues**: Report data quality issues or inconsistencies via GitHub Issues

**Methodology Questions**: See `docs/methodology.md` for detailed methodology documentation

**API Access**:

- NASA POWER: No registration required
- World Bank: Open data, no registration
- WorldPop: Free download, no registration
- GADM: Free download, no registration
- EM-DAT: Free registration required

---

## License & Usage

### Data Licenses

- **NASA POWER**: Public domain (U.S. Government work)
- **World Bank**: CC BY 4.0
- **WorldPop**: CC BY 4.0
- **GADM**: Free for academic use
- **EM-DAT**: Free for non-commercial use

### Dashboard License

This dashboard and its code are released under the MIT License.

---

**Last Updated**: January 9, 2026
**Version**: 1.0
**Maintainer**: Climate Risk Assessment Team
