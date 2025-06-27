import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load data from CSV file
def load_data():
    file_path = r"cleaned_scrapping_provision_from_modified1.csv"
    return pd.read_csv(file_path)

data = load_data()

# Dashboard title
st.title("Scrapping Provision Dashboard")

# Sidebar navigation for pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Summary Dashboard", "Detailed Analysis", "Risk & Financial Insights", "Additional Insights"])

# Page 1: Summary Dashboard
if page == "Summary Dashboard":
 st.header("Page 1: Summary Statistics")
 
 # KPIs: Total Quantity, Total Value, Unique Products
 with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Quantity", f"{data['Quantity'].sum():,.2f}")
    with col2:
        st.metric("Total Value (EGP)", f"{data['Value in EGP'].sum():,.2f}")
    with col3:
        st.metric("Unique Products", len(data["Product"].unique()))

 # Total Value by Segement
 if "Segement" in data.columns:
  st.subheader("Total Value by Segement")
  segement_value = data.groupby("Segement")["Value in EGP"].sum().reset_index()
  fig_segement = px.bar(segement_value, 
   x="Segement", 
   y="Value in EGP", 
   color="Segement", 
   title="Total Value by Segement", 
   labels={"Segement": "Segement", "Value in EGP": "Total Value (EGP)"},
   color_continuous_scale="Viridis", 
   text="Value in EGP")
  fig_segement.update_traces(texttemplate='%{text:.2s}', textposition='outside', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
  fig_segement.update_layout(barmode='group', xaxis_tickangle=-45, xaxis_title='Segement', yaxis_title='Total Value (EGP)', template="plotly_white")
  st.plotly_chart(fig_segement)

 # Total Value by Plant and Segement (Grouped/Stacked Bar Chart)
 if "Plant" in data.columns and "Segement" in data.columns:
  st.subheader("Total Value by Plant and Segement")
  plant_segment_value = data.groupby(["Plant", "Segement"])["Value in EGP"].sum().reset_index()
  fig_plant_segment = px.bar(plant_segment_value, 
   x="Plant", 
   y="Value in EGP", 
   color="Segement", 
   title="Total Value by Plant and Segement", 
   labels={"Plant": "Plant", "Value in EGP": "Total Value (EGP)", "Segement": "Segement"},
   barmode="stack", 
   color_discrete_sequence=px.colors.qualitative.Set2)
  fig_plant_segment.update_layout(xaxis_title='Plant', 
   yaxis_title='Total Value (EGP)', 
   template="plotly_white", 
   xaxis_tickangle=-45)
  st.plotly_chart(fig_plant_segment)

# Page 2: Detailed Analysis
elif page == "Detailed Analysis":
 st.header("Page 2: Detailed Analysis")
 
 # Filter options for month and plant
 month_filter = st.selectbox("Select Month", options=["All"] + list(data["Scrapping Month"].unique()))
 plant_filter = st.selectbox("Select Plant", options=["All"] + list(data["Plant"].unique()))

 # Filter the data based on selected month and plant
 filtered_data = data
 if month_filter != "All":
  filtered_data = filtered_data[filtered_data["Scrapping Month"] == month_filter]
 if plant_filter != "All":
  filtered_data = filtered_data[filtered_data["Plant"] == plant_filter]

 # Total Value per Classification (Bar Chart)
 st.subheader("Total Value per Classification (Plotly)")
 classification_value = filtered_data.groupby("Classification")["Value in EGP"].sum().reset_index()
 fig_classification = px.bar(classification_value, 
  x="Classification", 
  y="Value in EGP", 
  color="Classification", 
  title="Total Value per Classification",
  labels={"Value in EGP": "Total Value (EGP)"},
  color_continuous_scale="Viridis")
 fig_classification.update_layout(xaxis_tickangle=-45, template="plotly_white", yaxis_title="Total Value (EGP)")
 st.plotly_chart(fig_classification)
 
 # Product Details by Classification (Table with Red High Value)
 st.subheader("Product Details by Classification")
 product_table = filtered_data.groupby(["Product", "Classification"])["Value in EGP"].sum().reset_index()
 product_table = product_table.sort_values(by="Value in EGP", ascending=False)
 grand_total_value = product_table["Value in EGP"].sum()
 product_table["% of Grand Total"] = (product_table["Value in EGP"] / grand_total_value) * 100
 product_table["% of Grand Total"] = product_table["% of Grand Total"].apply(lambda x: f"{x:.2f}%")
 def color_high_value(val):
  if val > product_table["Value in EGP"].quantile(0.9):
   return "color: red"
  return ""
 styled_table = product_table.style.applymap(color_high_value, subset=["Value in EGP"])
 st.dataframe(styled_table)

# Page 3: Risk & Financial Insights
elif page == "Risk & Financial Insights":
 st.header("Page 3: Risk and Financial Insights")
 
 # Filter options for plant
 plant_filter = st.selectbox("Select Plant", options=["All"] + list(data["Plant"].unique()))

 # Filter the data based on selected plant
 filtered_data = data if plant_filter == "All" else data[data["Plant"] == plant_filter]
 
 # Pie chart: Risk Level Distribution (Plotly)
 st.subheader("Risk Level Distribution (Plotly)")
 fig = px.pie(filtered_data, names="Risk Level", title="Risk Level Distribution")
 st.plotly_chart(fig)
 
 # Scatter Plot: Value vs. Quantity by Risk Level (Plotly)
 st.subheader("Value vs. Quantity by Risk Level (Plotly)")
 fig = px.scatter(filtered_data, x="Quantity", y="Value in EGP", color="Risk Level", 
  title="Value vs. Quantity by Risk Level")
 st.plotly_chart(fig)
 
 # Boxplot: Value by Risk Level (Matplotlib)
 st.subheader("Value by Risk Level (Matplotlib)")
 plt.figure(figsize=(10, 6))
 filtered_data.boxplot(column="Value in EGP", by="Risk Level", grid=False, patch_artist=True, 
  boxprops=dict(facecolor="lightblue"))
 plt.xlabel("Risk Level")
 plt.ylabel("Value in EGP")
 plt.title("Value Distribution by Risk Level")
 plt.suptitle("")  # Remove default title from boxplot
 st.pyplot(plt)

# Page 4: Additional Insights
elif page == "Additional Insights":
 st.header("Page 4: Three-Level Hierarchical Scrapping Insights")
 
 # Total Value by Level 1
 st.subheader("Total Value by Level 1")
 level1_value = data.groupby("Level 1")["Value in EGP"].sum().reset_index()
 fig_level1 = px.bar(level1_value, 
  x="Level 1", 
  y="Value in EGP", 
  color="Level 1", 
  title="Total Value by Level 1",
  labels={"Value in EGP": "Total Value (EGP)"},
  color_discrete_sequence=px.colors.qualitative.Set3)
 fig_level1.update_layout(xaxis_tickangle=-45, template="plotly_white", yaxis_title="Total Value (EGP)")
 st.plotly_chart(fig_level1)
 
 # Sunburst Chart: Value Distribution across Levels
 st.subheader("Value Distribution across Levels (Sunburst Chart)")
 sunburst_data = data.groupby(["Level 1", "Level 2", "Level 3"])["Value in EGP"].sum().reset_index()
 fig_sunburst = px.sunburst(sunburst_data, 
  path=["Level 1", "Level 2", "Level 3"], 
  values="Value in EGP", 
  title="Value Distribution across Levels",
  color="Level 1",
  color_discrete_sequence=px.colors.qualitative.Pastel)
 fig_sunburst.update_layout(template="plotly_white")
 st.plotly_chart(fig_sunburst)
 
 # Detailed Classification Insights
 st.subheader("Detailed Classification Insights")
 detailed_classification = data.groupby(["Classification", "Level 1", "Level 2", "Level 3"])[["Quantity", "Value in EGP"]].sum().reset_index()
 st.dataframe(detailed_classification)
