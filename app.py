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
        dr_list = []
        ur_list = []
        backlinks_list = []
        refdomains_list = []
        estimated_traffic = []
        max_traffic_list = []
        position_list = []

        if st.session_state.testing_mode:
            # Generate random data for testing mode
            for keyword in keywords:
                dr_list.append(random.uniform(0, 100))  # Random domain rating
                ur_list.append(random.uniform(0, 100))  # Random URL rating
                backlinks_values = [random.randint(10, 5000) for _ in range(10)]
                refdomain_values = [random.randint(5, 1000) for _ in range(10)]
                position_values = [i + 1 for i in range(10)]  # Positions from 1 to 10

                # Remove outliers
                backlinks_values = [x for x in backlinks_values if x <= 10 * np.median(backlinks_values)]
                refdomain_values = [x for x in refdomain_values if x <= 10 * np.median(refdomain_values)]
                
                backlinks_list.append(sum(backlinks_values) / len(backlinks_values))
                refdomains_list.append(sum(refdomain_values) / len(refdomain_values))
                
                traffic_values = [random.randint(100, 50000) for _ in range(10)]  # Random traffic values
                estimated_traffic.append(sum(traffic_values) / 10)
                max_traffic_list.append(sum(sorted(traffic_values, reverse=True)[:3]) / 3)  # Average of the top 3 traffic values
                position_list.append(position_values)
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
                            # Extract individual values
                            backlinks_values = [item.get('backlinks', 0) or 0 for item in data['positions']]
                            refdomain_values = [item.get('refdomains', 0) or 0 for item in data['positions']]
                            position_values = [item.get('position', 1) or 1 for item in data['positions']]

                            # Remove outliers
                            backlinks_values = [x for x in backlinks_values if x <= 10 * np.median(backlinks_values)]
                            refdomain_values = [x for x in refdomain_values if x <= 10 * np.median(refdomain_values)]

                            avg_dr = sum(item.get('domain_rating', 0) or 0 for item in data['positions']) / len(data['positions'])
                            avg_ur = sum(item.get('url_rating', 0) or 0 for item in data['positions']) / len(data['positions'])
                            avg_backlinks = sum(backlinks_values) / len(backlinks_values)
                            avg_refdomains = sum(refdomain_values) / len(refdomain_values)
                            avg_traffic = sum(item.get('traffic', 0) or 0 for item in data['positions']) / len(data['positions'])
                            top_3_traffic = sum(sorted([item.get('traffic', 0) or 0 for item in data['positions']], reverse=True)[:3]) / 3

                            dr_list.append(round(avg_dr))
                            ur_list.append(round(avg_ur))
                            backlinks_list.append(round(avg_backlinks))
                            refdomains_list.append(round(avg_refdomains))
                            estimated_traffic.append(round(avg_traffic))
                            max_traffic_list.append(round(top_3_traffic))
                            position_list.append(position_values)
                        else:
                            # Handle case where no 'positions' data is found
                            dr_list.append(0)
                            ur_list.append(0)
                            backlinks_list.append(0)
                            refdomains_list.append(0)
                            estimated_traffic.append(0)
                            max_traffic_list.append(0)
                            position_list.append([1] * 10)  # Default positions
                    elif response.status_code == 403:
                        st.error(f"Access forbidden. Check your API key and permissions.")
                        break  # Stop processing if API key is invalid
                    else:
                        st.error(f"Failed to fetch data for keyword: {keyword}, Status Code: {response.status_code}")

                except Exception as e:
                    st.error(f"An error occurred while processing keyword '{keyword}': {str(e)}")
                    dr_list.append(0)
                    ur_list.append(0)
                    backlinks_list.append(0)
                    refdomains_list.append(0)
                    estimated_traffic.append(0)
                    max_traffic_list.append(0)
                    position_list.append([1] * 10)  # Default positions

        # Store keyword data in session state
        st.session_state.keywords_data = {
            "Keyword": keywords,
            "Domain Rating (DR) - Top 10 Avg": dr_list,
            "URL Rating (UR) - Top 10 Avg": ur_list,
            "Backlinks - Top 10 Avg": backlinks_list,
            "Referring Domains - Top 10 Avg": refdomains_list,
            "Initial Traffic - Top 10 Avg": estimated_traffic,
            "Max Traffic - Top 3 Avg": max_traffic_list,
            "Position List": position_list
        }

# Display the table outside of the button block to persist it
if st.session_state.keywords_data:
    keywords_df = pd.DataFrame(st.session_state.keywords_data)
    st.write("Averages for the Top 10 Results for Each Provided Keyword (Outliers Excluded):")
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
    estimated_traffic = keywords_data["Initial Traffic - Top 10 Avg"]
    avg_dr_list = keywords_data["Domain Rating (DR) - Top 10 Avg"]
    refdomains_list = keywords_data["Referring Domains - Top 10 Avg"]
    max_traffic_list = keywords_data["Max Traffic - Top 3 Avg"]
    position_list = keywords_data["Position List"]

    # Estimating traffic and ranking position
    total_forecast = []
    traffic_forecast = []
    hover_texts = []
    for i, traffic in enumerate(estimated_traffic):
        # Calculate average traffic per domain for each keyword, using current domains as the starting point
        current_domains = st.session_state.current_domains if st.session_state.current_domains > 0 else 1  # Avoid division by zero
        average_traffic_per_domain = traffic / current_domains

        # Calculate the correlations and weightings
        positions = np.array(position_list[i])
        dr_values = np.array([avg_dr_list[i]] * len(positions))
        domain_values = np.array([refdomains_list[i]] * len(positions))
        
        # Calculate the Pearson correlations
        corr_dr = np.corrcoef(positions, dr_values)[0, 1]
        corr_domains = np.corrcoef(positions, domain_values)[0, 1]
        
        # Calculate the weightings based on the absolute correlations
        corr_dr_abs = abs(corr_dr)
        corr_domains_abs = abs(corr_domains)
        total_influence = corr_dr_abs + corr_domains_abs
        weight_dr = corr_dr_abs / total_influence if total_influence != 0 else 0.5
        weight_domains = corr_domains_abs / total_influence if total_influence != 0 else 0.5

        forecasted_traffic = []
        hover_text = []
        for month in range(12):  # 12 months forecast
            additional_domains = month * st.session_state.domains_per_month
            total_domains = current_domains + additional_domains
            influence_score = (weight_dr * (current_dr / avg_dr_list[i] if avg_dr_list[i] > 0 else 1)) + (weight_domains * (total_domains / refdomains_list[i] if refdomains_list[i] > 0 else 1))

            # Estimate position based on influence score
            estimated_position = max(1, round(10 / influence_score))  # Position ranges from 1 to 10

            # Calculate traffic, capping it to the average of the top 3 traffic values
            estimated_total_traffic = traffic + (total_domains * average_traffic_per_domain) * influence_score
            capped_traffic = min(estimated_total_traffic, max_traffic_list[i])
            forecasted_traffic.append(round(capped_traffic))

            # Add hover text information
            hover_text.append(
                f"Keyword: {keywords[i]}<br>"
                f"Estimated Traffic: {round(capped_traffic)}<br>"
                f"Estimated Position: {estimated_position}"
            )

        traffic_forecast.append(forecasted_traffic)
        hover_texts.append(hover_text)
        total_forecast.append(forecasted_traffic)

    # Calculate the total line for the chart
    total_traffic_forecast = [sum(x) for x in zip(*total_forecast)]

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame(traffic_forecast, index=keywords, columns=[f'Month {i+1} ({st.session_state.current_domains + month * st.session_state.domains_per_month} estimated domains)' for i, month in enumerate(range(12))])
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
