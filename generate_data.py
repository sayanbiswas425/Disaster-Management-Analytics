import os
import random
import numpy as np
import pandas as pd

# Create output folder
os.makedirs("data", exist_ok=True)

# Set random seeds for exact reproducibility
np.random.seed(42)
random.seed(42)

# Define localities (Localities A through T)
localities = [f"Locality {chr(65+i)}" for i in range(20)]
disaster_types = ["Flood", "Cyclone", "Heatwave", "Waterlogging", "Landslide", "Earthquake", "Wildfire"]
severities = ["Low", "Medium", "High", "Critical"]
teams = [f"Team {name}" for name in ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]]
relief_items = ["Food Packets", "Drinking Water (L)", "Medical Kits", "Blankets", "Tents", "Hygiene Kits", "Generators"]

print("⏳ Generating 8,000+ dataset records across 8 files...")

# ---------------------------------------------------------
# 1. incidents.csv (8,000 records)
# ---------------------------------------------------------
n_incidents = 8000
incident_ids = [f"INC{i+1:05d}" for i in range(n_incidents)]
dates = pd.date_range("2024-01-01", "2026-09-30", periods=n_incidents)

incidents_df = pd.DataFrame({
    "incident_id": incident_ids,
    "date": dates.strftime("%Y-%m-%d"),
    "disaster_type": np.random.choice(disaster_types, n_incidents),
    "locality": np.random.choice(localities, n_incidents),
    "severity": np.random.choice(severities, n_incidents, p=[0.35, 0.40, 0.18, 0.07]),
    "casualties": np.random.poisson(lam=0.8, size=n_incidents),
    "injuries": np.random.poisson(lam=3.5, size=n_incidents),
    "damage_cost": np.random.randint(5000, 750000, n_incidents),
    "status": np.random.choice(["Active", "Closed"], n_incidents, p=[0.05, 0.95])
})
incidents_df.to_csv("data/incidents.csv", index=False)

# ---------------------------------------------------------
# 2. shelters.csv (500 records)
# ---------------------------------------------------------
shelters_df = pd.DataFrame({
    "shelter_id": [f"SH{i+1:04d}" for i in range(500)],
    "locality": np.random.choice(localities, 500),
    "capacity": np.random.randint(200, 1500, 500),
    "current_occupancy": np.random.randint(20, 1400, 500),
    "beds": np.random.randint(150, 1200, 500),
    "medical_support": np.random.choice(["Yes", "No"], 500, p=[0.85, 0.15]),
    "status": np.random.choice(["Operational", "Full", "Maintenance"], 500, p=[0.75, 0.18, 0.07])
})
shelters_df.to_csv("data/shelters.csv", index=False)

# ---------------------------------------------------------
# 3. responses.csv (8,000 records)
# ---------------------------------------------------------
alert_times = pd.to_datetime(incidents_df["date"]) + pd.to_timedelta(np.random.randint(0, 1440, n_incidents), unit="m")
dispatch_times = alert_times + pd.to_timedelta(np.random.randint(3, 40, n_incidents), unit="m")
arrival_times = dispatch_times + pd.to_timedelta(np.random.randint(8, 120, n_incidents), unit="m")
closure_times = arrival_times + pd.to_timedelta(np.random.randint(60, 2880, n_incidents), unit="m")

responses_df = pd.DataFrame({
    "response_id": [f"RES{i+1:05d}" for i in range(n_incidents)],
    "incident_id": incident_ids,
    "locality": incidents_df["locality"],
    "alert_time": alert_times.dt.strftime("%Y-%m-%d %H:%M:%S"),
    "dispatch_time": dispatch_times.dt.strftime("%Y-%m-%d %H:%M:%S"),
    "arrival_time": arrival_times.dt.strftime("%Y-%m-%d %H:%M:%S"),
    "closure_time": closure_times.dt.strftime("%Y-%m-%d %H:%M:%S"),
    "team": np.random.choice(teams, n_incidents)
})
responses_df.to_csv("data/responses.csv", index=False)

# ---------------------------------------------------------
# 4. relief.csv (8,000 records)
# ---------------------------------------------------------
n_relief = 8000
req = np.random.randint(100, 5000, n_relief)
disp = (req * np.random.uniform(0.75, 1.0, n_relief)).astype(int)
deliv = (disp * np.random.uniform(0.80, 1.0, n_relief)).astype(int)

relief_df = pd.DataFrame({
    "relief_id": [f"REL{i+1:05d}" for i in range(n_relief)],
    "incident_id": np.random.choice(incident_ids, n_relief),
    "locality": np.random.choice(localities, n_relief),
    "item": np.random.choice(relief_items, n_relief),
    "requested_qty": req,
    "dispatched_qty": disp,
    "delivered_qty": deliv,
    "delivery_date": np.random.choice(incidents_df["date"], n_relief)
})
relief_df.to_csv("data/relief.csv", index=False)

# ---------------------------------------------------------
# 5. population.csv (20 localities)
# ---------------------------------------------------------
pop_df = pd.DataFrame({
    "locality": localities,
    "population": np.random.randint(25000, 150000, 20),
    "elderly": np.random.randint(2500, 18000, 20),
    "disabled": np.random.randint(600, 4500, 20),
    "low_income": np.random.randint(8000, 45000, 20),
    "children": np.random.randint(5000, 30000, 20),
    "households": np.random.randint(6000, 35000, 20)
})
pop_df.to_csv("data/population.csv", index=False)

# ---------------------------------------------------------
# 6. resources.csv (500 records)
# ---------------------------------------------------------
resource_types = ["Ambulance", "Rescue Boat", "Medical Team", "Fire Engine", "Generator", "Mobile Kitchen"]
res_records = []
for i in range(500):
    loc = np.random.choice(localities)
    rt = np.random.choice(resource_types)
    total = np.random.randint(10, 100)
    avail = np.random.randint(1, total + 1)
    res_records.append({
        "resource_id": f"RES{i+1:04d}",
        "resource_type": rt,
        "locality": loc,
        "total_units": total,
        "available_units": avail,
        "status": "Ready" if (avail / total) > 0.4 else "Critical Shortage"
    })
resources_df = pd.DataFrame(res_records)
resources_df.to_csv("data/resources.csv", index=False)

# ---------------------------------------------------------
# 7. weather.csv (8,000 records)
# ---------------------------------------------------------
weather_dates = pd.date_range("2024-01-01", "2026-09-30", periods=400)
weather_records = []
count = 0
for d in weather_dates:
    for loc in localities:
        if count >= 8000:
            break
        weather_records.append({
            "date": d.strftime("%Y-%m-%d"),
            "locality": loc,
            "rainfall_mm": round(max(0, np.random.normal(30, 45)), 1),
            "temperature_c": round(np.random.normal(30, 6), 1),
            "wind_kmph": round(np.random.normal(25, 18), 1),
            "warning_level": np.random.choice(["Green", "Yellow", "Orange", "Red"], p=[0.55, 0.28, 0.12, 0.05])
        })
        count += 1
weather_df = pd.DataFrame(weather_records)
weather_df.to_csv("data/weather.csv", index=False)

# ---------------------------------------------------------
# 8. communication.csv (8,000 records)
# ---------------------------------------------------------
comm_df = pd.DataFrame({
    "message_id": [f"MSG{i+1:05d}" for i in range(8000)],
    "date": np.random.choice(incidents_df["date"], 8000),
    "locality": np.random.choice(localities, 8000),
    "message_type": np.random.choice(["Evacuation", "Weather Alert", "Relief Info", "Safety Tips"], 8000),
    "channel": np.random.choice(["SMS", "Radio", "PA System", "App"], 8000),
    "sent": np.random.randint(1000, 25000, 8000),
    "acknowledged": np.random.randint(500, 22000, 8000)
})
comm_df.to_csv("data/communication.csv", index=False)

print("✅ Success! All 8 large CSV files generated in 'data/':")
print(f" - incidents.csv:     {incidents_df.shape[0]:,} rows")
print(f" - responses.csv:     {responses_df.shape[0]:,} rows")
print(f" - relief.csv:        {relief_df.shape[0]:,} rows")
print(f" - weather.csv:       {weather_df.shape[0]:,} rows")
print(f" - communication.csv: {comm_df.shape[0]:,} rows")
print(f" - shelters.csv:      {shelters_df.shape[0]:,} rows")
print(f" - resources.csv:     {resources_df.shape[0]:,} rows")
print(f" - population.csv:    {pop_df.shape[0]:,} rows")
