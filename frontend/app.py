import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Shop Insight",
    page_icon="📊",
    layout="wide"
)

st.title("Shop Insight")
st.subheader("Business Analytics Platform")

api_url = os.getenv("API_URL", "http://localhost:8000")

try:
    response = requests.get(
        f"{api_url}/health",
        timeout=5
    )

    if response.status_code == 200:
        st.success("Backend connected successfully!")
        st.write(response.json())
    else:
        st.error("Backend connection failed.")

except requests.exceptions.RequestException:
    st.error("Cannot connect to the backend.")