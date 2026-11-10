import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set visual theme for charts and create output folder
sns.set_theme(style="whitegrid")
os.makedirs("outputs/charts", exist_ok=True)
print("⏳ Loading datasets for analysis...")
incidents = pd.read_csv("data/incidents.csv")
shelters = pd.read_csv("data/shelters.csv")
responses = pd.read_csv("data/responses.csv")
relief = pd.read_csv("data/relief.csv")
population = pd.read_csv("data/population.csv")
resources = pd.read_csv("data/resources.csv")
weather = pd.read_csv("data/weather.csv")
communication = pd.read_csv("data/communication.csv")
# Standardize locality text formatting
for df in [incidents, shelters, responses, relief, population, resources, weather, communication]:
    if "locality" in df.columns:
        df["locality"] = df["locality"].str.strip().str.title()

# Convert timestamp strings into pandas datetime objects
responses["alert_time"] = pd.to_datetime(responses["alert_time"])
responses["dispatch_time"] = pd.to_datetime(responses["dispatch_time"])
responses["arrival_time"] = pd.to_datetime(responses["arrival_time"])
responses["closure_time"] = pd.to_datetime(responses["closure_time"])
print("⚙️ Computing KPIs and derived features...")

# 1. Shelter Utilization & Vacancy
shelters["utilization_pct"] = (shelters["current_occupancy"] / shelters["capacity"]) * 100
shelters["vacancy"] = shelters["capacity"] - shelters["current_occupancy"]

# 2. Response & Dispatch Delays (in minutes)
responses["dispatch_delay_min"] = (responses["dispatch_time"] - responses["alert_time"]).dt.total_seconds() / 60
responses["response_time_min"] = (responses["arrival_time"] - responses["alert_time"]).dt.total_seconds() / 60

# 3. Relief Fulfillment Rates & Gaps
relief["delivery_rate_pct"] = (relief["delivered_qty"] / relief["requested_qty"]) * 100
relief["relief_gap"] = relief["requested_qty"] - relief["delivered_qty"]

# 4. Resource & Communication Readiness
resources["readiness_pct"] = (resources["available_units"] / resources["total_units"]) * 100
communication["coverage_pct"] = (communication["acknowledged"] / communication["sent"]) * 100
# Aggregate incident frequency and weighted severity scores by locality
inc_count = incidents.groupby("locality").size().rename("incident_count")
severity_weights = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
incidents["severity_score"] = incidents["severity"].map(severity_weights)
sev_score = incidents.groupby("locality")["severity_score"].sum().rename("total_severity")

# Calculate vulnerable population percentage
pop_summary = population.set_index("locality")
vulnerable_pct = ((pop_summary["elderly"] + pop_summary["disabled"] + pop_summary["low_income"]) / pop_summary["population"] * 100).rename("vulnerable_pct")

# Calculate resource readiness gaps and shelter pressure
readiness_gap = (100 - resources.groupby("locality")["readiness_pct"].mean()).clip(lower=0).rename("readiness_gap")
shelter_press = shelters.groupby("locality")["utilization_pct"].mean().rename("shelter_pressure")

# Combine all factors into a single dataframe
risk_df = pd.concat([inc_count, sev_score, vulnerable_pct, readiness_gap, shelter_press], axis=1).fillna(0)

# Normalize each factor from 0 to 100 scale
for col in risk_df.columns:
    max_val = risk_df[col].max()
    risk_df[col + "_norm"] = (risk_df[col] / max_val * 100) if max_val > 0 else 0

# Calculate weighted Risk Score (Weights: 25% Freq, 25% Severity, 20% Vulnerability, 15% Readiness Gap, 15% Shelter Pressure)
risk_df["Risk_Score"] = (
    0.25 * risk_df["incident_count_norm"] +
    0.25 * risk_df["total_severity_norm"] +
    0.20 * risk_df["vulnerable_pct_norm"] +
    0.15 * risk_df["readiness_gap_norm"] +
    0.15 * risk_df["shelter_pressure_norm"]
)

print("\n--- TOP 5 HIGHEST RISK LOCALITIES ---")
print(risk_df[["Risk_Score"]].sort_values(by="Risk_Score", ascending=False).head(5))
print("\n📊 Generating Exploratory Analysis Charts...")

# Chart 1: Incident Frequency & Severity Distribution by Locality
plt.figure(figsize=(12, 6))
sns.countplot(data=incidents, x="locality", hue="severity", palette="YlOrRd")
plt.title("Incident Frequency & Severity Distribution by Locality", fontsize=14, pad=12)
plt.xlabel("Locality", fontsize=11)
plt.ylabel("Incident Count", fontsize=11)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/charts/incidents_by_locality.png")
plt.close()

# Chart 2: Average Emergency Response Time by Team
plt.figure(figsize=(10, 5))
avg_resp = responses.groupby("team")["response_time_min"].mean().reset_index().sort_values("response_time_min")
sns.barplot(data=avg_resp, x="team", y="response_time_min", palette="Blues_d", hue="team", legend=False)
plt.title("Average Emergency Response Time by Team (Minutes)", fontsize=14, pad=12)
plt.xlabel("Emergency Response Team", fontsize=11)
plt.ylabel("Mean Response Time (Min)", fontsize=11)
plt.tight_layout()
plt.savefig("outputs/charts/response_time_by_team.png")
plt.close()

# Chart 3: Relief Demand vs Delivered Gap by Item
plt.figure(figsize=(10, 5))
relief_item = relief.groupby("item")[["requested_qty", "delivered_qty"]].sum().reset_index()
relief_melted = pd.melt(relief_item, id_vars=["item"], value_vars=["requested_qty", "delivered_qty"], var_name="Status", value_name="Quantity")
sns.barplot(data=relief_melted, x="item", y="Quantity", hue="Status", palette="muted")
plt.title("Relief Demand vs Fulfillment Gap by Item", fontsize=14, pad=12)
plt.xlabel("Relief Item", fontsize=11)
plt.ylabel("Total Quantity", fontsize=11)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("outputs/charts/relief_gap_by_item.png")
plt.close()

print("\n✅ Analysis complete! All calculated KPIs computed and charts saved inside 'outputs/charts/'[cite: 5].")
