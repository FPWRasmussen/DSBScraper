import re
from datetime import datetime
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_soup(url: str) -> BeautifulSoup:
    with requests.Session() as s:
        response = s.get(url, timeout=10)
    return BeautifulSoup(response.text, features="html.parser")

def clean_route_name(route: str) -> str:
    """Standardize route names"""
    route_mapping = {
        "København - København Lufthavn (CPH Lufthavn)": "København - CPH Lufthavn",
        "København - Kastrup (CPH Lufthavn)": "København - CPH Lufthavn",
        "København - CPH Lufthavn": "København - CPH Lufthavn"
    }
    route = re.sub(r'\s+', ' ', route.strip())
    route = route.replace('/ ', '/')
    return route_mapping.get(route, route)

def parse_percentage(value: str) -> float:
    """Handle percentage parsing with various edge cases"""
    if not value or value.strip().upper() == 'N/A':
        return None
        
    try:
        # Remove all non-digit characters except . and ,
        cleaned = re.sub(r'[^\d,.]', '', value.strip())
        
        # Handle cases with multiple decimal separators
        if cleaned.count(',') > 1 or cleaned.count('.') > 1:
            parts = re.split(r'[,.]', cleaned)
            cleaned = parts[0] + '.' + parts[1]
            
        cleaned = cleaned.replace(',', '.')
        result = float(cleaned)
        
        # Handle cases where the value might be already in decimal form
        return result if result <= 100 else result/10
    except (ValueError, AttributeError, IndexError):
        return None

def process_table_row(cells) -> dict:
    """Process a single table row and return structured data"""
    if len(cells) != 4:
        return None
        
    try:
        route = clean_route_name(cells[0].text)
        target = parse_percentage(cells[1].text)
        actual = parse_percentage(cells[2].text)
        compensation = parse_percentage(cells[3].text)
        
        # Allow rows where target and compensation exist
        if target is not None and compensation is not None:
            return {
                'Route': route,
                'Target_Punctuality': target,
                'Actual_Punctuality': actual if actual is not None else float('nan'),
                'Compensation': compensation
            }
    except Exception as e:
        print(f"Error processing row: {e}")
    
    return None

def extract_table_data(soup: BeautifulSoup) -> pd.DataFrame:
    """Extract and process all table data from the soup"""
    tables = []
    months = []
    years = []
    
    valid_months = [
        'Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 
        'Juli', 'August', 'September', 'Oktober', 'November', 'December'
    ]
    
    # Find all tables and their corresponding months
    for section in soup.find_all('section'):
        year_month_header = section.find('h2')
        if not year_month_header:
            continue
            
        header_text = year_month_header.text.strip()
        
        # Process year headers
        if header_text in str(np.arange(2014, datetime.now().year + 1)):
            year = header_text
        # Process month headers
        elif header_text in valid_months:
            month = header_text
            table = section.find('table')
            if table:
                years.append(year)
                months.append(month)
                tables.append(table)
    
    all_data = []
    
    for year, month, table in zip(years, months, tables):
        rows = table.find_all('tr')
        skip_rows = False
        
        for row in rows[1:]:  # Skip header row
            if "<strong>" in str(row):
                skip_rows = True
                continue
                
            if skip_rows:
                continue
                
            cells = row.find_all('td')
            row_data = process_table_row(cells)
            
            if row_data:
                row_data.update({
                    "Year": year,
                    "Month": month
                })
                all_data.append(row_data)

    df = pd.DataFrame(all_data)
    df.to_csv('train_punctuality_data.csv', index=False)
    return df
