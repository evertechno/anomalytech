import streamlit as st
import requests

API_URL = "https://mas-lrd6.onrender.com/sync"

st.title("MAS Circulars Sync Trigger")

st.write("Click the button below to run the MAS sync process.")

if st.button("Run Sync"):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            st.success("✅ Sync completed successfully!")
            st.json(response.json())
        else:
            st.error(f"❌ Error {response.status_code}")
            st.write(response.text)
    except Exception as e:
        st.error("❌ Failed to connect to API")
        st.write(str(e))
