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
        
        # Clean column names (removes spaces/tabs we found earlier)
        df.columns = df.columns.str.strip()
        
        # Combine 'Date' and 'Time' into a single Timestamp column
        # We use errors='coerce' to handle any messy data rows
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        
        # Ensure Temperature and Humidity are treated as numbers
        df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
        df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')
        
        # Drop any rows that failed to convert (cleaning the data)
        return df.dropna(subset=['Timestamp', 'Temperature', 'Humidity'])
    except FileNotFoundError:
        return None

df = load_data()

# 3. App Logic
if df is not None:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Settings")
    
    # Date Range Filter
    min_date = df['Timestamp'].min().date()
    max_date = df['Timestamp'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range", 
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtering the data based on sidebar selection
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    #
