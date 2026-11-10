#!/usr/bin/env python3
"""
Daily Surf Report - Lightweight script for GitHub Actions
Sends Telegram notifications based on 72-hour wave forecast

Uses the same logic as the Scriptable widget and Home Assistant integration
"""

import os
import re
import sys
import json
import urllib.request
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Card rendering is optional: if Pillow/bidi are missing, the text report
# below still works (the Action installs them via requirements.txt).
try:
    from surf_card import build_card
except Exception:
    build_card = None


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
                    # Get wave height - use average of from/to if available, fallback to WaveHeight
                    surf_from = hour_forecast.get('SurfHeightFrom', 0)
                    surf_to = hour_forecast.get('SurfHeightTo', 0)
                    
                    if surf_from > 0 and surf_to > 0:
                        wave_height_m = (surf_from + surf_to) / 2
                    else:
                        wave_height_m = hour_forecast.get('WaveHeight', 0)
                    
                    wave_height_ft = wave_height_m * 3.28084
                    hebrew_desc = hour_forecast.get('surfHeightDesc', '')
                    period_s = hour_forecast.get('WavePeriod', 0)
                    wind_kts = hour_forecast.get('WindSpeedInKnots', 0)
                    wind_dir = hour_forecast.get('WindDirection')
                    stars = get_star_rating(wave_height_m)
                    
                    sessions.append({
                        'time': f"{hour_dt.hour:02d}:00",
                        'height_m': round(wave_height_m, 2),
                        'height_ft': round(wave_height_ft, 1),  # Round to 1 decimal for consistency
                        'hebrew_desc': hebrew_desc,
                        'period_s': round(period_s, 1),  # Round period to 1 decimal
                        'wind_kts': wind_kts,
                        'wind_dir': wind_dir,
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
        OR if waves >= 1.8ft AND period >= 8s (quality long-period swell)
    """
    for day in forecast_days:
        for session in day['sessions']:
            height_ft = session['height_ft']
            period_s = session['period_s']
            
            # Standard condition: 2ft+ with 6.5s+ period
            standard_ok = height_ft >= min_height_ft and period_s >= min_period_s
            
            # Alternative condition: 1.8ft+ with 8s+ period (quality long-period swell)
            quality_swell = height_ft >= 1.8 and period_s >= 8.0
            
            if standard_ok or quality_swell:
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
            height_ft = session['height_ft']
            period_s = session['period_s']
            
            # Standard condition: 2ft+ with 6.5s+ period
            standard_ok = height_ft >= 2.0 and period_s >= 6.5
            
            # Alternative condition: 1.8ft+ with 8s+ period (quality long-period swell)
            quality_swell = height_ft >= 1.8 and period_s >= 8.0
            
            if standard_ok or quality_swell:
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


# ---------------------------------------------------------------------------
# Forecast card (surf_card.py) — the visual summary of the Ashkelon Wave
# Forecast page, sent as a Telegram photo. Verdict rules (Aviel, Nov 7-8):
# morning window only (06:00-08:00 workdays, 06:00-10:00 Fri-Sat); surfable
# if surf >= 0.61m + period >= 6.5s, or >= 0.55m + period >= 8s; onshore wind
# >= 24 km/h downgrades one level, >= 33 caps at YELLOW; a disputed wind
# direction (4surfers vs met.no at 06:00) downgrades one level.
# ---------------------------------------------------------------------------

def wind_class(wdir):
    """Delila-relative wind class: offshore E/SE (45-135), onshore W/NW (225-315), else side."""
    if wdir is None:
        return "?"
    if 45 <= wdir <= 135:
        return "offshore"
    if 225 <= wdir <= 315:
        return "onshore"
    return "side"


def _downgrade(score):
    order = ["FLAT", "YELLOW", "GREEN"]
    return order[max(0, order.index(score) - 1)]


def score_morning(surf_m, period_s, wind_kmh, wind_cls, disputed):
    """Morning-window verdict from the 4surfers best session + wind modifier."""
    if (surf_m >= 0.61 and period_s >= 6.5) or (surf_m >= 0.55 and period_s >= 8.0):
        score = "GREEN"
    elif surf_m >= 0.6 and period_s >= 6.0:
        score = "YELLOW"
    else:
        score = "FLAT"
    if wind_cls == "onshore" and wind_kmh is not None and wind_kmh >= 33:
        if score != "FLAT":
            score = "YELLOW"
    elif wind_cls == "onshore" and wind_kmh is not None and wind_kmh >= 24:
        score = _downgrade(score)
    if disputed:
        score = _downgrade(score)
    return score


def fetch_metno_timeseries():
    """Full met.no timeseries as {(date_iso, hour): (speed_ms, dir_deg)} or {}."""
    try:
        from zoneinfo import ZoneInfo
        ist = ZoneInfo("Asia/Jerusalem")
    except Exception:
        return {}
    try:
        req = urllib.request.Request(
            'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=31.67&lon=34.57',
            headers={'User-Agent': 'AshkelonSurfReport/1.0'})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        out = {}
        for x in data['properties']['timeseries']:
            dt = datetime.fromisoformat(x['time'].replace('Z', '+00:00')).astimezone(ist)
            det = x['data']['instant']['details']
            out[(dt.date().isoformat(), dt.hour)] = (det.get('wind_speed'), det.get('wind_from_direction'))
        return out
    except Exception:
        return {}


def _nearest_metno(wind, date_iso, hour=6):
    """met.no wind nearest to the given hour (past hours drop out of the forecast)."""
    for d in (0, 1, 2, 3, -1, -2, -3):
        if (date_iso, hour + d) in wind:
            return wind[(date_iso, hour + d)]
    return (None, None)


def fetch_seanow_delila():
    """SEANOW Delila spot page: recommended window + score. Returns dict or {}."""
    try:
        req = urllib.request.Request("https://seanow.co.il/surf/ashkelon-delilah/",
                                     headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        i = html.find("חלון מומלץ")
        text = re.sub(r"<[^>]+>", " ", html[i:i + 500]) if i >= 0 else ""
        text = re.sub(r"\s+", " ", text)
        m = re.search(r"חלון מומלץ:\s*(.+?)\s*\(ציון\s*([\d.]+)\s*\)", text)
        return {"recommended_window": m.group(1).strip() if m else None,
                "recommended_score": float(m.group(2)) if m else None}
    except Exception:
        return {}


def build_card_days(api_data):
    """7 day dicts for surf_card.build_card, with the page's verdict rules."""
    if 'dailyForecastList' not in api_data:
        return []
    metno = fetch_metno_timeseries()
    seanow = fetch_seanow_delila()
    seanow_date = None
    if seanow.get('recommended_window'):
        m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', seanow['recommended_window'])
        if m:
            seanow_date = f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"

    days = []
    for day_forecast in api_data['dailyForecastList'][:7]:
        if 'forecastLocalTime' not in day_forecast:
            continue
        dt = datetime.fromisoformat(day_forecast['forecastLocalTime'].replace('T', ' ').replace('+03:00', ''))
        date_iso = dt.strftime('%Y-%m-%d')
        weekend = dt.weekday() >= 4  # Fri=4, Sat=5
        window_hours = [6, 9] if weekend else [6]
        best = None
        s06 = None
        for h in day_forecast.get('forecastHours', []):
            try:
                hdt = datetime.fromisoformat(h.get('forecastLocalHour', '').replace('T', ' ').replace('+03:00', ''))
            except Exception:
                continue
            if hdt.hour not in window_hours:
                continue
            sf, st = h.get('SurfHeightFrom', 0), h.get('SurfHeightTo', 0)
            surf = (sf + st) / 2 if sf and st else h.get('WaveHeight', 0)
            sess = {'surf': surf, 'period': h.get('WavePeriod', 0),
                    'wind_kts': h.get('WindSpeedInKnots', 0),
                    'wind_dir': h.get('WindDirection'),
                    'desc': h.get('surfHeightDesc', '')}
            if hdt.hour == 6:
                s06 = sess
            if best is None or surf > best['surf']:
                best = sess
        if not s06 and not best:
            continue
        s06 = s06 or best
        wind_kmh = round(s06['wind_kts'] * 1.852) if s06.get('wind_kts') else None
        wind_cls = wind_class(s06.get('wind_dir'))
        # Disputed direction: 4surfers vs met.no at 06:00 (Aviel, Nov 8)
        disputed = False
        _, m6_dir = _nearest_metno(metno, date_iso, 6)
        m6_cls = wind_class(m6_dir)
        if wind_cls in ('offshore', 'onshore', 'side') and m6_cls in ('offshore', 'onshore', 'side') and wind_cls != m6_cls:
            disputed = True
        score = score_morning(best['surf'], best['period'], wind_kmh, wind_cls, disputed)
        days.append({
            'dow': get_hebrew_day(dt.weekday()),
            'dnum': dt.strftime('%d.%m'),
            'date': date_iso,
            'weekend': weekend,
            'score': score,
            'surf_m': round(best['surf'], 2),
            'desc': best.get('desc', ''),
            'period_s': round(best['period'], 1),
            'wind_kmh': wind_kmh,
            'wind_class': wind_cls,
            'wind_disputed': disputed,
            'seanow': seanow.get('recommended_score') if date_iso == seanow_date else None,
        })
    return days


def format_card_caption(hero):
    """Short HTML caption under the card photo."""
    verdict = {'GREEN': '🟢 לך', 'YELLOW': '🟡 שווה בדיקה', 'FLAT': '⚪ שטוח'}[hero['score']]
    win = '06:00–10:00' if hero.get('weekend') else '06:00–08:00'
    wind_he = {'offshore': 'מהיבשה (אוף־שור)', 'onshore': 'מהים (און־שור)',
               'side': 'מהצד'}.get(hero.get('wind_class', 'side'), '')
    lines = [
        f"🏄‍♂️ <b>תחזית גלים — אשקלון · {hero['dow']} {hero['dnum']}</b>",
        f"{verdict} · חלון {win}",
        f"גובה הגל בשבירה: {hero['surf_m']:.1f} מ׳ ({hero.get('desc', '')}) · משך {hero['period_s']:.1f} שניות",
        f"רוח: {hero['wind_kmh']} קמ״ש {wind_he}",
    ]
    if hero.get('seanow') is not None:
        lines.append(f"הציון של SEANOW דלילה לשעה 06:00 הוא {hero['seanow']:.1f}")
    lines.append("📷 מצלמה חיה: https://www.swellstock.co.il/cams")
    lines.append("📊 מקור: 4surfers.co.il")
    return "\n".join(lines)


def send_telegram_photo(bot_token, chat_id, photo_path, caption):
    """Send the forecast card via Telegram Bot API sendPhoto. Returns True/False."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(photo_path, 'rb') as f:
            files = {'photo': (os.path.basename(photo_path), f, 'image/png')}
            data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
            response = requests.post(url, data=data, files=files, timeout=30)
        if response.status_code == 200:
            print("✅ Telegram photo sent successfully!")
            return True
        print(f"❌ Telegram API error: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Error sending Telegram photo: {e}")
        return False


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
    
    # --- Forecast card (photo) first, text message as fallback ---
    if build_card is not None:
        try:
            card_days = build_card_days(api_data)
            hero_idx = 1 if len(card_days) > 1 else 0  # hero = tomorrow
            if card_days:
                card_path = build_card(
                    card_days, hero_idx=hero_idx, out_path="card.png",
                    footer_stamp=datetime.now().strftime('%d.%m.%Y %H:%M'))
                print(f"\n🖼️ Card rendered: {card_path}")
                caption = format_card_caption(card_days[hero_idx])
                if send_telegram_photo(bot_token, chat_id, card_path, caption):
                    print("✅ Daily report completed successfully (photo)!")
                    sys.exit(0)
                print("⚠️ Photo send failed — falling back to the text message.")
        except Exception as e:
            print(f"⚠️ Card failed ({e}) — falling back to the text message.")

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
