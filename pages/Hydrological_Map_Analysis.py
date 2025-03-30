import streamlit as st
import ee
import numpy as np
from datetime import datetime
import torch
import torchvision.transforms as T
from PIL import Image
import json
import matplotlib.pyplot as plt

import ee

# Initialize Earth Engine with a specific project ID
ee.Initialize(project='your-project-id')  # Replace 'your-project-id' with your actual project ID


# Initialize Google Earth Engine
ee.Initialize()

# 🔹 Streamlit UI
st.set_page_config(page_title="Water Resource Analysis (20 Years)", layout="wide")
st.title("🌍 Water Resource Analysis Over 20 Years")
st.write("Fetching and analyzing 20 yearly satellite images to measure water resource changes.")

# ✅ Load Bounding Box from JSON
bbox_file = "bounding_box.json"  # Ensure this file exists

try:
    with open(bbox_file, "r") as f:
        bbox_data = json.load(f)
        bbox = bbox_data["bounding_box"]
        min_lon, min_lat, max_lon, max_lat = bbox
        st.success(f"✅ Bounding Box Loaded: {bbox}")
except FileNotFoundError:
    st.error(f"❌ `bounding_box.json` not found!")
    st.stop()

# 🔥 Date Range
start_year = 2005
end_year = 2024

# ✅ Fetch Satellite Images Using Google Earth Engine
def fetch_satellite_image(year):
    st.info(f"🛰️ Fetching satellite image for {year}...")

    # Define the region of interest using bounding box
    geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

    # Load the Sentinel-2 satellite image collection and filter by date
    image_collection = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(geometry) \
        .filterDate(f"{year}-01-01", f"{year}-12-31") \
        .median()  # Using the median image for the year

    # Select bands and visualize
    image = image_collection.select(['B4', 'B3', 'B2'])  # Red, Green, Blue bands

    # Clip to region of interest
    clipped_image = image.clip(geometry)

    # Convert the image to an 8-bit format for display
    img_array = np.array(clipped_image.getMapId())
    img = Image.fromarray(img_array)

    return img, year

# ✅ ML Model for Water Detection
def segment_water(image):
    img_tensor = T.Compose([
        T.Resize((512, 512)),
        T.ToTensor()
    ])(image).unsqueeze(0)

    # Pre-trained DeepLabV3 segmentation model
    model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet101', pretrained=True)
    model.eval()

    with torch.no_grad():
        output = model(img_tensor)['out'][0]
        output = torch.argmax(output, dim=0).byte().cpu().numpy()

    # Water detection logic (class 1 = water)
    water_mask = (output == 1)

    # Apply colors: Blue for water, white for land
    result = np.zeros((512, 512, 3), dtype=np.uint8)
    result[water_mask] = [0, 0, 255]  # Blue for water
    result[~water_mask] = [255, 255, 255]  # White for land

    # Calculate water coverage percentage
    total_pixels = output.size
    water_pixels = np.sum(water_mask)
    water_coverage = (water_pixels / total_pixels) * 100

    return Image.fromarray(result), water_coverage

# ✅ Parallel Image Fetching
def fetch_all_images():
    years = list(range(start_year, end_year + 1))
    images = []
    water_percentages = []

    for year in years:
        img, year = fetch_satellite_image(year)
        if img:
            segmented_img, water_percentage = segment_water(img)
            images.append((img, segmented_img, year, water_percentage))
            water_percentages.append((year, water_percentage))
        else:
            st.warning(f"❌ No image fetched for year {year}.")
    
    return images, water_percentages

# ✅ Plot Water Coverage Trend
def plot_water_trend(water_percentages):
    years = [year for year, _ in water_percentages]
    percentages = [percentage for _, percentage in water_percentages]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(years, percentages, marker='o', color='blue', linestyle='-')

    ax.set_title("Water Resource Trend Over 20 Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Water Coverage (%)")
    ax.grid(True)

    st.pyplot(fig)

# ✅ Display Results
if st.button("Analyze 20 Years"):
    images, water_percentages = fetch_all_images()

    if images:
        # 🔹 Display all 20 images with segmentation
        st.write("🖼️ Displaying 20 images with segmentation and water coverage...")

        # Display segmented images for each year
        for i, (img, segmented_img, year, water_percentage) in enumerate(images):
            st.write(f"### Year: {year} - Water Coverage: {water_percentage:.2f}%")
            st.image(segmented_img, caption=f"Water Segmentation {year} ({water_percentage:.2f}%)", use_column_width=True)

        # ✅ Display Water Trend Graph
        st.write("📊 **Water Coverage Trend Over 20 Years:**")
        plot_water_trend(water_percentages)
    else:
        st.warning("❌ No images were processed.")
