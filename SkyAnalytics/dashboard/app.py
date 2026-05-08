import streamlit as st
import requests

st.title("SkyAnalytics Dashboard")

st.write("Welcome to the SkyAnalytics Dashboard")

# Example: Fetch data from backend
try:
    response = requests.get("http://backend:8000/health")
    if response.status_code == 200:
        st.success("Backend is healthy")
    else:
        st.error("Backend is not responding")
except:
    st.warning("Unable to connect to backend")