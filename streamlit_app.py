import streamlit as st
import requests

API_URL = "https://mas-lrd6.onrender.com/sync"  # your deployed Flask service

st.title("MAS Circulars Sync Trigger")

st.write("Click the button below to run the MAS sync process.")

if st.button("Run Sync"):
    try:
        response = requests.get(API_URL)  # change to post if needed
        if response.status_code == 200:
            st.success("✅ Sync completed successfully!")
            try:
                st.json(response.json())
            except:
                st.write(response.text)
        else:
            st.error(f"❌ Error {response.status_code}")
            st.write(response.text)
    except Exception as e:
        st.error("❌ Failed to connect to API")
        st.write(str(e))
