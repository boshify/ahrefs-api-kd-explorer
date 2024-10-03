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
        position_groups = {
            '#1-3': {'dr': [], 'refdomains': [], 'traffic': []},
            '#4-6': {'dr': [], 'refdomains': [], 'traffic': []},
            '#7-10': {'dr': [], 'refdomains': [], 'traffic': []}
        }
        estimated_traffic = []

        if st.session_state.testing_mode:
            # Generate random data for testing mode
            for keyword in keywords:
                positions = list(range(1, 11))
                random.shuffle(positions)  # Randomly assign positions
                traffic_values = [random.randint(100, 50000) for _ in positions]

                # Divide metrics into groups
                for pos in positions:
                    dr_value = random.uniform(20, 90)
                    refdomains_value = random.randint(5, 500)

                    if pos <= 3:
                        position_groups['#1-3']['dr'].append(dr_value)
                        position_groups['#1-3']['refdomains'].append(refdomains_value)
                        position_groups['#1-3']['traffic'].append(traffic_values[pos-1])
                    elif pos <= 6:
                        position_groups['#4-6']['dr'].append(dr_value)
                        position_groups['#4-6']['refdomains'].append(refdomains_value)
                        position_groups['#4-6']['traffic'].append(traffic_values[pos-1])
                    else:
                        position_groups['#7-10']['dr'].append(dr_value)
                        position_groups['#7-10']['refdomains'].append(refdomains_value)
                        position_groups['#7-10']['traffic'].append(traffic_values[pos-1])
                
                estimated_traffic.append(sum(traffic_values) / len(traffic_values))
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
                        f"?select=backlinks,refdomains,title,position,domain_rating,traffic&country={country}&keyword={encoded_keyword}"
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
                            for item in data['positions']:
                                pos = item.get('position', 0)
                                dr_value = item.get('domain_rating', 0) or 0
                                refdomains_value = item.get('refdomains', 0) or 0
                                traffic_value = item.get('traffic', 0) or 0

                                # Group by positions
                                if 1 <= pos <= 3:
                                    position_groups['#1-3']['dr'].append(dr_value)
                                    position_groups['#1-3']['refdomains'].append(refdomains_value)
                                    position_groups['#1-3']['traffic'].append(traffic_value)
                                elif 4 <= pos <= 6:
                                    position_groups['#4-6']['dr'].append(dr_value)
                                    position_groups['#4-6']['refdomains'].append(refdomains_value)
                                    position_groups['#4-6']['traffic'].append(traffic_value)
                                elif 7 <= pos <= 10:
                                    position_groups['#7-10']['dr'].append(dr_value)
                                    position_groups['#7-10']['refdomains'].append(refdomains_value)
                                    position_groups['#7-10']['traffic'].append(traffic_value)

                            estimated_traffic.append(sum(position_groups['#1-3']['traffic']) / len(position_groups['#1-3']['traffic']))
                        else:
                            # Handle case where no 'positions' data is found
                            estimated_traffic.append(0)
                    elif response.status_code == 403:
                        st.error(f"Access forbidden. Check your API key and permissions.")
                        break  # Stop processing if API key is invalid
                    else:
                        st.error(f"Failed to fetch data for keyword: {keyword}, Status Code: {response.status_code}")

                except Exception as e:
                    st.error(f"An error occurred while processing keyword '{keyword}': {str(e)}")
                    estimated_traffic.append(0)

        # Calculate the average for each group
        group_averages = {}
        for group in position_groups:
            group_averages[group] = {
                'avg_dr': np.mean(position_groups[group]['dr']),
                'avg_refdomains': np.mean(position_groups[group]['refdomains']),
                'avg_traffic': np.mean(position_groups[group]['traffic'])
            }

        # Store keyword data in session state
        st.session_state.keywords_data = {
            "Keyword": keywords,
            "Estimated Traffic": estimated_traffic
        }
        st.session_state.group_averages = group_averages

# Display the table outside of the button block to persist it
if st.session_state.keywords_data:
    keywords_df = pd.DataFrame(st.session_state.keywords_data)
    st.write("Estimated Traffic for Each Provided Keyword:")
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
    group_averages = st.session_state.group_averages
    keywords = keywords_data["Keyword"]
    estimated_traffic = keywords_data["Estimated Traffic"]

    # Estimating traffic and ranking position
    total_forecast = []
    traffic_forecast = []
    hover_texts = []
    for i, traffic in enumerate(estimated_traffic):
        # Calculate average traffic per domain for each keyword, using current domains as the starting point
        current_domains = st.session_state.current_domains if st.session_state.current_domains > 0 else 1  # Avoid division by zero

        forecasted_traffic = []
        hover_text = []
        for month in range(12):  # 12 months forecast
            additional_domains = month * st.session_state.domains_per_month
            total_domains = current_domains + additional_domains

            # Determine which group the influence score fits into
            dr_weight = 0.7
            domain_weight = 0.3
            influence_score = (dr_weight * (current_dr / group_averages['#7-10']['avg_dr'])) + \
                              (domain_weight * (total_domains / group_averages['#7-10']['avg_refdomains']))

            if influence_score < 1:
                # If influence score is less than 1, don't have enough DR or domains to rank in top 10
                estimated_position_range = "Not in top 10"
                estimated_total_traffic = 0
            elif influence_score < 1.5:
                estimated_position_range = "#7-10"
                estimated_total_traffic = min(traffic, group_averages['#7-10']['avg_traffic'])
            elif influence_score < 2.0:
                estimated_position_range = "#4-6"
                estimated_total_traffic = min(traffic, group_averages['#4-6']['avg_traffic'])
            else:
                estimated_position_range = "#1-3"
                estimated_total_traffic = min(traffic, group_averages['#1-3']['avg_traffic'])

            forecasted_traffic.append(round(estimated_total_traffic))

            # Add hover text information
            hover_text.append(
                f"Keyword: {keywords[i]}<br>"
                f"Estimated Traffic: {round(estimated_total_traffic)}<br>"
                f"Estimated Position: {estimated_position_range}"
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
