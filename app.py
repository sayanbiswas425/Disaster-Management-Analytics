from pathlib import Path
import io
import zipfile

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Disaster Management Analytics", page_icon="🚨", layout="wide")

REQUIRED_COLUMNS = {
    "incidents": ["incident_id", "date", "disaster_type", "locality", "severity", "casualties", "injuries", "damage_cost", "status"],
    "shelters": ["shelter_id", "locality", "capacity", "current_occupancy"],
    "responses": ["response_id", "incident_id", "locality", "alert_time", "dispatch_time", "arrival_time", "team"],
    "relief": ["relief_id", "incident_id", "locality", "item", "requested_qty", "delivered_qty"],
    "population": ["locality", "population", "elderly", "disabled", "low_income"],
    "resources": ["resource_id", "resource_type", "locality", "total_units", "available_units"],
    "weather": ["date", "locality", "rainfall_mm", "temperature_c", "wind_kmph", "warning_level"],
    "communication": ["message_id", "date", "locality", "message_type", "channel", "sent", "acknowledged"],
}

st.markdown("# 🚨 Disaster Management Analytics Platform")
st.caption("Upload your project CSV datasets to explore incidents, emergency response, shelters, relief, resources and locality risk.")

with st.sidebar:
    st.header("📂 Dataset Upload")
    uploads = st.file_uploader(
        "Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Upload files named incidents.csv, shelters.csv, responses.csv, relief.csv, population.csv, resources.csv, weather.csv and communication.csv.",
    )
    st.divider()
    st.caption("Tip: You can upload all 8 CSV files together. File names identify each dataset.")

if not uploads:
    st.info("👈 Start by uploading your CSV dataset files from the sidebar.")
    st.subheader("Datasets expected for the complete project")
    st.write("incidents.csv · shelters.csv · responses.csv · relief.csv · population.csv · resources.csv · weather.csv · communication.csv")
    st.markdown("### What this application provides")
    c1, c2, c3 = st.columns(3)
    c1.metric("Analysis", "Automated", "CSV-based")
    c2.metric("Visualizations", "Interactive", "Plotly charts")
    c3.metric("Risk assessment", "Weighted", "Locality-wise")
    st.stop()

frames = {}
errors = []
for uploaded in uploads:
    key = Path(uploaded.name).stem.lower().strip()
    if key not in REQUIRED_COLUMNS:
        errors.append(f"{uploaded.name}: unrecognized filename; expected one of the standard dataset names.")
        continue
    try:
        df = pd.read_csv(uploaded)
        missing = [c for c in REQUIRED_COLUMNS[key] if c not in df.columns]
        if missing:
            errors.append(f"{uploaded.name}: missing columns: {', '.join(missing)}")
            continue
        if "locality" in df.columns:
            df["locality"] = df["locality"].astype(str).str.strip().str.title()
        frames[key] = df
    except Exception as exc:
        errors.append(f"{uploaded.name}: could not read CSV ({exc})")

for error in errors:
    st.error(error)

if not frames:
    st.warning("No valid recognized dataset was uploaded. Check the file names and required columns.")
    st.stop()

st.success(f"Successfully loaded {len(frames)} dataset(s).")
with st.expander("📋 Uploaded dataset overview", expanded=True):
    overview = pd.DataFrame([
        {"Dataset": name + ".csv", "Rows": len(df), "Columns": len(df.columns)}
        for name, df in frames.items()
    ])
    st.dataframe(overview, use_container_width=True, hide_index=True)

available = list(frames.keys())
tabs = st.tabs(["🏠 Overview", "📊 Analysis", "⚠️ Locality Risk", "🗂️ Data Explorer"])

with tabs[0]:
    st.subheader("Executive Overview")
    incidents = frames.get("incidents")
    shelters = frames.get("shelters")
    responses = frames.get("responses")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Incidents", f"{len(incidents):,}" if incidents is not None else "N/A")
    k2.metric("Total Casualties", f"{incidents['casualties'].sum():,}" if incidents is not None else "N/A")
    if shelters is not None:
        cap = shelters["capacity"].sum()
        occ = shelters["current_occupancy"].sum()
        utilization = (occ / cap * 100) if cap else 0
        k3.metric("Shelter Utilization", f"{utilization:.1f}%")
    else:
        k3.metric("Shelter Utilization", "N/A")
    if responses is not None:
        rt = responses.copy()
        rt["alert_time"] = pd.to_datetime(rt["alert_time"], errors="coerce")
        rt["arrival_time"] = pd.to_datetime(rt["arrival_time"], errors="coerce")
        minutes = (rt["arrival_time"] - rt["alert_time"]).dt.total_seconds() / 60
        k4.metric("Average Response Time", f"{minutes.mean():.1f} min" if minutes.notna().any() else "N/A")
    else:
        k4.metric("Average Response Time", "N/A")

    if incidents is not None:
        left, right = st.columns(2)
        with left:
            st.markdown("#### Incidents by severity")
            sev = incidents["severity"].value_counts().rename_axis("Severity").reset_index(name="Incidents")
            st.plotly_chart(px.bar(sev, x="Severity", y="Incidents", color="Severity", title="Incident Severity Distribution"), use_container_width=True)
        with right:
            st.markdown("#### Disaster types")
            typ = incidents["disaster_type"].value_counts().rename_axis("Disaster Type").reset_index(name="Incidents")
            st.plotly_chart(px.pie(typ, names="Disaster Type", values="Incidents", hole=0.45, title="Disaster Type Share"), use_container_width=True)

with tabs[1]:
    st.subheader("Interactive Data Analysis")
    if "incidents" in frames:
        df = frames["incidents"]
        a, b = st.columns(2)
        with a:
            st.plotly_chart(px.histogram(df, x="severity", color="disaster_type", title="Severity by Disaster Type"), use_container_width=True)
        with b:
            loc = df.groupby("locality").size().reset_index(name="Incident Count").sort_values("Incident Count", ascending=False)
            st.plotly_chart(px.bar(loc, x="locality", y="Incident Count", title="Incidents by Locality"), use_container_width=True)
    if "responses" in frames:
        df = frames["responses"].copy()
        df["alert_time"] = pd.to_datetime(df["alert_time"], errors="coerce")
        df["arrival_time"] = pd.to_datetime(df["arrival_time"], errors="coerce")
        df["response_time_min"] = (df["arrival_time"] - df["alert_time"]).dt.total_seconds() / 60
        team = df.groupby("team", as_index=False)["response_time_min"].mean().dropna()
        st.plotly_chart(px.bar(team, x="team", y="response_time_min", title="Average Emergency Response Time by Team", labels={"response_time_min": "Minutes"}), use_container_width=True)
    if "relief" in frames:
        df = frames["relief"].groupby("item", as_index=False)[["requested_qty", "delivered_qty"]].sum()
        melted = df.melt(id_vars="item", var_name="Status", value_name="Quantity")
        st.plotly_chart(px.bar(melted, x="item", y="Quantity", color="Status", barmode="group", title="Relief Demand vs Delivered"), use_container_width=True)
    if not any(x in frames for x in ["incidents", "responses", "relief"]):
        st.info("Upload incidents.csv, responses.csv or relief.csv to view analysis charts.")

with tabs[2]:
    st.subheader("Locality-wise Disaster Risk Assessment")
    needed = {"incidents", "population", "resources", "shelters"}
    if needed.issubset(frames):
        inc = frames["incidents"].copy()
        pop = frames["population"].set_index("locality")
        res = frames["resources"].copy()
        sh = frames["shelters"].copy()
        incident_count = inc.groupby("locality").size().rename("incident_count")
        weights = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        inc["severity_score"] = inc["severity"].map(weights).fillna(0)
        severity = inc.groupby("locality")["severity_score"].sum().rename("total_severity")
        vulnerable = ((pop["elderly"] + pop["disabled"] + pop["low_income"]) / pop["population"] * 100).rename("vulnerable_pct")
        res["readiness_pct"] = res["available_units"] / res["total_units"].replace(0, pd.NA) * 100
        readiness_gap = (100 - res.groupby("locality")["readiness_pct"].mean()).clip(lower=0).rename("readiness_gap")
        sh["utilization_pct"] = sh["current_occupancy"] / sh["capacity"].replace(0, pd.NA) * 100
        shelter_pressure = sh.groupby("locality")["utilization_pct"].mean().rename("shelter_pressure")
        risk = pd.concat([incident_count, severity, vulnerable, readiness_gap, shelter_pressure], axis=1).fillna(0)
        for col in list(risk.columns):
            max_val = risk[col].max()
            risk[col + "_norm"] = risk[col] / max_val * 100 if max_val > 0 else 0
        risk["Risk_Score"] = (0.25 * risk["incident_count_norm"] + 0.25 * risk["total_severity_norm"] + 0.20 * risk["vulnerable_pct_norm"] + 0.15 * risk["readiness_gap_norm"] + 0.15 * risk["shelter_pressure_norm"])
        risk = risk.sort_values("Risk_Score", ascending=False).reset_index(names="Locality")
        risk["Risk Level"] = pd.cut(risk["Risk_Score"], bins=[-0.01, 25, 50, 75, 100.01], labels=["Low", "Moderate", "High", "Critical"])
        st.caption("Risk score uses the same weighted model as your existing analysis: incident frequency 25%, severity 25%, vulnerability 20%, resource readiness gap 15%, shelter pressure 15%.")
        st.plotly_chart(px.bar(risk, x="Locality", y="Risk_Score", color="Risk Level", title="Locality Risk Score (0–100)"), use_container_width=True)
        st.dataframe(risk.round(2), use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download Locality Risk Report", risk.to_csv(index=False).encode("utf-8"), "locality_risk_report.csv", "text/csv")
    else:
        missing = sorted(needed - set(frames))
        st.warning("For the full weighted risk model, upload: " + ", ".join(x + ".csv" for x in missing))

with tabs[3]:
    st.subheader("Dataset Explorer")
    selected = st.selectbox("Choose an uploaded dataset", available)
    df = frames[selected]
    st.write(f"**{selected}.csv** — {len(df):,} rows × {len(df.columns)} columns")
    st.dataframe(df.head(500), use_container_width=True)
    st.download_button("⬇️ Download this dataset", df.to_csv(index=False).encode("utf-8"), f"{selected}_cleaned.csv", "text/csv")

st.divider()
st.caption("Disaster Management Analytics Platform | Academic Project")
