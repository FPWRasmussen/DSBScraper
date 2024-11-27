import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_soup(url: str) -> BeautifulSoup:
    with requests.Session() as s:
        response = s.get(url, timeout=10)
    soup = BeautifulSoup(response.text, features="html.parser")
    return soup

def extract_table_data(soup):
    tables = []
    months = []
    years = []
    # Find all tables and their corresponding months
    for section in soup.find_all('section'):

        year_month_header = section.find('h2')

        if year_month_header and year_month_header.text.strip() in str((np.arange(2014, 2025))):
            year = year_month_header.text.strip()
            print(year)
                
        elif year_month_header and year_month_header.text.strip() in [
            'Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 
            'Juli', 'August', 'September', 'Oktober', 'November', 'December'
        ]:
            month = year_month_header.text.strip()
            print(month)
            # Find corresponding table
            table = section.find('table')
            if table:
                years.append(year)
                months.append(month)
                tables.append(table)
    
    all_data = []
    
    for year, month, table in zip(years, months, tables):
        rows = table.find_all('tr')
        skip_rows = False
        
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == 4:
                if "<strong>" in str(cells[0]):                 # Check if route contains a <strong> tag
                    print("SKIPPED")
                    skip_rows = True
                    continue
                
                if skip_rows:
                    continue

                # Clean the data
                route = re.sub(r'\s+', ' ', cells[0].text.strip())
                # route = route.replace('/', '-')  # Replace forward slash with dash
                # route = re.sub(r'[-/]+', '-', route)  # Normalize any combination of dashes and slashes
                # route = route.replace(' - ', '-').replace(' -', '-').replace('- ', '-')  # Normalize spaces around dashes
                route = route.replace('/ ', '/')
                if route in [
                "København - København Lufthavn (CPH Lufthavn)",
                "København - Kastrup (CPH Lufthavn)",
                "København - CPH Lufthavn"
                ]:
                    route = "København - CPH Lufthavn"

                target = re.sub(r'[^\d]', '', cells[1].text.strip())[:3]
                actual = re.sub(r'[^\d]', '', cells[2].text.strip())[:3]
                compensation = re.sub(r'[^\d]', '', cells[3].text.strip())[:3]
                
                # Convert to float where possible
                try:
                    target = float(target)/10
                    actual = float(actual)/10
                    compensation = float(compensation)/10

                    all_data.append({
                        "Year" : year,
                        'Month': month,
                        'Route': route,
                        'Target_Punctuality': target,
                        'Actual_Punctuality': actual,
                        'Compensation': compensation
                    })
                except:
                    continue

    df = pd.DataFrame(all_data)
    # Save to CSV
    df.to_csv('train_punctuality_data.csv', index=False)
    return df



if __name__ == "__main__":
    # Usage:
    df = extract_table_data(soup)