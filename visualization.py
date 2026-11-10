import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set visualization theme and create output directory
sns.set_theme(style="whitegrid")
os.makedirs("outputs/charts", exist_ok=True)

print("⏳ Loading datasets...")

# 1. Load Datasets
incidents = pd.read_csv("data/incidents.csv")
shelters = pd.read_csv("data/shelters.csv")
responses = pd.read_csv("data/responses.csv")
relief = pd.read_csv("data/relief.csv")

# Standardize locality formatting
for df in [incidents, shelters, responses, relief]:
    if "locality" in df.columns:
        df["locality"] = df["locality"].str.strip().str.title()

# Convert datetime columns for response time calculations
responses["alert_time"] = pd.to_datetime(responses["alert_time"])
responses["arrival_time"] = pd.to_datetime(responses["arrival_time"])
responses["response_time_min"] = (
    responses["arrival_time"] - responses["alert_time"]
).dt.total_seconds() / 60

# 2. Calculate Executive Key Performance Indicators (KPIs)
total_incidents = len(incidents)
total_casualties = incidents["casualties"].sum()
shelter_utilization_pct = round(
    shelters["current_occupancy"].sum() / shelters["capacity"].sum() * 100, 1
)
avg_response_time = round(responses["response_time_min"].mean(), 1)

print("\n==================================================")
print("📊 EXECUTIVE KEY PERFORMANCE INDICATORS (KPIs)")
print("==================================================")
print(f" • Total Incidents Recorded:     {total_incidents:,}")
print(f" • Total Casualties:             {total_casualties:,}")
print(
    f" • Overall Shelter Utilization:  {shelter_utilization_pct}%"
)
print(f" • Average Response Time:        {avg_response_time} minutes")
print("==================================================\n")

# 3. Generate Matplotlib & Seaborn Visualizations
print("📊 Generating and saving charts into 'outputs/charts/'...")

# --- Chart 1: Incidents by Severity ---
plt.figure(figsize=(8, 5))
sns.countplot(
    data=incidents,
    x="severity",
    order=["Low", "Medium", "High", "Critical"],
    palette="YlOrRd",
    hue="severity",
    legend=False,
)
plt.title(
    "Incident Frequency Across Severity Levels", fontsize=14, pad=12, weight="bold"
)
plt.xlabel("Severity Level", fontsize=11)
plt.ylabel("Incident Count", fontsize=11)
plt.tight_layout()
plt.savefig("outputs/charts/incidents_by_severity.png")
plt.close()

# --- Chart 2: Shelter Occupancy vs Capacity (Top 10 Shelters) ---
plt.figure(figsize=(12, 6))
shelter_summary = (
    shelters.groupby("shelter_id")[["capacity", "current_occupancy"]]
    .sum()
    .reset_index()
    .head(10)
)
shelter_melted = pd.melt(
    shelter_summary,
    id_vars=["shelter_id"],
    value_vars=["capacity", "current_occupancy"],
    var_name="Metric",
    value_name="Count",
)
sns.barplot(
    data=shelter_melted, x="shelter_id", y="Count", hue="Metric", palette="muted"
)
plt.title(
    "Top Shelters: Capacity vs. Current Occupancy",
    fontsize=14,
    pad=12,
    weight="bold",
)
plt.xlabel("Shelter ID", fontsize=11)
plt.ylabel("People Count / Beds", fontsize=11)
plt.xticks(rotation=45)
plt.legend(title="Status")
plt.tight_layout()
plt.savefig("outputs/charts/shelter_capacity_vs_occupancy.png")
plt.close()

# --- Chart 3: Response Time Distribution by Team ---
plt.figure(figsize=(10, 5))
sns.boxplot(
    data=responses,
    x="team",
    y="response_time_min",
    palette="Blues",
    hue="team",
    legend=False,
)
plt.title(
    "Emergency Response Time Distribution by Team",
    fontsize=14,
    pad=12,
    weight="bold",
)
plt.xlabel("Emergency Team", fontsize=11)
plt.ylabel("Response Time (Minutes)", fontsize=11)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("outputs/charts/response_time_boxplot.png")
plt.close()

print(
    "✅ Success! All KPI reports printed and high-resolution charts saved to 'outputs/charts/'."
)
