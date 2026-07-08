import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# 1. PAGE CONFIGURATION & METADATA
st.set_page_config(
    page_title="Delhi Air Quality Medallion Pipeline",
    page_icon="📊",
    layout="wide"
)

# 2. SECURE DATABASE CONNECTION
@st.cache_resource
def init_connection():
    """Establishes a cached connection pool to the Neon Postgres Data Warehouse."""
    # Fetches from Streamlit's secure secrets layout manager
    db_url = st.secrets["NEON_DATABASE_URL"]
    
    # 🔥 PURE-PYTHON DRIVER SWAP: Enforce pg8000 prefix to remain fully stable on Python 3.14+
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)
        
    return create_engine(db_url)

try:
    engine = init_connection()
except Exception as e:
    st.error(f"Database Connection Initialization Failed: {e}")
    st.stop()

# 3. HIGH-PERFORMANCE DATA CACHING TIER
@st.cache_data(ttl=3600)
def load_warehouse_data(table_name):
    """Fetches records from the serving layer with an explicit 1-hour time-to-live cache."""
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql(query, con=engine)

# Ingest warehouse tables into memory frames
with st.spinner("Synchronizing states with Neon Cloud Data Warehouse..."):
    df_silver = load_warehouse_data("silver_pollution_master")
    df_gold_peaks = load_warehouse_data("gold_yearly_peaks")

# Parse structural temporal sorting axes
df_silver['record_date'] = pd.to_datetime(df_silver['record_date'])
df_silver = df_silver.sort_values('record_date', ascending=False)
df_gold_peaks = df_gold_peaks.sort_values('peak_year', ascending=True)

# 4. EXECUTIVE HERO PANEL (THE MAIN HEADER)
st.title("🏭 Delhi Air Quality Index (AQI) Production Pipeline Dashboard")
st.markdown("""
This production-grade analytical platform maps over a decade of environmental metrics for Delhi. 
The system runs entirely within zero-cost constraints, using **GitHub Actions** for serverless daily orchestration, 
**Neon Serverless PostgreSQL** as the primary relational data warehouse, and **Streamlit Community Cloud** for rendering.
""")
st.sidebar.header("Pipeline Controls")
st.sidebar.success("🔴 Status: Live & Automating")

# 5. RENDER THE CORE METRIC COMPONENT HIGHLIGHTS
if not df_silver.empty:
    latest_row = df_silver.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Latest PM2.5 Concentration", value=f"{latest_row['pm25_cleaned']:.2f} µg/m³")
    with col2:
        st.metric(label="Calculated Statutory AQI Score", value=int(latest_row['calculated_aqi']))
    with col3:
        st.metric(label="CPCB Risk Category Bucket", value=str(latest_row['aqi_bucket']))
    with col4:
        st.metric(label="Last Verified Sync Execution", value=latest_row['record_date'].strftime('%Y-%m-%d'))

st.markdown("---")

# 6. LAY OUT THREE TAB VIEW CHANNELS
tab1, tab2, tab3 = st.tabs([
    "📈 Historical Continuous Trends", 
    "🛡️ Policy Interventions & Weather", 
    "🔥 Anomalies & Peak Toxicity Matrix"
])

# ================= Tab 1: Historical Continuous Trends =================
with tab1:
    st.subheader("Time-Series Baseline Ingestion Tracking")
    
    # Visual 1: Continuous Historical Timeline Chart
    st.markdown("**10-Year Particulate Matter Time-Series Trend Line**")
    chart_data = df_silver.set_index('record_date')[['pm25_cleaned', 'calculated_aqi']]
    st.line_chart(chart_data['calculated_aqi'])
    
    # Visual 2: Category Distribution Breakdown
    st.markdown("**CPCB Category Distribution Matrix (Baseline Density Check)**")
    bucket_counts = df_silver['aqi_bucket'].value_counts()
    st.bar_chart(bucket_counts)

# ================= Tab 2: Policy Interventions & Weather =================
with tab2:
    st.subheader("Policy Effect & Forcing Factor Multi-Variate Check")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**COVID-19 Lockdown Structural Density Split**")
        # Isolate Lockdown averages vs standard windows
        lockdown_metrics = df_silver.groupby('is_covid_lockdown')['pm25_cleaned'].mean().reset_index()
        lockdown_metrics['is_covid_lockdown'] = lockdown_metrics['is_covid_lockdown'].map({1: "Active Lockdown", 0: "Standard Baseline"})
        st.dataframe(lockdown_metrics.rename(columns={'pm25_cleaned': 'Mean PM2.5 Value'}))
        st.caption("Proves how industrial closures systematically flattened the concentration curve.")
        
    with col_right:
        st.markdown("**Odd-Even Traffic Policy Impact Averages**")
        oddeven_metrics = df_silver.groupby('is_odd_even_active')['pm25_cleaned'].mean().reset_index()
        oddeven_metrics['is_odd_even_active'] = oddeven_metrics['is_odd_even_active'].map({1: "Odd-Even Week", 0: "Standard Week"})
        st.dataframe(oddeven_metrics.rename(columns={'pm25_cleaned': 'Mean PM2.5 Value'}))
        st.caption("Validates vehicular emission reduction strategies against matching baselines.")

    st.markdown("#### Weather Variable Interdependence Metrics")
    # Multi-Variate Scatter: Temperature vs Toxicity
    st.scatter_chart(data=df_silver, x='temperature_c', y='pm25_cleaned', color='aqi_bucket')

# ================= Tab 3: Anomalies & Peak Toxicity Matrix =================
with tab3:
    st.subheader("Window Partition Aggregations (Gold Serving Tier)")
    st.markdown("""
    The data below utilizes a downstream analytical window logic to isolate the single worst pollution anomaly day for every calendar year. 
    This allows the UI to surface acute events instantly without scanning millions of historical transaction indices.
    """)
    
    # Visual: Yearly Peak Bar Multi-Matrix
    st.bar_chart(data=df_gold_peaks, x='peak_year', y='max_pm25')
    
    # Structural Table View Showcase
    st.markdown("**Gold Serving Tier Structural Data Inventory Representation**")
    st.dataframe(df_gold_peaks, use_container_width=True)
