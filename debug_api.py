#!/usr/bin/env python3
"""Debug script to see raw API data"""

import requests
import json

def debug_api():
    """Fetch and display raw API data"""
    
    url = 'https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast'
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://4surfers.co.il',
        'Referer': 'https://4surfers.co.il/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    data = {"beachAreaId": "80"}
    
    print("🌊 Fetching API data...")
    response = requests.post(url, json=data, headers=headers, timeout=30)
    
    if response.status_code == 200:
        api_data = response.json()
        
        print("\n✅ Got API response\n")
        print("=" * 80)
        
        # Show first day's data
        if 'dailyForecastList' in api_data:
            first_day = api_data['dailyForecastList'][0]
            
            print(f"📅 Date: {first_day.get('forecastLocalTime', 'N/A')}")
            print(f"\n🔍 Available fields in day forecast:")
            for key in first_day.keys():
                if key != 'forecastHours':
                    print(f"   - {key}: {first_day[key]}")
            
            print("\n⏰ Hourly forecasts:\n")
            forecast_hours = first_day.get('forecastHours', [])
            
            # Show first few hours in detail
            for i, hour in enumerate(forecast_hours[:8]):
                hour_time = hour.get('forecastLocalHour', 'N/A')
                print(f"\n🕐 Hour {i+1}: {hour_time}")
                print("-" * 80)
                
                # Show ALL fields
                for key, value in hour.items():
                    if isinstance(value, (int, float, str, bool)) or value is None:
                        print(f"   {key:25s} = {value}")
                
            # Focus on wave-related fields for all hours
            print("\n\n" + "=" * 80)
            print("📊 WAVE DATA FOR ALL HOURS TODAY:")
            print("=" * 80)
            
            for hour in forecast_hours:
                hour_time = hour.get('forecastLocalHour', 'N/A')
                try:
                    dt_str = hour_time.split('T')[1][:5]  # Get HH:MM
                except:
                    dt_str = hour_time
                
                wave_height = hour.get('waveHeight', 0)
                swell_height = hour.get('swellHeight', 0)
                surf_from = hour.get('surfHeightFrom', 0)
                surf_to = hour.get('surfHeightTo', 0)
                period = hour.get('wavePeriod', 0)
                wind = hour.get('windSpeed', 0)
                desc = hour.get('surfHeightDesc', '')
                
                print(f"{dt_str} | wave:{wave_height}m swell:{swell_height}m surf:{surf_from}-{surf_to}m period:{period}s wind:{wind}kts | {desc}")
        
        # Save full response to file for inspection
        with open('api_debug_full.json', 'w', encoding='utf-8') as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n💾 Full API response saved to: api_debug_full.json")
        
    else:
        print(f"❌ API error: {response.status_code}")

if __name__ == "__main__":
    debug_api()
