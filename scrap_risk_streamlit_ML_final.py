
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

# Load data
df = pd.read_csv("cleaned_scrapping_provision_from_modified1.csv")

# Fix Scrapping Month format
df = df.dropna(subset=["Segement", "Plant", "Product", "Quantity", "Value in EGP", "Scrapping Month"])
df["Scrapping Month"] = pd.to_datetime(df["Scrapping Month"], format="%y-%b", errors="coerce")
df = df.dropna(subset=["Scrapping Month"])
df["Year"] = df["Scrapping Month"].dt.year

st.set_page_config(page_title="Scrap Risk Report", page_icon="📈")
st.title("📈 Scrap Risk Report")

# -------------------------------
# 🔍 Shared Filters
# -------------------------------
st.sidebar.header("Filter Data")
segment_choice = st.sidebar.selectbox("Segment", sorted(df["Segement"].unique()))
plant_options = sorted(df[df["Segement"] == segment_choice]["Plant"].unique())
plant_choice = st.sidebar.selectbox("Plant", plant_options)

year_options = sorted(df["Year"].unique())
year_choice = st.sidebar.selectbox("Scrap Year", year_options)

# Apply filters
filtered_df = df[(df["Segement"] == segment_choice) & 
                 (df["Plant"] == plant_choice) & 
                 (df["Year"] == year_choice)]

# -------------------------------
# 📊 Chart: Risk by Product
# -------------------------------
st.subheader(f"📊 Top Risky Products in {year_choice} ({segment_choice} / {plant_choice})")

if filtered_df.empty:
    st.warning("No data available for this combination.")
else:
    top_n = 10
    top_products = (
        filtered_df.groupby("Product")["Value in EGP"]
        .mean()
        .reset_index()
        .sort_values(by="Value in EGP", ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top_products["Product"], top_products["Value in EGP"], color="darkgreen")
    ax.set_title(f"📊 Top {top_n} Risky Products in {year_choice}")
    ax.set_xlabel("Average Scrap Risk (EGP)")
    ax.invert_yaxis()
    st.pyplot(fig)

# -------------------------------
# 📉 Scrap Risk Level Estimator
# -------------------------------
st.subheader("📉 Scrap Risk Level Estimator (Value-Based)")

est_product_options = sorted(df[(df["Segement"] == segment_choice) & (df["Plant"] == plant_choice)]["Product"].unique())
est_product_choice = st.selectbox("Product", est_product_options)

quantity = st.number_input("Quantity", min_value=1.0, value=10.0)
min_date = date.today() - timedelta(days=365)
max_date = date.today() + timedelta(days=365 * 10)
scrap_date = st.date_input("Scrap Date", value=date.today(), min_value=min_date, max_value=max_date)

# Unit price estimation
product_data = df[(df["Product"] == est_product_choice) & (df["Quantity"] > 0)]
if not product_data.empty:
    unit_price = (product_data["Value in EGP"] / product_data["Quantity"]).mean().round(2)
else:
    unit_price = 0

value_egp = round(quantity * unit_price, 2)

if value_egp <= 1000:
    risk = "Low"
    color = "🟢"
elif value_egp <= 10000:
    risk = "Medium"
    color = "🟡"
else:
    risk = "High"
    color = "🔴"

st.markdown(f"**📅 Scrap Date:** {scrap_date.strftime('%Y-%m-%d')}")
st.markdown(f"**💰 Estimated Total Value:** {value_egp:,} EGP _(Unit Price: {unit_price} EGP)_")
st.markdown(f"**{color} Risk Level:** **{risk}**")
