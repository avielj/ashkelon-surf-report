from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        
        try:
            if path == '/':
                self.send_html_response(self.get_main_page())
            elif path == '/widget':
                self.send_html_response(self.get_widget_page())
            elif path == '/api/widget':
                self.send_json_response(self.get_widget_data())
            elif path == '/health':
                self.send_json_response({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            else:
                self.send_404()
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_html_response(self, html_content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'<h1>404 - Page not found</h1><p>Available routes: /, /widget, /api/widget, /health</p>')
    
    def send_error_response(self, error_msg):
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'error': error_msg}, ensure_ascii=False).encode('utf-8'))
    
    def wave_height_to_quality(self, height):
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
    
    def get_hebrew_day(self, weekday):
        days = ['ב\'', 'ג\'', 'ד\'', 'ה\'', 'ו\'', 'שבת', 'א\'']
        return days[weekday]
    
    def get_forecast_data(self):
        today = datetime.now()
        forecast_data = {
            'beach': 'Ashkelon',
            'beach_hebrew': 'אשקלון',
            'last_update': today.strftime('%H:%M'),
            'days': []
        }
        
        for day in range(3):
            date = today + timedelta(days=day)
            hebrew_day = self.get_hebrew_day(date.weekday())
            base_height = 0.4 + (day * 0.2)
            
            day_info = {
                'date': date.strftime('%Y-%m-%d'),
                'hebrew_day': hebrew_day,
                'english_day': date.strftime('%A'),
                'formatted_date': date.strftime('%d/%m'),
                'sessions': []
            }
            
            for time_key, time_multiplier, hebrew_time in [
                ('06:00', 1.0, 'בוקר'),
                ('12:00', 1.2, 'צהרים'),
                ('18:00', 0.9, 'ערב')
            ]:
                height = base_height * time_multiplier
                session = {
                    'time': time_key,
                    'hebrew_time': hebrew_time,
                    'height': height,
                    'height_text': f"{height:.1f}מ'",
                    'quality_hebrew': self.wave_height_to_quality(height),
                    'emoji': "🌊🌊" if height >= 1.0 else "🌊" if height >= 0.5 else "〰️",
                    'is_good': height >= 0.4
                }
                day_info['sessions'].append(session)
            
            forecast_data['days'].append(day_info)
        
        return forecast_data
    
    def get_widget_data(self):
        forecast = self.get_forecast_data()
        today_data = forecast['days'][0] if forecast['days'] else {}
        
        widget_data = {
            'success': True,
            'beach': 'אשקלון',
            'beach_english': 'Ashkelon',
            'date': today_data.get('formatted_date', ''),
            'day': today_data.get('hebrew_day', ''),
            'last_update': datetime.now().strftime('%H:%M'),
            'sessions': []
        }
        
        for session in today_data.get('sessions', []):
            widget_data['sessions'].append({
                'time': session['time'],
                'hebrew_time': session['hebrew_time'],
                'height': session['height'],
                'height_text': session['height_text'],
                'quality_hebrew': session['quality_hebrew'],
                'period': int(session['height'] * 3 + 8),
                'rating_stars': '⭐' * min(5, max(1, int(session['height'] * 3))),
                'is_good': session['is_good']
            })
        
        return widget_data
    
    def get_main_page(self):
        forecast = self.get_forecast_data()
        
        html = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌊 תחזית גלים אשקלון</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/css/materialdesignicons.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Heebo', sans-serif;
            background: #1a1a1a;
            min-height: 100vh;
            color: #fff;
            direction: rtl;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .app-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .app-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .surf-forecast-card {
            background: linear-gradient(135deg, #4f9ded 0%, #2c5aa0 100%);
            border-radius: 16px;
            padding: 20px;
            min-height: 280px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
        }
        .location-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .surf-icon {
            font-size: 2.5rem;
            color: #ffffff;
        }
        .location-text h2 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
        }
        .location-subtitle {
            color: #e6fbc9;
        }
        .date-info {
            text-align: left;
            direction: ltr;
        }
        .hebrew-day {
            display: block;
            font-size: 1.2rem;
            font-weight: 600;
            color: #ffffff;
        }
        .date {
            font-size: 0.9rem;
            color: #e6fbc9;
        }
        .forecast-grid-sessions {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .session-column {
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: center;
        }
        .forecast-chip {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 500;
            min-width: 80px;
            height: 32px;
            padding: 4px 8px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        .info-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #e6fbc9;
            margin-top: auto;
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .surf-forecast-card { padding: 15px; min-height: 240px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="app-header">
            <h1 class="app-title">🌊 תחזית גלים אשקלון</h1>
            <p>Ashkelon Surf Forecast - Live on Vercel</p>
        </header>'''
        
        for day in forecast['days']:
            html += f'''
        <div class="surf-forecast-card">
            <div class="card-header">
                <div class="location-info">
                    <i class="mdi mdi-surfing surf-icon"></i>
                    <div class="location-text">
                        <h2>אשקלון</h2>
                        <p class="location-subtitle">Ashkelon</p>
                    </div>
                </div>
                <div class="date-info">
                    <span class="hebrew-day">{day["hebrew_day"]}</span>
                    <span class="date">{day["formatted_date"]}</span>
                </div>
            </div>
            
            <div class="forecast-grid-sessions">'''
            
            for session in day['sessions']:
                html += f'''
                <div class="session-column">
                    <div class="forecast-chip">
                        <i class="mdi mdi-clock-outline"></i>
                        <span>{session["time"]}</span>
                    </div>
                    <div class="forecast-chip">
                        <i class="mdi mdi-star"></i>
                        <span>{session["quality_hebrew"]}</span>
                    </div>
                    <div class="forecast-chip">
                        <i class="mdi mdi-sine-wave"></i>
                        <span>{session["height_text"]}</span>
                    </div>
                    <div class="forecast-chip">
                        <i class="mdi mdi-timer-sand"></i>
                        <span>{int(session["height"] * 3 + 8)}s</span>
                    </div>
                </div>'''
            
            html += '''
            </div>
            
            <div class="info-bar">
                <span>📊 מקור: Vercel Demo</span>
                <span>⏰ ''' + forecast['last_update'] + '''</span>
            </div>
        </div>'''
        
        html += '''
        <footer style="text-align: center; padding: 20px; color: rgba(255, 255, 255, 0.6);">
            <p>🚀 Working on Vercel!</p>
            <p><a href="/widget" style="color: #4f9ded;">Widget View</a> • <a href="/api/widget" style="color: #4f9ded;">JSON API</a></p>
        </footer>
    </div>
</body>
</html>'''
        
        return html
    
    def get_widget_page(self):
        forecast = self.get_forecast_data()
        today = forecast['days'][0] if forecast['days'] else {}
        
        html = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌊 אשקלון - Widget</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Heebo', sans-serif;
            background: linear-gradient(135deg, #4f9ded 0%, #2c5aa0 100%);
            min-height: 100vh;
            color: #fff;
            direction: rtl;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .widget-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 100%;
        }
        .widget-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .beach-name {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .widget-sessions {
            display: flex;
            justify-content: space-around;
            gap: 10px;
        }
        .session-item {
            text-align: center;
            flex: 1;
        }
        .session-time {
            font-size: 0.9rem;
            margin-bottom: 5px;
            opacity: 0.8;
        }
        .session-height {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 3px;
        }
        .session-quality {
            font-size: 0.8rem;
            opacity: 0.9;
        }
        .widget-footer {
            text-align: center;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="widget-card">
        <div class="widget-header">
            <div class="beach-name">🌊 אשקלון</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">''' + today.get('hebrew_day', '') + ' • ' + today.get('formatted_date', '') + '''</div>
        </div>
        <div class="widget-sessions">'''
        
        for session in today.get('sessions', []):
            html += f'''
            <div class="session-item">
                <div class="session-time">{session["hebrew_time"]}</div>
                <div class="session-height">{session["height_text"]}</div>
                <div class="session-quality">{session["quality_hebrew"]}</div>
            </div>'''
        
        html += '''
        </div>
        <div class="widget-footer">
            <div style="font-size: 0.8rem; opacity: 0.7;">
                <a href="/" style="color: white;">← Full Forecast</a>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        return html