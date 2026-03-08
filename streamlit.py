import streamlit as st
import requests
from PIL import Image
import io

# URL of the running FastAPI application
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fashion Search", layout="wide")

st.title("Fashion Item Search")
st.markdown("Search for fashion items using text or by uploading an image.")

#Search by Text
st.header("Search by Text")
text_query = st.text_input("Enter your search query (e.g., 'pink floral dress')", placeholder="pink floral dress")
if st.button("Search Text"):
    if text_query:
        with st.spinner('Searching for text query...'):
            try:
                response = requests.post(f"{FASTAPI_URL}/search_by_text", json={"query": text_query, "top_k": 5})
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    st.success("Search complete!")
                    if results:
                        st.subheader("Top results:")
                        # Display results in a grid
                        cols = st.columns(len(results))
                        for i, item in enumerate(results):
                            col = cols[i]
                            with col:
                                #Join the base URL and the relative image URL
                                image_url = f"{FASTAPI_URL}{item['image_url']}"
                                image_response = requests.get(image_url)
                                if image_response.status_code == 200:
                                    image_data = image_response.content
                                    st.image(image_data, use_column_width=True, caption=item['name'])
                                else:
                                    st.write(f"Could not load image for {item['name']}")
                                st.write(f"**Name:** {item['name']}")
                                st.write(f"**Category:** {item['category']}")
                                st.write(f"**Gender:** {item['gender']}")
                    else:
                        st.write("No results found.")
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection error. Please ensure your FastAPI server is running.")

#Search by Image 
st.header("Search by Image")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if st.button("Search Image"):
    if uploaded_file is not None:
        with st.spinner('Uploading and searching for image...'):
            try:
                files = {'file': uploaded_file.getvalue()}
                response = requests.post(f"{FASTAPI_URL}/search_by_image", files=files, params={"top_k": 5})
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    st.success("Search complete!")
                    if results:
                        st.subheader("Top results:")
                        # Display results in a grid
                        cols = st.columns(len(results))
                        for i, item in enumerate(results):
                            col = cols[i]
                            with col:
                                #Join the base URL and the relative image URL
                                image_url = f"{FASTAPI_URL}{item['image_url']}"
                                image_response = requests.get(image_url)
                                if image_response.status_code == 200:
                                    image_data = image_response.content
                                    st.image(image_data, use_column_width=True, caption=item['name'])
                                else:
                                    st.write(f"Could not load image for {item['name']}")
                                st.write(f"**Name:** {item['name']}")
                                st.write(f"**Category:** {item['category']}")
                                st.write(f"**Gender:** {item['gender']}")
                    else:
                        st.write("No results found.")
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection error. Please ensure your FastAPI server is running.")
    else:
        st.warning("Please upload an image to search.")
