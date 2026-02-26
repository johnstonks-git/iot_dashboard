import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="ESP32 DHT11 Analysis", page_icon="🌡️", layout="wide")

st.title("🌡️ ESP32 Sensor Data Analysis")
st.markdown("Analyzing Temperature and Humidity logs from your DHT11 sensor.")

# 2. Data Loading & Wrangling
@st.cache_data
def load_data():
    try:
        # Load the CSV
        df = pd.read_csv('ESP32 Data Log.csv')
        
        # Clean column names (removes hidden spaces/tabs)
        df.columns = df.columns.str.strip()
        
        # CRITICAL FIX: Merge Date and Time using dayfirst=True for DD/MM/YYYY
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True, errors='coerce')
        
        # FIX for potential cut-off header 'Temperat'
        if 'Temperat' in df.columns:
            df = df.rename(columns={'Temperat': 'Temperature'})
            
        # Ensure numbers are numeric
        df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
        df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')
        
        # Drop any rows where timestamp failed to convert
        return df.dropna(subset=['Timestamp'])
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None

df = load_data()

# 3. App Logic
if df is not None and not df.empty:
    # KPI Metrics for the latest reading
    latest = df.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Temp", f"{latest['Temperature']}°C")
    col2.metric("Current Humidity", f"{latest['Humidity']}%")
    col3.metric("Total Readings", len(df))

    st.divider()

    # Interactive Plotly Charts
    col_left, col_right = st.columns(2)

    with col_left:
        fig_temp = px.line(df, x='Timestamp', y='Temperature', 
                          title='Temperature Trend (°C)', 
                          color_discrete_sequence=['#ef4444'])
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_right:
        fig_hum = px.line(df, x='Timestamp', y='Humidity', 
                         title='Humidity Trend (%)', 
                         color_discrete_sequence=['#3b82f6'])
        st.plotly_chart(fig_hum, use_container_width=True)

    # Statistical Summary
    st.subheader("Statistical Summary")
    st.dataframe(df[['Temperature', 'Humidity']].describe().T, use_container_width=True)

    with st.expander("View Raw Data Log"):
        st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

elif df is not None and df.empty:
    st.warning("The CSV was found, but no valid data could be processed. Check your Date/Time formats.")
else:
    st.error("⚠️ File 'ESP32 Data Log.csv' not found. Please ensure it is uploaded to your GitHub repository.")
