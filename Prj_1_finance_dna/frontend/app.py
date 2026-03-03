import streamlit as st
import requests
import json

st.set_page_config(page_title="Finance DNA Validator", layout="centered")

st.title("Finance DNA Validation System")

st.write("Enter JSON payload below:")

payload_input = st.text_area(
    "Payload JSON",
    value='{"company_name": "ABC Ltd", "revenue": 1000000}'
)

if st.button("Validate Data"):

    try:
        payload_dict = json.loads(payload_input)

        response = requests.post(
            "https://your-backend-name.onrender.com/validate",
            json={
                "payload": payload_dict,
                "rules": {}
            }
        )

        st.subheader("Response from Backend:")
        st.json(response.json())

    except Exception as e:
        st.error(f"Error: {e}")
        