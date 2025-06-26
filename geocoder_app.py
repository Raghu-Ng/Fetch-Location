import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="Geocoder", layout="centered")
st.title("Address to Coordinates App 🌍")

with st.sidebar:
    st.subheader("🔑 API Key Setup")
    api_key_input = st.text_input("Enter your OpenCage API Key", type="password", value=st.session_state.get("api_key", ""))
    if api_key_input:
        st.session_state["api_key"] = api_key_input
    if not st.session_state.get("api_key"):
        st.warning("Please enter your OpenCage API Key to use the app.")
        st.stop()
API_KEY = st.session_state["api_key"]

# Caching the geocoding request
@st.cache_data(ttl=3600)
def geocode_address(address):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={API_KEY}"
    return requests.get(url).json()

@st.cache_data(ttl=3600)
def reverse_geocode(lat, lng):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lng}&key={API_KEY}"
    return requests.get(url).json()

# -------------------------
# Address to Coordinates
address = st.text_input("Enter an address")

if address:
    data = geocode_address(address)
    if data["results"]:
        lat = data["results"][0]["geometry"]["lat"]
        lng = data["results"][0]["geometry"]["lng"]
        st.success("Coordinates found!")
        st.write(f"**Latitude**: {lat}")
        st.write(f"**Longitude**: {lng}")

        # Save to history
        if "history" not in st.session_state:
            st.session_state["history"] = []
        st.session_state["history"].append({"address": address, "lat": lat, "lng": lng})

        # Show on map
        m = folium.Map(location=[lat, lng], zoom_start=14)
        folium.Marker([lat, lng], tooltip=address).add_to(m)
        st_folium(m, width=700, height=500)

    else:
        st.error("Invalid address or not found.")

# -------------------------
# Reverse Geocoding
st.subheader("🔁 Reverse Geocoding")
col1, col2 = st.columns(2)
with col1:
    lat_input = st.text_input("Enter latitude")
with col2:
    lng_input = st.text_input("Enter longitude")

if lat_input and lng_input:
    try:
        float(lat_input), float(lng_input)
        reverse_data = reverse_geocode(lat_input, lng_input)
        if reverse_data["results"]:
            st.write("**Address**:", reverse_data["results"][0]["formatted"])
        else:
            st.error("Could not find address.")
    except ValueError:
        st.error("Latitude and longitude must be numbers.")

# -------------------------
# CSV Upload Geocoding
st.subheader("📄 Geocode Addresses from CSV")
uploaded_file = st.file_uploader("Upload a CSV with an 'address' column", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if 'address' not in df.columns:
        st.error("CSV must contain 'address' column.")
    else:
        coords = []
        for addr in df['address']:
            r = geocode_address(addr)
            if r["results"]:
                loc = r["results"][0]["geometry"]
                coords.append((loc["lat"], loc["lng"]))
            else:
                coords.append((None, None))
        df['latitude'] = [c[0] for c in coords]
        df['longitude'] = [c[1] for c in coords]
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Geocoded CSV", data=csv, file_name="geocoded_output.csv", mime="text/csv")

# -------------------------
# Search History
with st.sidebar:
    st.subheader("🕘 Search History")
    if "history" in st.session_state and st.session_state["history"]:
        for item in reversed(st.session_state["history"][-10:]):
            st.write(f"📍 {item['address']} ➝ ({item['lat']:.5f}, {item['lng']:.5f})")
    else:
        st.write("No history yet.")
