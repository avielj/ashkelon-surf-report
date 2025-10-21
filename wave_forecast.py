"""
Wave Forecast Application for 4surfers.co.il

This application scrapes wave data from 4surfers.co.il specifically for Israeli beaches,
with a focus on Ashkelon wave forecasting.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import requests
from typing import Dict, List, Optional
import re


class FourSurfersWaveForecast:
    """Main class for wave forecasting from 4surfers.co.il"""
    
    def __init__(self, telegram_bot_token=None):
        self.base_url = "https://4surfers.co.il"
        self.ashkelon_url = "https://4surfers.co.il/#/beachArea?beachAreaId=80"
        self.telegram_bot_token = telegram_bot_token
        self.beach_slugs = {
            "nahariya": "נהריה",
            "haifa-bay": "חיפה-מפרץ", 
            "haifa-west": "חיפה-מערב",
            "carmel-beach": "חוף כרמל",
            "netanya": "נתניה",
            "tel-aviv-jaffa": "תל אביב-יפו",
            "ashdod": "אשדוד",
            "ashkelon": "אשקלון"
        }
    
    def _try_extended_forecast_api(self) -> Optional[Dict]:
        """
        Try the extended forecast API that provides 10 days with detailed hourly data
        
        Returns:
            Dictionary with extended forecast data or None if failed
        """
        try:
            print("🔥 Trying extended forecast API (10 days detailed data)...")
            
            url = 'https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast'
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=UTF-8',
                'DNT': '1',
                'Origin': 'https://4surfers.co.il',
                'Referer': 'https://4surfers.co.il/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'X-App-JWT': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkFub255bW91cyIsIm5iZiI6MTc2MDk0MTkyOCwiZXhwIjoxNzYwOTQzNzI4LCJpYXQiOjE3NjA5NDE5Mjh9.vXfU8piO4em6AMU3GxFcjHAmxz_2RT6lYUxr0gUdMRs',
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }
            
            data = {"beachAreaId": "80"}
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                api_data = response.json()
                print("🎉 Extended API successful!")
                print(f"📊 Extended API response size: {len(str(api_data))} characters")
                
                # Check if we got daily forecast data
                if 'dailyForecastList' in api_data and api_data['dailyForecastList']:
                    forecast_days = len(api_data['dailyForecastList'])
                    print(f"📅 Got {forecast_days} days of detailed forecast data!")
                    
                    # Save raw extended API response
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    extended_filename = f"extended_api_response_{timestamp}.json"
                    with open(extended_filename, 'w', encoding='utf-8') as f:
                        json.dump(api_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Extended API response saved: {extended_filename}")
                    
                    # Parse the extended API response
                    return self._parse_extended_api_response(api_data)
                else:
                    print("⚠️ Extended API response doesn't contain dailyForecastList")
                    return None
            else:
                print(f"❌ Extended API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Extended API error: {e}")
            return None

    def get_ashkelon_forecast_api(self) -> Optional[Dict]:
        """Get wave forecast for Ashkelon using direct API method (faster)"""
        try:
            print("🚀 Using direct 4surfers API...")
            
            # Try extended forecast API first (10 days with detailed hourly data)
            extended_result = self._try_extended_forecast_api()
            if extended_result:
                return extended_result
            
            print("🔄 Extended API failed, falling back to basic API...")
            
            # Fallback to basic API endpoint for current conditions
            url = 'https://4surfers.co.il/webapi/BeachArea/GetBeachAreaData'
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=UTF-8',
                'DNT': '1',
                'Origin': 'https://4surfers.co.il',
                'Referer': 'https://4surfers.co.il/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"'
            }
            
            # Request data for Ashkelon (beachAreaId: 80)
            data = {"beachAreaId": "80"}
            
            # Make the API request
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                api_data = response.json()
                print("✅ Successfully retrieved data from 4surfers API!")
                print(f"📊 API response size: {len(str(api_data))} characters")
                
                # Save raw API response for debugging
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                api_filename = f"api_response_ashkelon_{timestamp}.json"
                with open(api_filename, 'w', encoding='utf-8') as f:
                    json.dump(api_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Raw API response saved: {api_filename}")
                
                # Parse the API response into our format
                return self._parse_api_response(api_data)
            else:
                print(f"❌ API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ API method error: {e}")
            return None
    
    def _parse_api_response(self, api_data: Dict) -> Optional[Dict]:
        """Parse the API response into our standard format"""
        try:
            forecast_data = {
                'beach': 'ashkelon',
                'beach_hebrew': 'אשקלון',
                'source': '4surfers.co.il API',
                'timestamp': datetime.now().isoformat(),
                'daily_forecasts': {},
                'surf_quality_indicators': [],
                'surf_quality_counts': {}
            }
            
            print("📊 Parsing API response data...")
            
            # Look for forecast data in the API response
            if isinstance(api_data, dict):
                print(f"📋 API data keys: {list(api_data.keys())}")
                
                # Extract surf quality indicators from the response
                surf_terms = {
                    'פלטה': 'flat', 'שטוח': 'flat',
                    'קרסול': 'ankle_high', 'קרסול עד ברך': 'ankle_to_knee',
                    'ברך': 'knee_high', 'מעל ברך': 'above_knee',
                    'כתף': 'shoulder_high', 'מעל כתף': 'above_shoulder',
                    'מותן': 'waist_high', 'ראש': 'head_high', 'מעל ראש': 'overhead'
                }
                api_str = str(api_data)
                
                for hebrew_term, english_term in surf_terms.items():
                    count = api_str.count(hebrew_term)
                    if count > 0:
                        forecast_data['surf_quality_indicators'].append({
                            'hebrew': hebrew_term,
                            'english': english_term,
                            'count': count
                        })
                        forecast_data['surf_quality_counts'][hebrew_term] = count
                
                print(f"🔍 Found {len(forecast_data['surf_quality_indicators'])} surf quality indicators")
                
                # Try to extract daily forecasts from API structure
                daily_count = self._extract_daily_forecasts_from_api(api_data, forecast_data)
                print(f"📅 Extracted {daily_count} days of forecast data")
            
            return forecast_data
            
        except Exception as e:
            print(f"Error parsing API response: {e}")
            return None
    
    def _extract_daily_forecasts_from_api(self, api_data: Dict, forecast_data: Dict) -> int:
        """Extract daily forecasts from API data"""
        daily_count = 0
        try:
            hebrew_days = {
                0: 'שני', 1: 'שלישי', 2: 'רביעי', 3: 'חמישי', 
                4: 'שישי', 5: 'שבת', 6: 'ראשון'
            }
            
            # Process DailyForecast array
            if 'DailyForecast' in api_data and isinstance(api_data['DailyForecast'], list):
                daily_forecast = api_data['DailyForecast']
                print(f"📊 Processing {len(daily_forecast)} DailyForecast entries")
                
                # Group forecasts by date
                daily_groups = {}
                
                for item in daily_forecast:
                    if isinstance(item, dict) and 'forecastLocalHour' in item:
                        # Parse the date/time
                        forecast_time = item.get('forecastLocalHour', '')
                        wave_height = item.get('waveHeight', 0)
                        
                        try:
                            # Parse the datetime string (e.g., "2025-10-20T06:00:00+03:00")
                            dt = datetime.fromisoformat(forecast_time.replace('+03:00', ''))
                            date_key = dt.strftime('%Y-%m-%d')
                            time_key = dt.strftime('%H:%M')
                            
                            # Get Hebrew day name
                            hebrew_day = hebrew_days.get(dt.weekday(), 'לא ידוע')
                            
                            # Initialize date group if needed
                            if date_key not in daily_groups:
                                daily_groups[date_key] = {
                                    'hebrew_day': hebrew_day,
                                    'english_day': self._get_english_day(dt.weekday()),
                                    'hebrew_date': dt.strftime('%d/%m'),
                                    'times': {}
                                }
                            
                            # Add time data - focus on key times
                            if time_key in ['06:00', '12:00', '18:00']:
                                # Determine surf quality based on wave height
                                surf_quality = self._wave_height_to_quality(wave_height)
                                
                                daily_groups[date_key]['times'][time_key] = {
                                    'wave_height': wave_height,
                                    'surf_quality': surf_quality,
                                    'source': 'api'
                                }
                        
                        except Exception as e:
                            print(f"Error parsing forecast item: {e}")
                            continue
                
                # Convert grouped data to our format
                for date_key, day_data in daily_groups.items():
                    if day_data['times']:  # Only include days with time data
                        forecast_data['daily_forecasts'][date_key] = day_data
                        daily_count += 1
                
                print(f"✅ Extracted {daily_count} days of forecast data from API")
            
            # Also check current conditions from 'lastCSC'
            if 'lastCSC' in api_data:
                current = api_data['lastCSC']
                wave_height = current.get('surfHeightFrom', 0)
                if wave_height > 0:
                    print(f"🌊 Current conditions: {wave_height}m - {current.get('surfHeightDesc', 'N/A')}")
            
            return daily_count
            
        except Exception as e:
            print(f"Error extracting daily forecasts from API: {e}")
            return 0
    
    def _parse_extended_api_response(self, api_data: Dict) -> Optional[Dict]:
        """
        Parse the extended API response from GetBeachAreaForecast endpoint
        
        Args:
            api_data: Raw API response containing dailyForecastList
            
        Returns:
            Structured forecast data dictionary
        """
        try:
            if 'dailyForecastList' not in api_data:
                print("❌ No dailyForecastList in extended API response")
                return None
            
            daily_forecast_list = api_data['dailyForecastList']
            print(f"📊 Processing {len(daily_forecast_list)} days from extended API...")
            
            # Hebrew day names mapping
            hebrew_days = {
                0: 'שני',    # Monday
                1: 'שלישי',  # Tuesday
                2: 'רביעי',  # Wednesday
                3: 'חמישי',  # Thursday
                4: 'שישי',   # Friday
                5: 'שבת',    # Saturday
                6: 'ראשון'   # Sunday
            }
            
            daily_forecasts = {}
            surf_quality_counts = {}
            
            for day_forecast in daily_forecast_list:
                if 'forecastLocalTime' not in day_forecast:
                    continue
                    
                # Parse the forecast date
                forecast_date = day_forecast['forecastLocalTime']
                try:
                    dt = datetime.fromisoformat(forecast_date.replace('T', ' ').replace('+03:00', ''))
                    date_key = dt.strftime('%Y-%m-%d')
                    hebrew_date = dt.strftime('%d/%m')
                    hebrew_day = hebrew_days.get(dt.weekday(), 'לא ידוע')
                    english_day = dt.strftime('%A')
                    
                    # Process hourly forecasts for this day
                    forecast_hours = day_forecast.get('forecastHours', [])
                    
                    if forecast_hours:
                        times_data = {}
                        
                        for hour_forecast in forecast_hours:
                            hour_time = hour_forecast.get('forecastLocalHour', '')
                            wave_height = hour_forecast.get('waveHeight', 0)
                            surf_quality_hebrew = hour_forecast.get('surfHeightDesc', '')
                            
                            # Parse hour for time key
                            try:
                                hour_dt = datetime.fromisoformat(hour_time.replace('T', ' ').replace('+03:00', ''))
                                time_key = hour_dt.strftime('%H:%M')
                                
                                # Convert to surf quality with English
                                surf_quality_english = self._wave_height_to_quality(wave_height).split('(')[1].replace(')', '') if '(' in self._wave_height_to_quality(wave_height) else 'unknown'
                                surf_quality = f"{surf_quality_hebrew} ({surf_quality_english})" if surf_quality_hebrew else self._wave_height_to_quality(wave_height)
                                
                                times_data[time_key] = {
                                    'wave_height': wave_height,
                                    'surf_quality': surf_quality,
                                    'hebrew_time': self._get_hebrew_time_period(hour_dt.hour),
                                    'english_time': time_key,
                                    'source': 'extended_api'
                                }
                                
                                # Count surf qualities
                                if surf_quality_hebrew:
                                    surf_quality_counts[surf_quality_hebrew] = surf_quality_counts.get(surf_quality_hebrew, 0) + 1
                                    
                            except Exception as e:
                                print(f"Error parsing hour {hour_time}: {e}")
                                continue
                        
                        if times_data:
                            daily_forecasts[date_key] = {
                                'date': date_key,
                                'hebrew_date': hebrew_date,
                                'hebrew_day': hebrew_day,
                                'english_day': english_day,
                                'times': times_data
                            }
                            
                except Exception as e:
                    print(f"Error parsing date {forecast_date}: {e}")
                    continue
            
            # Create surf quality indicators list
            surf_quality_indicators = []
            for hebrew_quality, count in surf_quality_counts.items():
                english_quality = "unknown"
                if "פלטה" in hebrew_quality or "שטוח" in hebrew_quality:
                    english_quality = "flat"
                elif "קרסול עד ברך" in hebrew_quality:
                    english_quality = "ankle_to_knee"
                elif "קרסול" in hebrew_quality:
                    english_quality = "ankle_high"
                elif "מעל ברך" in hebrew_quality:
                    english_quality = "above_knee"
                elif "ברך" in hebrew_quality:
                    english_quality = "knee_high"
                elif "מעל כתף" in hebrew_quality:
                    english_quality = "above_shoulder"
                elif "כתף" in hebrew_quality:
                    english_quality = "shoulder_high"
                elif "מותן" in hebrew_quality:
                    english_quality = "waist_high"
                elif "מעל ראש" in hebrew_quality:
                    english_quality = "overhead"
                elif "ראש" in hebrew_quality:
                    english_quality = "head_high"
                
                surf_quality_indicators.append({
                    'hebrew': hebrew_quality,
                    'english': english_quality,
                    'count': count
                })
            
            print(f"✅ Successfully parsed {len(daily_forecasts)} days from extended API")
            print(f"🔍 Found {len(surf_quality_indicators)} surf quality indicators")
            
            return {
                'beach': 'ashkelon',
                'beach_hebrew': 'אשקלון',
                'source': '4surfers.co.il Extended API',
                'timestamp': datetime.now().isoformat(),
                'daily_forecasts': daily_forecasts,
                'surf_quality_indicators': surf_quality_indicators,
                'surf_quality_counts': surf_quality_counts
            }
            
        except Exception as e:
            print(f"❌ Error parsing extended API response: {e}")
            return None
    
    def _get_hebrew_time_period(self, hour: int) -> str:
        """Convert hour to Hebrew time period"""
        if 5 <= hour < 11:
            return "בוקר"  # Morning
        elif 11 <= hour < 17:
            return "צהרים"  # Afternoon
        elif 17 <= hour < 22:
            return "ערב"  # Evening
        else:
            return "לילה"  # Night
    
    def _wave_height_to_quality(self, wave_height: float) -> str:
        """Convert wave height to Hebrew surf quality"""
        if wave_height <= 0.1:
            return "פלטה (flat)"
        elif wave_height <= 0.2:
            return "שטוח (flat)"
        elif wave_height <= 0.4:
            return "קרסול (ankle_high)"
        elif wave_height <= 0.6:
            return "קרסול עד ברך (ankle_to_knee)"
        elif wave_height <= 0.8:
            return "ברך (knee_high)"
        elif wave_height <= 1.1:
            return "מעל ברך (above_knee)"
        elif wave_height <= 1.4:
            return "כתף (shoulder_high)"
        elif wave_height <= 1.7:
            return "מעל כתף (above_shoulder)"
        elif wave_height <= 2.1:
            return "מותן (waist_high)"
        elif wave_height <= 2.6:
            return "ראש (head_high)"
        else:
            return "מעל ראש (overhead)"
    
    def _get_english_day(self, weekday: int) -> str:
        """Get English day name from weekday number"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[weekday] if 0 <= weekday <= 6 else 'Unknown'

    def get_ashkelon_forecast(self) -> Optional[Dict]:
        """
        Get wave forecast specifically for Ashkelon - try API first for best data, fallback to browser
        
        Returns:
            Dictionary containing wave forecast data or None if failed
        """
        # Try API method first (now provides 10 days with detailed hourly data)
        print("� Attempting enhanced API method first...")
        api_result = self.get_ashkelon_forecast_api()
        
        if api_result and api_result.get('daily_forecasts'):
            forecast_days = len(api_result.get('daily_forecasts', {}))
            print(f"✅ API method successful! Got {forecast_days} days of detailed forecast data")
            return api_result
        
        # Fallback to browser method
        print("🔄 API method failed, trying browser method...")
        browser_result = self.fetch_wave_data_direct_url()
        
        if browser_result and browser_result.get('daily_forecasts'):
            forecast_days = len(browser_result.get('daily_forecasts', {}))
            print(f"✅ Browser method successful! Got {forecast_days} days of forecast data")
            return browser_result
            
        print("❌ Both methods failed!")
        return None
    
    def fetch_wave_data_direct_url(self) -> Optional[Dict]:
        """
        Fetch wave data from Ashkelon direct URL
        
        Returns:
            Dictionary containing wave data or None if failed
        """
        try:
            print(f"Fetching wave data for Ashkelon using direct URL...")
            print(f"URL: {self.ashkelon_url}")
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                page = browser.new_page()
                
                # Set user agent to avoid blocking
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                try:
                    # Load Ashkelon page directly
                    print("Loading Ashkelon forecast page...")
                    page.goto(self.ashkelon_url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for forecast data to load
                    print("Waiting for forecast data to load...")
                    time.sleep(8)  # Give more time for the specific page to load
                    
                    # Wait for network to settle
                    try:
                        page.wait_for_load_state("networkidle", timeout=15000)
                        print("Page fully loaded")
                    except:
                        print("Timeout waiting for network idle, proceeding...")
                    
                    # Look for and click the forecast tab (תחזית)
                    print("Looking for forecast tab 'תחזית'...")
                    
                    forecast_tab_found = False
                    
                    # Try to find the forecast tab specifically
                    forecast_tab_selectors = [
                        'a:has-text("תחזית")',
                        'li:has-text("תחזית")',
                        '[heading="תחזית"]',
                        'text="תחזית"',
                        '.nav-tabs a:has-text("תחזית")',
                        '.nav-tabs li:has-text("תחזית")'
                    ]
                    
                    for selector in forecast_tab_selectors:
                        try:
                            forecast_tab = page.locator(selector)
                            if forecast_tab.count() > 0:
                                print(f"Found forecast tab with selector: {selector}")
                                forecast_tab.first.click(timeout=5000)
                                forecast_tab_found = True
                                print("✅ Successfully clicked on תחזית tab!")
                                time.sleep(5)  # Wait for forecast content to load
                                break
                        except Exception as e:
                            print(f"Could not click forecast tab with {selector}: {str(e)[:100]}")
                            continue
                    
                    if not forecast_tab_found:
                        print("Forecast tab not found, trying alternative methods...")
                        
                        # Try to find any tabs and look for the one with forecast text
                        nav_tabs = page.locator('.nav-tabs li, .nav-tabs a, [class*="tab"]')
                        tab_count = nav_tabs.count()
                        
                        print(f"Found {tab_count} potential tabs")
                        
                        for i in range(min(10, tab_count)):
                            try:
                                tab = nav_tabs.nth(i)
                                tab_text = tab.inner_text()
                                print(f"Tab {i}: '{tab_text}'")
                                
                                if 'תחזית' in tab_text:
                                    print(f"Found תחזית in tab {i}, clicking...")
                                    tab.click(timeout=5000)
                                    forecast_tab_found = True
                                    time.sleep(5)
                                    break
                            except Exception as e:
                                print(f"Could not interact with tab {i}: {str(e)[:50]}")
                                continue
                    
                    # Also try clicking the beachAreaForecastTabClicked function if available
                    if not forecast_tab_found:
                        try:
                            print("Trying to trigger forecast tab function...")
                            page.evaluate("if(window.beachAreaForecastTabClicked) window.beachAreaForecastTabClicked()")
                            time.sleep(3)
                            forecast_tab_found = True
                        except:
                            pass
                    
                    if forecast_tab_found:
                        print("✅ Forecast tab activated, waiting for weekly data...")
                        
                        # Wait for forecast content to load
                        try:
                            page.wait_for_load_state("networkidle", timeout=10000)
                        except:
                            print("Timeout waiting for network idle after tab click")
                        
                        time.sleep(5)  # Additional wait for dynamic content
                        
                        # Look for weekly forecast elements
                        print("Looking for weekly forecast elements...")
                        weekly_indicators = ['יום', 'תאריך', 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
                        for indicator in weekly_indicators:
                            try:
                                count = page.locator(f'text*="{indicator}"').count()
                                if count > 0:
                                    print(f"Found {count} instances of weekly indicator '{indicator}'")
                            except:
                                continue
                    else:
                        print("❌ Could not activate forecast tab, proceeding with current page content...")
                    
                    # Look for forecast indicators to ensure data is loaded
                    forecast_indicators = ['קרסול', 'ברך', 'כתף', 'מותן']
                    indicators_found = 0
                    for indicator in forecast_indicators:
                        try:
                            count = page.locator(f'text="{indicator}"').count()
                            if count > 0:
                                indicators_found += 1
                                print(f"Found {count} instances of '{indicator}'")
                        except:
                            continue
                    
                    # Also look for time indicators
                    time_indicators = ['06:00', '6:00', '12:00', '18:00']
                    times_found = 0
                    for time_str in time_indicators:
                        try:
                            count = page.locator(f'text="{time_str}"').count()
                            if count > 0:
                                times_found += 1
                                print(f"Found {count} instances of time '{time_str}'")
                        except:
                            continue
                    
                    # Look for date patterns in the page
                    date_patterns = ['יום', 'תאריך', 'היום', 'מחר']  # Hebrew date-related words
                    for pattern in date_patterns:
                        try:
                            count = page.locator(f'text*="{pattern}"').count()
                            if count > 0:
                                print(f"Found {count} instances of date pattern '{pattern}'")
                        except:
                            continue
                    
                    if indicators_found > 0:
                        print(f"Found {indicators_found} different surf quality indicators")
                    if times_found > 0:
                        print(f"Found {times_found} different time indicators")
                    
                    if indicators_found == 0 and times_found == 0:
                        print("No forecast indicators found, trying to scroll and load more content...")
                        try:
                            # Scroll down to load more content
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(3)
                            page.evaluate("window.scrollTo(0, 0)")
                            time.sleep(2)
                        except:
                            pass
                    
                    # Take screenshot for debugging
                    try:
                        page.screenshot(path="ashkelon_direct.png", full_page=True)
                        print("Screenshot saved as ashkelon_direct.png")
                    except Exception as e:
                        print(f"Could not save screenshot: {e}")
                    
                    # Get the page content after all loading
                    html = page.content()
                    
                    # Look for and extract Highcharts data
                    print("Looking for Highcharts data...")
                    highcharts_data = self._extract_highcharts_data(page, html)
                    
                    # Parse the HTML content for forecast data
                    forecast_data = self._parse_forecast_html_enhanced(html, "ashkelon", "אשקלון")
                    
                    # Merge Highcharts data into forecast data
                    if highcharts_data:
                        forecast_data.update(highcharts_data)
                    
                    return forecast_data
                    
                except Exception as e:
                    print(f"Error during page interaction: {e}")
                    try:
                        html = page.content()
                        return self._parse_forecast_html_enhanced(html, "ashkelon", "אשקלון")
                    except:
                        return None
                        
                finally:
                    browser.close()
                    
        except Exception as e:
            print(f"Error fetching wave data: {e}")
            return None
    
    def fetch_wave_data(self, beach_name: str) -> Optional[Dict]:
        """
        Fetch wave data from 4surfers.co.il using Playwright
        
        Args:
            beach_name: The beach name (English key from beach_slugs)
            
        Returns:
            Dictionary containing wave data or None if failed
        """
        try:
            slug = self.beach_slugs.get(beach_name.lower().replace(" ", "-"), "")
            if not slug:
                print(f"Beach '{beach_name}' not found. Available beaches: {list(self.beach_slugs.keys())}")
                return None
            
            print(f"Fetching wave data for {beach_name} ({slug}) from 4surfers.co.il...")
            
            with sync_playwright() as p:
                # Launch browser (set headless=False for debugging)
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                page = browser.new_page()
                
                # Set user agent to avoid blocking
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                try:
                    # Load main page
                    print("Loading 4surfers.co.il...")
                    page.goto(f"{self.base_url}/#/", wait_until='networkidle', timeout=30000)
                    time.sleep(3)  # Wait for JavaScript to initialize
                    
                    # Try to find and click the beach selection
                    print(f"Looking for {slug} beach option...")
                    
                    # Try multiple selectors to find the beach selection
                    selectors_to_try = [
                        f'text="{slug}"',  # Direct text match
                        f'[title="{slug}"]',  # Title attribute
                        f'[alt="{slug}"]',  # Alt attribute
                        f'a[href*="{slug}"]',  # Link containing slug
                        f'button:has-text("{slug}")',  # Button with text
                        f'div:has-text("{slug}")',  # Div with text
                    ]
                    
                    beach_found = False
                    for selector in selectors_to_try:
                        try:
                            if page.locator(selector).count() > 0:
                                print(f"Found beach selector: {selector}")
                                page.click(selector, timeout=5000)
                                beach_found = True
                                break
                        except Exception as e:
                            print(f"Selector {selector} failed: {str(e)[:100]}")
                            continue
                    
                    if not beach_found:
                        # Try to look for any clickable elements containing the beach name
                        print("Trying to find beach in dropdown or menu...")
                        page.screenshot(path="debug_main_page.png")  # For debugging
                        
                        # Look for dropdown or menu elements
                        dropdowns = page.locator('select, .dropdown, .menu, [role="menu"]')
                        for i in range(dropdowns.count()):
                            try:
                                dropdown = dropdowns.nth(i)
                                if slug in dropdown.inner_text():
                                    dropdown.click()
                                    page.click(f'text="{slug}"')
                                    beach_found = True
                                    break
                            except:
                                continue
                    
                    if beach_found:
                        print("Beach selected, waiting for forecast data...")
                        
                        # Wait for network requests and dynamic content
                        try:
                            # Wait for network activity to settle
                            page.wait_for_load_state("networkidle", timeout=15000)
                            print("Network activity settled")
                            
                            # Wait a bit more for JavaScript to update content
                            time.sleep(5)
                            
                            # Try to wait for forecast content to appear
                            forecast_indicators = [
                                'קרסול', 'ברך', 'כתף', 'מותן',  # Surf quality terms
                                '06:00', '6:00', '12:00', '18:00'  # Time indicators
                            ]
                            
                            # Check if any forecast indicators appear
                            for indicator in forecast_indicators:
                                try:
                                    if page.locator(f'text="{indicator}"').count() > 0:
                                        print(f"Found forecast indicator: {indicator}")
                                        break
                                except:
                                    continue
                            
                        except Exception as e:
                            print(f"Timeout or error waiting for content: {str(e)[:100]}")
                            print("Proceeding with current page content...")
                        
                        # Additional wait for any remaining dynamic updates
                        time.sleep(2)
                        
                    else:
                        print("Could not find beach selector, trying to parse main page...")
                    
                    # Take screenshot for debugging
                    try:
                        page.screenshot(path=f"forecast_{beach_name}.png")
                        print(f"Screenshot saved as forecast_{beach_name}.png")
                    except Exception as e:
                        print(f"Could not save screenshot: {e}")
                    
                    # Get the page content after all loading
                    html = page.content()
                    
                    # Parse the HTML content for forecast data
                    forecast_data = self._parse_forecast_html(html, beach_name, slug)
                    
                    return forecast_data
                    
                except Exception as e:
                    print(f"Error during page interaction: {e}")
                    # Still try to parse whatever we have
                    try:
                        html = page.content()
                        return self._parse_forecast_html(html, beach_name, slug)
                    except:
                        return None
                        
                finally:
                    browser.close()
                    
        except Exception as e:
            print(f"Error fetching wave data: {e}")
            return None
    
    def _parse_forecast_html(self, html: str, beach_name: str, slug: str) -> Dict:
        """
        Parse forecast data from HTML content, specifically looking for 
        6:00, 12:00, 18:00 forecasts and surf quality indicators
        
        Args:
            html: HTML content from the page
            beach_name: Beach name in English
            slug: Beach name in Hebrew
            
        Returns:
            Dictionary with parsed forecast data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        forecast_data = {
            'beach': beach_name,
            'beach_hebrew': slug,
            'timestamp': datetime.now().isoformat(),
            'source': '4surfers.co.il',
            'raw_data_available': True,
            'hourly_forecasts': {}
        }
        
        try:
            # Get the full page text for comprehensive analysis
            full_text = soup.get_text()
            
            # Look for surf quality indicators (קרסול ברך כתף מותן)
            surf_quality_terms = {
                'קרסול': 'ankle_high',
                'ברך': 'knee_high', 
                'כתף': 'shoulder_high',
                'מותן': 'waist_high'
            }
            
            found_qualities = []
            for hebrew_term, english_term in surf_quality_terms.items():
                if hebrew_term in full_text:
                    found_qualities.append({
                        'hebrew': hebrew_term,
                        'english': english_term
                    })
            
            forecast_data['surf_quality_indicators'] = found_qualities
            
            # Look for specific time forecasts (6:00, 12:00, 18:00)
            target_times = ['06:00', '6:00', '12:00', '18:00']
            
            for time_str in target_times:
                # Find elements containing the target time
                time_elements = soup.find_all(text=re.compile(time_str))
                
                for element in time_elements:
                    # Get the parent container for this time
                    parent = element.parent if element.parent else None
                    if not parent:
                        continue
                    
                    # Look for surrounding forecast data
                    parent_text = parent.get_text()
                    
                    # Initialize time forecast data
                    time_forecast = {
                        'time': time_str,
                        'raw_text': parent_text.strip()[:200]  # First 200 chars
                    }
                    
                    # Look for surf quality in this time block
                    for hebrew_term, english_term in surf_quality_terms.items():
                        if hebrew_term in parent_text:
                            time_forecast['surf_quality'] = {
                                'hebrew': hebrew_term,
                                'english': english_term
                            }
                            break
                    
                    # Look for wave height numbers near this time
                    numbers_in_section = re.findall(r'\d+\.?\d*', parent_text)
                    if numbers_in_section:
                        time_forecast['numbers_found'] = [float(n) for n in numbers_in_section[:5]]
                    
                    # Look for wind information
                    if 'רוח' in parent_text or 'wind' in parent_text.lower():
                        wind_matches = re.findall(r'רוח.*?(\d+)', parent_text)
                        if wind_matches:
                            time_forecast['wind_speed'] = int(wind_matches[0])
                    
                    forecast_data['hourly_forecasts'][time_str] = time_forecast
            
            # Look for forecast tables or structured data
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text()
                
                # Check if this table contains our target times
                if any(time in table_text for time in target_times):
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        row_text = row.get_text().strip()
                        
                        # Check if this row contains a target time
                        for time_str in target_times:
                            if time_str in row_text:
                                if time_str not in forecast_data['hourly_forecasts']:
                                    forecast_data['hourly_forecasts'][time_str] = {}
                                
                                forecast_data['hourly_forecasts'][time_str]['table_row'] = row_text
                                
                                # Look for surf quality in this row
                                for hebrew_term, english_term in surf_quality_terms.items():
                                    if hebrew_term in row_text:
                                        forecast_data['hourly_forecasts'][time_str]['surf_quality'] = {
                                            'hebrew': hebrew_term,
                                            'english': english_term
                                        }
            
            # Look for any elements with time-related classes or IDs
            time_related_elements = soup.find_all(['div', 'span', 'td'], 
                                                 class_=re.compile(r'time|hour|forecast', re.I))
            time_related_elements.extend(soup.find_all(['div', 'span', 'td'], 
                                                      id=re.compile(r'time|hour|forecast', re.I)))
            
            for element in time_related_elements:
                element_text = element.get_text()
                for time_str in target_times:
                    if time_str in element_text:
                        if time_str not in forecast_data['hourly_forecasts']:
                            forecast_data['hourly_forecasts'][time_str] = {}
                        
                        forecast_data['hourly_forecasts'][time_str]['element_text'] = element_text.strip()[:200]
                        
                        # Look for surf quality
                        for hebrew_term, english_term in surf_quality_terms.items():
                            if hebrew_term in element_text:
                                forecast_data['hourly_forecasts'][time_str]['surf_quality'] = {
                                    'hebrew': hebrew_term,
                                    'english': english_term
                                }
            
            # General wave and wind extraction from full page
            # Look for wave height patterns
            wave_patterns = [
                r'גובה.*?(\d+\.?\d*)',  # Hebrew "height" + number
                r'גלים.*?(\d+\.?\d*)',  # Hebrew "waves" + number  
                r'(\d+\.?\d*)\s*מטר',   # Number + Hebrew "meter"
            ]
            
            for pattern in wave_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    forecast_data['wave_heights_found'] = [float(m) for m in matches[:5]]
                    break
            
            # Look for wind patterns
            wind_patterns = [
                r'רוח.*?(\d+)',  # Hebrew "wind" + number
                r'(\d+).*?רוח',  # Number + Hebrew "wind"
            ]
            
            for pattern in wind_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    forecast_data['wind_speeds_found'] = [int(m) for m in matches[:5]]
                    break
            
            # Store a sample of the full text for manual inspection
            forecast_data['full_text_sample'] = full_text[:2000]  # First 2000 chars
            
            # Count occurrences of surf quality terms
            quality_counts = {}
            for hebrew_term in surf_quality_terms.keys():
                count = full_text.count(hebrew_term)
                if count > 0:
                    quality_counts[hebrew_term] = count
            
            if quality_counts:
                forecast_data['surf_quality_counts'] = quality_counts
            
            # Summary assessment
            if forecast_data['hourly_forecasts']:
                forecast_data['forecast_times_found'] = len(forecast_data['hourly_forecasts'])
            else:
                forecast_data['forecast_times_found'] = 0
                
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            forecast_data['parsing_error'] = str(e)
        
        return forecast_data
    
    def _parse_forecast_html_enhanced(self, html: str, beach_name: str, slug: str) -> Dict:
        """
        Enhanced parsing for forecast data with dates and times
        
        Args:
            html: HTML content from the page
            beach_name: Beach name in English
            slug: Beach name in Hebrew
            
        Returns:
            Dictionary with parsed forecast data organized by dates and times
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        forecast_data = {
            'beach': beach_name,
            'beach_hebrew': slug,
            'timestamp': datetime.now().isoformat(),
            'source': '4surfers.co.il',
            'daily_forecasts': {},
            'surf_quality_indicators': [],
            'summary': {}
        }
        
        try:
            full_text = soup.get_text()
            
            # Surf quality indicators
            surf_quality_terms = {
                'קרסול': 'ankle_high',
                'ברך': 'knee_high', 
                'כתף': 'shoulder_high',
                'מותן': 'waist_high'
            }
            
            # Find quality indicators
            found_qualities = []
            quality_counts = {}
            for hebrew_term, english_term in surf_quality_terms.items():
                count = full_text.count(hebrew_term)
                if count > 0:
                    found_qualities.append({
                        'hebrew': hebrew_term,
                        'english': english_term,
                        'count': count
                    })
                    quality_counts[hebrew_term] = count
            
            forecast_data['surf_quality_indicators'] = found_qualities
            forecast_data['surf_quality_counts'] = quality_counts
            
            # Target times for each day
            target_times = ['06:00', '6:00', '12:00', '18:00']
            
            # Try to extract dates (look for date patterns)
            date_patterns = [
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # DD/MM/YYYY or similar
                r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',    # YYYY/MM/DD
            ]
            
            dates_found = []
            for pattern in date_patterns:
                matches = re.findall(pattern, full_text)
                dates_found.extend(matches)
            
            # Get next few days as potential forecast dates
            forecast_dates = []
            today = datetime.now()
            for i in range(7):  # Next 7 days
                date = today + timedelta(days=i)
                forecast_dates.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'display': date.strftime('%d/%m'),
                    'day_name': date.strftime('%A'),
                    'hebrew_day': self._get_hebrew_day(date.weekday())
                })
            
            forecast_data['forecast_dates'] = forecast_dates
            
            # Parse forecast tables and structured data
            tables = soup.find_all('table')
            for table in tables:
                self._parse_forecast_table(table, forecast_data, target_times, surf_quality_terms)
            
            # Look for weekly/daily forecast sections
            self._parse_weekly_forecast_sections(soup, forecast_data, target_times, surf_quality_terms)
            
            # Look for forecast containers with class/id patterns
            forecast_containers = soup.find_all(['div', 'section'], 
                                              class_=re.compile(r'forecast|weather|surf|wave|day|week|date', re.I))
            forecast_containers.extend(soup.find_all(['div', 'section'], 
                                                   id=re.compile(r'forecast|weather|surf|wave|day|week|date', re.I)))
            
            for container in forecast_containers:
                self._parse_forecast_container(container, forecast_data, target_times, surf_quality_terms)
            
            # Extract general wave and weather data
            self._extract_general_conditions(full_text, forecast_data)
            
            # Create summary
            forecast_data['summary'] = {
                'total_days_found': len(forecast_data['daily_forecasts']),
                'quality_indicators_found': len(found_qualities),
                'most_common_condition': max(quality_counts, key=quality_counts.get) if quality_counts else 'Unknown'
            }
            
        except Exception as e:
            print(f"Error in enhanced parsing: {e}")
            forecast_data['parsing_error'] = str(e)
        
        return forecast_data
    
    def _get_hebrew_day(self, weekday: int) -> str:
        """Convert weekday number to Hebrew day name"""
        hebrew_days = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
        return hebrew_days[weekday]
    
    def _parse_forecast_table(self, table, forecast_data: Dict, target_times: list, surf_quality_terms: Dict):
        """Parse forecast data from HTML tables"""
        try:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_text = row.get_text().strip()
                
                # Look for time indicators in this row
                for time_str in target_times:
                    if time_str in row_text:
                        # Try to find date context
                        date_key = 'unknown_date'
                        
                        # Look for surf quality in this row
                        surf_condition = 'unknown'
                        for hebrew_term, english_term in surf_quality_terms.items():
                            if hebrew_term in row_text:
                                surf_condition = f"{hebrew_term} ({english_term})"
                                break
                        
                        # Initialize date entry if not exists
                        if date_key not in forecast_data['daily_forecasts']:
                            forecast_data['daily_forecasts'][date_key] = {}
                        
                        # Store time forecast
                        forecast_data['daily_forecasts'][date_key][time_str] = {
                            'surf_condition': surf_condition,
                            'raw_text': row_text[:150],
                            'source': 'table'
                        }
                        
        except Exception as e:
            print(f"Error parsing table: {e}")
    
    def _parse_forecast_container(self, container, forecast_data: Dict, target_times: list, surf_quality_terms: Dict):
        """Parse forecast data from div/section containers"""
        try:
            container_text = container.get_text()
            
            # Look for time and quality combinations
            for time_str in target_times:
                if time_str in container_text:
                    # Find surf quality near this time
                    surf_condition = 'unknown'
                    for hebrew_term, english_term in surf_quality_terms.items():
                        if hebrew_term in container_text:
                            surf_condition = f"{hebrew_term} ({english_term})"
                            break
                    
                    date_key = 'container_data'
                    if date_key not in forecast_data['daily_forecasts']:
                        forecast_data['daily_forecasts'][date_key] = {}
                    
                    forecast_data['daily_forecasts'][date_key][time_str] = {
                        'surf_condition': surf_condition,
                        'raw_text': container_text[:150],
                        'source': 'container'
                    }
                    
        except Exception as e:
            print(f"Error parsing container: {e}")
    
    def _parse_weekly_forecast_sections(self, soup, forecast_data: Dict, target_times: list, surf_quality_terms: Dict):
        """Parse weekly forecast sections with dates and times, including Highcharts data"""
        try:
            # First, look for Highcharts SVG data
            self._parse_highcharts_data(soup, forecast_data)
            
            # Look for elements that might contain weekly/daily forecasts
            weekly_selectors = [
                '[class*="week"]',
                '[class*="daily"]', 
                '[class*="forecast"]',
                '[class*="day"]',
                '[class*="date"]'
            ]
            
            for selector in weekly_selectors:
                elements = soup.select(selector)
                
                for element in elements:
                    element_text = element.get_text()
                    
                    # Skip if element is too small or too large
                    if len(element_text) < 10 or len(element_text) > 2000:
                        continue
                    
                    # Look for date patterns in Hebrew/English
                    date_patterns = [
                        r'(\d{1,2}[\/\-\.]\d{1,2})',  # DD/MM format
                        r'(יום\s+[א-ת]+)',  # Hebrew day names
                        r'(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)',  # Hebrew day names
                        r'(היום|מחר|מחרתיים)',  # Today/tomorrow in Hebrew
                    ]
                    
                    date_found = None
                    for pattern in date_patterns:
                        match = re.search(pattern, element_text)
                        if match:
                            date_found = match.group(1)
                            break
                    
                    if date_found:
                        # Look for times and conditions in this date section
                        for time_str in target_times:
                            if time_str in element_text:
                                # Find surf quality
                                surf_condition = 'unknown'
                                for hebrew_term, english_term in surf_quality_terms.items():
                                    if hebrew_term in element_text:
                                        surf_condition = f"{hebrew_term} ({english_term})"
                                        break
                                
                                # Convert Hebrew date to standardized format if possible
                                date_key = self._normalize_date_key(date_found, element_text)
                                
                                if date_key not in forecast_data['daily_forecasts']:
                                    forecast_data['daily_forecasts'][date_key] = {}
                                
                                forecast_data['daily_forecasts'][date_key][time_str] = {
                                    'surf_condition': surf_condition,
                                    'raw_text': element_text[:200],
                                    'source': 'weekly_section',
                                    'original_date': date_found
                                }
                                
                                print(f"Found forecast: {date_key} {time_str} -> {surf_condition}")
            
        except Exception as e:
            print(f"Error parsing weekly forecast sections: {e}")
    
    def _parse_highcharts_data(self, soup, forecast_data: Dict):
        """Parse Highcharts SVG data to extract wave height forecasts"""
        try:
            # Look for Highcharts container
            highcharts_containers = soup.find_all('div', class_=re.compile(r'highcharts-container'))
            
            if not highcharts_containers:
                print("No Highcharts container found")
                return
            
            print(f"Found {len(highcharts_containers)} Highcharts container(s)")
            
            for container in highcharts_containers:
                # Look for SVG within the container
                svg_element = container.find('svg', class_='highcharts-root')
                
                if not svg_element:
                    continue
                
                print("Found Highcharts SVG, extracting data...")
                
                # Extract date labels from x-axis
                date_labels = []
                x_axis_labels = svg_element.find('g', class_='highcharts-axis-labels highcharts-xaxis-labels')
                
                if x_axis_labels:
                    label_texts = x_axis_labels.find_all('text')
                    for label_text in label_texts:
                        tspans = label_text.find_all('tspan')
                        if len(tspans) >= 2:
                            date_str = tspans[0].get_text().strip()  # e.g., "21/10"
                            day_name = tspans[1].get_text().strip()  # e.g., "שלישי"
                            
                            # Convert DD/MM to YYYY-MM-DD
                            try:
                                day, month = date_str.split('/')
                                year = datetime.now().year
                                if int(month) < datetime.now().month:
                                    year += 1  # Next year if month is in the past
                                
                                standardized_date = f"{year}-{int(month):02d}-{int(day):02d}"
                                
                                date_labels.append({
                                    'date': standardized_date,
                                    'display_date': date_str,
                                    'hebrew_day': day_name,
                                    'x_position': float(label_text.get('x', 0))
                                })
                            except:
                                continue
                
                print(f"Extracted {len(date_labels)} date labels from chart")
                
                # Extract wave height data from data labels
                wave_heights = []
                data_label_groups = svg_element.find_all('g', class_=re.compile(r'highcharts-data-labels'))
                
                for group in data_label_groups:
                    labels = group.find_all('g', class_='highcharts-label')
                    
                    for label in labels:
                        # Get the transform to find position
                        transform = label.get('transform', '')
                        x_pos = 0
                        y_pos = 0
                        
                        if 'translate(' in transform:
                            coords = transform.replace('translate(', '').replace(')', '').split(',')
                            if len(coords) >= 2:
                                x_pos = float(coords[0])
                                y_pos = float(coords[1])
                        
                        # Get the text content (wave height)
                        text_element = label.find('text')
                        if text_element:
                            tspans = text_element.find_all('tspan')
                            if tspans:
                                height_text = tspans[-1].get_text().strip()  # Last tspan has the actual value
                                try:
                                    height_value = float(height_text)
                                    wave_heights.append({
                                        'height': height_value,
                                        'x_position': x_pos,
                                        'y_position': y_pos
                                    })
                                except:
                                    continue
                
                print(f"Extracted {len(wave_heights)} wave height data points from chart")
                
                # Map wave heights to dates and times
                # Highcharts typically shows 3 data points per date (morning, noon, evening)
                times_hebrew = {'בוקר': '06:00', 'צהרים': '12:00', 'ערב': '18:00'}
                times_order = ['06:00', '12:00', '18:00']
                
                if date_labels and wave_heights:
                    # Sort dates by x position
                    date_labels.sort(key=lambda x: x['x_position'])
                    wave_heights.sort(key=lambda x: x['x_position'])
                    
                    # Group wave heights by date (3 per date)
                    points_per_date = 3
                    for i, date_info in enumerate(date_labels):
                        date_key = date_info['date']
                        
                        if date_key not in forecast_data['daily_forecasts']:
                            forecast_data['daily_forecasts'][date_key] = {}
                        
                        # Get the 3 wave height points for this date
                        start_idx = i * points_per_date
                        end_idx = start_idx + points_per_date
                        
                        if end_idx <= len(wave_heights):
                            date_wave_points = wave_heights[start_idx:end_idx]
                            
                            for j, (time_str, wave_point) in enumerate(zip(times_order, date_wave_points)):
                                height = wave_point['height']
                                
                                # Convert height to surf condition
                                if height >= 1.0:
                                    condition = 'כתף (shoulder_high)'
                                elif height >= 0.6:
                                    condition = 'ברך (knee_high)'
                                elif height >= 0.3:
                                    condition = 'קרסול (ankle_high)'
                                else:
                                    condition = 'שטוח (flat)'
                                
                                forecast_data['daily_forecasts'][date_key][time_str] = {
                                    'surf_condition': condition,
                                    'wave_height': height,
                                    'raw_text': f"Height: {height}m at {time_str}",
                                    'source': 'highcharts',
                                    'hebrew_day': date_info['hebrew_day'],
                                    'display_date': date_info['display_date']
                                }
                                
                                print(f"Mapped: {date_info['display_date']} ({date_info['hebrew_day']}) {time_str} -> {height}m ({condition})")
                
                break  # Process first chart found
                
        except Exception as e:
            print(f"Error parsing Highcharts data: {e}")
            import traceback
            traceback.print_exc()
    
    def _normalize_date_key(self, date_found: str, context_text: str) -> str:
        """Convert Hebrew/various date formats to standardized date key"""
        try:
            # Hebrew day name mapping
            hebrew_days = {
                'ראשון': 0, 'שני': 1, 'שלישי': 2, 'רביעי': 3, 
                'חמישי': 4, 'שישי': 5, 'שבת': 6
            }
            
            today = datetime.now()
            
            # Handle Hebrew day names
            for hebrew_day, weekday in hebrew_days.items():
                if hebrew_day in date_found:
                    # Calculate the date for this weekday
                    days_ahead = (weekday - today.weekday()) % 7
                    target_date = today + timedelta(days=days_ahead)
                    return target_date.strftime('%Y-%m-%d')
            
            # Handle today/tomorrow
            if 'היום' in date_found:
                return today.strftime('%Y-%m-%d')
            elif 'מחר' in date_found:
                return (today + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Handle DD/MM format
            if '/' in date_found or '-' in date_found or '.' in date_found:
                try:
                    # Try to parse DD/MM format
                    separator = '/' if '/' in date_found else ('-' if '-' in date_found else '.')
                    parts = date_found.split(separator)
                    if len(parts) >= 2:
                        day = int(parts[0])
                        month = int(parts[1])
                        year = today.year
                        
                        # If the date is in the past, assume next year
                        target_date = datetime(year, month, day)
                        if target_date < today:
                            target_date = datetime(year + 1, month, day)
                        
                        return target_date.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Fallback - return as is
            return date_found
            
        except Exception as e:
            print(f"Error normalizing date: {e}")
            return date_found
    
    def _extract_highcharts_data(self, page, html: str) -> Dict:
        """
        Extract data from Highcharts charts on the page
        
        Args:
            page: Playwright page object
            html: HTML content
            
        Returns:
            Dictionary with extracted chart data
        """
        try:
            chart_data = {
                'highcharts_found': False,
                'chart_dates': [],
                'chart_wave_data': [],
                'daily_forecasts': {}
            }
            
            # Look for Highcharts containers
            soup = BeautifulSoup(html, 'html.parser')
            highcharts_containers = soup.find_all(['div'], class_=re.compile(r'highcharts-container'))
            
            if highcharts_containers:
                print(f"Found {len(highcharts_containers)} Highcharts container(s)")
                chart_data['highcharts_found'] = True
                
                # Try to extract data using Playwright/JavaScript
                try:
                    # Execute JavaScript to get Highcharts data
                    chart_js_data = page.evaluate("""
                        () => {
                            const charts = [];
                            if (window.Highcharts && window.Highcharts.charts) {
                                for (let chart of window.Highcharts.charts) {
                                    if (chart && chart.series && chart.xAxis && chart.xAxis[0]) {
                                        const categories = chart.xAxis[0].categories || [];
                                        const series_data = [];
                                        
                                        for (let series of chart.series) {
                                            if (series.data) {
                                                series_data.push({
                                                    name: series.name,
                                                    data: series.data.map(point => ({
                                                        x: point.x,
                                                        y: point.y,
                                                        category: point.category
                                                    }))
                                                });
                                            }
                                        }
                                        
                                        charts.push({
                                            categories: categories,
                                            series: series_data
                                        });
                                    }
                                }
                            }
                            return charts;
                        }
                    """)
                    
                    if chart_js_data:
                        print(f"Extracted data from {len(chart_js_data)} chart(s) via JavaScript")
                        chart_data['js_chart_data'] = chart_js_data
                        
                        # Process JavaScript chart data for structured forecasts
                        self._process_js_chart_data(chart_data, chart_js_data)
                    
                except Exception as e:
                    print(f"Could not extract chart data via JavaScript: {e}")
                
                # Parse HTML for chart data
                for container in highcharts_containers:
                    container_html = str(container)
                    
                    # Extract date labels from SVG text elements
                    date_patterns = [
                        r'<text[^>]*>(\d{2}/\d{2})</text>',
                        r'<tspan[^>]*>(\d{2}/\d{2})</tspan>',
                        r'<text[^>]*><tspan>(\d{2}/\d{2})</tspan>'
                    ]
                    
                    dates_found = []
                    for pattern in date_patterns:
                        matches = re.findall(pattern, container_html)
                        dates_found.extend(matches)
                    
                    print(f"Extracted {len(dates_found)} date labels from chart: {dates_found}")
                    chart_data['chart_dates'] = dates_found
                    
                    # Extract Hebrew day names
                    hebrew_day_patterns = [
                        r'<tspan[^>]*>(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)</tspan>',
                        r'<text[^>]*>(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)</text>'
                    ]
                    
                    hebrew_days = []
                    for pattern in hebrew_day_patterns:
                        matches = re.findall(pattern, container_html)
                        hebrew_days.extend(matches)
                    
                    print(f"Extracted Hebrew days: {hebrew_days}")
                    chart_data['hebrew_days'] = hebrew_days
                    
                    # Extract wave height data from chart labels
                    wave_height_patterns = [
                        r'<tspan[^>]*>(\d\.?\d?)</tspan>',  # Wave heights like 0.4, 0.6
                        r'>(\d\.\d)<',  # Alternative pattern
                    ]
                    
                    wave_heights = []
                    for pattern in wave_height_patterns:
                        matches = re.findall(pattern, container_html)
                        for match in matches:
                            try:
                                height = float(match)
                                if 0.0 <= height <= 3.0:  # Reasonable wave height range
                                    wave_heights.append(height)
                            except:
                                continue
                    
                    print(f"Extracted {len(wave_heights)} wave height data points from chart: {wave_heights}")
                    chart_data['chart_wave_data'] = wave_heights
                    
                    # Extract tooltip data which contains detailed time/height info
                    tooltip_patterns = [
                        r'<td align="right">(בוקר|צהרים|ערב):</td><td[^>]*><b>\s*(\d\.?\d?)\s*<span[^>]*>מ\'</span></b></td>',
                        r'(בוקר|צהרים|ערב):[^>]*?(\d\.\d)',
                    ]
                    
                    time_data = []
                    for pattern in tooltip_patterns:
                        matches = re.findall(pattern, container_html)
                        time_data.extend(matches)
                    
                    print(f"Extracted time/height data: {time_data}")
                    chart_data['time_height_data'] = time_data
                    
                    # Create structured daily forecasts from extracted data
                    if dates_found and hebrew_days and time_data:
                        self._create_structured_forecast_from_chart(chart_data, dates_found, hebrew_days, time_data)
            
            else:
                print("No Highcharts containers found")
            
            return chart_data
            
        except Exception as e:
            print(f"Error extracting Highcharts data: {e}")
            return {}
    
    def _create_structured_forecast_from_chart(self, chart_data: Dict, dates: list, hebrew_days: list, time_data: list):
        """Create structured daily forecasts from chart data"""
        try:
            # Hebrew time mapping
            hebrew_time_map = {
                'בוקר': '06:00',    # Morning
                'צהרים': '12:00',   # Noon  
                'ערב': '18:00'      # Evening
            }
            
            # Hebrew day to weekday mapping
            hebrew_day_map = {
                'ראשון': 0, 'שני': 1, 'שלישי': 2, 'רביעי': 3, 
                'חמישי': 4, 'שישי': 5, 'שבת': 6
            }
            
            today = datetime.now()
            
            # Process each date
            for i, date_str in enumerate(dates):
                try:
                    # Parse date (DD/MM format)
                    day, month = map(int, date_str.split('/'))
                    year = today.year
                    
                    # Create date object
                    date_obj = datetime(year, month, day)
                    if date_obj < today:
                        date_obj = datetime(year + 1, month, day)
                    
                    date_key = date_obj.strftime('%Y-%m-%d')
                    
                    # Get Hebrew day if available
                    hebrew_day = hebrew_days[i] if i < len(hebrew_days) else 'לא ידוע'
                    
                    # Initialize date entry
                    if date_key not in chart_data['daily_forecasts']:
                        chart_data['daily_forecasts'][date_key] = {
                            'date': date_key,
                            'hebrew_date': date_str,
                            'hebrew_day': hebrew_day,
                            'english_day': date_obj.strftime('%A'),
                            'times': {}
                        }
                    
                    # Add time data for this date
                    base_index = i * 3  # Each date should have 3 times (morning, noon, evening)
                    
                    for j, (hebrew_time, english_time) in enumerate(hebrew_time_map.items()):
                        data_index = base_index + j
                        
                        if data_index < len(time_data):
                            time_hebrew, height_str = time_data[data_index]
                            
                            if time_hebrew == hebrew_time:
                                try:
                                    height = float(height_str)
                                    
                                    # Determine surf quality
                                    if height >= 1.0:
                                        quality_hebrew = 'כתף'
                                        quality_english = 'shoulder_high'
                                    elif height >= 0.6:
                                        quality_hebrew = 'ברך'
                                        quality_english = 'knee_high'
                                    elif height >= 0.3:
                                        quality_hebrew = 'קרסול'
                                        quality_english = 'ankle_high'
                                    else:
                                        quality_hebrew = 'שטוח'
                                        quality_english = 'flat'
                                    
                                    chart_data['daily_forecasts'][date_key]['times'][english_time] = {
                                        'hebrew_time': hebrew_time,
                                        'english_time': english_time,
                                        'wave_height': height,
                                        'surf_quality': f'{quality_hebrew} ({quality_english})',
                                        'source': 'highcharts'
                                    }
                                    
                                    print(f"Chart data: {date_str} ({hebrew_day}) {hebrew_time} -> {height}m ({quality_hebrew})")
                                    
                                except ValueError:
                                    continue
                    
                except Exception as e:
                    print(f"Error processing date {date_str}: {e}")
                    continue
            
        except Exception as e:
            print(f"Error creating structured forecast: {e}")
    
    def _process_js_chart_data(self, chart_data: Dict, js_chart_data: list):
        """Process JavaScript-extracted chart data into structured forecasts"""
        try:
            # Hebrew time mapping
            hebrew_time_map = {
                'בוקר': '06:00',    # Morning
                'צהרים': '12:00',   # Noon  
                'ערב': '18:00'      # Evening
            }
            
            # Hebrew day to English mapping  
            hebrew_day_eng_map = {
                'ראשון': 'Sunday', 'שני': 'Monday', 'שלישי': 'Tuesday', 'רביעי': 'Wednesday', 
                'חמישי': 'Thursday', 'שישי': 'Friday', 'שבת': 'Saturday'
            }
            
            today = datetime.now()
            
            # Process the first chart (wave forecast data)
            for chart in js_chart_data:
                if not chart.get('categories') or not chart.get('series'):
                    continue
                    
                # Skip if this looks like tidal data (has timestamps)
                if any(isinstance(point.get('x'), (int, float)) and point.get('x') > 1000000000 for series in chart.get('series', []) for point in series.get('data', [])):
                    print("Skipping tidal data chart")
                    continue
                
                categories = chart['categories']
                series = chart['series']
                
                print(f"Processing chart with {len(categories)} dates and {len(series)} time series")
                
                # Create mapping of series names to data
                series_map = {}
                for s in series:
                    series_name = s.get('name', '')
                    if series_name in hebrew_time_map:
                        series_map[series_name] = s.get('data', [])
                
                # Process each date category
                for i, category in enumerate(categories):
                    try:
                        # Parse category like "28/10<br/> <b>שלישי</b>"
                        if '<br/>' in category:
                            date_part, day_part = category.split('<br/>')
                            date_str = date_part.strip()
                            # Extract Hebrew day from <b>שלישי</b>
                            hebrew_day = day_part.replace('<b>', '').replace('</b>', '').strip()
                        else:
                            date_str = category.strip()
                            hebrew_day = 'לא ידוע'
                        
                        # Parse date (DD/MM format)
                        if '/' in date_str:
                            day, month = map(int, date_str.split('/'))
                            year = today.year
                            
                            # Create date object
                            date_obj = datetime(year, month, day)
                            if date_obj < today:
                                date_obj = datetime(year + 1, month, day)
                            
                            date_key = date_obj.strftime('%Y-%m-%d')
                            
                            # Initialize date entry
                            if date_key not in chart_data['daily_forecasts']:
                                chart_data['daily_forecasts'][date_key] = {
                                    'date': date_key,
                                    'hebrew_date': date_str,
                                    'hebrew_day': hebrew_day,
                                    'english_day': hebrew_day_eng_map.get(hebrew_day, date_obj.strftime('%A')),
                                    'times': {}
                                }
                            
                            # Process each time series for this date
                            for hebrew_time, english_time in hebrew_time_map.items():
                                if hebrew_time in series_map:
                                    series_data = series_map[hebrew_time]
                                    
                                    # Find data point for this date index
                                    if i < len(series_data):
                                        data_point = series_data[i]
                                        height = data_point.get('y', 0.0)
                                        
                                        # Determine surf quality based on height
                                        if height >= 1.0:
                                            quality_hebrew = 'כתף'
                                            quality_english = 'shoulder_high'
                                        elif height >= 0.6:
                                            quality_hebrew = 'ברך'
                                            quality_english = 'knee_high'
                                        elif height >= 0.3:
                                            quality_hebrew = 'קרסול'
                                            quality_english = 'ankle_high'
                                        else:
                                            quality_hebrew = 'שטוח'
                                            quality_english = 'flat'
                                        
                                        chart_data['daily_forecasts'][date_key]['times'][english_time] = {
                                            'hebrew_time': hebrew_time,
                                            'english_time': english_time,
                                            'wave_height': height,
                                            'surf_quality': f'{quality_hebrew} ({quality_english})',
                                            'source': 'javascript_highcharts'
                                        }
                                        
                                        print(f"JS Chart: {date_str} ({hebrew_day}) {hebrew_time} -> {height}m ({quality_hebrew})")
                        
                    except Exception as e:
                        print(f"Error processing category {category}: {e}")
                        continue
                
                # Only process the first valid chart (wave forecast)
                break
                
        except Exception as e:
            print(f"Error processing JavaScript chart data: {e}")
    
    def _extract_general_conditions(self, full_text: str, forecast_data: Dict):
        """Extract general wave and weather conditions"""
        try:
            # Wave height patterns
            wave_patterns = [
                r'(\d+\.?\d*)\s*מטר',  # X meters
                r'גובה.*?(\d+\.?\d*)',  # height X
                r'גלים.*?(\d+\.?\d*)',  # waves X
            ]
            
            wave_heights = []
            for pattern in wave_patterns:
                matches = re.findall(pattern, full_text)
                wave_heights.extend([float(m) for m in matches])
            
            if wave_heights:
                forecast_data['wave_heights'] = list(set(wave_heights))  # Remove duplicates
            
            # Wind patterns
            wind_patterns = [
                r'רוח.*?(\d+)',  # wind X
                r'(\d+).*?קמ״ה',  # X km/h
            ]
            
            wind_speeds = []
            for pattern in wind_patterns:
                matches = re.findall(pattern, full_text)
                wind_speeds.extend([int(m) for m in matches])
            
            if wind_speeds:
                forecast_data['wind_speeds'] = list(set(wind_speeds))
            
            # Extract wave height data for chart generation
            self._extract_wave_height_timeline(full_text, forecast_data)
                
        except Exception as e:
            print(f"Error extracting general conditions: {e}")
    
    def _extract_wave_height_timeline(self, full_text: str, forecast_data: Dict):
        """Extract wave height data for timeline chart"""
        try:
            # Convert surf quality to approximate wave heights (in meters)
            quality_to_height = {
                'פלטה': 0.1,      # flat
                'שטוח': 0.15,     # flat
                'קרסול': 0.3,     # ankle_high  
                'קרסול עד ברך': 0.5, # ankle_to_knee
                'ברך': 0.7,       # knee_high
                'מעל ברך': 1.0,   # above_knee
                'כתף': 1.3,       # shoulder_high
                'מעל כתף': 1.6,   # above_shoulder
                'מותן': 1.9,      # waist_high
                'ראש': 2.4,       # head_high
                'מעל ראש': 3.0    # overhead
            }
            
            # Generate wave height timeline based on daily forecasts
            wave_timeline = []
            
            if 'daily_forecasts' in forecast_data:
                for date_key, times_data in forecast_data['daily_forecasts'].items():
                    for time_str, time_info in times_data.items():
                        surf_condition = time_info.get('surf_condition', '')
                        
                        # Extract Hebrew surf quality from condition
                        height = 0.2  # Default small wave
                        for hebrew_term, wave_height in quality_to_height.items():
                            if hebrew_term in surf_condition:
                                height = wave_height
                                break
                        
                        wave_timeline.append({
                            'date': date_key,
                            'time': time_str,
                            'height': height,
                            'condition': surf_condition
                        })
            
            # If no daily forecasts, create timeline from general quality indicators
            if not wave_timeline and 'surf_quality_counts' in forecast_data:
                today = datetime.now()
                
                # Create a 7-day forecast based on most common conditions
                most_common = max(forecast_data['surf_quality_counts'], 
                                key=forecast_data['surf_quality_counts'].get) if forecast_data['surf_quality_counts'] else 'קרסול'
                
                base_height = quality_to_height.get(most_common, 0.3)
                
                for day in range(7):
                    date = today + timedelta(days=day)
                    date_str = date.strftime('%Y-%m-%d')
                    
                    for time_str in ['06:00', '12:00', '18:00']:
                        # Add some variation to make chart more interesting
                        variation = np.random.uniform(-0.1, 0.1) if day > 0 else 0
                        height = max(0.1, base_height + variation)
                        
                        wave_timeline.append({
                            'date': date_str,
                            'time': time_str,
                            'height': round(height, 2),
                            'condition': f'{most_common} (estimated)'
                        })
            
            forecast_data['wave_timeline'] = wave_timeline
            
        except Exception as e:
            print(f"Error creating wave timeline: {e}")
    
    def create_wave_height_chart(self, forecast_data: Dict, filename: str = None) -> str:
        """
        Create a 4surfers-style bar chart with Hebrew font support and RTL text
        
        Args:
            forecast_data: The forecast data dictionary
            filename: Optional filename for the chart image
            
        Returns:
            The filename of the generated chart image
        """
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import numpy as np
        from datetime import datetime, timedelta
        import matplotlib.font_manager as fm
        
        # Hebrew text support
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError:
            print("Warning: Hebrew text support not available. Install arabic-reshaper and python-bidi")
            arabic_reshaper = None
            get_display = None
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"wave_height_chart_{timestamp}.png"
        
        def format_hebrew_text(text):
            """Format Hebrew text for proper RTL display"""
            if arabic_reshaper and get_display:
                try:
                    reshaped_text = arabic_reshaper.reshape(text)
                    return get_display(reshaped_text)
                except:
                    return text
            return text
        
        try:
            daily_forecasts = forecast_data.get('daily_forecasts', {})
            
            if not daily_forecasts:
                print("No daily forecast data available for chart")
                return None
            
            # Prepare data for 4surfers-style bar chart
            dates = []
            hebrew_days = []
            morning_heights = []
            noon_heights = []
            evening_heights = []
            date_labels = []
            
            # Sort dates chronologically 
            sorted_dates = sorted(daily_forecasts.items())
            
            for date_key, day_data in sorted_dates:
                try:
                    date_obj = datetime.strptime(date_key, '%Y-%m-%d')
                    dates.append(date_obj)
                    
                    hebrew_day = day_data.get('hebrew_day', '')
                    hebrew_date = day_data.get('hebrew_date', date_obj.strftime('%d/%m'))
                    hebrew_days.append(hebrew_day)
                    date_labels.append(hebrew_date)
                    
                    times_data = day_data.get('times', {})
                    
                    # Extract heights for each time
                    morning_heights.append(times_data.get('06:00', {}).get('wave_height', 0))
                    noon_heights.append(times_data.get('12:00', {}).get('wave_height', 0))
                    evening_heights.append(times_data.get('18:00', {}).get('wave_height', 0))
                    
                except Exception as e:
                    print(f"Error parsing date {date_key}: {e}")
                    continue
            
            if not dates:
                print("No valid dates found for chart")
                return None
            
            # Create 4surfers-style bar chart
            fig, ax = plt.subplots(figsize=(18, 10))
            
            # Set up x positions for grouped bars (like 4surfers)
            x_positions = np.arange(len(dates))
            bar_width = 0.25
            
            # Create grouped bars like the 4surfers chart
            bars1 = ax.bar(x_positions - bar_width, morning_heights, bar_width, 
                          label=format_hebrew_text('בוקר (06:00)'), 
                          color='#87CEEB', alpha=0.8, edgecolor='white', linewidth=1)
            
            bars2 = ax.bar(x_positions, noon_heights, bar_width, 
                          label=format_hebrew_text('צהרים (12:00)'), 
                          color='#4682B4', alpha=0.8, edgecolor='white', linewidth=1)
            
            bars3 = ax.bar(x_positions + bar_width, evening_heights, bar_width, 
                          label=format_hebrew_text('ערב (18:00)'), 
                          color='#2F4F4F', alpha=0.8, edgecolor='white', linewidth=1)
            
            # Add value labels on top of bars
            def add_bar_labels(bars, heights):
                for bar, height in zip(bars, heights):
                    if height > 0:
                        ax.annotate(f'{height:.1f}m',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 3),  # 3 points vertical offset
                                   textcoords="offset points",
                                   ha='center', va='bottom',
                                   fontsize=9, weight='bold', 
                                   color='#2C3E50')
            
            add_bar_labels(bars1, morning_heights)
            add_bar_labels(bars2, noon_heights)
            add_bar_labels(bars3, evening_heights)
            
            # Set custom x-axis labels with dates and Hebrew days
            custom_labels = []
            for i in range(len(date_labels)):
                hebrew_formatted = format_hebrew_text(hebrew_days[i])
                custom_labels.append(f"{date_labels[i]}\n{hebrew_formatted}")
            
            ax.set_xticks(x_positions)
            ax.set_xticklabels(custom_labels, fontsize=11, ha='center', weight='bold')
            
            # Customize chart appearance with Hebrew support
            title_text = format_hebrew_text('תחזית גלים אשקלון') + ' - Ashkelon Wave Forecast'
            subtitle_text = format_hebrew_text('גובה גלים לפי שעות היום')
            ax.set_title(f'🌊 {title_text}\n{subtitle_text}', 
                        fontsize=18, fontweight='bold', pad=25)
            
            ylabel_text = format_hebrew_text('גובה גלים (מטר)') + '\nWave Height (meters)'
            ax.set_ylabel(ylabel_text, fontsize=13, weight='bold')
            
            xlabel_text = format_hebrew_text('תאריך ויום') + '\nDate & Day'
            ax.set_xlabel(xlabel_text, fontsize=13, weight='bold')
            
            # Add horizontal reference lines
            ax.axhline(y=0.3, color='orange', linestyle='--', alpha=0.7, linewidth=2,
                      label=format_hebrew_text('קרסול') + ' - Ankle High (0.3m)')
            ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.7, linewidth=2,
                      label=format_hebrew_text('ברך') + ' - Knee High (0.7m)')  
            ax.axhline(y=1.0, color='blue', linestyle='--', alpha=0.7, linewidth=2,
                      label=format_hebrew_text('מעל ברך') + ' - Above Knee (1.0m)')
            ax.axhline(y=1.3, color='red', linestyle='--', alpha=0.7, linewidth=2,
                      label=format_hebrew_text('כתף') + ' - Shoulder High (1.3m)')
            ax.axhline(y=2.0, color='purple', linestyle='--', alpha=0.5, linewidth=1,
                      label=format_hebrew_text('ראש') + ' - Head High (2.0m)')
            
            # Set y-axis limits
            all_heights = morning_heights + noon_heights + evening_heights
            max_height = max(all_heights) if all_heights else 1.0
            ax.set_ylim(0, max(1.2, max_height + 0.1))
            
            # Add enhanced grid
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
            ax.set_axisbelow(True)
            
            # Add legend with Hebrew support
            ax.legend(loc='upper right', framealpha=0.95, fontsize=11, 
                     shadow=True, fancybox=True)
            
            # Enhance visual styling to match 4surfers
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(1)
            ax.spines['bottom'].set_linewidth(1)
            
            # Set background color
            ax.set_facecolor('#F8F9FA')
            fig.patch.set_facecolor('white')
            
            # Improve layout
            plt.tight_layout()
            
            # Save with high quality
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"📊 4surfers-style bar chart with Hebrew support saved as: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating wave height chart: {e}")
            return None
    
    def generate_good_wave_days_summary_hebrew(self, forecast_data: Dict) -> str:
        """Generate Hebrew-enabled summary for PDF"""
        try:
            # Import Hebrew text processing
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            def format_hebrew_text(text):
                """Format Hebrew text for display"""
                try:
                    reshaped_text = arabic_reshaper.reshape(text)
                    return get_display(reshaped_text)
                except:
                    return text
            
            excellent_wave_days = []
            good_wave_days = []
            daily_max_heights = {}
            
            # Extract daily max heights
            if 'daily_forecasts' in forecast_data:
                for date, day_data in forecast_data['daily_forecasts'].items():
                    times_data = day_data.get('times', {})
                    max_height = 0
                    
                    for time_data in times_data.values():
                        height = time_data.get('wave_height', 0)
                        max_height = max(max_height, height)
                    
                    if max_height >= 0.3:
                        try:
                            date_obj = datetime.strptime(date, '%Y-%m-%d')
                            hebrew_day = day_data.get('hebrew_day', '')
                            
                            day_info = {
                                'date': date,
                                'formatted_date': date_obj.strftime('%d/%m'),
                                'hebrew_day': hebrew_day,
                                'max_height': max_height
                            }
                            
                            if max_height >= 0.6:
                                excellent_wave_days.append(day_info)
                            else:
                                good_wave_days.append(day_info)
                        except:
                            continue
            
            # Generate summary message with Hebrew
            all_good_days = excellent_wave_days + good_wave_days
            
            if all_good_days:
                all_good_days.sort(key=lambda x: x['date'])
                
                if excellent_wave_days:
                    # Hebrew version for PDF
                    hebrew_names = []
                    english_names = []
                    hebrew_to_english = {
                        'שני': 'Monday', 'שלישי': 'Tuesday', 'רביעי': 'Wednesday', 
                        'חמישי': 'Thursday', 'שישי': 'Friday', 'שבת': 'Saturday', 'ראשון': 'Sunday'
                    }
                    
                    for day in sorted(excellent_wave_days, key=lambda x: x['date']):
                        hebrew_day = day['hebrew_day']
                        english_day = hebrew_to_english.get(hebrew_day, hebrew_day)
                        formatted_hebrew = format_hebrew_text(hebrew_day)
                        hebrew_names.append(f"{formatted_hebrew} ({day['formatted_date']}) - {day['max_height']:.1f}m 🌊🌊")
                        english_names.append(f"{english_day} ({day['formatted_date']}) - {day['max_height']:.1f}m 🌊🌊")
                    
                    if len(excellent_wave_days) == 1:
                        hebrew_excellent = format_hebrew_text("גלים מעולים ב")
                        hebrew_perfect = format_hebrew_text("מושלם לגלישה!")
                        return f"🌊🌊 {hebrew_excellent} {hebrew_names[0]}! {hebrew_perfect}"
                    else:
                        hebrew_conditions = format_hebrew_text("תנאי גלישה מעולים:")
                        days_str = ", ".join(hebrew_names)
                        return f"🌊🌊 {hebrew_conditions} {days_str}!"
                        
                elif len(all_good_days) == 1:
                    day = all_good_days[0]
                    hebrew_day = format_hebrew_text(day['hebrew_day'])
                    hebrew_good = format_hebrew_text("גלים טובים ב")
                    hebrew_suitable = format_hebrew_text("טוב לגלישה!")
                    return f"🌊 {hebrew_good} {hebrew_day} ({day['formatted_date']}) - {day['max_height']:.1f}m. {hebrew_suitable}"
                else:
                    hebrew_good_days = format_hebrew_text("ימי גלישה טובים:")
                    day_names = []
                    for day in all_good_days:
                        hebrew_day = format_hebrew_text(day['hebrew_day'])
                        day_names.append(f"{hebrew_day} ({day['formatted_date']}) - {day['max_height']:.1f}m")
                    
                    if len(day_names) <= 3:
                        days_str = ", ".join(day_names)
                    else:
                        days_str = ", ".join(day_names[:3]) + f" ועוד {len(day_names)-3} ימים"
                    
                    return f"🌊 {hebrew_good_days} {days_str}!"
            else:
                hebrew_small = format_hebrew_text("גלים קטנים השבוע")
                hebrew_expected = format_hebrew_text("(כולם מתחת ל-0.3 מ')")
                return f"📅 {hebrew_small} {hebrew_expected}. Better conditions may come later."
                
        except Exception as e:
            print(f"Error generating Hebrew wave days summary: {e}")
            return self.generate_good_wave_days_summary(forecast_data)
    
    def generate_good_wave_days_summary(self, forecast_data: Dict) -> str:
        """
        Generate summary of days with good waves (above קרסול/0.3m) from daily forecasts
        
        Args:
            forecast_data: The forecast data dictionary
            
        Returns:
            Summary string for good wave days
        """
        try:
            # Hebrew to English day mapping for terminal display
            hebrew_to_english = {
                'שני': 'Monday', 'שלישי': 'Tuesday', 'רביעי': 'Wednesday', 
                'חמישי': 'Thursday', 'שישי': 'Friday', 'שבת': 'Saturday', 'ראשון': 'Sunday'
            }
            
            good_wave_days = []
            excellent_wave_days = []
            
            # Use the new daily_forecasts structure first
            if 'daily_forecasts' in forecast_data and forecast_data['daily_forecasts']:
                for date_key, day_data in forecast_data['daily_forecasts'].items():
                    times_data = day_data.get('times', {})
                    if not times_data:
                        continue
                    
                    # Find max wave height for this day
                    max_height = 0
                    for time_key, time_info in times_data.items():
                        height = time_info.get('wave_height', 0)
                        max_height = max(max_height, height)
                    
                    if max_height >= 0.3:  # Good surfable waves
                        hebrew_day = day_data.get('hebrew_day', 'N/A')
                        hebrew_date = day_data.get('hebrew_date', date_key[-5:])
                        
                        day_info = {
                            'date': date_key,
                            'formatted_date': hebrew_date,
                            'hebrew_day': hebrew_day,
                            'max_height': max_height
                        }
                        
                        if max_height >= 0.6:  # Excellent waves (ברך level)
                            excellent_wave_days.append(day_info)
                        else:
                            good_wave_days.append(day_info)
            
            # Fallback to wave_timeline if daily_forecasts not available
            elif 'wave_timeline' in forecast_data:
                daily_max_heights = {}
                
                for item in forecast_data['wave_timeline']:
                    date = item['date']
                    height = item['height']
                    
                    if date in ['unknown_date', 'container_data']:
                        continue
                    
                    if date not in daily_max_heights:
                        daily_max_heights[date] = 0
                    daily_max_heights[date] = max(daily_max_heights[date], height)
                
                for date, max_height in daily_max_heights.items():
                    if max_height >= 0.3:
                        try:
                            date_obj = datetime.strptime(date, '%Y-%m-%d')
                            hebrew_day = self._get_hebrew_day(date_obj.weekday())
                            
                            day_info = {
                                'date': date,
                                'formatted_date': date_obj.strftime('%d/%m'),
                                'hebrew_day': hebrew_day,
                                'max_height': max_height
                            }
                            
                            if max_height >= 0.6:
                                excellent_wave_days.append(day_info)
                            else:
                                good_wave_days.append(day_info)
                        except:
                            continue
            
            # Generate summary message
            all_good_days = excellent_wave_days + good_wave_days
            
            if all_good_days:
                # Sort by date
                all_good_days.sort(key=lambda x: x['date'])
                
                if excellent_wave_days:
                    # Highlight excellent days - use English for terminal to avoid Hebrew display issues
                    excellent_names = [f"{day['hebrew_day']} ({day['formatted_date']}) - {day['max_height']:.1f}m 🌊🌊" 
                                     for day in sorted(excellent_wave_days, key=lambda x: x['date'])]
                    
                    # Create English version for terminal display
                    english_names = []
                    
                    for day in sorted(excellent_wave_days, key=lambda x: x['date']):
                        hebrew_day = day['hebrew_day']
                        english_day = hebrew_to_english.get(hebrew_day, hebrew_day)
                        english_names.append(f"{english_day} ({day['formatted_date']}) - {day['max_height']:.1f}m 🌊🌊")
                    
                    if len(excellent_wave_days) == 1:
                        return f"🌊🌊 Excellent waves on {english_names[0]}! Perfect for surfing!"
                    else:
                        days_str = ", ".join(english_names)
                        return f"🌊🌊 Excellent surfing conditions: {days_str}!"
                        
                elif len(all_good_days) == 1:
                    day = all_good_days[0]
                    hebrew_day = day['hebrew_day']
                    english_day = hebrew_to_english.get(hebrew_day, hebrew_day)
                    return f"🌊 Good waves on {english_day} ({day['formatted_date']}) - {day['max_height']:.1f}m. Good for surfing!"
                else:
                    day_names = []
                    for day in all_good_days:
                        hebrew_day = day['hebrew_day']
                        english_day = hebrew_to_english.get(hebrew_day, hebrew_day)
                        day_names.append(f"{english_day} ({day['formatted_date']}) - {day['max_height']:.1f}m")
                    
                    if len(day_names) <= 3:
                        days_str = ", ".join(day_names)
                    else:
                        days_str = ", ".join(day_names[:3]) + f" and {len(day_names)-3} more days"
                    
                    return f"🌊 Good surfing days: {days_str}!"
            else:
                return "📅 Small waves expected this week (all below 0.3m). Better conditions may come later."
                
        except Exception as e:
            print(f"Error generating good wave days summary: {e}")
            return "📅 Wave forecast summary unavailable."
    
    def generate_pdf_report(self, forecast_data: Dict, filename: str = None) -> str:
        """
        Generate a PDF report of the wave forecast
        
        Args:
            forecast_data: The forecast data dictionary
            filename: Optional filename for the PDF
            
        Returns:
            The filename of the generated PDF
        """
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ashkelon_forecast_report_{timestamp}.pdf"
        
        try:
            # Create PDF document with 4surfers-style design
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            
            # Register Hebrew font support
            hebrew_font_registered = False
            try:
                # Try to find and register a Hebrew-compatible font
                hebrew_fonts = [
                    '/System/Library/Fonts/Arial Unicode MS.ttf',  # macOS
                    '/System/Library/Fonts/Helvetica.ttc',         # macOS fallback
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                    'C:\\Windows\\Fonts\\arial.ttf',               # Windows
                ]
                
                for font_path in hebrew_fonts:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont('HebrewFont', font_path))
                            pdfmetrics.registerFont(TTFont('HebrewFont-Bold', font_path))
                            hebrew_font_registered = True
                            print(f"✅ Hebrew font registered: {font_path}")
                            break
                        except:
                            continue
                            
                if not hebrew_font_registered:
                    print("⚠️ No Hebrew font found, using default fonts")
            except Exception as e:
                print(f"⚠️ Font registration error: {e}")
            
            # Get styles and configure Hebrew text support
            styles = getSampleStyleSheet()
            
            # Hebrew text formatting function with better fallback
            def format_hebrew_text_pdf(text):
                """Format Hebrew text for PDF display - use English equivalents to avoid squares"""
                if not text:
                    return text
                
                # For PDF, use English equivalents to avoid display issues
                hebrew_to_english = {
                    'תחזית': 'Forecast', 'גלים': 'Waves', 'אשקלון': 'Ashkelon',
                    'תאריך': 'Date', 'יום': 'Day', 'בוקר': 'Morning', 
                    'צהרים': 'Noon', 'ערב': 'Evening', 'זמן': 'Time', 'טוב': 'Best',
                    'שני': 'Monday', 'שלישי': 'Tuesday', 'רביעי': 'Wednesday',
                    'חמישי': 'Thursday', 'שישי': 'Friday', 'שבת': 'Saturday', 
                    'ראשון': 'Sunday', 'קרסול': 'Ankle', 'ברך': 'Knee', 
                    'כתף': 'Shoulder', 'שטוח': 'Flat', 'מדריך': 'Guide',
                    'איכות': 'Quality', 'מעולים': 'Excellent', 'גלישה': 'Surfing',
                    'תנאי': 'Conditions', 'יומית': 'Daily'
                }
                
                # Try direct translation first
                if text in hebrew_to_english:
                    return hebrew_to_english[text]
                
                # For longer Hebrew phrases, use English equivalents
                if 'תחזית יומית' in text:
                    return 'Daily Forecast'
                elif 'תנאי גלישה מעולים' in text:
                    return 'Excellent Surfing Conditions'
                elif 'מדריך איכות גלים' in text:
                    return 'Wave Quality Guide'
                
                # If no translation found, return as-is (might work with proper font)
                return text
            
            # 4surfers.co.il inspired color scheme
            surfers_blue = colors.Color(0, 0.48, 1, 1)  # #007BFF - oceanic blue
            surfers_light_blue = colors.Color(0.89, 0.95, 0.99, 1)  # #E3F2FD - light blue background
            surfers_dark_blue = colors.Color(0, 0.33, 0.8, 1)  # Darker blue for headers
            
            # Custom styles with Hebrew support and 4surfers theme
            title_style = ParagraphStyle(
                'SurfersTitle',
                parent=styles['Heading1'],
                fontSize=22,
                spaceAfter=20,
                alignment=1,  # Center alignment
                fontName='HebrewFont-Bold' if hebrew_font_registered else 'Helvetica-Bold',
                textColor=surfers_dark_blue,
                backColor=surfers_light_blue,
                borderColor=surfers_blue,
                borderWidth=2,
                borderPadding=10
            )
            
            heading_style = ParagraphStyle(
                'SurfersHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=10,
                fontName='HebrewFont-Bold' if hebrew_font_registered else 'Helvetica-Bold',
                textColor=surfers_dark_blue,
                backColor=colors.white,
                borderColor=surfers_blue,
                borderWidth=1,
                borderPadding=8
            )
            
            # Hebrew-aware text style with proper font
            hebrew_style = ParagraphStyle(
                'SurfersHebrew',
                parent=styles['Normal'],
                fontSize=11,
                fontName='HebrewFont' if hebrew_font_registered else 'Helvetica',
                alignment=0,  # Left alignment for mixed Hebrew/English
                textColor=colors.black
            )
            
            # 4surfers-style title with Hebrew
            hebrew_title = format_hebrew_text_pdf("תחזית גלים אשקלון")
            title_text = f"�‍♂️ 4SURFERS.co.il | {hebrew_title}<br/>Ashkelon Wave Forecast Report"
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 15))
            
            # Good Wave Days Summary (Top of page) - Hebrew version for PDF in 4surfers style
            good_days_summary = self.generate_good_wave_days_summary_hebrew(forecast_data)
            summary_style = ParagraphStyle(
                'SurfersSummary',
                parent=styles['Normal'],
                fontSize=13,
                spaceAfter=18,
                spaceBefore=5,
                backColor=surfers_light_blue,
                borderColor=surfers_blue,
                borderWidth=2,
                borderPadding=12,
                fontName='HebrewFont-Bold' if hebrew_font_registered else 'Helvetica-Bold',
                textColor=surfers_dark_blue,
                alignment=1  # Center alignment for summary
            )
            story.append(Paragraph(good_days_summary, summary_style))
            story.append(Spacer(1, 15))
            
            # Create and include wave height chart
            chart_filename = self.create_wave_height_chart(forecast_data)
            if chart_filename:
                try:
                    from reportlab.platypus import Image
                    from reportlab.lib.utils import ImageReader
                    
                    # Add chart to PDF
                    story.append(Paragraph("📊 Wave Height Timeline", heading_style))
                    chart_image = Image(chart_filename, width=6*inch, height=3*inch)
                    story.append(chart_image)
                    story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Could not include chart in PDF: {e}")
            
            # Beach Info with 4surfers styling and Hebrew support
            beach_hebrew = forecast_data.get('beach_hebrew', 'N/A')
            formatted_beach_hebrew = format_hebrew_text_pdf(beach_hebrew) if beach_hebrew != 'N/A' else 'N/A'
            
            beach_info_style = ParagraphStyle(
                'SurfersInfo',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                fontName='HebrewFont' if hebrew_font_registered else 'Helvetica',
                backColor=colors.white,
                borderColor=surfers_blue,
                borderWidth=1,
                borderPadding=8
            )
            
            beach_info = f"""
            <b>🏖️ Beach | חוף:</b> {forecast_data.get('beach', 'N/A')} ({formatted_beach_hebrew})<br/>
            <b>🌐 Source | מקור:</b> {forecast_data.get('source', 'N/A')}<br/>
            <b>📅 Report Generated | דוח נוצר:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>⏱️ Data Retrieved | נתונים נאספו:</b> {forecast_data.get('timestamp', 'N/A')[:19]}
            """
            story.append(Paragraph(beach_info, beach_info_style))
            story.append(Spacer(1, 15))
            
            # Surf Quality Summary
            story.append(Paragraph("🏄 Surf Quality Indicators Found", heading_style))
            
            if forecast_data.get('surf_quality_indicators'):
                quality_data = []
                quality_data.append(['Hebrew Term', 'English', 'Frequency'])
                
                for quality in forecast_data['surf_quality_indicators']:
                    quality_data.append([
                        quality['hebrew'],
                        quality['english'],
                        str(quality['count'])
                    ])
                
                quality_table = Table(quality_data)
                quality_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(quality_table)
            else:
                story.append(Paragraph("No surf quality indicators found", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Enhanced Daily Forecasts with proper dates - 4surfers style
            hebrew_title = format_hebrew_text_pdf("תחזית יומית")
            story.append(Paragraph(f"📅 Daily Breakdown - {hebrew_title} (בוקר/צהרים/ערב)", heading_style))
            
            # Create 4surfers-style forecast table from daily forecasts
            if forecast_data.get('daily_forecasts'):
                # Create table headers with Hebrew support
                forecast_table_data = []
                forecast_table_data.append([
                    f'Date\n{format_hebrew_text_pdf("תאריך")}', 
                    f'Day\n{format_hebrew_text_pdf("יום")}',
                    f'Morning 06:00\n{format_hebrew_text_pdf("בוקר")}', 
                    f'Noon 12:00\n{format_hebrew_text_pdf("צהרים")}', 
                    f'Evening 18:00\n{format_hebrew_text_pdf("ערב")}',
                    f'Best Time\n{format_hebrew_text_pdf("זמן טוב")}'
                ])
                
                # Sort dates and add data
                sorted_forecasts = sorted(forecast_data['daily_forecasts'].items())
                
                for date_key, day_data in sorted_forecasts:
                    hebrew_date = day_data.get('hebrew_date', date_key[-5:])  # DD/MM format
                    hebrew_day = day_data.get('hebrew_day', '')
                    english_day = day_data.get('english_day', '')
                    
                    times_data = day_data.get('times', {})
                    
                    # Get wave heights and conditions
                    morning_info = times_data.get('06:00', {})
                    noon_info = times_data.get('12:00', {})
                    evening_info = times_data.get('18:00', {})
                    
                    # Get wave heights and conditions with Hebrew support
                    def format_time_cell(time_info):
                        if not time_info:
                            return "N/A"
                        
                        height = time_info.get('wave_height', 0)
                        surf_quality = time_info.get('surf_quality', 'N/A')
                        
                        # Extract Hebrew condition if available
                        if '(' in surf_quality:
                            hebrew_condition = surf_quality.split('(')[0].strip()
                            english_condition = surf_quality.split('(')[1].replace(')', '').strip()
                            formatted_hebrew = format_hebrew_text_pdf(hebrew_condition)
                            return f"{height:.1f}m\n{formatted_hebrew}\n({english_condition})"
                        else:
                            return f"{height:.1f}m\n{surf_quality}"
                    
                    morning_text = format_time_cell(morning_info)
                    noon_text = format_time_cell(noon_info)
                    evening_text = format_time_cell(evening_info)
                    
                    # Determine best time with Hebrew labels
                    time_hebrew = {'Morning': 'בוקר', 'Noon': 'צהרים', 'Evening': 'ערב'}
                    heights = []
                    if morning_info: heights.append(('Morning', morning_info.get('wave_height', 0)))
                    if noon_info: heights.append(('Noon', noon_info.get('wave_height', 0)))
                    if evening_info: heights.append(('Evening', evening_info.get('wave_height', 0)))
                    
                    if heights:
                        best_time = max(heights, key=lambda x: x[1])
                        if best_time[1] >= 0.3:
                            hebrew_time = format_hebrew_text_pdf(time_hebrew[best_time[0]])
                            best_text = f"{best_time[0]}\n{hebrew_time}\n{best_time[1]:.1f}m ✅"
                        else:
                            hebrew_flat = format_hebrew_text_pdf("שטוח")
                            best_text = f"Flat\n{hebrew_flat}\n❌"
                    else:
                        best_text = "N/A"
                    
                    # Use English day names for PDF to avoid Hebrew display issues
                    hebrew_to_english = {
                        'שני': 'Monday', 'שלישי': 'Tuesday', 'רביעי': 'Wednesday', 
                        'חמישי': 'Thursday', 'שישי': 'Friday', 'שבת': 'Saturday', 'ראשון': 'Sunday'
                    }
                    english_day_name = hebrew_to_english.get(hebrew_day, english_day)
                    
                    forecast_table_data.append([
                        hebrew_date,
                        f"{format_hebrew_text_pdf(hebrew_day)}\n{english_day_name}",
                        morning_text,
                        noon_text, 
                        evening_text,
                        best_text
                    ])
                
                # Create and style the forecast table with 4surfers theme
                forecast_table = Table(forecast_table_data, colWidths=[0.8*inch, 1.1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                
                # 4surfers-inspired table styling
                forecast_table.setStyle(TableStyle([
                    # Header styling with oceanic theme
                    ('BACKGROUND', (0, 0), (-1, 0), surfers_dark_blue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'HebrewFont-Bold' if hebrew_font_registered else 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
                    ('TOPPADDING', (0, 0), (-1, 0), 15),
                    
                    # Data rows styling with alternating ocean colors
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('FONTNAME', (0, 1), (1, -1), 'HebrewFont-Bold' if hebrew_font_registered else 'Helvetica-Bold'),
                    ('FONTNAME', (2, 1), (-1, -1), 'HebrewFont' if hebrew_font_registered else 'Helvetica'),
                    ('TOPPADDING', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    
                    # Grid and borders with oceanic styling
                    ('GRID', (0, 0), (-1, -1), 1.5, surfers_blue),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Alternating row colors with oceanic theme
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [surfers_light_blue, colors.white]),
                    
                    # Highlight best time column with green accent
                    ('BACKGROUND', (5, 0), (5, 0), colors.green),
                    ('BACKGROUND', (5, 1), (5, -1), colors.lightgreen),
                    
                    # Special styling for wave height cells
                    ('TEXTCOLOR', (2, 1), (4, -1), surfers_dark_blue),
                ]))
                
                story.append(forecast_table)
                story.append(Spacer(1, 20))
                
                # Add surf quality legend with 4surfers styling
                legend_style = ParagraphStyle(
                    'SurfersLegend',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=12,
                    spaceBefore=8,
                    backColor=surfers_light_blue,
                    borderColor=surfers_blue,
                    borderWidth=1.5,
                    borderPadding=10,
                    fontName='HebrewFont' if hebrew_font_registered else 'Helvetica',
                    textColor=surfers_dark_blue
                )
                
                # Create legend with Hebrew and English
                hebrew_legend_title = format_hebrew_text_pdf("מדריך איכות גלים")
                hebrew_flat = format_hebrew_text_pdf("פלטה")
                hebrew_ankle = format_hebrew_text_pdf("קרסול") 
                hebrew_ankle_knee = format_hebrew_text_pdf("קרסול עד ברך")
                hebrew_knee = format_hebrew_text_pdf("ברך")
                hebrew_above_knee = format_hebrew_text_pdf("מעל ברך")
                hebrew_shoulder = format_hebrew_text_pdf("כתף")
                hebrew_head = format_hebrew_text_pdf("ראש")
                
                legend_text = f"""
                <b>🏄 Surf Quality Legend - {hebrew_legend_title}:</b><br/>
                • <b>{hebrew_flat} (Flat):</b> 0-0.1m - No waves<br/>
                • <b>{hebrew_ankle} (Ankle High):</b> 0.2-0.4m - Very small waves<br/>
                • <b>{hebrew_ankle_knee} (Ankle-Knee):</b> 0.5-0.6m - Small waves for beginners<br/>
                • <b>{hebrew_knee} (Knee High):</b> 0.7-0.9m - Good waves for surfing<br/>
                • <b>{hebrew_above_knee} (Above Knee):</b> 1.0-1.2m - Great waves<br/>
                • <b>{hebrew_shoulder} (Shoulder High):</b> 1.3-1.5m - Excellent waves<br/>
                • <b>{hebrew_head} (Head High):</b> 2.0m+ - Epic conditions for experts
                """
                
                story.append(Paragraph(legend_text, legend_style))
                
            else:
                # Fallback to old timeline data if daily_forecasts not available
                daily_organized = {}
                if forecast_data.get('wave_timeline'):
                    for item in forecast_data['wave_timeline']:
                        date = item['date']
                        if date not in daily_organized:
                            daily_organized[date] = {}
                        time_str = item['time']
                        daily_organized[date][time_str] = item
                
                # Create tables for each day
                for date_key in sorted(daily_organized.keys()):
                    if date_key in ['unknown_date', 'container_data']:
                        continue
                    
                    try:
                        date_obj = datetime.strptime(date_key, '%Y-%m-%d')
                        hebrew_day = self._get_hebrew_day(date_obj.weekday())
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                        english_day = date_obj.strftime('%A')
                        
                        day_title = f"{hebrew_day} - {formatted_date} ({english_day})"
                    except:
                        day_title = date_key
                    
                    story.append(Paragraph(f"<b>{day_title}</b>", styles['Heading3']))
                    
                    times_data = daily_organized[date_key]
                    if times_data:
                        time_data = []
                        time_data.append(['Time', 'Wave Height', 'Surf Condition', 'Quality'])
                        
                        for time_str in ['06:00', '6:00', '12:00', '18:00']:
                            if time_str in times_data:
                                item = times_data[time_str]
                                height = f"{item['height']:.1f}m"
                                condition = item.get('condition', 'Unknown')
                                
                                # Determine quality level
                                if item['height'] >= 1.0:
                                    quality = "🟢 Good"
                                elif item['height'] >= 0.6:
                                    quality = "🟡 Fair" 
                                elif item['height'] >= 0.3:
                                    quality = "🟠 Small"
                                else:
                                    quality = "🔴 Flat"
                                
                                time_data.append([time_str, height, condition, quality])
                        
                        if len(time_data) > 1:  # Has data beyond header
                            time_table = Table(time_data, colWidths=[0.8*inch, 1*inch, 2.2*inch, 1*inch])
                            time_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 1), (-1, -1), 9)
                            ]))
                            story.append(time_table)
                    
                    story.append(Spacer(1, 15))
            

            
            # Wave Heights and Wind Speeds
            if forecast_data.get('wave_heights') or forecast_data.get('wind_speeds'):
                story.append(Spacer(1, 20))
                story.append(Paragraph("🌊 Conditions Summary", heading_style))
                
                conditions_text = ""
                if forecast_data.get('wave_heights'):
                    conditions_text += f"<b>Wave Heights:</b> {', '.join(map(str, forecast_data['wave_heights']))} meters<br/>"
                
                if forecast_data.get('wind_speeds'):
                    conditions_text += f"<b>Wind Speeds:</b> {', '.join(map(str, forecast_data['wind_speeds']))} km/h<br/>"
                
                story.append(Paragraph(conditions_text, styles['Normal']))
            
            # Summary
            if forecast_data.get('summary'):
                story.append(Spacer(1, 20))
                story.append(Paragraph("📊 Report Summary", heading_style))
                
                summary = forecast_data['summary']
                summary_text = f"""
                <b>Days with Forecasts:</b> {summary.get('total_days_found', 0)}<br/>
                <b>Quality Indicators Found:</b> {summary.get('quality_indicators_found', 0)}<br/>
                <b>Most Common Condition:</b> {summary.get('most_common_condition', 'Unknown')}
                """
                story.append(Paragraph(summary_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            print(f"📄 PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def send_telegram_message(self, chat_id: int, message: str) -> bool:
        """Send a message via Telegram bot"""
        if not self.telegram_bot_token:
            print("❌ No Telegram bot token provided")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print("✅ Telegram message sent successfully!")
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
    
    def generate_hebrew_wave_summary(self, forecast_data: Dict) -> str:
        """Generate Hebrew wave summary for Telegram with 06:00, 12:00, 18:00 surf sessions"""
        try:
            surf_days = []
            
            # Extract surf sessions for key times: 06:00, 12:00, 18:00
            if 'daily_forecasts' in forecast_data:
                for date, day_data in forecast_data['daily_forecasts'].items():
                    times_data = day_data.get('times', {})
                    
                    # Get surf conditions for key surf times
                    surf_sessions = {}
                    key_times = ['06:00', '12:00', '18:00']
                    
                    for time_key in key_times:
                        if time_key in times_data:
                            time_info = times_data[time_key]
                            wave_height = time_info.get('wave_height', 0)
                            surf_quality = time_info.get('surf_quality', '')
                            
                            # Extract ONLY the Hebrew surf quality from API (קרסול, ברך, etc.)
                            # The API already provides the correct Hebrew terms from 4surfers website
                            hebrew_quality = surf_quality.split('(')[0].strip() if surf_quality else ''
                            
                            if wave_height >= 0.3:  # Only include surfable conditions
                                surf_sessions[time_key] = {
                                    'height': wave_height,
                                    'quality': hebrew_quality,  # Use original Hebrew from API
                                    'time_hebrew': self._get_hebrew_session_name(time_key)
                                }
                    
                    # Only include days with surfable conditions
                    if surf_sessions:
                        try:
                            date_obj = datetime.strptime(date, '%Y-%m-%d')
                            hebrew_day = day_data.get('hebrew_day', '')
                            formatted_date = date_obj.strftime('%d/%m')
                            
                            surf_days.append({
                                'date': date,
                                'hebrew_day': hebrew_day,
                                'formatted_date': formatted_date,
                                'sessions': surf_sessions
                            })
                        except:
                            continue
            
            # Generate Hebrew summary with surf sessions
            if surf_days:
                surf_days.sort(key=lambda x: x['date'])
                
                summary_lines = []
                summary_lines.append("🌊 <b>תחזית גלים אשקלון</b> 🏄‍♂️")
                summary_lines.append("=" * 30)
                
                for day in surf_days[:7]:  # Show max 7 days to keep message concise
                    hebrew_day = day['hebrew_day']
                    formatted_date = day['formatted_date']
                    sessions = day['sessions']
                    
                    # Create day header
                    summary_lines.append(f"📅 <b>{hebrew_day} ({formatted_date})</b>")
                    
                    # Add surf sessions for this day
                    for time_key in ['06:00', '12:00', '18:00']:
                        if time_key in sessions:
                            session = sessions[time_key]
                            height = session['height']
                            quality = session['quality']
                            time_hebrew = session['time_hebrew']
                            
                            # Choose emoji based on wave quality
                            if height >= 0.8:
                                emoji = "🌊🌊"
                            elif height >= 0.5:
                                emoji = "🌊"
                            else:
                                emoji = "〰️"
                            
                            summary_lines.append(f"  {emoji} {time_hebrew}: {quality} ({height:.1f}מ')")
                    
                    summary_lines.append("")  # Empty line between days
                
                # Add footer
                summary_lines.append("📊 <b>מקור:</b> 4surfers.co.il")
                summary_lines.append(f"⏰ <b>עודכן:</b> {datetime.now().strftime('%d/%m %H:%M')}")
                
                return "\n".join(summary_lines)
            else:
                return "🌊 <b>תחזית גלים אשקלון</b>\n\n😔 אין גלים טובים לגלישה השבוע\n(כל הגלים מתחת ל-0.3 מ')\n\n📊 מקור: 4surfers.co.il"
                
        except Exception as e:
            print(f"Error generating Hebrew summary: {e}")
            return "❌ שגיאה ביצירת תחזית הגלים"
    
    def _get_hebrew_session_name(self, time_key: str) -> str:
        """Get Hebrew name for surf session time"""
        session_names = {
            '06:00': 'בוקר',     # Morning
            '12:00': 'צהרים',    # Noon  
            '18:00': 'ערב'       # Evening
        }
        return session_names.get(time_key, time_key)
    
    def check_good_waves_next_72h(self, forecast_data: Dict) -> bool:
        """Check if there are waves above ankle height (>0.4m) in the next 72 hours"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate 72 hours from now
            now = datetime.now()
            cutoff_time = now + timedelta(hours=72)
            
            daily_forecasts = forecast_data.get('daily_forecasts', {})
            
            for date_str, day_data in daily_forecasts.items():
                # Parse date
                try:
                    forecast_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    # Skip if beyond 72 hours
                    if forecast_date > cutoff_time:
                        continue
                        
                    # Check times for this day
                    times_data = day_data.get('times', {})
                    for time_key, time_data in times_data.items():
                        wave_height = time_data.get('wave_height', 0)
                        
                        # If any wave is above 0.4m (above ankle), return True
                        if wave_height > 0.4:
                            print(f"🌊 Good waves found: {wave_height:.1f}m on {date_str} at {time_key}")
                            return True
                            
                except ValueError:
                    continue
                    
            print("〰️ No waves above ankle height (0.4m) found in next 72 hours")
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking wave conditions: {e}")
            # If there's an error, send anyway to be safe
            return True

    def send_wave_report_telegram(self, forecast_data: Dict, chat_id: int) -> bool:
        """Send Hebrew wave summary via Telegram only if there are good waves in next 72h"""
        
        # Check if there are waves worth surfing in the next 72 hours
        if not self.check_good_waves_next_72h(forecast_data):
            print("📱 Skipping Telegram message - no surfable waves in next 72 hours")
            return True  # Return True since this is expected behavior
            
        print("📱 Good waves detected - sending Telegram summary...")
        hebrew_summary = self.generate_hebrew_wave_summary(forecast_data)
        return self.send_telegram_message(chat_id, hebrew_summary)
    
    def save_forecast_data(self, forecast_data: Dict, filename: str = None):
        """Save forecast data to file"""
        if not filename:
            beach_name = forecast_data.get('beach', 'unknown')
            filename = f"ashkelon_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(forecast_data, f, indent=2, ensure_ascii=False)
        
        print(f"Forecast data saved to {filename}")
    
    def display_forecast(self, forecast_data: Dict):
        """Display forecast data in a readable format"""
        if not forecast_data:
            print("No forecast data available.")
            return
        
        print(f"\n🌊 Wave Forecast for {forecast_data.get('beach', 'Unknown')}")
        print("=" * 70)
        print(f"Beach (Hebrew): {forecast_data.get('beach_hebrew', 'N/A')}")
        print(f"Source: {forecast_data.get('source', 'N/A')}")
        print(f"Retrieved: {forecast_data.get('timestamp', 'N/A')}")
        
        # Display surf quality indicators found
        if 'surf_quality_indicators' in forecast_data and forecast_data['surf_quality_indicators']:
            print(f"\n� Surf Quality Indicators Found:")
            for quality in forecast_data['surf_quality_indicators']:
                print(f"   • {quality['hebrew']} ({quality['english']})")
        
        # Display surf quality counts
        if 'surf_quality_counts' in forecast_data:
            print(f"\n� Quality Term Frequency:")
            for term, count in forecast_data['surf_quality_counts'].items():
                print(f"   • {term}: {count} times")
        
        # Display daily forecasts from Highcharts data
        if 'daily_forecasts' in forecast_data and forecast_data['daily_forecasts']:
            print(f"\n📅 Daily Forecasts with Hourly Breakdown:")
            print("=" * 70)
            
            # Sort by date
            sorted_dates = sorted(forecast_data['daily_forecasts'].items())
            
            for date_key, day_data in sorted_dates:
                print(f"\n📆 {day_data.get('hebrew_date', date_key)} - {day_data.get('hebrew_day', 'N/A')} ({day_data.get('english_day', 'N/A')})")
                print("-" * 50)
                
                if day_data.get('times'):
                    # Sort times by order (06:00, 12:00, 18:00)
                    time_order = ['06:00', '12:00', '18:00']
                    
                    for time_key in time_order:
                        if time_key in day_data['times']:
                            time_info = day_data['times'][time_key]
                            hebrew_time = time_info.get('hebrew_time', time_key)
                            height = time_info.get('wave_height', 0)
                            quality = time_info.get('surf_quality', 'N/A')
                            
                            # Add emoji based on wave height
                            if height >= 0.6:
                                wave_emoji = "🌊🌊"  # Good waves
                            elif height >= 0.3:
                                wave_emoji = "🌊"    # Some waves
                            else:
                                wave_emoji = "〰️"     # Flat
                            
                            print(f"  {wave_emoji} {hebrew_time} ({time_key}): {height}m - {quality}")
                else:
                    print("  No hourly data available")
        
        # Display legacy hourly forecasts if available
        elif 'hourly_forecasts' in forecast_data and forecast_data['hourly_forecasts']:
            print(f"\n⏰ Hourly Forecasts (6:00, 12:00, 18:00):")
            print("-" * 40)
            
            for time_str, time_data in sorted(forecast_data['hourly_forecasts'].items()):
                print(f"\n🕕 {time_str}:")
                
                if 'surf_quality' in time_data:
                    quality = time_data['surf_quality']
                    print(f"   🌊 Surf: {quality['hebrew']} ({quality['english']})")
                
                if 'wind_speed' in time_data:
                    print(f"   💨 Wind: {time_data['wind_speed']} km/h")
                
                if 'numbers_found' in time_data:
                    print(f"   📊 Numbers: {time_data['numbers_found']}")
                
                # Show raw text if available (truncated)
                for text_key in ['raw_text', 'table_row', 'element_text']:
                    if text_key in time_data:
                        text = time_data[text_key]
                        if len(text) > 100:
                            text = text[:100] + "..."
                        print(f"   📝 Data: {text}")
                        break
        else:
            print(f"\n❌ No detailed daily forecasts available")
        
        # Display general wave and wind data found
        if 'wave_heights_found' in forecast_data:
            print(f"\n🌊 Wave Heights Found: {forecast_data['wave_heights_found']}")
        
        if 'wind_speeds_found' in forecast_data:
            print(f"💨 Wind Speeds Found: {forecast_data['wind_speeds_found']}")
        
        # Show forecast summary
        if 'daily_forecasts' in forecast_data and forecast_data['daily_forecasts']:
            daily_count = len(forecast_data['daily_forecasts'])
            total_times = sum(len(day_data.get('times', {})) for day_data in forecast_data['daily_forecasts'].values())
            print(f"\n📈 Summary: Found {daily_count} days with {total_times} time-specific forecasts")
        else:
            forecast_count = forecast_data.get('forecast_times_found', 0)
            print(f"\n📈 Summary: Found {forecast_count} time-specific forecasts")
        
        print("=" * 70)


def main():
    """Main function to run the Ashkelon wave forecast application"""
    print("🏄‍♂️ Enhanced Ashkelon Wave Forecast from 4surfers.co.il")
    print("=" * 60)
    
    # Telegram configuration - use environment variables for security
    import os
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '-1002522870307'))  # Channel ID from channel_post
    
    # Initialize the forecast system with Telegram support
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  Warning: TELEGRAM_BOT_TOKEN environment variable not set")
        print("   Telegram notifications will be disabled")
    
    wave_forecast = FourSurfersWaveForecast(telegram_bot_token=TELEGRAM_BOT_TOKEN)
    
    # Get Ashkelon forecast using direct URL
    print("Getting wave forecast for Ashkelon using direct URL...")
    forecast_data = wave_forecast.get_ashkelon_forecast()
    
    if forecast_data:
        # Display the forecast
        wave_forecast.display_forecast(forecast_data)
        
        # Save the JSON data
        wave_forecast.save_forecast_data(forecast_data)
        
        # Skip PDF and chart generation - only send Telegram summary
        
        # Show good wave days summary
        summary = wave_forecast.generate_good_wave_days_summary(forecast_data)
        print(f"\n🌊 {summary}")
        
        # Send Hebrew summary via Telegram (only if good waves in next 72h)
        print("\n📱 Checking for surfable conditions in next 72 hours...")
        telegram_success = wave_forecast.send_wave_report_telegram(forecast_data, TELEGRAM_CHAT_ID)
        
        if telegram_success:
            print("✅ Telegram process completed successfully!")
        else:
            print("❌ Failed to send Telegram message")
        
        # In automation mode, always save raw data but don't ask for user input
        automation_mode = os.getenv('GITHUB_ACTIONS') == 'true' or os.getenv('CI') == 'true'
        if automation_mode:
            print("\n🤖 Running in automation mode - forecast completed!")
        else:
            # Ask if user wants to see raw data (only in interactive mode)
            show_raw = input("\nWould you like to see the raw extracted data? (y/n): ").strip().lower()
            if show_raw == 'y':
                print("\n🔍 Raw Data:")
                print(json.dumps(forecast_data, indent=2, ensure_ascii=False))
    else:
        print("❌ Unable to retrieve forecast data.")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify that 4surfers.co.il is accessible")
        print("3. The site structure might have changed")
        print("4. Try running with debug mode (set headless=False in the code)")
        print("5. Check the direct URL:", wave_forecast.ashkelon_url)


if __name__ == "__main__":
    main()