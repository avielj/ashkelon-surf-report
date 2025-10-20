from flask import Flask, render_template, jsonify
import os
from datetime import datetime, timedelta

# Create Flask app with correct template path
app = Flask(__name__, template_folder='../templates')

class SurfForecast:
    def _wave_height_to_quality(self, height: float) -> str:
        """Convert wave height to Hebrew surf quality"""
        if height <= 0.1: return 'פלטה'
        elif height <= 0.2: return 'שטוח'
        elif height <= 0.4: return 'קרסול'
        elif height <= 0.6: return 'קרסול עד ברך'
        elif height <= 0.9: return 'ברך'
        elif height <= 1.2: return 'מעל ברך'
        elif height <= 1.5: return 'כתף'
        elif height <= 1.8: return 'מעל כתף'
        elif height <= 2.2: return 'מותן'
        elif height <= 2.8: return 'ראש'
        else: return 'מעל ראש'
    
    def _get_hebrew_day(self, weekday: int) -> str:
        """Get Hebrew day name"""
        days = ['ב\'', 'ג\'', 'ד\'', 'ה\'', 'ו\'', 'שבת', 'א\'']
        return days[weekday]
    
    def get_mock_data(self):
        """Generate mock data"""
        today = datetime.now()
        forecast_data = {
            'beach': 'Ashkelon',
            'beach_hebrew': 'אשקלון',
            'source': '4surfers.co.il',
            'timestamp': today.isoformat(),
            'offline_mode': False,
            'daily_forecasts': {}
        }
        
        # Generate 3 days of forecast
        for day in range(3):
            date = today + timedelta(days=day)
            date_key = date.strftime('%Y-%m-%d')
            hebrew_day = self._get_hebrew_day(date.weekday())
            
            base_height = 0.4 + (day * 0.2)
            
            forecast_data['daily_forecasts'][date_key] = {
                'hebrew_date': date.strftime('%d/%m'),
                'hebrew_day': hebrew_day,
                'english_day': date.strftime('%A'),
                'times': {
                    '06:00': {
                        'wave_height': base_height,
                        'surf_quality': f"{self._wave_height_to_quality(base_height)} (morning)",
                        'hebrew_time': 'בוקר'
                    },
                    '12:00': {
                        'wave_height': base_height * 1.2,
                        'surf_quality': f"{self._wave_height_to_quality(base_height * 1.2)} (noon)",
                        'hebrew_time': 'צהרים'
                    },
                    '18:00': {
                        'wave_height': base_height * 0.9,
                        'surf_quality': f"{self._wave_height_to_quality(base_height * 0.9)} (evening)",
                        'hebrew_time': 'ערב'
                    }
                }
            }
        
        return forecast_data

surf_forecast = SurfForecast()

@app.route('/')
def index():
    """Main surf forecast page"""
    try:
        forecast_cache = surf_forecast.get_mock_data()
        
        forecast_display = {
            'beach_name': 'Ashkelon',
            'last_update': datetime.now().strftime('%H:%M'),
            'days': [],
            'offline_mode': False
        }
        
        if forecast_cache.get('daily_forecasts'):
            sorted_dates = sorted(forecast_cache['daily_forecasts'].items())
            
            for date_key, day_data in sorted_dates[:3]:
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
                        
                        session = {
                            'time': time_key,
                            'hebrew_time': time_info.get('hebrew_time', time_key),
                            'height': height,
                            'height_text': f"{height:.1f}מ'",
                            'quality_hebrew': surf_forecast._wave_height_to_quality(height),
                            'emoji': "🌊" if height >= 0.5 else "〰️",
                            'is_good': height >= 0.4
                        }
                        day_info['sessions'].append(session)
                
                forecast_display['days'].append(day_info)
        
        return render_template('standalone_index.html', forecast=forecast_display)
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/widget')
def widget():
    """Widget view"""
    try:
        forecast_cache = surf_forecast.get_mock_data()
        
        forecast_display = {
            'days': [],
            'last_update': datetime.now().strftime('%H:%M'),
            'offline_mode': False
        }
        
        if forecast_cache.get('daily_forecasts'):
            today = datetime.now().strftime('%Y-%m-%d')
            today_forecast = forecast_cache['daily_forecasts'].get(today)
            
            if today_forecast:
                day_info = {
                    'hebrew_day': today_forecast.get('hebrew_day', ''),
                    'formatted_date': today_forecast.get('hebrew_date', ''),
                    'sessions': []
                }
                
                times_data = today_forecast.get('times', {})
                for time_key in ['06:00', '12:00', '18:00']:
                    if time_key in times_data:
                        time_info = times_data[time_key]
                        height = time_info.get('wave_height', 0)
                        
                        session = {
                            'time': time_key,
                            'hebrew_time': time_info.get('hebrew_time', time_key),
                            'height': height,
                            'height_text': f"{height:.1f}מ'",
                            'quality_hebrew': surf_forecast._wave_height_to_quality(height),
                        }
                        day_info['sessions'].append(session)
                
                forecast_display['days'] = [day_info]
        
        return render_template('widget.html', forecast=forecast_display)
        
    except Exception as e:
        return f"Widget Error: {str(e)}", 500

@app.route('/api/widget')
def api_widget():
    """JSON API"""
    try:
        forecast_cache = surf_forecast.get_mock_data()
        today = datetime.now().strftime('%Y-%m-%d')
        today_forecast = forecast_cache['daily_forecasts'].get(today, {})
        
        widget_data = {
            'success': True,
            'beach': 'אשקלון',
            'beach_english': 'Ashkelon',
            'date': today_forecast.get('hebrew_date', ''),
            'day': today_forecast.get('hebrew_day', ''),
            'last_update': datetime.now().strftime('%H:%M'),
            'sessions': [],
            'offline_mode': False
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
                    'quality_hebrew': surf_forecast._wave_height_to_quality(height),
                    'period': int(height * 3 + 8),
                    'rating_stars': '⭐' * min(5, max(1, int(height * 3))),
                    'is_good': height >= 0.4
                })
        
        return jsonify(widget_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Ashkelon Surf Forecast',
        'timestamp': datetime.now().isoformat()
    })

# Vercel WSGI handler
from werkzeug.wrappers import Request, Response

def application(environ, start_response):
    """WSGI application for Vercel"""
    return app.wsgi_app(environ, start_response)

# Also export app directly
if __name__ == "__main__":
    app.run(debug=True)