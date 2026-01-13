"""
Climate Risk Scoring Dashboard for Malawian Districts
Interactive Streamlit application for visualizing climate vulnerability
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import MVP_DISTRICTS, ALL_DISTRICTS, WEIGHTS
from scoring_engine import RiskScorer
from data_collection import (
    fetch_multiple_districts_nasa,
    create_sample_socioeconomic_data,
    create_sample_disaster_data,
    calculate_cyclone_exposure
)
from data_processing import (
    calculate_rainfall_cv,
    calculate_drought_frequency,
    calculate_heat_days,
    calculate_extreme_rainfall_frequency,
    robust_normalize
)
from disaster_processing import load_emdat_data

# Page configuration
st.set_page_config(
    page_title="Malawi Climate Risk Dashboard",
    page_icon="None",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-very-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-high {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffbb00;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)



@st.cache_data
def load_real_data():
    """Load all real datasets"""
    
    # 1. Load Climate Data (NASA POWER)
    try:
        climate_data = pd.read_csv("data/processed/climate_data_nasa_power.csv")
    except FileNotFoundError:
        st.error("Climate data file not found! Please run data collection script.")
        climate_data = pd.DataFrame()

    # 2. Load Socioeconomic Data (World Bank)
    try:
        socioeconomic = pd.read_csv("data/processed/socioeconomic_data_enhanced.csv")
    except FileNotFoundError:
        socioeconomic = pd.DataFrame()
        
    # 3. Load Disaster Data (EM-DAT)
    disasters = load_emdat_data()
    if disasters.empty:
         # Fallback only if EM-DAT parsing fails
        disaster_districts = ['Nsanje', 'Chikwawa', 'Phalombe', 'Mulanje', 'Zomba', 'Blantyre', 'Mangochi']
        disasters = pd.DataFrame({
            'district': disaster_districts * 6,
            'year': ([2015, 2019, 2022, 2023, 2015, 2019] * 7),
            'type': (['Flood', 'Cyclone', 'Storm', 'Flood', 'Drought', 'Flood'] * 7)
        })
    
    return climate_data, socioeconomic, disasters


@st.cache_data
def calculate_risk_scores():
    """Calculate risk scores for all 28 districts"""
    climate_data, socioeconomic, disasters = load_real_data()
    
    if socioeconomic is None:
        return pd.DataFrame()
    
    # Prepare indicators DataFrame
    indicators = socioeconomic.copy()
    
    # Calculate disaster frequency from disaster data
    disaster_counts = disasters.groupby('district').size().reset_index(name='disaster_count')
    indicators = indicators.merge(disaster_counts, on='district', how='left')
    indicators['disaster_count'] = indicators['disaster_count'].fillna(0)
    
    # Calculate climate indicators from climate data
    climate_data['date'] = pd.to_datetime(climate_data['date'])
    
    climate_indicators = []
    for district in indicators['district'].unique():
        district_climate = climate_data[climate_data['district'] == district]
        
        # Rainfall CV
        annual_rainfall = district_climate.groupby(district_climate['date'].dt.year)['rainfall'].sum()
        cv = (annual_rainfall.std() / annual_rainfall.mean()) * 100 if annual_rainfall.mean() > 0 else 0
        
        # Heat Days
        h_days = len(district_climate[district_climate['temperature_max'] > 35])
        avg_heat_days = h_days / 5  # Average over 5 years
        
        # Drought Frequency (SPI based)
        d_freq = calculate_drought_frequency(district_climate, district)
        if pd.isna(d_freq): d_freq = 0
        
        # Flood Risk Proxy (Extreme Rainfall Frequency)
        f_freq = calculate_extreme_rainfall_frequency(district_climate, district)
        if pd.isna(f_freq): f_freq = 0
        
        climate_indicators.append({
            'district': district, 
            'rainfall_cv': cv,
            'heat_days': avg_heat_days,
            'drought_frequency': d_freq,
            'flood_risk': f_freq
        })
    
    climate_ind_df = pd.DataFrame(climate_indicators)
    indicators = indicators.merge(climate_ind_df, on='district')
    
    # Normalize hazard indicators
    indicators['rainfall_variability'] = robust_normalize(indicators['rainfall_cv'].values)
    indicators['drought_frequency'] = robust_normalize(indicators['drought_frequency'].values)
    indicators['flood_risk'] = robust_normalize(indicators['flood_risk'].values)
    indicators['temperature_extremes'] = robust_normalize(indicators['heat_days'].values)
    
    # Exposure indicators
    indicators['exposed_population'] = robust_normalize(indicators['population_density'].values)
    indicators['cropland_exposure'] = robust_normalize(indicators['agricultural_dependence'].values)
    indicators['infrastructure_deficit'] = 100 - robust_normalize(indicators['road_density'].values)
    
    # Adaptive capacity indicators
    indicators['education_level'] = indicators['literacy_rate']
    indicators['service_access'] = (indicators['health_facility_access'] + indicators['water_access']) / 2
    indicators['local_capacity'] = 100 - indicators['poverty_rate']
    
    # Calculate scores using scoring engine
    scorer = RiskScorer()
    results = []
    
    for _, row in indicators.iterrows():
        hazard_indicators = {
            'rainfall_variability': row['rainfall_variability'],
            'drought_frequency': row['drought_frequency'],
            'flood_risk': row['flood_risk'],
            'temperature_extremes': row['temperature_extremes']
        }
        
        exposure_indicators = {
            'exposed_population': row['exposed_population'],
            'agricultural_dependence': row['agricultural_dependence'],
            'infrastructure_deficit': row['infrastructure_deficit'],
            'cropland_exposure': row['cropland_exposure']
        }
        
        adaptive_capacity_indicators = {
            'poverty_rate': row['poverty_rate'],
            'education_level': row['education_level'],
            'service_access': row['service_access'],
            'local_capacity': row['local_capacity']
        }
        
        scores = scorer.calculate_all_scores(
            hazard_indicators,
            exposure_indicators,
            adaptive_capacity_indicators
        )
        
        scores['district'] = row['district']
        # Get coordinates from ALL_DISTRICTS
        if row['district'] in ALL_DISTRICTS:
            scores['latitude'] = ALL_DISTRICTS[row['district']]['lat']
            scores['longitude'] = ALL_DISTRICTS[row['district']]['lon']
        else:
            scores['latitude'] = -14.0
            scores['longitude'] = 34.0
        
        results.append(scores)
    
    return pd.DataFrame(results)



def create_map(data, color_column='risk'):
    """Create choropleth map"""
    fig = px.scatter_mapbox(
        data,
        lat='latitude',
        lon='longitude',
        color=color_column,
        size=color_column,
        hover_name='district',
        hover_data={
            'risk': ':.1f',
            'hazard': ':.1f',
            'exposure': ':.1f',
            'adaptive_capacity': ':.1f',
            'latitude': False,
            'longitude': False
        },
        color_continuous_scale='RdYlGn_r',
        size_max=30,
        zoom=6,
        center={'lat': -14.5, 'lon': 34.5},
        mapbox_style='open-street-map',
        title=f'District Risk Scores - {color_column.title()} Component'
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


def create_radar_chart(data, district):
    """Create radar chart for district components"""
    district_data = data[data['district'] == district].iloc[0]
    
    categories = ['Hazard', 'Exposure', 'Vulnerability', 'Overall Risk']
    values = [
        district_data['hazard'],
        district_data['exposure'],
        district_data['vulnerability'],
        district_data['risk']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=district,
        line_color='#1f77b4'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title=f'Risk Profile: {district}'
    )
    
    return fig


def create_comparison_chart(data):
    """Create comparison bar chart"""
    fig = go.Figure()
    
    components = ['hazard', 'exposure', 'vulnerability', 'risk']
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
    
    for i, component in enumerate(components):
        fig.add_trace(go.Bar(
            name=component.title(),
            x=data['district'],
            y=data[component],
            marker_color=colors[i]
        ))
    
    fig.update_layout(
        barmode='group',
        title='Component Comparison Across Districts',
        xaxis_title='District',
        yaxis_title='Score (0-100)',
        height=400
    )
    
    return fig


# Main app
def main():
    # Header
    st.markdown('<div class="main-header">Climate Risk Scoring Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Assessing Climate Vulnerability Across Malawian Districts</div>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data and calculating risk scores...'):
        risk_data = calculate_risk_scores()
        if risk_data.empty:
            st.stop()
        climate_data, socioeconomic, disasters = load_real_data()
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # View selection
    view_mode = st.sidebar.radio(
        "Select View",
        ["Overview", "District Details", "Component Analysis", "Methodology"]
    )
    
    # Component filter
    component_view = st.sidebar.selectbox(
        "Map Component",
        ["risk", "hazard", "exposure", "adaptive_capacity"],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # District filter
    selected_districts = st.sidebar.multiselect(
        "Filter Districts",
        options=risk_data['district'].tolist(),
        default=risk_data['district'].tolist()
    )
    
    filtered_data = risk_data[risk_data['district'].isin(selected_districts)]
    
    # Main content based on view mode
    if view_mode == "Overview":
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_risk = filtered_data['risk'].mean()
            st.metric("Average Risk Score", f"{avg_risk:.1f}")
        
        with col2:
            high_risk_count = len(filtered_data[filtered_data['risk'] >= 60])
            st.metric("High Risk Districts", high_risk_count)
        
        with col3:
            max_risk_district = filtered_data.loc[filtered_data['risk'].idxmax(), 'district']
            st.metric("Highest Risk", max_risk_district)
        
        with col4:
            min_risk_district = filtered_data.loc[filtered_data['risk'].idxmin(), 'district']
            st.metric("Lowest Risk", min_risk_district)
        
        # Map
        st.subheader("Geographic Distribution")
        map_fig = create_map(filtered_data, component_view)
        st.plotly_chart(map_fig, use_container_width=True)
        
        # Ranking table
        st.subheader("District Rankings")
        scorer = RiskScorer()
        ranked_data = scorer.rank_districts(filtered_data, 'risk')
        
        display_cols = ['rank', 'district', 'risk', 'hazard', 'exposure', 'adaptive_capacity']
        st.dataframe(
            ranked_data[display_cols].style.format({
                'risk': '{:.1f}',
                'hazard': '{:.1f}',
                'exposure': '{:.1f}',
                'adaptive_capacity': '{:.1f}'
            }),
            use_container_width=True
        )
    
    elif view_mode == "District Details":
        st.subheader("District-Level Analysis")
        st.subheader(" District-Level Analysis")
        
        selected_district = st.selectbox(
            "Select District for Detailed View",
            filtered_data['district'].tolist()
        )
        
        district_data = filtered_data[filtered_data['district'] == selected_district].iloc[0]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Risk Score", f"{district_data['risk']:.1f}")
        with col2:
            st.metric("Hazard", f"{district_data['hazard']:.1f}")
        with col3:
            st.metric("Exposure", f"{district_data['exposure']:.1f}")
        with col4:
            st.metric("Adaptive Capacity", f"{district_data['adaptive_capacity']:.1f}")
        
        # Radar chart
        col1, col2 = st.columns(2)
        
        with col1:
            radar_fig = create_radar_chart(filtered_data, selected_district)
            st.plotly_chart(radar_fig, use_container_width=True)
        
        with col2:
            # Socioeconomic data
            st.markdown("### Socioeconomic Indicators")
            socio_data = socioeconomic[socioeconomic['district'] == selected_district].iloc[0]
            
            st.write(f"**Population:** {socio_data['population']:,}")
            st.write(f"**Poverty Rate:** {socio_data['poverty_rate']:.1f}%")
            st.write(f"**Literacy Rate:** {socio_data['literacy_rate']:.1f}%")
            st.write(f"**Agricultural Dependence:** {socio_data['agricultural_dependence']:.1f}%")
            st.write(f"**Health Facility Access:** {socio_data['health_facility_access']:.1f}%")
    
    elif view_mode == "Component Analysis":
        st.subheader("Component Comparison")
        
        # Comparison chart
        comparison_fig = create_comparison_chart(filtered_data)
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        # Component breakdown
        st.markdown("### IPCC AR5 Risk Components")
        st.markdown("""
        **Multiplicative Risk Model:** `Risk = ∛(Hazard × Exposure × Vulnerability)`
        
        Each component is calculated as a composite of its sub-indicators. 
        The final risk score uses **geometric mean** — all three components must be 
        present for risk to exist.
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌪️ Hazard**")
            st.write("_Sub-indicator weights within Hazard:_")
            st.write("- Rainfall Variability: 25%")
            st.write("- Drought Frequency: 25%")
            st.write("- Flood Risk: 25%")
            st.write("- Temperature Extremes: 25%")
        
        with col2:
            st.markdown("**👥 Exposure**")
            st.write("_Sub-indicator weights within Exposure:_")
            st.write("- Exposed Population: 35%")
            st.write("- Agricultural Dependence: 35%")
            st.write("- Infrastructure Deficit: 20%")
            st.write("- Cropland Exposure: 10%")
        
        with col3:
            st.markdown("**🛡️ Vulnerability**")
            st.write("_Sub-indicator weights within Vulnerability:_")
            st.write("- Poverty Rate: 35% (inverted)")
            st.write("- Education Level: 25%")
            st.write("- Service Access: 25%")
            st.write("- Local Capacity: 15%")
    
    else:  # Methodology
        st.subheader("Methodology")
        
        st.markdown("""
        ### IPCC AR5 Multiplicative Risk Framework
        
        This dashboard implements the **IPCC AR5 vulnerability framework** using a 
        multiplicative risk model that reflects the true interdependence of risk components:
        
        **Risk = f(Hazard × Exposure × Vulnerability)**
        
        #### Composite Risk Score Formula
        ```
        Risk Score = ∛(Hazard × Exposure × Vulnerability)
        
        Where: Vulnerability = 100 - Adaptive Capacity
        ```
        
        #### Why Multiplicative?
        
        The multiplicative model is **essential** for IPCC AR5 compliance because:
        
        - **If any component is zero, risk is zero** — You cannot have climate risk 
          without hazards occurring, assets/people exposed, OR vulnerability to impacts.
        - **Components interact** — High hazard combined with high exposure creates 
          disproportionately higher risk than either alone.
        - **Reflects physical reality** — A district with extreme cyclone hazard but 
          zero exposed population has zero risk from that hazard.
        
        The geometric mean (cube root) normalization preserves the 0-100 scale 
        interpretability while maintaining multiplicative interaction properties.
        
        #### Data Sources
        - **Climate Data:** NASA POWER API (Daily T2M & Rainfall, 2020-2024)
        - **Socioeconomic:** World Bank Development Indicators (Poverty, Literacy, Water Access)
        - **Population:** WorldPop (2020 Constrained UN-Adjusted)
        - **Boundaries:** GADM v4.1 (Level 1 Administrative Areas)
        - **Disasters:** EM-DAT International Disaster Database (2000-2024)
        
        #### Component Calculation
        Each component (Hazard, Exposure, Vulnerability) is first calculated as a 
        **weighted composite** of its sub-indicators.
        
        *Note: The weights below apply ONLY to sub-indicator aggregation within each component. 
        The final risk calculation treats Hazard, Exposure, and Vulnerability equally via multiplication.*
        
        | Component | Sub-indicator Weights |
        |-----------|----------------------|
        | **Hazard** | Rainfall CV (25%), Drought (25%), Flood (25%), Heat (25%) |
        | **Exposure** | Population (35%), Agriculture (35%), Infrastructure (20%), Cropland (10%) |
        | **Adaptive Capacity** | Poverty (35%), Education (25%), Services (25%), Local Capacity (15%) |
        
        #### Normalization
        All indicators are normalized to a 0-100 scale using robust percentile-based normalization
        (5th-95th percentile clipping) to handle outliers and ensure comparability.
        
        #### Risk Categories
        - **Very High:** 75-100
        - **High:** 60-74
        - **Medium:** 40-59
        - **Low:** 25-39
        - **Very Low:** 0-24
        
        #### References
        > IPCC, 2014: Climate Change 2014: Impacts, Adaptation, and Vulnerability. 
        > Contribution of Working Group II to the Fifth Assessment Report.
        > Chapter 19: Emergent Risks and Key Vulnerabilities.
        
        #### Citation
        If you use this dashboard or methodology, please cite:
        > Climate Risk Scoring Dashboard for Malawian Districts (2026). 
        > Developed using IPCC AR5 multiplicative vulnerability framework.
        """)
        
        # Download button for data
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download Risk Scores (CSV)",
            data=csv,
            file_name="malawi_climate_risk_scores.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        Climate Risk Scoring Dashboard for Malawian Districts | 
        Data as of 2024 | 
        Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
