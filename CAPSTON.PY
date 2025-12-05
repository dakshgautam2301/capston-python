# -----------------------------------------------------------
# CAPSTONE PROJECT – CAMPUS ENERGY DASHBOARD
# Submitted by: Daksh Gautam
# -----------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------
# TASK 1: READ & CLEAN DATA
# ---------------------------

data_folder = Path("data/")
all_files = list(data_folder.glob("*.csv"))

combined_data = []
logs = []

for file in all_files:
    try:
        df = pd.read_csv(file)

        # Add building name from file name
        df["building"] = file.stem

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce")

        df = df.dropna()  # remove corrupted rows

        combined_data.append(df)

    except Exception as e:
        logs.append(f"Error in file {file}: {e}")

df_combined = pd.concat(combined_data, ignore_index=True)

df_combined.to_csv("cleaned_energy_data.csv", index=False)

print("TASK 1 COMPLETED — Data cleaned and combined.")

# ---------------------------
# TASK 2: AGGREGATION
# ---------------------------

df_combined = df_combined.sort_values("timestamp")
df_combined["date"] = df_combined["timestamp"].dt.date
df_combined["week"] = df_combined["timestamp"].dt.isocalendar().week

# Daily usage
daily_usage = df_combined.groupby(["building", "date"])["kwh"].sum().reset_index()

# Weekly usage
weekly_usage = df_combined.groupby(["building", "week"])["kwh"].mean().reset_index()

# Building summary
building_summary = df_combined.groupby("building")["kwh"].agg(
    total="sum", minimum="min", maximum="max", average="mean"
).reset_index()

building_summary.to_csv("building_summary.csv", index=False)

print("TASK 2 COMPLETED — Aggregation done.")

# ---------------------------
# TASK 3: OOP DESIGN
# ---------------------------

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.readings = []

    def add_reading(self, reading: MeterReading):
        self.readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.readings)

    def generate_report(self):
        values = [r.kwh for r in self.readings]
        return {
            "building": self.name,
            "total": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values)
        }

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def add_reading(self, building_name, reading):
        if building_name not in self.buildings:
            self.buildings[building_name] = Building(building_name)
        self.buildings[building_name].add_reading(reading)

    def generate_all_reports(self):
        return [b.generate_report() for b in self.buildings.values()]

manager = BuildingManager()

# add all readings to OOP manager
for _, row in df_combined.iterrows():
    manager.add_reading(row["building"], MeterReading(row["timestamp"], row["kwh"]))

oop_summary = manager.generate_all_reports()

print("TASK 3 COMPLETED — OOP system created.")

# ---------------------------
# TASK 4: DASHBOARD VISUALS
# ---------------------------

plt.figure(figsize=(15, 10))

# 1. Line chart — Daily consumption
plt.subplot(3, 1, 1)
for b in daily_usage["building"].unique():
    data = daily_usage[daily_usage["building"] == b]
    plt.plot(data["date"], data["kwh"], label=b)
plt.title("Daily Electricity Consumption")
plt.legend()

# 2. Bar chart — Weekly average
plt.subplot(3, 1, 2)
plt.bar(weekly_usage["building"], weekly_usage["kwh"])
plt.title("Weekly Average Electricity Usage")

# 3. Scatter — Peak hours
plt.subplot(3, 1, 3)
plt.scatter(df_combined["timestamp"], df_combined["kwh"])
plt.title("Peak Hour Usage")

plt.tight_layout()
plt.savefig("dashboard.png")

print("TASK 4 COMPLETED — Dashboard saved as dashboard.png")

# ---------------------------
# TASK 5: SUMMARY FILE
# ---------------------------

total_usage = df_combined["kwh"].sum()
highest_building = building_summary.loc[building_summary["total"].idxmax(), "building"]
peak_time = df_combined.loc[df_combined["kwh"].idxmax(), "timestamp"]

summary_text = f"""
CAMPUS ENERGY SUMMARY
-----------------------
Total campus electricity usage: {total_usage:.2f} kWh
Highest consuming building: {highest_building}
Peak load occurred at: {peak_time}

Daily trends and weekly averages stored in output files.
"""

with open("summary.txt", "w") as f:
    f.write(summary_text)

print("TASK 5 COMPLETED — Summary exported.")
