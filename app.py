import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit UI
st.title("Ahrefs Keyword Analysis Tool")

# Initialize session state for slider and data if not already present
if 'domains_per_month' not in st.session_state:
    st.session_state.domains_per_month = 0

if 'keywords_data' not in st.session_state:
    st.session_state.keywords_data = None

# Input fields
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

        # Ensure all lists have the same length
        num_keywords = len(keywords)
        if len(word_counts) < num_keywords:
            word_counts.extend([0] * (num_keywords - len(word_counts)))
        if len(dr_list) < num_keywords:
            dr_list.extend([0] * (num_keywords - len(dr_list)))
        if len(ur_list) < num_keywords:
            ur_list.extend([0] * (num_keywords - len(ur_list)))
        if len(backlinks_list) < num_keywords:
            backlinks_list.extend([0] * (num_keywords - len(backlinks_list)))
        if len(refdomains_list) < num_keywords:
            refdomains_list.extend([0] * (num_keywords - len(refdomains_list)))
        if len(estimated_traffic) < num_keywords:
            estimated_traffic.extend([0] * (num_keywords - len(estimated_traffic)))

        # Store keyword data in session state
        st.session_state.keywords_data = {
            "Keyword": keywords,
            "Word Count": word_counts,
            "Domain Rating (DR)": dr_list,
            "URL Rating (UR)": ur_list,
            "Backlinks": backlinks_list,
            "Referring Domains": refdomains_list,
            "Initial Traffic": estimated_traffic
        }

# Display the table outside of the button block to persist it
if st.session_state.keywords_data:
    keywords_df = pd.DataFrame(st.session_state.keywords_data)
    st.write("Metrics for each provided keyword:")
    st.table(keywords_df)

# Show the slider and use session state to keep its value
st.session_state.domains_per_month = st.slider(
    "Domains per Month",
    0, 100, st.session_state.domains_per_month
)

# If keyword data is available, calculate and plot forecast
if st.session_state.keywords_data:
    keywords_data = st.session_state.keywords_data
    keywords = keywords_data["Keyword"]
    estimated_traffic = keywords_data["Initial Traffic"]
    refdomains_list = keywords_data["Referring Domains"]

    # Estimating traffic based on domains per month
    total_forecast = []
    traffic_forecast = []
    for i, traffic in enumerate(estimated_traffic):
        # Calculate average traffic per domain for each keyword
        ref_domains = refdomains_list[i] if refdomains_list[i] > 0 else 1  # Avoid division by zero
        average_traffic_per_domain = traffic / ref_domains

        # Calculate forecasted traffic for each domain per month value
        forecasted_traffic = []
        for month in range(st.session_state.domains_per_month + 1):
            additional_traffic = month * average_traffic_per_domain
            estimated_total_traffic = traffic + additional_traffic
            forecasted_traffic.append(estimated_total_traffic)

        traffic_forecast.append(forecasted_traffic)
        total_forecast.append(forecasted_traffic)

    # Calculate the total line for the chart
    total_traffic_forecast = [sum(x) for x in zip(*total_forecast)]

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame(traffic_forecast, index=keywords, columns=[f'Month {i}' for i in range(st.session_state.domains_per_month + 1)])
    plot_df.loc['Total'] = total_traffic_forecast

    # Plotting the forecast
    fig, ax = plt.subplots()
    for keyword in plot_df.index:
        ax.plot(plot_df.columns, plot_df.loc[keyword], marker='o', linestyle='-', label=keyword)

    ax.set_xlabel("Months")
    ax.set_ylabel("Estimated Traffic")
    ax.set_title("Estimated Traffic Forecast Based on Domains per Month")
    plt.xticks(rotation=45, ha='right')
    ax.legend()
    st.pyplot(fig)
