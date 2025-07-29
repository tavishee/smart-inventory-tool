
import streamlit as st
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Smart Inventory Optimization Tool", layout="wide")
st.title("🚗 Smart Inventory Optimization Tool")

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final_merged_car_inventory.csv")
    return df

# -------------------- FILE UPLOAD --------------------
st.sidebar.header("🔄 Data Upload")
uploaded_file = st.sidebar.file_uploader("📁 Upload Updated Inventory CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Using uploaded dataset")
else:
    df = load_data()
    st.sidebar.info("ℹ️ Using default dataset")

# -------------------- TIMESTAMP --------------------
st.sidebar.markdown(f"📅 Last updated: {pd.Timestamp.now().strftime('%d %b %Y, %I:%M %p')}")

# -------------------- ALERT LOGIC --------------------
df['Alert'] = df['DemandScore'].apply(lambda x: "⚠️ Low demand – consider relocation" if x < 50 else "")

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔍 Filters")
city_options = ["All"] + sorted(df['City'].dropna().unique().tolist())
model_options = ["All"] + sorted(df['Base_Model'].dropna().unique().tolist())

selected_city = st.sidebar.selectbox("Filter by City", city_options)
selected_model = st.sidebar.selectbox("Filter by Base Model", model_options)

# -------------------- APPLY FILTERS --------------------
filtered_df = df.copy()
if selected_city != "All":
    filtered_df = filtered_df[filtered_df['City'] == selected_city]
if selected_model != "All":
    filtered_df = filtered_df[filtered_df['Base_Model'] == selected_model]

# -------------------- TABS SETUP --------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Demand Heatmap", 
    "🚨 Alerts", 
    "📦 Inventory", 
    "🔁 Relocation Suggestions"
])

# -------------------- TAB 1: DEMAND HEATMAP --------------------
with tab1:
    st.subheader("📊 Average Demand Score by City")
    chart_data = filtered_df.groupby('City')['DemandScore'].mean().sort_values(ascending=False)
    st.bar_chart(chart_data)

# -------------------- TAB 2: ALERTS --------------------
with tab2:
    st.subheader("🚨 Cars in Low-Demand Cities")
    alerts = filtered_df[filtered_df['Alert'] != ""]
    st.dataframe(alerts[['Car_Name', 'City', 'Base_Model', 'Selling_Price', 'DemandScore', 'Alert']])

# -------------------- TAB 3: FULL INVENTORY --------------------
with tab3:
    st.subheader("📦 Full Car Inventory")
    st.dataframe(filtered_df[['Car_Name', 'Year', 'City', 'Base_Model', 'Selling_Price', 'Kms_Driven', 'Fuel_Type', 'Transmission', 'DemandScore']])

# -------------------- TAB 4: SMART RELOCATION --------------------
with tab4:
    st.subheader("🔁 Relocation Recommendations")
    recommendations = []

    for model in df['Base_Model'].dropna().unique():
        model_df = df[df['Base_Model'] == model]
        low_demand_cities = model_df[model_df['DemandScore'] < 50]['City'].unique()
        high_demand_cities = model_df[model_df['DemandScore'] > 70]['City'].unique()

        for from_city in low_demand_cities:
            for to_city in high_demand_cities:
                if from_city != to_city:
                    recommendations.append({
                        "Model": model,
                        "Move From": from_city,
                        "To": to_city,
                        "Reason": "High demand in destination"
                    })

    relocation_df = pd.DataFrame(recommendations).drop_duplicates()
    st.dataframe(relocation_df)

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with 💡 using Streamlit for smart used-car inventory decisions")
