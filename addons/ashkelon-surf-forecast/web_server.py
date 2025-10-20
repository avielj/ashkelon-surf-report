#!/usr/bin/env python3
"""
Web server for Ashkelon Surf Forecast Home Assistant Addon
Provides a beautiful web interface displaying surf forecast data
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import logging

# Import the simplified wave forecast functionality
try:
    from surf_forecast_simplified import SyncFourSurfersWaveForecast as FourSurfersWaveForecast
except ImportError:
    # Fallback to original if simplified not available
    import sys
    sys.path.append('/app')
    from wave_forecast import FourSurfersWaveForecast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for cached forecast data
forecast_cache = {}
last_update = None
update_lock = threading.Lock()

app = Flask(__name__)

def get_config():
    """Get configuration from environment variables"""
    return {
        'update_interval': int(os.getenv('UPDATE_INTERVAL', 3600)),
        'show_hebrew': os.getenv('SHOW_HEBREW', 'true').lower() == 'true',
        'show_chart': os.getenv('SHOW_CHART', 'true').lower() == 'true'
    }

def update_forecast_data():
    """Update forecast data in background"""
    global forecast_cache, last_update
    
    logger.info("Updating surf forecast data...")
    
    try:
        # Initialize the forecast system
        wave_forecast = FourSurfersWaveForecast()
        
        # Get Ashkelon forecast
        forecast_data = wave_forecast.get_ashkelon_forecast()
        
        if forecast_data:
            with update_lock:
                forecast_cache = forecast_data
                last_update = datetime.now()
            logger.info("Forecast data updated successfully")
        else:
            logger.error("Failed to retrieve forecast data")
            
    except Exception as e:
        logger.error(f"Error updating forecast: {e}")

def background_updater():
    """Background thread to periodically update forecast data"""
    config = get_config()
    update_interval = config['update_interval']
    
    while True:
        try:
            update_forecast_data()
            time.sleep(update_interval)
        except Exception as e:
            logger.error(f"Error in background updater: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

def format_wave_height_hebrew(height):
    """Convert wave height to Hebrew surf quality term"""
    if height <= 0.1:
        return "פלטה"
    elif height <= 0.3:
        return "קרסול"
    elif height <= 0.6:
        return "קרסול עד ברך"
    elif height <= 0.8:
        return "ברך"
    elif height <= 1.1:
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

def get_wave_emoji(height):
    """Get appropriate emoji for wave height"""
    if height >= 1.0:
        return "🌊🌊"
    elif height >= 0.5:
        return "🌊"
    elif height >= 0.2:
        return "〰️"
    else:
        return "🏖️"

@app.route('/')
def index():
    """Main page showing surf forecast"""
    config = get_config()
    
    # Check if we need to update data
    if not forecast_cache or not last_update or \
       (datetime.now() - last_update).total_seconds() > config['update_interval']:
        # Update in background if too old
        threading.Thread(target=update_forecast_data, daemon=True).start()
    
    # Prepare forecast data for template
    forecast_display = {
        'beach_name': forecast_cache.get('beach', 'Ashkelon'),
        'last_update': last_update.strftime('%Y-%m-%d %H:%M') if last_update else 'Never',
        'days': [],
        'config': config
    }
    
    if forecast_cache.get('daily_forecasts'):
        # Process daily forecasts for display
        sorted_dates = sorted(forecast_cache['daily_forecasts'].items())
        
        for date_key, day_data in sorted_dates[:7]:  # Show 7 days max
            day_info = {
                'date': date_key,
                'hebrew_day': day_data.get('hebrew_day', ''),
                'english_day': day_data.get('english_day', ''),
                'formatted_date': day_data.get('hebrew_date', ''),
                'sessions': []
            }
            
            # Process surf sessions
            times_data = day_data.get('times', {})
            for time_key in ['06:00', '12:00', '18:00']:
                if time_key in times_data:
                    time_info = times_data[time_key]
                    height = time_info.get('wave_height', 0)
                    quality = time_info.get('surf_quality', '')
                    
                    session = {
                        'time': time_key,
                        'hebrew_time': {'06:00': 'בוקר', '12:00': 'צהרים', '18:00': 'ערב'}.get(time_key, time_key),
                        'height': height,
                        'height_text': f"{height:.1f}מ'",
                        'quality_hebrew': format_wave_height_hebrew(height),
                        'quality_english': quality.split('(')[1].rstrip(')') if '(' in quality else '',
                        'emoji': get_wave_emoji(height),
                        'is_good': height >= 0.4
                    }
                    day_info['sessions'].append(session)
            
            forecast_display['days'].append(day_info)
    
    return render_template('index.html', forecast=forecast_display)

@app.route('/api/forecast')
def api_forecast():
    """API endpoint returning JSON forecast data"""
    return jsonify({
        'success': True,
        'last_update': last_update.isoformat() if last_update else None,
        'data': forecast_cache
    })

@app.route('/api/status')
def api_status():
    """API endpoint for addon status"""
    config = get_config()
    
    return jsonify({
        'status': 'running',
        'last_update': last_update.isoformat() if last_update else None,
        'config': config,
        'data_available': bool(forecast_cache)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/widget')
def widget():
    """iOS Widget optimized view"""
    config = get_config()
    
    # Prepare minimal forecast data for widget
    widget_data = {
        'beach_name': forecast_cache.get('beach', 'Ashkelon'),
        'last_update': last_update.strftime('%H:%M') if last_update else 'N/A',
        'current_session': None,
        'config': config
    }
    
    if forecast_cache.get('daily_forecasts'):
        # Get today's forecast
        today = datetime.now().strftime('%Y-%m-%d')
        today_forecast = forecast_cache['daily_forecasts'].get(today)
        
        if today_forecast:
            # Find current or next session
            current_hour = datetime.now().hour
            
            times_data = today_forecast.get('times', {})
            
            # Determine which session to show
            if current_hour < 9:
                session_key = '06:00'
            elif current_hour < 15:
                session_key = '12:00' 
            else:
                session_key = '18:00'
            
            if session_key in times_data:
                time_info = times_data[session_key]
                height = time_info.get('wave_height', 0)
                quality = time_info.get('surf_quality', '')
                
                widget_data['current_session'] = {
                    'time': session_key,
                    'hebrew_time': {'06:00': 'בוקר', '12:00': 'צהרים', '18:00': 'ערב'}.get(session_key, session_key),
                    'height': height,
                    'height_text': f"{height:.1f}מ'",
                    'quality_hebrew': format_wave_height_hebrew(height),
                    'emoji': get_wave_emoji(height),
                    'period': int(height * 3 + 8),  # Simulated period
                    'hebrew_day': today_forecast.get('hebrew_day', ''),
                    'formatted_date': today_forecast.get('hebrew_date', ''),
                }
    
    return render_template('widget.html', widget=widget_data)

@app.route('/api/widget')
def api_widget():
    """JSON API for iOS Shortcuts/Widgets"""
    if not forecast_cache or not forecast_cache.get('daily_forecasts'):
        return jsonify({
            'success': False,
            'error': 'No forecast data available'
        })
    
    # Get today's forecast
    today = datetime.now().strftime('%Y-%m-%d')
    today_forecast = forecast_cache['daily_forecasts'].get(today)
    
    if not today_forecast:
        return jsonify({
            'success': False,
            'error': 'No forecast for today'
        })
    
    # Build widget data
    widget_data = {
        'success': True,
        'beach': 'אשקלון',
        'beach_english': 'Ashkelon',
        'date': today_forecast.get('hebrew_date', ''),
        'day': today_forecast.get('hebrew_day', ''),
        'last_update': last_update.strftime('%H:%M') if last_update else '',
        'sessions': []
    }
    
    # Add session data
    times_data = today_forecast.get('times', {})
    for time_key in ['06:00', '12:00', '18:00']:
        if time_key in times_data:
            time_info = times_data[time_key]
            height = time_info.get('wave_height', 0)
            
            widget_data['sessions'].append({
                'time': time_key,
                'hebrew_time': {'06:00': 'בוקר', '12:00': 'צהרים', '18:00': 'ערב'}.get(time_key, time_key),
                'height': height,
                'height_text': f"{height:.1f}מ'",
                'quality_hebrew': format_wave_height_hebrew(height),
                'quality_english': time_info.get('surf_quality', '').split('(')[1].rstrip(')') if '(' in time_info.get('surf_quality', '') else '',
                'period': int(height * 3 + 8),
                'rating_stars': '⭐' * min(5, max(1, int(height * 3))),
                'is_good': height >= 0.4
            })
    
    return jsonify(widget_data)

@app.route('/api/ha-sensor')
def ha_sensor():
    """Home Assistant sensor data"""
    if not forecast_cache or not forecast_cache.get('daily_forecasts'):
        return jsonify({
            'state': 'unavailable',
            'attributes': {
                'friendly_name': 'Ashkelon Surf Forecast',
                'last_update': None,
                'forecast_days': 0
            }
        })
    
    # Calculate overall surf quality for today
    today = datetime.now().strftime('%Y-%m-%d')
    today_forecast = forecast_cache['daily_forecasts'].get(today, {})
    times_data = today_forecast.get('times', {})
    
    if not times_data:
        state = 'flat'
        max_height = 0
    else:
        heights = [t.get('wave_height', 0) for t in times_data.values()]
        max_height = max(heights) if heights else 0
        
        if max_height >= 1.0:
            state = 'excellent'
        elif max_height >= 0.6:
            state = 'good'  
        elif max_height >= 0.3:
            state = 'fair'
        else:
            state = 'flat'
    
    return jsonify({
        'state': state,
        'attributes': {
            'friendly_name': 'Ashkelon Surf Forecast',
            'max_wave_height': max_height,
            'max_wave_height_hebrew': format_wave_height_hebrew(max_height),
            'hebrew_day': today_forecast.get('hebrew_day', ''),
            'forecast_date': today_forecast.get('hebrew_date', ''),
            'last_update': last_update.isoformat() if last_update else None,
            'forecast_days': len(forecast_cache.get('daily_forecasts', {})),
            'morning_height': times_data.get('06:00', {}).get('wave_height', 0),
            'noon_height': times_data.get('12:00', {}).get('wave_height', 0), 
            'evening_height': times_data.get('18:00', {}).get('wave_height', 0),
            'source': '4surfers.co.il',
            'unit_of_measurement': 'meters'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Ashkelon Surf Forecast Web Server...")
    
    # Start background updater
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Initial data load
    update_forecast_data()
    
    # Start Flask app
    logger.info("Web server starting on port 8099...")
    app.run(host='0.0.0.0', port=8099, debug=False)