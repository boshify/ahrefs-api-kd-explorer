import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

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
        estimated_traffic = []

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
                # Extract fields and store in lists (adjust based on actual JSON structure)
                for entry in data.get('serp_overview', []):
                    word_counts.append(len(entry['title'].split()))  # Example word count
                    dr_list.append(entry.get('domain_rating', 0))
                    ur_list.append(entry.get('url_rating', 0))
                    backlinks_list.append(entry.get('backlinks', 0))
                    refdomains_list.append(entry.get('refdomains', 0))
                    estimated_traffic.append(entry.get('traffic', 0))
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

        # Slider for domains per month
        domains_per_month = st.slider("Domains per Month", 0, 100, 0)

        # Estimating traffic based on domains per month
        traffic_forecast = []
        for i, traffic in enumerate(estimated_traffic):
            # Calculate average traffic per domain for each keyword
            ref_domains = refdomains_list[i] if refdomains_list[i] > 0 else 1  # Avoid division by zero
            average_traffic_per_domain = traffic / ref_domains
            
            # Estimate additional traffic based on the domains per month
            additional_traffic = domains_per_month * average_traffic_per_domain
            estimated_total_traffic = traffic + additional_traffic
            
            traffic_forecast.append(estimated_total_traffic)

        # Create DataFrame for traffic forecast
        forecast_df = pd.DataFrame({
            "Keyword": keywords,
            "Initial Traffic": estimated_traffic,
            "Estimated Traffic with Domains per Month": traffic_forecast
        })

        # Plotting the forecast
        fig, ax = plt.subplots()
        ax.plot(forecast_df["Keyword"], forecast_df["Estimated Traffic with Domains per Month"], marker='o', linestyle='-', label='Estimated Traffic')
        ax.set_xlabel("Keywords")
        ax.set_ylabel("Estimated Traffic")
        ax.set_title("Estimated Traffic Forecast Based on Domains per Month")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    else:
        st.error("Please enter all required fields.")
