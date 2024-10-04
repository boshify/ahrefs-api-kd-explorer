import streamlit as st
import requests
import pandas as pd
import random
import plotly.graph_objects as go
import io
from requests.utils import quote
import numpy as np

# Backend toggle for enabling/disabling testing mode
TEST_MODE_ENABLED = True  # Set this to False to completely disable testing mode

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Streamlit UI
st.title("Ahrefs Keyword Analysis Tool")

# Initialize session state for inputs and data if not already present
if 'domains_per_month' not in st.session_state:
    st.session_state.domains_per_month = 0

if 'current_domains' not in st.session_state:
    st.session_state.current_domains = 0

if 'keywords_data' not in st.session_state:
    st.session_state.keywords_data = None

# Display testing mode slider if testing mode is enabled
if TEST_MODE_ENABLED:
    st.session_state.testing_mode = st.checkbox("Enable Testing Mode (Generate Random Data)", False)

# Input fields
api_key = st.text_input("Enter your Ahrefs API Key")

# Country selection dropdown
country = st.selectbox(
    "Select Country",
    ["us", "uk", "ca", "au", "de", "fr", "es", "it", "nl", "jp", "in", "br", "mx", "ru", "cn"]
)

keywords_input = st.text_area("Enter keywords (one per line)")

# Button to analyze keywords
if st.button("Analyze Keywords"):
    if (api_key and keywords_input) or (TEST_MODE_ENABLED and st.session_state.testing_mode):
        # Process the input keywords
        keywords = keywords_input.strip().split('\n')
        
        # Initialize lists to store each field's data
        dr_top3_list, dr_4_7_list, dr_8_10_list = [], [], []
        ur_top3_list, ur_4_7_list, ur_8_10_list = [], [], []
        backlinks_top3_list, backlinks_4_7_list, backlinks_8_10_list = [], [], []
        refdomains_top3_list, refdomains_4_7_list, refdomains_8_10_list = [], [], []
        initial_traffic_top3_list, initial_traffic_4_7_list, initial_traffic_8_10_list = [], [], []
        max_traffic_top3_list, max_traffic_4_7_list, max_traffic_8_10_list = [], [], []
        position_list = []

        if st.session_state.testing_mode:
            # Generate random data for testing mode
            for keyword in keywords:
                positions = [i + 1 for i in range(10)]  # Positions from 1 to 10

                dr_values = [random.uniform(0, 100) for _ in positions]
                ur_values = [random.uniform(0, 100) for _ in positions]
                backlinks_values = [random.randint(10, 5000) for _ in positions]
                refdomain_values = [random.randint(5, 1000) for _ in positions]
                traffic_values = [random.randint(100, 50000) for _ in positions]

                # Calculate top 3 averages
                dr_top3_avg = sum(dr_values[:3]) / 3
                ur_top3_avg = sum(ur_values[:3]) / 3
                backlinks_top3_avg = sum(backlinks_values[:3]) / 3
                refdomains_top3_avg = sum(refdomain_values[:3]) / 3
                initial_traffic_top3 = min(traffic_values[:3])
                max_traffic_top3 = max(traffic_values[:3])

                # Calculate #4-7 averages
                dr_4_7_avg = sum(dr_values[3:7]) / 4
                ur_4_7_avg = sum(ur_values[3:7]) / 4
                backlinks_4_7_avg = sum(backlinks_values[3:7]) / 4
                refdomains_4_7_avg = sum(refdomain_values[3:7]) / 4
                initial_traffic_4_7 = min(traffic_values[3:7])
                max_traffic_4_7 = max(traffic_values[3:7])

                # Calculate #8-10 averages
                dr_8_10_avg = sum(dr_values[7:10]) / 3
                ur_8_10_avg = sum(ur_values[7:10]) / 3
                backlinks_8_10_avg = sum(backlinks_values[7:10]) / 3
                refdomains_8_10_avg = sum(refdomain_values[7:10]) / 3
                initial_traffic_8_10 = min(traffic_values[7:10])
                max_traffic_8_10 = max(traffic_values[7:10])

                # Append to lists
                dr_top3_list.append(dr_top3_avg)
                ur_top3_list.append(ur_top3_avg)
                backlinks_top3_list.append(backlinks_top3_avg)
                refdomains_top3_list.append(refdomains_top3_avg)
                initial_traffic_top3_list.append(initial_traffic_top3)
                max_traffic_top3_list.append(max_traffic_top3)

                dr_4_7_list.append(dr_4_7_avg)
                ur_4_7_list.append(ur_4_7_avg)
                backlinks_4_7_list.append(backlinks_4_7_avg)
                refdomains_4_7_list.append(refdomains_4_7_avg)
                initial_traffic_4_7_list.append(initial_traffic_4_7)
                max_traffic_4_7_list.append(max_traffic_4_7)

                dr_8_10_list.append(dr_8_10_avg)
                ur_8_10_list.append(ur_8_10_avg)
                backlinks_8_10_list.append(backlinks_8_10_avg)
                refdomains_8_10_list.append(refdomains_8_10_avg)
                initial_traffic_8_10_list.append(initial_traffic_8_10)
                max_traffic_8_10_list.append(max_traffic_8_10)

                position_list.append(positions)

        else:
            # Fetch data from Ahrefs API for each keyword
            for keyword in keywords:
                keyword = keyword.strip()
                try:
                    # URL-encode the keyword
                    encoded_keyword = quote(keyword)

                    # Construct the API request URL, limiting to top 10 positions
                    api_url = (
                        f"https://api.ahrefs.com/v3/serp-overview/serp-overview"
                        f"?select=backlinks,refdomains,title,position,domain_rating,url_rating,traffic&country={country}&keyword={encoded_keyword}"
                        f"&top_positions=10"
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
                        data = response.json()
                        # Extract fields and store in lists
                        if 'positions' in data and len(data['positions']) > 0:
                            dr_values = [item.get('domain_rating', 0) or 0 for item in data['positions']]
                            ur_values = [item.get('url_rating', 0) or 0 for item in data['positions']]
                            backlinks_values = [item.get('backlinks', 0) or 0 for item in data['positions']]
                            refdomain_values = [item.get('refdomains', 0) or 0 for item in data['positions']]
                            traffic_values = [item.get('traffic', 0) or 0 for item in data['positions']]
                            positions = [item.get('position', 1) or 1 for item in data['positions']]

                            # Calculate top 3 averages
                            dr_top3_avg = sum(dr_values[:3]) / 3
                            ur_top3_avg = sum(ur_values[:3]) / 3
                            backlinks_top3_avg = sum(backlinks_values[:3]) / 3
                            refdomains_top3_avg = sum(refdomain_values[:3]) / 3
                            initial_traffic_top3 = min(traffic_values[:3])
                            max_traffic_top3 = max(traffic_values[:3])

                            # Calculate #4-7 averages
                            dr_4_7_avg = sum(dr_values[3:7]) / 4
                            ur_4_7_avg = sum(ur_values[3:7]) / 4
                            backlinks_4_7_avg = sum(backlinks_values[3:7]) / 4
                            refdomains_4_7_avg = sum(refdomain_values[3:7]) / 4
                            initial_traffic_4_7 = min(traffic_values[3:7])
                            max_traffic_4_7 = max(traffic_values[3:7])

                            # Calculate #8-10 averages
                            dr_8_10_avg = sum(dr_values[7:10]) / 3
                            ur_8_10_avg = sum(ur_values[7:10]) / 3
                            backlinks_8_10_avg = sum(backlinks_values[7:10]) / 3
                            refdomains_8_10_avg = sum(refdomain_values[7:10]) / 3
                            initial_traffic_8_10 = min(traffic_values[7:10])
                            max_traffic_8_10 = max(traffic_values[7:10])

                            # Append to lists
                            dr_top3_list.append(dr_top3_avg)
                            ur_top3_list.append(ur_top3_avg)
                            backlinks_top3_list.append(backlinks_top3_avg)
                            refdomains_top3_list.append(refdomains_top3_avg)
                            initial_traffic_top3_list.append(initial_traffic_top3)
                            max_traffic_top3_list.append(max_traffic_top3)

                            dr_4_7_list.append(dr_4_7_avg)
                            ur_4_7_list.append(ur_4_7_avg)
                            backlinks_4_7_list.append(backlinks_4_7_avg)
                            refdomains_4_7_list.append(refdomains_4_7_avg)
                            initial_traffic_4_7_list.append(initial_traffic_4_7)
                            max_traffic_4_7_list.append(max_traffic_4_7)

                            dr_8_10_list.append(dr_8_10_avg)
                            ur_8_10_list.append(ur_8_10_avg)
                            backlinks_8_10_list.append(backlinks_8_10_avg)
                            refdomains_8_10_list.append(refdomains_8_10_avg)
                            initial_traffic_8_10_list.append(initial_traffic_8_10)
                            max_traffic_8_10_list.append(max_traffic_8_10)

                            position_list.append(positions)
                        else:
                            # Handle case where no 'positions' data is found
                            dr_top3_list.append(0)
                            ur_top3_list.append(0)
                            backlinks_top3_list.append(0)
                            refdomains_top3_list.append(0)
                            initial_traffic_top3_list.append(0)
                            max_traffic_top3_list.append(0)
                            dr_4_7_list.append(0)
                            ur_4_7_list.append(0)
                            backlinks_4_7_list.append(0)
                            refdomains_4_7_list.append(0)
                            initial_traffic_4_7_list.append(0)
                            max_traffic_4_7_list.append(0)
                            dr_8_10_list.append(0)
                            ur_8_10_list.append(0)
                            backlinks_8_10_list.append(0)
                            refdomains_8_10_list.append(0)
                            initial_traffic_8_10_list.append(0)
                            max_traffic_8_10_list.append(0)
                            position_list.append([1] * 10)  # Default positions
                    elif response.status_code == 403:
                        st.error(f"Access forbidden. Check your API key and permissions.")
                        break  # Stop processing if API key is invalid
                    else:
                        st.error(f"Failed to fetch data for keyword: {keyword}, Status Code: {response.status_code}")

                except Exception as e:
                    st.error(f"An error occurred while processing keyword '{keyword}': {str(e)}")
                    dr_top3_list.append(0)
                    ur_top3_list.append(0)
                    backlinks_top3_list.append(0)
                    refdomains_top3_list.append(0)
                    initial_traffic_top3_list.append(0)
                    max_traffic_top3_list.append(0)
                    dr_4_7_list.append(0)
                    ur_4_7_list.append(0)
                    backlinks_4_7_list.append(0)
                    refdomains_4_7_list.append(0)
                    initial_traffic_4_7_list.append(0)
                    max_traffic_4_7_list.append(0)
                    dr_8_10_list.append(0)
                    ur_8_10_list.append(0)
                    backlinks_8_10_list.append(0)
                    refdomains_8_10_list.append(0)
                    initial_traffic_8_10_list.append(0)
                    max_traffic_8_10_list.append(0)
                    position_list.append([1] * 10)  # Default positions

        # Store keyword data in session state
        st.session_state.keywords_data = {
            "Keyword": keywords,
            "Domain Rating (DR) - Top 3 Avg": dr_top3_list,
            "URL Rating (UR) - Top 3 Avg": ur_top3_list,
            "Backlinks - Top 3 Avg": backlinks_top3_list,
            "Referring Domains - Top 3 Avg": refdomains_top3_list,
            "Initial Traffic - Top 3": initial_traffic_top3_list,
            "Max Traffic - Top 3": max_traffic_top3_list,
            "Domain Rating (DR) - #4-7 Avg": dr_4_7_list,
            "URL Rating (UR) - #4-7 Avg": ur_4_7_list,
            "Backlinks - #4-7 Avg": backlinks_4_7_list,
            "Referring Domains - #4-7 Avg": refdomains_4_7_list,
            "Initial Traffic - #4-7": initial_traffic_4_7_list,
            "Max Traffic - #4-7": max_traffic_4_7_list,
            "Domain Rating (DR) - #8-10 Avg": dr_8_10_list,
            "URL Rating (UR) - #8-10 Avg": ur_8_10_list,
            "Backlinks - #8-10 Avg": backlinks_8_10_list,
            "Referring Domains - #8-10 Avg": refdomains_8_10_list,
            "Initial Traffic - #8-10": initial_traffic_8_10_list,
            "Max Traffic - #8-10": max_traffic_8_10_list,
            "Position List": position_list
        }

# Display the table outside of the button block to persist it
if st.session_state.keywords_data:
    keywords_df = pd.DataFrame(st.session_state.keywords_data)
    st.write("Averages for the Top 3, #4-7, and #8-10 Results for Each Provided Keyword (Outliers Excluded):")
    st.table(keywords_df)

# Show the slider for domains per month
st.session_state.domains_per_month = st.slider(
    "Domains per Month",
    0, 100, st.session_state.domains_per_month
)

# Place the Current DR and Current Referring Domains below the slider
current_dr = st.number_input("Enter your current Domain Rating (DR)", min_value=0, max_value=100, value=50)
st.session_state.current_domains = st.number_input(
    "Current Referring Domains",
    min_value=0, value=st.session_state.current_domains
)

# If keyword data is available, calculate and plot forecast
if st.session_state.keywords_data:
    keywords_data = st.session_state.keywords_data
    keywords = keywords_data["Keyword"]
    avg_dr_list = keywords_data["Domain Rating (DR) - Top 3 Avg"]
    avg_dr_4_7_list = keywords_data["Domain Rating (DR) - #4-7 Avg"]
    avg_dr_8_10_list = keywords_data["Domain Rating (DR) - #8-10 Avg"]
    refdomains_list = keywords_data["Referring Domains - Top 3 Avg"]
    refdomains_4_7_list = keywords_data["Referring Domains - #4-7 Avg"]
    refdomains_8_10_list = keywords_data["Referring Domains - #8-10 Avg"]
    max_traffic_top3_list = keywords_data["Max Traffic - Top 3"]
    max_traffic_4_7_list = keywords_data["Max Traffic - #4-7"]
    max_traffic_8_10_list = keywords_data["Max Traffic - #8-10"]
    initial_traffic_top3_list = keywords_data["Initial Traffic - Top 3"]
    initial_traffic_4_7_list = keywords_data["Initial Traffic - #4-7"]
    initial_traffic_8_10_list = keywords_data["Initial Traffic - #8-10"]

    # Estimating traffic and ranking position
    total_forecast = []
    traffic_forecast = []
    hover_texts = []
    for i, keyword in enumerate(keywords):
        current_domains = st.session_state.current_domains
        forecasted_traffic = []
        hover_text = []

        # Calculate the traffic forecast for each month
        for month in range(12):  # 12 months forecast
            additional_domains = month * st.session_state.domains_per_month
            total_domains = current_domains + additional_domains

            # Determine which bucket the current keyword belongs to based on the current domains and domain rating
            if total_domains <= avg_dr_8_10_list[i]:
                estimated_bucket = '8-10'
                initial_traffic = initial_traffic_8_10_list[i]
                max_traffic = max_traffic_8_10_list[i]
                influence_score = (current_dr / avg_dr_8_10_list[i] if avg_dr_8_10_list[i] > 0 else 1)
            elif total_domains <= avg_dr_4_7_list[i]:
                estimated_bucket = '4-7'
                initial_traffic = initial_traffic_4_7_list[i]
                max_traffic = max_traffic_4_7_list[i]
                influence_score = (current_dr / avg_dr_4_7_list[i] if avg_dr_4_7_list[i] > 0 else 1)
            else:
                estimated_bucket = '1-3'
                initial_traffic = initial_traffic_top3_list[i]
                max_traffic = max_traffic_top3_list[i]
                influence_score = (current_dr / avg_dr_list[i] if avg_dr_list[i] > 0 else 1)

            # Ensure influence_score is not zero or too small to avoid division errors
            influence_score = max(influence_score, 0.01)  # Setting a small minimum threshold

            # Logarithmic growth for traffic estimation
            estimated_total_traffic = initial_traffic + (np.log1p(total_domains) * influence_score)
            capped_traffic = min(estimated_total_traffic, max_traffic)
            forecasted_traffic.append(round(capped_traffic))

            # Add hover text information that changes dynamically
            hover_text.append(
                f"Keyword: {keywords[i]}<br>"
                f"Estimated Traffic: {round(capped_traffic)}<br>"
                f"Estimated Position: {estimated_bucket}"
            )

        traffic_forecast.append(forecasted_traffic)
        hover_texts.append(hover_text)
        total_forecast.append(forecasted_traffic)

    # Calculate the total line for the chart
    total_traffic_forecast = [sum(x) for x in zip(*total_forecast)]

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame(
        traffic_forecast,
        index=keywords,
        columns=[f'Month {i+1} ({st.session_state.current_domains + month * st.session_state.domains_per_month} estimated domains)' for i, month in enumerate(range(12))]
    )
    plot_df.loc['Total'] = total_traffic_forecast

    # Plotting the forecast using Plotly
    fig = go.Figure()

    # Add lines for each keyword
    for i, keyword in enumerate(keywords):
        fig.add_trace(go.Scatter(
            x=[f'Month {i+1} ({st.session_state.current_domains + month * st.session_state.domains_per_month} estimated domains)' for i, month in enumerate(range(12))],
            y=traffic_forecast[i],
            mode='lines+markers',
            name=keyword,
            text=hover_texts[i],  # Hover text with detailed information
            hoverinfo='text'
        ))

    # Add a line for the total
    fig.add_trace(go.Scatter(
        x=[f'Month {i+1} ({st.session_state.current_domains + month * st.session_state.domains_per_month} estimated domains)' for i, month in enumerate(range(12))],
        y=total_traffic_forecast,
        mode='lines+markers',
        name='Total',
        line=dict(color='black', width=2, dash='dash')
    ))

    # Update layout to display full numbers on the y-axis and adjust figure height
    fig.update_layout(
        title='Estimated Traffic Forecast Based on Domains per Month and DR Adjustment',
        xaxis_title='Months',
        yaxis_title='Estimated Traffic',
        yaxis=dict(tickformat=','),
        hovermode='x unified',
        height=600  # Adjust the chart height
    )

    st.plotly_chart(fig)

    # Create CSV download functionality
    csv_output = plot_df.T
    csv_buffer = io.StringIO()
    csv_output.to_csv(csv_buffer)
    st.download_button(
        label="Download Forecast Data as CSV",
        data=csv_buffer.getvalue(),
        file_name='forecasted_traffic.csv',
        mime='text/csv'
    )
