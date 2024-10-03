import streamlit as st
import requests
import pandas as pd
import random
import plotly.graph_objects as go
import io

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
url_input = st.text_input("Enter the Ahrefs URL")
keywords_input = st.text_area("Enter keywords (one per line)")

if st.button("Analyze Keywords"):
    if (api_key and url_input and keywords_input) or (TEST_MODE_ENABLED and st.session_state.testing_mode):
        # Process the input keywords
        keywords = keywords_input.strip().split('\n')
        
        # Initialize lists to store each field's data
        word_counts = []
        dr_list = []
        ur_list = []
        backlinks_list = []
        refdomains_list = []
        estimated_traffic = []
        positions = []

        if st.session_state.testing_mode:
            # Generate random data for testing mode
            for keyword in keywords:
                word_counts.append(random.randint(500, 2000))  # Random word count
                dr_list.append(random.uniform(0, 100))  # Random domain rating
                ur_list.append(random.uniform(0, 100))  # Random URL rating
                backlinks_list.append(random.randint(10, 5000))  # Random backlinks
                refdomains_list.append(random.randint(5, 1000))  # Random referring domains
                estimated_traffic.append(random.randint(100, 50000))  # Random traffic
                positions.append(random.randint(1, 50))  # Random estimated position
        else:
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
                        positions.append(entry.get('position', 0))
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
        if len(positions) < num_keywords:
            positions.extend([0] * (num_keywords - len(positions)))

        # Store keyword data in session state
        st.session_state.keywords_data = {
            "Keyword": keywords,
            "Word Count": word_counts,
            "Domain Rating (DR)": dr_list,
            "URL Rating (UR)": ur_list,
            "Backlinks": backlinks_list,
            "Referring Domains": refdomains_list,
            "Initial Traffic": estimated_traffic,
            "Position": positions
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

# Input for current domains
st.session_state.current_domains = st.number_input(
    "Current Referring Domains",
    min_value=0, value=st.session_state.current_domains
)

# If keyword data is available, calculate and plot forecast
if st.session_state.keywords_data:
    keywords_data = st.session_state.keywords_data
    keywords = keywords_data["Keyword"]
    estimated_traffic = keywords_data["Initial Traffic"]
    refdomains_list = keywords_data["Referring Domains"]
    positions = keywords_data["Position"]

    # Estimating traffic based on domains per month
    total_forecast = []
    traffic_forecast = []
    hover_texts = []
    for i, traffic in enumerate(estimated_traffic):
        # Calculate average traffic per domain for each keyword, using current domains as the starting point
        current_domains = st.session_state.current_domains if st.session_state.current_domains > 0 else 1  # Avoid division by zero
        average_traffic_per_domain = traffic / current_domains

        # Calculate forecasted traffic for each month, up to 12 months
        forecasted_traffic = []
        hover_text = []
        for month in range(12):  # 12 months forecast
            additional_domains = month * st.session_state.domains_per_month
            total_domains = current_domains + additional_domains
            estimated_total_traffic = traffic + (total_domains * average_traffic_per_domain)
            forecasted_traffic.append(estimated_total_traffic)

            # Add hover text information
            hover_text.append(
                f"Keyword: {keywords[i]}<br>Estimated Domains: {total_domains}<br>"
                f"Estimated Traffic: {estimated_total_traffic:.0f}<br>Position: {positions[i]}"
            )

        traffic_forecast.append(forecasted_traffic)
        hover_texts.append(hover_text)
        total_forecast.append(forecasted_traffic)

    # Calculate the total line for the chart
    total_traffic_forecast = [sum(x) for x in zip(*total_forecast)]

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame(traffic_forecast, index=keywords, columns=[f'Month {i+1}' for i in range(12)])
    plot_df.loc['Total'] = total_traffic_forecast

    # Plotting the forecast using Plotly
    fig = go.Figure()

    # Add lines for each keyword
    for i, keyword in enumerate(keywords):
        fig.add_trace(go.Scatter(
            x=[f'Month {i+1}' for i in range(12)],
            y=traffic_forecast[i],
            mode='lines+markers',
            name=keyword,
            text=hover_texts[i],  # Hover text with detailed information
            hoverinfo='text'
        ))

    # Add a line for the total
    fig.add_trace(go.Scatter(
        x=[f'Month {i+1}' for i in range(12)],
        y=total_traffic_forecast,
        mode='lines+markers',
        name='Total',
        line=dict(color='black', width=2, dash='dash')
    ))

    # Update layout to display full numbers on the y-axis and adjust figure height
    fig.update_layout(
        title='Estimated Traffic Forecast Based on Domains per Month',
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
