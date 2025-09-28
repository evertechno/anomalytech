import streamlit as st
import requests

# Replace with your actual Render URL
API_URL = "https://mas-lrd6.onrender.com"

st.title("Trigger MAS Sync")

if st.button("Run MAS Scraper"):
    try:
        response = requests.get(API_URL)  # or post, or specific route
        if response.status_code == 200:
            st.success("✅ Success")
            st.json(response.json())
        else:
            st.error(f"❌ Error {response.status_code}")
            st.write(response.text)
    except Exception as e:
        st.error("❌ Request failed")
        st.write(str(e))
