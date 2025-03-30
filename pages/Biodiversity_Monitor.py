import streamlit as st
import planetary_computer
import pystac_client
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import json

# 🔹 Streamlit UI
st.set_page_config(page_title="Environmental & Recreational Areas", layout="wide")

# 🔹 Sidebar with logo
with st.sidebar:
    st.image("assets/logo.jpg", use_container_width=True)

st.title("🪴 Biodiversity Monitor")
st.write("A visual tool that tracks vegetation coverage and ecosystem diversity around a city. It highlights green spaces, plant density, and environmental changes over time. Useful for conservation efforts, urban planning, and ecological studies.")


# ✅ Read bounding box coordinates from JSON file
json_file_path = "bounding_box.json"

try:
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
        location_bbox = data["bounding_box"]
        st.success(f"✅ Loaded coordinates for {data['city']}: {location_bbox}")
except FileNotFoundError:
    st.error("❌ Bounding box file not found.")
    st.stop()

# 🔹 Select number of images
num_images = st.slider("Select number of images to display:", min_value=1, max_value=55, value=5)

# 🔹 Connect to Azure STAC API
catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

# 🔹 Search for Sentinel-2 L2A images (2023)
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=location_bbox,
    datetime="2023-01-01/2023-12-31",
    query={"eo:cloud_cover": {"lt": 10}}  # Use cloud-free images
)

# 🔹 Get available images
items = list(search.items())[:num_images]

if not items:
    st.warning("❌ No suitable images found.")
    st.stop()

st.success(f"✅ Found {len(items)} images.")

# 🔹 Display NDVI images
for idx, item in enumerate(items):
    try:
        # ✅ Sign the item for access
        item = planetary_computer.sign(item)

        # ✅ Extract date from metadata
        image_date = item.properties.get("datetime", "Unknown Date").split("T")[0]

        # ✅ Get NDVI preview URL
        ndvi_url = item.assets["rendered_preview"].href

        # ✅ Open and process NDVI image
        with rasterio.open(ndvi_url) as src:
            ndvi_data = src.read(1)
            ndvi_data = np.nan_to_num(ndvi_data)

        # ✅ Display NDVI image
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(ndvi_data, cmap="Greens")
        ax.set_title(f"NDVI (Green Areas) - {image_date} ({idx + 1}/{len(items)})")
        ax.axis("off")
        
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error processing image {idx+1}:{e}")