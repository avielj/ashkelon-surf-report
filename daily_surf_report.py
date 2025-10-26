#!/usr/bin/env python3
"""
Daily Surf Report - Lightweight script for GitHub Actions
Sends Telegram notifications based on 72-hour wave forecast

Uses the same logic as the Scriptable widget and Home Assistant integration
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def get_surf_forecast(beach_id: str = "80") -> Optional[Dict]:
    """
    Get surf forecast from 4surfers.co.il API
    
    Args:
        beach_id: Beach area ID (80 = Ashkelon)
    
    Returns:
        API response dictionary or None if failed
    """
    try:
        url = 'https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast'
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://4surfers.co.il',
            'Referer': 'https://4surfers.co.il/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        }
        
        data = {"beachAreaId": beach_id}
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching forecast: {e}")
        return None


def get_star_rating(height_m: float) -> str:
    """Convert wave height to star rating (same as widget logic)"""
    if height_m >= 2.5:
        return "⭐⭐⭐⭐⭐"
    elif height_m >= 2.0:
        return "⭐⭐⭐⭐"
    elif height_m >= 1.5:
        return "⭐⭐⭐"
    elif height_m >= 1.0:
        return "⭐⭐"
    elif height_m >= 0.5:
        return "⭐"
    else:
        return ""


def get_hebrew_day(weekday: int) -> str:
    """Get Hebrew day name from weekday number (0=Monday)"""
    hebrew_days = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
    return hebrew_days[weekday]


def parse_forecast_data(api_data: Dict) -> List[Dict]:
    """
    Parse API response into structured forecast days
    Same logic as Home Assistant sensor
    
    Returns:
        List of forecast days with sessions
    """
    if 'dailyForecastList' not in api_data:
        return []
    
    forecast_days = []
    
    for day_forecast in api_data['dailyForecastList'][:3]:  # Only next 3 days
        if 'forecastLocalTime' not in day_forecast:
            continue
        
        # Parse the forecast date
        forecast_date = day_forecast['forecastLocalTime']
        dt = datetime.fromisoformat(forecast_date.replace('T', ' ').replace('+03:00', ''))
        
        # Process hourly forecasts for this day
        forecast_hours = day_forecast.get('forecastHours', [])
        
        # Filter to 4 key times: 06:00, 09:00, 12:00, 18:00
        sessions = []
        target_hours = [6, 9, 12, 18]
        
        for hour_forecast in forecast_hours:
            hour_time = hour_forecast.get('forecastLocalHour', '')
            
            try:
                hour_dt = datetime.fromisoformat(hour_time.replace('T', ' ').replace('+03:00', ''))
                
                if hour_dt.hour in target_hours:
                    # Get wave height - use average of from/to if available, fallback to waveHeight
                    surf_from = hour_forecast.get('surfHeightFrom', 0)
                    surf_to = hour_forecast.get('surfHeightTo', 0)
                    
                    if surf_from > 0 and surf_to > 0:
                        wave_height_m = (surf_from + surf_to) / 2
                    else:
                        wave_height_m = hour_forecast.get('waveHeight', 0)
                    
                    wave_height_ft = wave_height_m * 3.28084
                    hebrew_desc = hour_forecast.get('surfHeightDesc', '')
                    period_s = hour_forecast.get('wavePeriod', 0)
                    wind_kts = hour_forecast.get('windSpeed', 0)
                    stars = get_star_rating(wave_height_m)
                    
                    sessions.append({
                        'time': f"{hour_dt.hour:02d}:00",
                        'height_m': round(wave_height_m, 2),
                        'height_ft': round(wave_height_ft, 2),
                        'hebrew_desc': hebrew_desc,
                        'period_s': period_s,
                        'wind_kts': wind_kts,
                        'stars': stars
                    })
            except:
                continue
        
        if sessions:
            forecast_days.append({
                'date': dt.strftime('%Y-%m-%d'),
                'date_display': dt.strftime('%d/%m'),
                'hebrew_day': get_hebrew_day(dt.weekday()),
                'sessions': sessions
            })
    
    return forecast_days


def has_surfable_waves(forecast_days: List[Dict], min_height_ft: float = 2.0, min_period_s: float = 6.5) -> bool:
    """
    Check if there are surfable waves in the forecast
    
    Args:
        forecast_days: List of parsed forecast days
        min_height_ft: Minimum wave height in feet to be considered surfable (default: 2.0ft)
        min_period_s: Minimum wave period in seconds for quality waves (default: 6.5s)
    
    Returns:
        True if any session has waves >= min_height_ft AND period >= min_period_s
    """
    for day in forecast_days:
        for session in day['sessions']:
            height_ok = session['height_ft'] >= min_height_ft
            period_ok = session['period_s'] >= min_period_s
            
            if height_ok and period_ok:
                return True
    return False


def format_telegram_message(forecast_days: List[Dict]) -> str:
    """
    Format forecast into Hebrew Telegram message
    
    Returns:
        Formatted message string
    """
    if not forecast_days:
        return "אין מידע על תחזית גלים"
    
    # Check if there are surfable waves
    if not has_surfable_waves(forecast_days):
        return "אין גלים בימים הקרובים 🏖️"
    
    # Build 3-day forecast message
    lines = []
    lines.append("🏄‍♂️ <b>תחזית גלים - אשקלון</b> 🌊")
    lines.append("")
    
    for day in forecast_days:
        # Only show days that have quality sessions
        quality_sessions = []
        
        for session in day['sessions']:
            height_ok = session['height_ft'] >= 2.0
            period_ok = session['period_s'] >= 6.5
            
            if height_ok and period_ok:
                quality_sessions.append(session)
        
        # Skip days with no quality sessions
        if not quality_sessions:
            continue
            
        # Day header
        day_header = f"📅 <b>{day['hebrew_day']} {day['date_display']}</b>"
        lines.append(day_header)
        
        # Show only quality sessions for this day
        for session in quality_sessions:
            stars = session['stars'] if session['stars'] else "⭐"
            height_ft = session['height_ft']
            hebrew_desc = session['hebrew_desc']
            period = session['period_s']
            wind = session['wind_kts']
            
            # Add quality indicator for really good waves
            quality_emoji = ""
            if height_ft >= 3.0 and period >= 8.0:
                quality_emoji = " 🔥"  # Epic conditions
            elif height_ft >= 2.5 and period >= 7.0:
                quality_emoji = " 💪"  # Great conditions
            
            # Format: "� 06:00: ⭐⭐ 2.3ft (ברך) ⏱️ 7s 💨 12kts 💪"
            line = f"  🕐 {session['time']}: {stars} {height_ft}ft"
            
            if hebrew_desc:
                line += f" ({hebrew_desc})"
            
            if period > 0:
                line += f" ⏱️ {period}s"
            
            if wind > 0:
                line += f" 💨 {wind}kts"
            
            line += quality_emoji
            lines.append(line)
        
        lines.append("")  # Blank line between days
    
    lines.append("📊 מקור: 4surfers.co.il")
    
    return "\n".join(lines)


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send message via Telegram Bot API
    
    Args:
        bot_token: Telegram bot token
        chat_id: Chat/channel ID
        message: Message text (HTML formatted)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully!")
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False


def main():
    """Main function for daily surf report"""
    print("🏄‍♂️ Daily Surf Report - Ashkelon")
    print("=" * 50)
    
    # Get environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID environment variable not set")
        sys.exit(1)
    
    # Fetch forecast
    print("📡 Fetching forecast from 4surfers.co.il...")
    api_data = get_surf_forecast()
    
    if not api_data:
        print("❌ Failed to fetch forecast data")
        sys.exit(1)
    
    # Parse forecast
    print("📊 Parsing forecast data...")
    forecast_days = parse_forecast_data(api_data)
    
    if not forecast_days:
        print("❌ No forecast data available")
        sys.exit(1)
    
    print(f"✅ Got {len(forecast_days)} days of forecast")
    
    # Format message
    message = format_telegram_message(forecast_days)
    print("\n📝 Message to send:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Send to Telegram
    print("\n📱 Sending to Telegram...")
    success = send_telegram_message(bot_token, chat_id, message)
    
    if success:
        print("✅ Daily report completed successfully!")
        sys.exit(0)
    else:
        print("❌ Failed to send daily report")
        sys.exit(1)


if __name__ == "__main__":
    main()
