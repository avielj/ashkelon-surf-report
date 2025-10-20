#!/usr/bin/env python3
"""
Standalone Ashkelon Surf Forecast Web Service
Independent of Home Assistant - can be deployed anywhere
Direct integration with 4surfers.co.il API
"""

from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta
import json
import re
import logging
import os
from typing import Dict, Optional, List
import asyncio
from playwright.async_api import async_playwright
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global cache for forecast data
forecast_cache = {}
last_update = None
cache_lock = threading.Lock()

class StandaloneSurfForecast:
    """Standalone surf forecast class - no Home Assistant dependency"""
    
    def __init__(self):
        self.ashkelon_url = "https://www.4surfers.co.il/אשקלון"
        self.api_base_url = "https://www.4surfers.co.il"
        
        # Hebrew surf quality mapping
        self.quality_to_height = {
            'פלטה': 0.1, 'שטוח': 0.1, 'קרסול': 0.3, 'קרסול עד ברך': 0.5,
            'ברך': 0.7, 'מעל ברך': 1.0, 'כתף': 1.3, 'מעל כתף': 1.6,
            'מותן': 1.9, 'ראש': 2.4, 'מעל ראש': 3.0
        }
    
    def _wave_height_to_quality(self, height: float) -> str:
        """Convert wave height to Hebrew surf quality"""
        if height <= 0.1: return "פלטה"
        elif height <= 0.3: return "קרסול"
        elif height <= 0.6: return "קרסול עד ברך"
        elif height <= 0.8: return "ברך"
        elif height <= 1.1: return "מעל ברך"
        elif height <= 1.4: return "כתף"
        elif height <= 1.7: return "מעל כתף"
        elif height <= 2.2: return "מותן"
        elif height <= 2.9: return "ראש"
        else: return "מעל ראש"
    
    def _get_hebrew_day(self, weekday: int) -> str:
        """Get Hebrew day name"""
        hebrew_days = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        return hebrew_days[weekday]
    
    async def get_forecast_data(self) -> Optional[Dict]:
        """Get forecast data using Playwright - standalone method"""
        try:
            logger.info("Fetching Ashkelon surf forecast...")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'
                )
                page = await context.new_page()
                
                # Navigate to Ashkelon page
                await page.goto(self.ashkelon_url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)
                
                # Try extended API first
                forecast_data = await self._get_api_data(page)
                
                if not forecast_data or not forecast_data.get('daily_forecasts'):
                    # Fallback to HTML parsing
                    html = await page.content()
                    forecast_data = self._parse_html_fallback(html)
                
                await browser.close()
                
                if forecast_data:
                    forecast_data.update({
                        'beach': 'Ashkelon',
                        'beach_hebrew': 'אשקלון',
                        'source': '4surfers.co.il',
                        'timestamp': datetime.now().isoformat(),
                        'standalone': True
                    })
                    return forecast_data
                else:
                    return self._get_fallback_data()
                    
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return self._get_fallback_data()
    
    async def _get_api_data(self, page) -> Optional[Dict]:
        """Try to get data from 4surfers API"""
        try:
            # Extract JWT token
            jwt_token = await page.evaluate("""
                () => {
                    return localStorage.getItem('jwt-token') || 
                           localStorage.getItem('authToken') ||
                           window.jwtToken || 
                           window.authToken;
                }
            """)
            
            if not jwt_token:
                return None
            
            # Make API request
            response = await page.request.post(
                f"{self.api_base_url}/api/GetBeachAreaForecast",
                headers={
                    'Authorization': f'Bearer {jwt_token}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({"beachAreaId": 1})
            )
            
            if response.status == 200:
                api_data = await response.json()
                return self._process_api_data(api_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"API data fetch failed: {e}")
            return None
    
    def _process_api_data(self, api_data: Dict) -> Dict:
        """Process API response into forecast structure"""
        try:
            forecast_data = {
                'daily_forecasts': {},
                'surf_quality_indicators': [],
                'surf_quality_counts': {}
            }
            
            forecast_points = api_data.get('forecastPoints', [])
            
            for point in forecast_points:
                forecast_time = datetime.fromisoformat(point['forecastDateTime'].replace('Z', '+00:00'))
                date_key = forecast_time.strftime('%Y-%m-%d')
                time_key = forecast_time.strftime('%H:%M')
                
                # Only keep surf session times
                if time_key not in ['06:00', '12:00', '18:00']:
                    continue
                
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
                forecast_data['surf_quality_counts'][surf_quality_hebrew] = \
                    forecast_data['surf_quality_counts'].get(surf_quality_hebrew, 0) + 1
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error processing API data: {e}")
            return {}
    
    def _get_english_quality(self, hebrew_quality: str) -> str:
        """Get English translation"""
        translations = {
            'פלטה': 'flat', 'שטוח': 'flat', 'קרסול': 'ankle_high',
            'קרסול עד ברך': 'ankle_to_knee', 'ברך': 'knee_high', 'מעל ברך': 'above_knee',
            'כתף': 'shoulder_high', 'מעל כתף': 'above_shoulder', 'מותן': 'waist_high',
            'ראש': 'head_high', 'מעל ראש': 'overhead'
        }
        return translations.get(hebrew_quality, 'unknown')
    
    def _parse_html_fallback(self, html: str) -> Dict:
        """Fallback HTML parsing"""
        try:
            forecast_data = {
                'daily_forecasts': {},
                'surf_quality_indicators': [],
                'surf_quality_counts': {}
            }
            
            # Look for Hebrew surf terms
            hebrew_terms = ['פלטה', 'קרסול', 'ברך', 'כתף', 'ראש']
            
            for term in hebrew_terms:
                matches = len(re.findall(term, html))
                if matches > 0:
                    forecast_data['surf_quality_counts'][term] = matches
            
            # Generate basic forecast for next 3 days
            today = datetime.now()
            
            for day in range(3):
                date = today + timedelta(days=day)
                date_key = date.strftime('%Y-%m-%d')
                hebrew_day = self._get_hebrew_day(date.weekday())
                
                # Use most common quality or default
                common_quality = 'קרסול'
                if forecast_data['surf_quality_counts']:
                    common_quality = max(forecast_data['surf_quality_counts'], 
                                       key=forecast_data['surf_quality_counts'].get)
                
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
                            'wave_height': wave_height * 0.9,
                            'surf_quality': f"{common_quality} ({self._get_english_quality(common_quality)})",
                            'hebrew_time': 'צהרים'
                        },
                        '18:00': {
                            'wave_height': wave_height * 1.1,
                            'surf_quality': f"{common_quality} ({self._get_english_quality(common_quality)})",
                            'hebrew_time': 'ערב'
                        }
                    }
                }
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            return {}
    
    def _get_fallback_data(self) -> Dict:
        """Emergency fallback data"""
        today = datetime.now()
        
        return {
            'beach': 'Ashkelon',
            'beach_hebrew': 'אשקלון',
            'source': '4surfers.co.il',
            'timestamp': today.isoformat(),
            'standalone': True,
            'offline_mode': True,
            'daily_forecasts': {
                today.strftime('%Y-%m-%d'): {
                    'hebrew_date': today.strftime('%d/%m'),
                    'hebrew_day': self._get_hebrew_day(today.weekday()),
                    'english_day': today.strftime('%A'),
                    'times': {
                        '06:00': {
                            'wave_height': 0.3,
                            'surf_quality': 'קרסול (ankle_high)',
                            'hebrew_time': 'בוקר'
                        },
                        '12:00': {
                            'wave_height': 0.3,
                            'surf_quality': 'קרסול (ankle_high)', 
                            'hebrew_time': 'צהרים'
                        },
                        '18:00': {
                            'wave_height': 0.3,
                            'surf_quality': 'קרסול (ankle_high)',
                            'hebrew_time': 'ערב'
                        }
                    }
                }
            }
        }

# Synchronous wrapper
def get_surf_forecast_sync():
    """Synchronous wrapper for async forecast"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        surf_forecast = StandaloneSurfForecast()
        result = loop.run_until_complete(surf_forecast.get_forecast_data())
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Sync forecast error: {e}")
        return StandaloneSurfForecast()._get_fallback_data()

def update_forecast_cache():
    """Update forecast cache in background"""
    global forecast_cache, last_update
    
    logger.info("Updating forecast cache...")
    
    try:
        new_data = get_surf_forecast_sync()
        
        if new_data:
            with cache_lock:
                forecast_cache = new_data
                last_update = datetime.now()
            logger.info("Forecast cache updated successfully")
        else:
            logger.error("Failed to update forecast cache")
            
    except Exception as e:
        logger.error(f"Cache update error: {e}")

def background_updater():
    """Background thread for automatic updates"""
    update_interval = int(os.getenv('UPDATE_INTERVAL', 3600))  # 1 hour default
    
    while True:
        try:
            update_forecast_cache()
            time.sleep(update_interval)
        except Exception as e:
            logger.error(f"Background updater error: {e}")
            time.sleep(60)

# Helper functions for templates
def format_wave_height_hebrew(height):
    """Convert wave height to Hebrew surf quality term"""
    surf_forecast = StandaloneSurfForecast()
    return surf_forecast._wave_height_to_quality(height)

def get_wave_emoji(height):
    """Get wave emoji for height"""
    if height >= 1.0: return "🌊🌊"
    elif height >= 0.5: return "🌊"
    elif height >= 0.2: return "〰️"
    else: return "🏖️"

# Routes
@app.route('/')
def index():
    """Main surf forecast page - Aguacatec style"""
    # Ensure we have recent data
    if not forecast_cache or not last_update or \
       (datetime.now() - last_update).total_seconds() > 1800:  # 30 min
        threading.Thread(target=update_forecast_cache, daemon=True).start()
    
    # Prepare forecast display data
    forecast_display = {
        'beach_name': forecast_cache.get('beach', 'Ashkelon'),
        'last_update': last_update.strftime('%H:%M') if last_update else 'Loading...',
        'days': [],
        'offline_mode': forecast_cache.get('offline_mode', False)
    }
    
    if forecast_cache.get('daily_forecasts'):
        sorted_dates = sorted(forecast_cache['daily_forecasts'].items())
        
        for date_key, day_data in sorted_dates[:3]:  # Show 3 days max
            day_info = {
                'date': date_key,
                'hebrew_day': day_data.get('hebrew_day', ''),
                'english_day': day_data.get('english_day', ''),
                'formatted_date': day_data.get('hebrew_date', ''),
                'sessions': []
            }
            
            times_data = day_data.get('times', {})
            for time_key in ['06:00', '12:00', '18:00']:
                if time_key in times_data:
                    time_info = times_data[time_key]
                    height = time_info.get('wave_height', 0)
                    quality = time_info.get('surf_quality', '')
                    
                    session = {
                        'time': time_key,
                        'hebrew_time': time_info.get('hebrew_time', time_key),
                        'height': height,
                        'height_text': f"{height:.1f}מ'",
                        'quality_hebrew': format_wave_height_hebrew(height),
                        'quality_english': quality.split('(')[1].rstrip(')') if '(' in quality else '',
                        'emoji': get_wave_emoji(height),
                        'is_good': height >= 0.4
                    }
                    day_info['sessions'].append(session)
            
            forecast_display['days'].append(day_info)
    
    return render_template('standalone_index.html', forecast=forecast_display)

@app.route('/widget')
def widget():
    """iOS widget optimized page"""
    # Get current session for widget
    widget_data = {
        'beach': 'אשקלון',
        'beach_english': 'Ashkelon', 
        'last_update': last_update.strftime('%H:%M') if last_update else 'N/A',
        'current_session': None,
        'offline_mode': forecast_cache.get('offline_mode', False)
    }
    
    if forecast_cache.get('daily_forecasts'):
        today = datetime.now().strftime('%Y-%m-%d')
        today_forecast = forecast_cache['daily_forecasts'].get(today)
        
        if today_forecast:
            current_hour = datetime.now().hour
            
            # Determine session
            if current_hour < 9:
                session_key = '06:00'
            elif current_hour < 15:
                session_key = '12:00'
            else:
                session_key = '18:00'
            
            times_data = today_forecast.get('times', {})
            if session_key in times_data:
                time_info = times_data[session_key]
                height = time_info.get('wave_height', 0)
                
                widget_data['current_session'] = {
                    'time': session_key,
                    'hebrew_time': time_info.get('hebrew_time', session_key),
                    'height': height,
                    'height_text': f"{height:.1f}מ'",
                    'quality_hebrew': format_wave_height_hebrew(height),
                    'emoji': get_wave_emoji(height),
                    'period': int(height * 3 + 8),
                    'hebrew_day': today_forecast.get('hebrew_day', ''),
                    'formatted_date': today_forecast.get('hebrew_date', ''),
                }
    
    return render_template('standalone_widget.html', widget=widget_data)

@app.route('/api/forecast')
def api_forecast():
    """JSON API for forecast data"""
    return jsonify({
        'success': bool(forecast_cache and not forecast_cache.get('offline_mode')),
        'last_update': last_update.isoformat() if last_update else None,
        'offline_mode': forecast_cache.get('offline_mode', False),
        'data': forecast_cache
    })

@app.route('/api/widget')
def api_widget():
    """JSON API optimized for widgets"""
    if not forecast_cache:
        return jsonify({'success': False, 'error': 'No data available'})
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_forecast = forecast_cache['daily_forecasts'].get(today, {})
    
    widget_data = {
        'success': not forecast_cache.get('offline_mode', False),
        'beach': 'אשקלון',
        'beach_english': 'Ashkelon',
        'date': today_forecast.get('hebrew_date', ''),
        'day': today_forecast.get('hebrew_day', ''),
        'last_update': last_update.strftime('%H:%M') if last_update else '',
        'sessions': [],
        'offline_mode': forecast_cache.get('offline_mode', False)
    }
    
    times_data = today_forecast.get('times', {})
    for time_key in ['06:00', '12:00', '18:00']:
        if time_key in times_data:
            time_info = times_data[time_key]
            height = time_info.get('wave_height', 0)
            
            widget_data['sessions'].append({
                'time': time_key,
                'hebrew_time': time_info.get('hebrew_time', time_key),
                'height': height,
                'height_text': f"{height:.1f}מ'",
                'quality_hebrew': format_wave_height_hebrew(height),
                'quality_english': time_info.get('surf_quality', '').split('(')[1].rstrip(')') if '(' in time_info.get('surf_quality', '') else '',
                'period': int(height * 3 + 8),
                'rating_stars': '⭐' * min(5, max(1, int(height * 3))),
                'is_good': height >= 0.4
            })
    
    return jsonify(widget_data)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'last_update': last_update.isoformat() if last_update else None,
        'cache_available': bool(forecast_cache),
        'standalone': True
    })

if __name__ == '__main__':
    logger.info("Starting Standalone Ashkelon Surf Forecast Server...")
    
    # Start background updater
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Initial cache load
    update_forecast_cache()
    
    # Start Flask app
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)