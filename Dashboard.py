import streamlit as st
import os
import google.generativeai as genai  # ✅ Import Gemini AI SDK
import json  # ✅ Import JSON module

# 🔹 Streamlit page config
st.set_page_config(page_title="Dashboard", layout="wide")

# 🔹 Authenticate with Gemini AI API key
genai.configure(api_key="AIzaSyAFhsswo0dtOGTRzDRQmbAsupQPSa27oVQ")

# 🔹 Sidebar with logo
with st.sidebar:
    logo_path = os.path.join("assets", "logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.warning("Logo not found in /assets folder!")

# 🔹 Main content
st.title("📋 Dashboard")
st.write("Explore and manage infrastructure data efficiently using this portal. Select an Indian city and get its demographics and various other data metrics.")

# 🔹 Dropdown with 10 popular Indian cities
indian_cities = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]

selected_city = st.selectbox("Select an Indian city:", indian_cities)

# 🔹 Submit button
if st.button("Submit"):
    # ✅ Save the selected city to `selected_city_name.json`
    city_data = {"city": selected_city}

    with open("selected_city_name.json", "w") as city_file:
        json.dump(city_data, city_file)

    st.success(f"✅ Selected city '{selected_city}' saved to selected_city_name.json!")

    # ✅ Prompt for demographics
    demographics_prompt = (
        f"Provide demographics for {selected_city}, India, including:\n"
        "- City size (area in sq km)\n"
        "- Population\n"
        "- Languages spoken\n"
        "- Major industries\n"
        "- Key landmarks\n"
        "- Major Biodiversity issues and solutions\n"
        "- Major Energy issues and solutions\n"
        "- Major Irrigation issues and solutions\n"
        "- Major Urban Infrastructure issues and solutions"
    )

    # ✅ Prompt for bounding box coordinates
    coordinates_prompt = (
        f"Give me the bounding box coordinates (longitude and latitude) of {selected_city} "
        "in the format [x1, y1, x2, y2] where x1 is the lower adjacent longitude, "
        "y1 is the lower adjacent latitude, x2 is the higher adjacent longitude, and y2 is the higher adjacent latitude. "
        "Only return the coordinates in the format [x1, y1, x2, y2] with no additional text."
    )

    try:
        # 🔥 Use Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # ✅ Get demographics
        demographics_response = model.generate_content(demographics_prompt)
        demographics = demographics_response.text.strip()

        # ✅ Get coordinates
        coordinates_response = model.generate_content(coordinates_prompt)
        coordinates = coordinates_response.text.strip()

        # 🔹 Display demographics
        st.subheader(f"Demographics of {selected_city}")
        st.write(demographics)

        # 🔹 Display bounding box coordinates
        st.subheader(f"Bounding Box Coordinates for {selected_city}")
        st.write(coordinates)

        # ✅ Save coordinates to a JSON file
        coords_list = [float(x) for x in coordinates.strip("[]").split(",")]
        data = {
            "city": selected_city,
            "bounding_box": coords_list
        }

        with open("bounding_box.json", "w") as json_file:
            json.dump(data, json_file)

        st.success("✅ Bounding box coordinates saved successfully!")

    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
