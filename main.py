import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import get_soup, extract_table_data
from datetime import datetime
# Page configuration
st.set_page_config(page_title="Train Punctuality Dashboard", layout="wide")
st.title("Train Punctuality Dashboard")

# Sidebar for train type selection
st.sidebar.title("Settings")
train_type = st.sidebar.radio(
    "Select Train Type",
    ["Regional & Long Distance", "S-trains"],
    index=0
)

# Define URLs based on selection
urls = {
    "Regional & Long Distance": "https://www.dsb.dk/find-produkter-og-services/dsb-rejsetidsgaranti/dsb-pendler-rejsetidsgaranti/kompensationsstorrelse/trafikdata-for-fr---ny/",
    "S-trains": "https://www.dsb.dk/find-produkter-og-services/dsb-rejsetidsgaranti/dsb-pendler-rejsetidsgaranti/kompensationsstorrelse/data-s-tog/"
}

# Cache the data loading function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(url):
    soup = get_soup(url)
    df = extract_table_data(soup)
    
    # Convert Danish months to datetime
    danish_months = {
        'Januar': 1, 'Februar': 2, 'Marts': 3, 'April': 4, 'Maj': 5, 'Juni': 6,
        'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'December': 12
    }
    
    # Create Date column
    df['Date'] = pd.to_datetime(df.apply(lambda x: f"{x['Year']}-{danish_months[x['Month']]}-01", axis=1))
    return df

# Load data using the cached function
df = load_data(urls[train_type])
# Route selection
st.header("Filter Options")
all_routes = df['Route'].unique().tolist()
selected_routes = st.multiselect(
    "Select Routes to Display",
    options=all_routes,
    default=all_routes[:5]
)

# Convert datetime to string for the slider
date_options = sorted(df['Date'].unique())
date_options_str = [d.strftime('%Y-%m') for d in date_options]

# Create the date range selector
start_idx, end_idx = st.select_slider(
    'Select Date Range',
    options=range(len(date_options_str)),
    value=(0, len(date_options_str)-1),
    format_func=lambda x: date_options_str[x]
)

# Convert back to datetime for filtering
start_date = date_options[start_idx]
end_date = date_options[end_idx]

# Filter data based on selection
filtered_df = df[
    (df['Route'].isin(selected_routes)) & 
    (df['Date'].between(start_date, end_date))
]

# Create three plots
def create_plot(data, y_column, title):
    # Replace underscores with spaces in column names
    y_label = y_column.replace('_', ' ')
    
    fig = px.line(
        data,
        x='Date',
        y=y_column,
        color='Route',
        title=title,
        markers=True
    )
    fig.update_layout(
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150),
        xaxis_title="Date",
        yaxis_title=f"{y_label} (%)"  # Add percentage unit
    )
    return fig

# Add introductory text
st.markdown("""
### DSB Train Punctuality Analysis
This dashboard presents punctuality data from DSB (Danish State Railways) for both regional/long-distance trains and S-trains. 
Use the sidebar to switch between train types and the filters below to analyze specific routes and time periods.

#### How to use this dashboard:
1. Select train type (Regional & Long Distance or S-trains) from the sidebar
2. Choose specific routes using the multiselect dropdown
3. Adjust the time period using the date range slider
""")

# ... (filtering code remains the same)

# Display plots vertically with better titles
st.plotly_chart(
    create_plot(filtered_df, 'Compensation', 'Monthly Compensation Rates'),
    use_container_width=True
)
st.plotly_chart(
    create_plot(filtered_df, 'Actual_Punctuality', 'Monthly Actual Punctuality Performance'),
    use_container_width=True
)
st.plotly_chart(
    create_plot(filtered_df, 'Target_Punctuality', 'Monthly Target Punctuality Thresholds'),
    use_container_width=True
)

# Add download button for filtered data
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_train_data.csv",
    mime="text/csv",
)

# Enhanced explanatory text
st.markdown("""
#### About the Metrics
- **Target Punctuality**: The minimum punctuality percentage that DSB aims to achieve for each route. This represents the service level agreement.
- **Actual Punctuality**: The percentage of trains that arrived on time for each route. A train is considered punctual if it arrives within 2:59 minutes of schedule.
- **Compensation**: The percentage of compensation that passengers are eligible for based on the difference between target and actual punctuality.

#### Data Updates
The data is refreshed hourly from DSB's official website. Last update: {}.
""".format(datetime.now().strftime('%Y-%m-%d %H:%M UTC')))