import streamlit as st
import requests

# Title
st.title("Address to Coordinates App 🌍")

# Input field
address = st.text_input("Enter an address")

# API Key
API_KEY = "a0326684eb334377a52fbb3cfefdde86"

# When user inputs address
if address:
    # API request
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["results"]:
        lat = data["results"][0]["geometry"]["lat"]
        lng = data["results"][0]["geometry"]["lng"]

        st.success("Coordinates found!")
        st.write(f"**Latitude**: {lat}")
        st.write(f"**Longitude**: {lng}")
    else:
        st.error("Could not find location. Please check the address.")
