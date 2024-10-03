import streamlit as st
import requests
import pandas as pd

# Streamlit UI
st.title("Ahrefs Keyword Analysis Tool")
api_key = st.text_input("Enter your Ahrefs API Key")
url_input = st.text_input("Enter the Ahrefs URL")
keywords_input = st.text_area("Enter keywords (one per line)")

if st.button("Analyze Keywords"):
    if api_key and url_input and keywords_input:
        # Process the input keywords
        keywords = keywords_input.strip().split('\n')
        
        # Initialize lists to store each field's data
        word_counts = []
        dr_list = []
        ur_list = []
        backlinks_list = []
        refdomains_list = []

        # Fetch data from Ahrefs API for each keyword
        for keyword in keywords:
            keyword = keyword.strip()
            response = requests.get(
                f"https://api.ahrefs.com/v3/serp-overview/serp-overview",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "country": "us",
                    "keyword": keyword,
                    "select": "url,title,position,type,ahrefs_rank,domain_rating,url_rating,backlinks,refdomains,traffic,value,keywords,top_keyword,top_keyword_volume,update_date"
                }
            )

            if response.status_code == 200:
                data = response.json()
                # Extract fields and store in lists (this assumes JSON structure; adjust as needed)
                for entry in data.get('serp_overview', []):
                    word_counts.append(len(entry['title'].split()))  # Example word count
                    dr_list.append(entry.get('domain_rating', 0))
                    ur_list.append(entry.get('url_rating', 0))
                    backlinks_list.append(entry.get('backlinks', 0))
                    refdomains_list.append(entry.get('refdomains', 0))
            else:
                st.error(f"Failed to fetch data for keyword: {keyword}")

        # Calculate averages
        averages = {
            "Average Word Count": sum(word_counts) / len(word_counts) if word_counts else 0,
            "Average DR": sum(dr_list) / len(dr_list) if dr_list else 0,
            "Average UR": sum(ur_list) / len(ur_list) if ur_list else 0,
            "Average Backlinks": sum(backlinks_list) / len(backlinks_list) if backlinks_list else 0,
            "Average Referring Domains": sum(refdomains_list) / len(refdomains_list) if refdomains_list else 0
        }

        # Create a DataFrame for display
        avg_df = pd.DataFrame([averages])

        # Display the DataFrame
        st.write("Averages for the provided keywords:")
        st.table(avg_df)

        # Allow download of the data as CSV
        csv = avg_df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='keyword_analysis_averages.csv',
            mime='text/csv'
        )
    else:
        st.error("Please enter all required fields.")
