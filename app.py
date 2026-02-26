import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="ESP32 DHT11 Analysis", page_icon="📊", layout="wide")

st.title("📊 ESP32 Sensor Data Analysis")
st.markdown("Analysis of DHT11 Temperature and Humidity logs.")

# 2. Load Data
@st.cache_data # This makes the app fast by not re-loading the CSV every click
def load_data():
    try:
        # Load your specific file
        df = pd.read_csv('ESP32 Data Log.csv')
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is not None:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Data")
    # Allow user to select a date range
    min_date = df['DateTime'].min().date()
    max_date = df['DateTime'].max().date()
    
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    
    # Filter dataframe based on selection
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['DateTime'].dt.date >= start_date) & (df['DateTime'].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    # --- MAIN DASHBOARD ---
    latest = df_filtered.iloc[-1]
    
    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Temp", f"{latest['Temperature']}°C")
    col2.metric("Current Humidity", f"{latest['Humidity']}%")
    col3.metric("Total Readings", len(df_filtered))

    st.divider()

    # Interactive Plotly Charts
    col_left, col_right = st.columns(2)

    with col_left:
        fig_temp = px.line(df_filtered, x='DateTime', y='Temperature', 
                          title='Temperature Trend', color_discrete_sequence=['#ef4444'])
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_right:
        fig_hum = px.line(df_filtered, x='DateTime', y='Humidity', 
                         title='Humidity Trend', color_discrete_sequence=['#3b82f6'])
        st.plotly_chart(fig_hum, use_container_width=True)

    # Statistical Summary (Great for your project report)
    st.subheader("Data Summary Statistics")
    st.dataframe(df_filtered.describe().T, use_container_width=True)

else:
    st.error("⚠️ 'ESP32 Data Log.csv' not found! Please upload it to your GitHub repo.")
