import streamlit as st
import planetary_computer
import pystac_client
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase

# 🔹 Streamlit UI
st.set_page_config(page_title="Urban Density Visualization", layout="wide")

# 🔹 Sidebar with logo
with st.sidebar:
    st.image("assets/logo.jpg", use_container_width=True)

st.title("🏬 Urban Density Map")
st.write("A visual representation of building distribution and city expansion trends. It highlights built-up areas, open spaces, and urban growth over time. Useful for city planning, infrastructure development, and land-use analysis.")


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

# 🔹 Display Urban Density images with scale and legend
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

            # 🔹 Invert NDVI for urban density
            urban_density = 1 - ndvi_data

            # 🔹 Enhance contrast (stretching the values)
            urban_density = (urban_density - np.min(urban_density)) / (np.max(urban_density) - np.min(urban_density))
            urban_density = np.clip(urban_density, 0, 1)

        # ✅ Display Urban Density image with scale and legend
        fig, ax = plt.subplots(figsize=(12, 8))

        # Urban Density Image (Black & White)
        img = ax.imshow(urban_density, cmap="gray", norm=Normalize(vmin=0, vmax=1))
        ax.set_title(f"Urban Density - {image_date} ({idx + 1}/{len(items)})", fontsize=14)
        ax.axis("off")

        # 🔹 Add color scale on the right
        cbar_ax = fig.add_axes([0.85, 0.2, 0.03, 0.6])  # [x, y, width, height]
        cbar = ColorbarBase(cbar_ax, cmap="gray", norm=Normalize(vmin=0, vmax=1))
        cbar.set_label("Urban Density", fontsize=12)
        cbar.set_ticks([0, 0.5, 1])
        cbar.set_ticklabels(["Dense (Black)", "Medium", "Sparse (White)"])

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error processing image {idx + 1}: {e}")