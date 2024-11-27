# DSB Train Punctuality Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dsbscraper.streamlit.app)

An interactive dashboard that visualizes punctuality data from DSB (Danish State Railways) for both regional/long-distance trains and S-trains. The dashboard provides real-time insights into train performance across different routes in Denmark.

## Features

- **Real-time Data**: Automatically fetches and caches data from DSB's official website
- **Multiple Train Types**: Switch between Regional & Long Distance trains and S-trains
- **Interactive Filtering**: Select specific routes and date ranges
- **Performance Metrics**:
  - Target Punctuality
  - Actual Punctuality
  - Compensation Rates
- **Data Export**: Download filtered data as CSV

## Installation

1. Clone the repository:
```bash
git clone https://github.com/FPWRasmussen/DSBScraper.git
cd dsb-punctuality-dashboard
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```