import streamlit as st
import requests

st.title("First Aid Assistant")
st.write("Enter your symptoms or ask for first aid advice.")

query = st.text_input("Your Question:")
if st.button("Ask"): 
    if query:
        response = requests.post("http://127.0.0.1:5000/process_query", json={"query": query})
        if response.status_code == 200:
            st.write("*Response:*", response.json().get("response", "No response received."))
        else:
            st.write("Error processing your request.")