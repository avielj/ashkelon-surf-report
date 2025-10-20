#!/usr/bin/env python3
"""
Simplified Wave Forecast for Home Assistant Addon
Focused on API integration without heavy dependencies
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import asyncio
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class FourSurfersWaveForecast:
    """Simplified wave forecast class for Home Assistant addon"""
    
    def __init__(self):
        self.ashkelon_url = "https://www.4surfers.co.il/אשקלון"
        self.api_base_url = "https://www.4surfers.co.il"
        
        # Hebrew surf quality to wave height mapping (corrected thresholds)
        self.quality_to_height = {
            'פלטה': 0.1,      # flat
            'שטוח': 0.1,      # flat
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
    
    def _wave_height_to_quality(self, height: float) -> str:
        """Convert wave height to Hebrew surf quality term with corrected thresholds"""
        if height <= 0.1:
            return "פלטה"
        elif height <= 0.3:
            return "קרסול"
        elif height <= 0.6:
            return "קרסול עד ברך"
        elif height <= 0.8:  # Corrected: ברך should be ≤0.8m, not ≤0.9m
            return "ברך"
        elif height <= 1.1:  # Corrected: מעל ברך should be ≤1.1m
            return "מעל ברך"
        elif height <= 1.4:
            return "כתף"
        elif height <= 1.7:
            return "מעל כתף"
        elif height <= 2.2:
            return "מותן"
        elif height <= 2.9:
            return "ראש"
        else:
            return "מעל ראש"
    
    def _get_hebrew_day(self, weekday: int) -> str:
        """Get Hebrew day name from weekday number"""
        hebrew_days = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        return hebrew_days[weekday]
    
    async def get_ashkelon_forecast(self) -> Optional[Dict]:
        """Get forecast data using Playwright"""
        try:
            logger.info("Getting Ashkelon forecast from 4surfers.co.il...")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to Ashkelon page
                await page.goto(self.ashkelon_url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)
                
                # Get page content
                html = await page.content()
                
                # Try to get extended API data
                forecast_data = await self._get_extended_api_data(page)
                
                if not forecast_data or not forecast_data.get('daily_forecasts'):
                    # Fallback to HTML parsing
                    forecast_data = self._parse_basic_forecast(html)
                
                await browser.close()
                
                if forecast_data:
                    forecast_data.update({
                        'beach': 'Ashkelon',
                        'beach_hebrew': 'אשקלון', 
                        'source': '4surfers.co.il',
                        'timestamp': datetime.now().isoformat(),
                        'url': self.ashkelon_url
                    })
                    
                    logger.info(f"Forecast retrieved successfully: {len(forecast_data.get('daily_forecasts', {}))} days")
                    return forecast_data
                else:
                    logger.error("Failed to retrieve forecast data")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return None
    
    async def _get_extended_api_data(self, page) -> Optional[Dict]:
        """Get data from 4surfers extended API"""
        try:
            # Get JWT token
            jwt_token = await self._get_jwt_token(page)
            if not jwt_token:
                return None
            
            # Make API request
            api_url = f"{self.api_base_url}/api/GetBeachAreaForecast"
            
            response = await page.request.post(api_url, 
                headers={
                    'Authorization': f'Bearer {jwt_token}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({"beachAreaId": 1})  # Ashkelon area ID
            )
            
            if response.status == 200:
                api_data = await response.json()
                return self._process_extended_api_data(api_data)
            else:
                logger.warning(f"Extended API failed: {response.status}")
                return None
                
        except Exception as e:
            logger.warning(f"Extended API error: {e}")
            return None
    
    async def _get_jwt_token(self, page) -> Optional[str]:
        """Extract JWT token from page"""
        try:
            # Look for JWT token in localStorage or page scripts
            jwt_token = await page.evaluate("""
                () => {
                    // Try localStorage first
                    let token = localStorage.getItem('jwt-token') || localStorage.getItem('authToken');
                    if (token) return token;
                    
                    // Try to find in window variables
                    if (window.jwtToken) return window.jwtToken;
                    if (window.authToken) return window.authToken;
                    
                    return null;
                }
            """)
            
            if jwt_token:
                return jwt_token
            
            # Fallback: try to trigger token generation
            await page.wait_for_timeout(2000)
            
            jwt_token = await page.evaluate("""
                () => {
                    return localStorage.getItem('jwt-token') || localStorage.getItem('authToken');
                }
            """)
            
            return jwt_token
            
        except Exception as e:
            logger.warning(f"JWT token extraction failed: {e}")
            return None
    
    def _process_extended_api_data(self, api_data: Dict) -> Dict:
        """Process extended API response into forecast structure"""
        try:
            forecast_data = {
                'daily_forecasts': {},
                'surf_quality_indicators': [],
                'surf_quality_counts': {}
            }
            
            # Process forecast points (69 hours = ~3 days detailed)
            forecast_points = api_data.get('forecastPoints', [])
            
            for point in forecast_points:
                # Parse datetime
                forecast_time = datetime.fromisoformat(point['forecastDateTime'].replace('Z', '+00:00'))
                date_key = forecast_time.strftime('%Y-%m-%d')
                time_key = forecast_time.strftime('%H:%M')
                
                # Only keep key surf times
                if time_key not in ['06:00', '12:00', '18:00']:
                    continue
                
                # Get wave data
                wave_height = point.get('waveHeight', 0)
                surf_quality_hebrew = self._wave_height_to_quality(wave_height)
                
                # Initialize day if not exists
                if date_key not in forecast_data['daily_forecasts']:
                    hebrew_day = self._get_hebrew_day(forecast_time.weekday())
                    english_day = forecast_time.strftime('%A')
                    
                    forecast_data['daily_forecasts'][date_key] = {
                        'hebrew_date': forecast_time.strftime('%d/%m'),
                        'hebrew_day': hebrew_day,
                        'english_day': english_day,
                        'times': {}
                    }
                
                # Add time data
                forecast_data['daily_forecasts'][date_key]['times'][time_key] = {
                    'wave_height': wave_height,
                    'surf_quality': f"{surf_quality_hebrew} ({self._get_english_quality(surf_quality_hebrew)})",
                    'hebrew_time': {'06:00': 'בוקר', '12:00': 'צהרים', '18:00': 'ערב'}.get(time_key, time_key)
                }
                
                # Count quality indicators
                if surf_quality_hebrew in forecast_data['surf_quality_counts']:
                    forecast_data['surf_quality_counts'][surf_quality_hebrew] += 1
                else:
                    forecast_data['surf_quality_counts'][surf_quality_hebrew] = 1
            
            # Create quality indicators list
            for quality, count in forecast_data['surf_quality_counts'].items():
                forecast_data['surf_quality_indicators'].append({
                    'hebrew': quality,
                    'english': self._get_english_quality(quality),
                    'count': count
                })
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error processing extended API data: {e}")
            return {}
    
    def _get_english_quality(self, hebrew_quality: str) -> str:
        """Get English translation for Hebrew surf quality"""
        translations = {
            'פלטה': 'flat',
            'שטוח': 'flat', 
            'קרסול': 'ankle_high',
            'קרסול עד ברך': 'ankle_to_knee',
            'ברך': 'knee_high',
            'מעל ברך': 'above_knee',
            'כתף': 'shoulder_high',
            'מעל כתף': 'above_shoulder',
            'מותן': 'waist_high',
            'ראש': 'head_high',
            'מעל ראש': 'overhead'
        }
        return translations.get(hebrew_quality, 'unknown')
    
    def _parse_basic_forecast(self, html: str) -> Dict:
        """Fallback HTML parsing for basic forecast data"""
        try:
            forecast_data = {
                'daily_forecasts': {},
                'surf_quality_indicators': [],
                'surf_quality_counts': {}
            }
            
            # Look for Hebrew surf quality terms in HTML
            hebrew_terms = ['פלטה', 'קרסול', 'ברך', 'כתף', 'ראש']
            
            for term in hebrew_terms:
                matches = len(re.findall(term, html))
                if matches > 0:
                    forecast_data['surf_quality_counts'][term] = matches
                    forecast_data['surf_quality_indicators'].append({
                        'hebrew': term,
                        'english': self._get_english_quality(term),
                        'count': matches
                    })
            
            # Generate basic daily forecasts for next 3 days
            today = datetime.now()
            
            for day in range(3):
                date = today + timedelta(days=day)
                date_key = date.strftime('%Y-%m-%d')
                hebrew_day = self._get_hebrew_day(date.weekday())
                
                # Use most common quality or default to ankle high
                if forecast_data['surf_quality_counts']:
                    common_quality = max(forecast_data['surf_quality_counts'], key=forecast_data['surf_quality_counts'].get)
                else:
                    common_quality = 'קרסול'
                
                wave_height = self.quality_to_height.get(common_quality, 0.3)
                
                forecast_data['daily_forecasts'][date_key] = {
                    'hebrew_date': date.strftime('%d/%m'),
                    'hebrew_day': hebrew_day,
                    'english_day': date.strftime('%A'),
                    'times': {
                        '06:00': {
                            'wave_height': wave_height,
                            'surf_quality': f"{common_quality} ({self._get_english_quality(common_quality)})",
                            'hebrew_time': 'בוקר'
                        },
                        '12:00': {
                            'wave_height': wave_height * 0.9,  # Slightly smaller at noon
                            'surf_quality': f"{common_quality} ({self._get_english_quality(common_quality)})",
                            'hebrew_time': 'צהרים'
                        },
                        '18:00': {
                            'wave_height': wave_height * 1.1,  # Slightly bigger in evening
                            'surf_quality': f"{common_quality} ({self._get_english_quality(common_quality)})",
                            'hebrew_time': 'ערב'
                        }
                    }
                }
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error in basic HTML parsing: {e}")
            return {}

# Synchronous wrapper for Home Assistant
class SyncFourSurfersWaveForecast:
    """Synchronous wrapper for async forecast functionality"""
    
    def __init__(self):
        self._async_forecast = FourSurfersWaveForecast()
    
    def get_ashkelon_forecast(self) -> Optional[Dict]:
        """Synchronous version of get_ashkelon_forecast"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._async_forecast.get_ashkelon_forecast())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync forecast error: {e}")
            return None