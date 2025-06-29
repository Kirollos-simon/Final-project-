import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

st.set_page_config(page_title="Scrap Risk Report", page_icon="📈")
st.title("Scrap Risk Report")

data = pd.read_csv("cleaned_scrapping_provision_from_modified1.csv")
data = data.dropna(subset=["Segement", "Plant", "Product", "Quantity", "Value in EGP", "Scrapping Month"])
data["Scrapping Month"] = pd.to_datetime(data["Scrapping Month"], format="%y-%b", errors="coerce")
data = data.dropna(subset=["Scrapping Month"])
data["Year"] = data["Scrapping Month"].dt.year

seg1 = st.sidebar.selectbox("Segment", sorted(data["Segement"].unique()))
plants = data[data["Segement"] == seg1]["Plant"].unique()
plant1 = st.sidebar.selectbox("Plant", sorted(plants))
years = data["Year"].unique()
year1 = st.sidebar.selectbox("Scrap Year", sorted(years))

df1 = data[(data["Segement"] == seg1) & (data["Plant"] == plant1) & (data["Year"] == year1)]

st.subheader("Risky Products")

if df1.empty:
    st.write("No records found.")
else:
    df2 = df1.groupby("Product")["Value in EGP"].mean()
    df3 = df2.reset_index()
    df4 = df3.sort_values("Value in EGP", ascending=False)
    df5 = df4.head(10)

    fig, ax = plt.subplots()
    ax.barh(df5["Product"], df5["Value in EGP"], color="green")
    ax.set_title("Top Products")
    ax.set_xlabel("Avg Value")
    ax.invert_yaxis()
    st.pyplot(fig)

st.subheader("Risk Estimate")

prods = data[(data["Segement"] == seg1) & (data["Plant"] == plant1)]["Product"].unique()
prod1 = st.selectbox("Product", sorted(prods))
qty = st.number_input("Quantity", min_value=1.0, value=10.0)
d1 = date.today()
d2 = d1 + timedelta(days=365 * 10)
scrap_d = st.date_input("Scrap Date", value=d1, min_value=d1 - timedelta(days=365), max_value=d2)

dfp = data[(data["Product"] == prod1) & (data["Quantity"] > 0)]
if not dfp.empty:
    unit = (dfp["Value in EGP"] / dfp["Quantity"]).mean()
    unit = round(unit, 2)
else:
    unit = 0

valx = qty * unit
valx = round(valx, 2)

if valx <= 1000:
    level = "Low"
    sym = "🟢"
elif valx <= 10000:
    level = "Medium"
    sym = "🟡"
else:
    level = "High"
    sym = "🔴"

st.write("Scrap Date:", scrap_d.strftime("%Y-%m-%d"))
st.write("Total Value:", valx, "EGP  (Unit:", unit, ")")
st.write(sym, "Risk Level:", level)
