import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(
    page_title="IoT DHT11 Dashboard",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ DHT11 Sensor: Real-Time Monitoring")
st.markdown("This dashboard tracks live Temperature and Humidity data from Google Sheets.")

# 2. Establish Google Sheets Connection
# This looks for the URL in your .streamlit/secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Data Loading Function
def load_data():
    # ttl=0 ensures we bypass the cache for live updates
    data = conn.read(ttl=0)
    
    # Data Cleaning for Data Science consistency
    data['DateTime'] = pd.to_datetime(data['DateTime'])
    data['Temperature'] = pd.to_numeric(data['Temperature'], errors='coerce')
    data['Humidity'] = pd.to_numeric(data['Humidity'], errors='coerce')
    
    return data.dropna()

# 4. Dashboard Layout
# Create a placeholder so we can refresh the data without reloading the whole page
placeholder = st.empty()

# 5. Live Update Loop
while True:
    df = load_data()
    
    # Get the very last row for the "Current Status"
    latest_reading = df.iloc[-1]
    
    with placeholder.container():
        # --- TOP ROW: KPI METRICS ---
        col1, col2, col3 = st.columns(3)
        
        # Calculate Delta (change from previous reading) if possible
        if len(df) > 1:
            temp_delta = float(latest_reading['Temperature'] - df.iloc[-2]['Temperature'])
            hum_delta = float(latest_reading['Humidity'] - df.iloc[-2]['Humidity'])
        else:
            temp_delta = hum_delta = 0

        col1.metric("Temperature", f"{latest_reading['Temperature']}°C", delta=f"{temp_delta:.1f}°C")
        col2.metric("Humidity", f"{latest_reading['Humidity']}%", delta=f"{hum_delta:.1f}%")
        col3.metric("Last Update", latest_reading['DateTime'].strftime('%H:%M:%S'))

        # --- MIDDLE ROW: CHARTS ---
        st.divider()
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Temperature Trend")
            st.line_chart(df, x="DateTime", y="Temperature", color="#FF4B4B")
            
        with chart_col2:
            st.subheader("Humidity Trend")
            st.line_chart(df, x="DateTime", y="Humidity", color="#0072B2")

        # --- BOTTOM ROW: DATA TABLE ---
        with st.expander("View Full Dataset"):
            st.dataframe(df.sort_values(by="DateTime", ascending=False), use_container_width=True)

    # Refresh rate (seconds) - Adjust based on how fast your DHT11 sends data
    time.sleep(10)
