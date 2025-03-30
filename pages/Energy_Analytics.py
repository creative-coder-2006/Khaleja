import json
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import random

# ✅ Load bounding box from JSON
json_file_path = "bounding_box.json"

st.title("⚡Energy Analytics")
st.write("Energy analytics provides insights into energy consumption, efficiency, and trends across a city. It helps identify areas for optimization, reduce wastage, and support sustainable energy planning.")

try:
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
        bbox = data["bounding_box"]
        city = data["city"]
        st.success(f"✅ Loaded coordinates for {city}: {bbox}")
except FileNotFoundError:
    st.error("❌ Bounding box file not found.")
    exit()

# ✅ Generate random energy consumption and outages data
dates = [datetime(2023, month, 1) for month in range(1, 13)]
consumption = [random.randint(300, 600) for _ in range(12)]  # Random values between 300-600 kWh
outages = [random.randint(2, 20) for _ in range(12)]          # Random values between 2-20 outages

# ✅ Streamlit UI Components
st.title("Energy Consumption and Outages Visualization (Randomized Data)")
st.write(f"📍 **Location:** {city}")
st.write(f"🌐 **Coordinates:** {bbox}")

# ✅ Energy Consumption Plot
st.subheader("🔋 Energy Consumption Over Time (2023)")
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(dates, consumption, label="Energy Consumption (kWh)", color="green", marker="o")
ax1.set_ylabel("Energy Consumption (kWh)")
ax1.set_xlabel("Date")
ax1.set_title(f"Energy Consumption in {city} (2023)")
ax1.grid(True)
ax1.legend()

# Display the Energy Consumption Graph
st.pyplot(fig1)

# ✅ Energy Outages Plot
st.subheader("⚠️ Energy Outages Over Time (2023)")
fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.plot(dates, outages, label="Energy Outages (Count)", color="red", marker="x")
ax2.set_ylabel("Outages (Count)")
ax2.set_xlabel("Date")
ax2.set_title(f"Energy Outages in {city} (2023)")
ax2.grid(True)
ax2.legend()

# Display the Energy Outages Graph
st.pyplot(fig2)
