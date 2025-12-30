import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Professional page config
st.set_page_config(page_title="Pro Used Car Analyzer", layout="wide")

# Professional header
st.markdown("""
<style>
    .main-header {font-size: 42px; font-weight: bold; color: #1E88E5; text-align: center;}
    .sub-header {font-size: 20px; text-align: center; color: #424242;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Professional Used Car Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">2025 Market Data • KBB-Style Valuation • Profit Calculator</div>', unsafe_allow_html=True)
st.markdown("---")

# Tabs
tab1, tab2 = st.tabs(["📊 Market Overview", "💰 Valuation & Profit Calculator"])

# Data
base_data = {
    'Type': ['Truck', 'Truck', 'Truck', 'Truck', 'Truck', 'SUV', 'SUV', 'SUV', 'SUV', 'SUV', 'Sedan', 'Sedan', 'Sedan', 'Sedan'],
    'Make': ['Ford', 'Chevrolet', 'Ram', 'GMC', 'Toyota', 'Toyota', 'Honda', 'Chevrolet', 'Jeep', 'Nissan', 'Toyota', 'Honda', 'Toyota', 'Chevrolet'],
    'Model': ['F-150', 'Silverado 1500', '1500', 'Sierra 1500', 'Tacoma', 'RAV4', 'CR-V', 'Equinox', 'Grand Cherokee', 'Rogue', 'Camry', 'Civic', 'Corolla', 'Malibu'],
    'Full_Name': ['Ford F-150', 'Chevrolet Silverado 1500', 'Ram 1500', 'GMC Sierra 1500', 'Toyota Tacoma',
                  'Toyota RAV4', 'Honda CR-V', 'Chevrolet Equinox', 'Jeep Grand Cherokee', 'Nissan Rogue',
                  'Toyota Camry', 'Honda Civic', 'Toyota Corolla', 'Chevrolet Malibu'],
    'National_Sales': [750000, 620000, 530000, 460000, 400000, 380000, 350000, 330000, 280000, 260000, 310000, 290000, 270000, 230000],
    'Base_Price_Clean_AvgMile': [38000, 36000, 37000, 39000, 34000, 31000, 30000, 25000, 35000, 28000, 24000, 22000, 21000, 23000],
    'Base_Days_Clean_AvgMile': [28, 32, 35, 38, 30, 22, 24, 26, 40, 31, 25, 23, 20, 39]
}

df = pd.DataFrame(base_data)

# Sidebar filters (shared across tabs)
with st.sidebar:
    st.header("Filters")
    location_input = st.text_input("Location (ZIP, city, state e.g. CA, TX)")

    location_input = location_input.lower().strip()
    if 'ca' in location_input or 'california' in location_input:
        location = "California/West Coast"
        sales_multiplier = [0.8, 0.8, 0.7, 0.8, 0.9, 1.3, 1.3, 1.1, 1.0, 1.1, 1.2, 1.2, 1.2, 0.9]
    elif 'tx' in location_input or 'texas' in location_input:
        location = "Texas/South"
        sales_multiplier = [1.3, 1.2, 1.2, 1.1, 1.1, 0.9, 0.9, 1.0, 1.0, 0.9, 0.8, 0.8, 0.8, 0.9]
    elif 'fl' in location_input or 'florida' in location_input:
        location = "Florida"
        sales_multiplier = [1.2, 1.1, 1.1, 1.0, 1.0, 1.1, 1.0, 1.1, 1.0, 1.0, 0.9, 0.9, 0.9, 0.9]
    else:
        location = "National"
        sales_multiplier = [1.0] * len(df)

    vehicle_type = st.selectbox("Vehicle Type", ["All", "Truck", "SUV", "Sedan"])

# Apply filters
df_display = df.copy()
df_display['Est_Sales_2025'] = (df_display['National_Sales'] * sales_multiplier).astype(int)

if vehicle_type != "All":
    df_display = df_display[df_display['Type'] == vehicle_type]

df_display = df_display.sort_values('Est_Sales_2025', ascending=False)

# TAB 1: Market Overview
with tab1:
    st.header(f"Market Overview - {location}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Top Selling Models")
        st.dataframe(df_display[['Full_Name', 'Est_Sales_2025', 'Base_Price_Clean_AvgMile']]
                     .style.format({"Est_Sales_2025": "{:,}", "Base_Price_Clean_AvgMile": "${:,}"}))
    
    with col2:
        st.subheader("Sales Volume Chart")
        chart_df = df_display.head(10)
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.barh(chart_df['Full_Name'][::-1], chart_df['Est_Sales_2025'][::-1], color='#1E88E5')
        ax.set_xlabel("Estimated Sales Volume")
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)

# TAB 2: Valuation & Profit Calculator
with tab2:
    st.header("KBB-Style Valuation & Profit Calculator")

    selected_car = st.selectbox("Select Model", options=df_display['Full_Name'])
    car_row = df_display[df_display['Full_Name'] == selected_car].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        model_year = st.number_input("Model Year", 2010, 2025, 2023)
    with col2:
        odometer_miles = st.number_input("Odometer Miles", 0, 300000, 50000, 1000)
    with col3:
        title_status = st.selectbox("Title Status", ["Clean Title", "Salvage/Rebuilt Title"])

    # KBB-style calculation
    current_year = 2025
    age = current_year - model_year
    if age < 0: age = 0

    avg_annual_miles = 13500
    expected_miles = age * avg_annual_miles
    mile_diff = odometer_miles - expected_miles

    if mile_diff > 0:
        mile_factor = max(0.5, 1 - (mile_diff * 0.0003))
        days_add = int(mile_diff / 5000)
    elif mile_diff < 0:
        mile_factor = 1 - (mile_diff * 0.0004)
        days_add = int(mile_diff / 10000)
    else:
        mile_factor = 1.0
        days_add = 0

    dep_factor = 1.0
    if age == 1:
        dep_factor = 0.80
    elif age > 1:
        dep_factor = 0.80 * (0.90 ** (age - 1))

    if title_status == "Salvage/Rebuilt Title":
        dep_factor *= 0.60
        days_add += 20

    kbb_market_value = int(car_row['Base_Price_Clean_AvgMile'] * dep_factor * mile_factor)
    adjusted_days = max(10, car_row['Base_Days_Clean_AvgMile'] + days_add)

    st.success(f"**Estimated Fair Market Value**: ${kbb_market_value:,}\n\n**Est. Days to Sell**: {adjusted_days} days")

    col1, col2 = st.columns(2)
    with col1:
        buy_price = st.number_input("Your Buy Price", 1000, None, int(kbb_market_value * 0.85), 500)
    with col2:
        sell_price = st.number_input("Your Sell Price", buy_price + 500, None, kbb_market_value, 500)

    gross_profit = sell_price - buy_price
    monthly_cars = st.slider("Monthly Sales Goal", 1, 30, 5)

    st.markdown(f"""
    **Profit Summary**
    - Gross Profit per Car: **${gross_profit:,}**
    - Monthly Profit ({monthly_cars} cars): **${gross_profit * monthly_cars:,}**
    - Yearly Profit: **${gross_profit * monthly_cars * 12:,}**
    """)

    if gross_profit > 6000:
        st.success("Excellent profit potential!")
    elif gross_profit > 2000:
        st.info("Solid margin.")
    else:
        st.warning("Tight margin — consider costs carefully.")

st.caption("Professional tool based on 2025 US used car market data. Estimates only — consult local market.")