import streamlit as st
import requests
from requests.utils import quote

# Input fields
api_key = st.text_input("Enter your Ahrefs API Key")

# Country selection dropdown
country = st.selectbox(
    "Select Country",
    ["us", "uk", "ca", "au", "de", "fr", "es", "it", "nl", "jp", "in", "br", "mx", "ru", "cn"]
)

keyword = st.text_input("Enter a single keyword to test")

if st.button("Test API Request"):
    if api_key and keyword:
        try:
            # URL-encode the keyword
            encoded_keyword = quote(keyword.strip())

            # Construct the API request URL
            api_url = (
                f"https://api.ahrefs.com/v3/serp-overview/serp-overview"
                f"?select=backlinks,refdomains,title&country={country}&keyword={encoded_keyword}"
            )

            # Set headers
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            # Make the API request using requests
            response = requests.get(api_url, headers=headers)

            # Check the response
            if response.status_code == 200:
                st.success("API request successful!")
                st.json(response.json())  # Display the JSON response
            elif response.status_code == 403:
                st.error(f"Access forbidden. Check your API key and permissions.")
                st.write(f"Response headers: {response.headers}")
                st.write(f"Response content: {response.content}")
            else:
                st.error(f"Failed to fetch data. Status Code: {response.status_code}")
                st.write(f"Response headers: {response.headers}")
                st.write(f"Response content: {response.content}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
