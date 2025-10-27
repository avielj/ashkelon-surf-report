#!/usr/bin/env python3
"""
Test script to explore gosurf.co.il data
This is for research purposes - to see what data is available
"""

import requests
from bs4 import BeautifulSoup
import json

def fetch_gosurf_data():
    """Fetch and parse gosurf.co.il forecast page"""
    
    url = 'https://gosurf.co.il/forecast/ashqelon'
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'dnt': '1',
    }
    
    try:
        print("🌊 Fetching gosurf.co.il forecast...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return None
        
        print(f"✅ Got response ({len(response.text)} bytes)")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find forecast tables
        tables = soup.find_all('table')
        print(f"📊 Found {len(tables)} tables")
        
        # Look for data in script tags or data attributes
        scripts = soup.find_all('script')
        print(f"📜 Found {len(scripts)} script tags")
        
        # Try to find JSON data
        for script in scripts:
            script_text = script.string
            if script_text and ('forecast' in script_text.lower() or 'swell' in script_text.lower()):
                print("\n🔍 Found potential forecast data in script:")
                print(script_text[:500])
                print("...")
        
        # Parse first table as example
        if tables:
            print("\n📋 First table structure:")
            first_table = tables[0]
            rows = first_table.find_all('tr')
            print(f"   Rows: {len(rows)}")
            
            for i, row in enumerate(rows[:5]):  # First 5 rows
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"   Row {i}: {cell_texts}")
        
        return soup
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("🏄‍♂️ GoSurf.co.il API Explorer\n")
    print("=" * 60)
    
    soup = fetch_gosurf_data()
    
    if soup:
        print("\n✅ Page fetched successfully")
        print("\n💡 Notes:")
        print("   - GoSurf uses client-side rendering")
        print("   - May need browser automation or API discovery")
        print("   - 4surfers.co.il API is cleaner and more reliable")
        print("\n📌 Recommendation: Stick with 4surfers.co.il API")
        print("   It provides: wave height, swell height, period, wind")
        print("   All the data we need for quality surf detection!")
    else:
        print("\n❌ Failed to fetch data")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
