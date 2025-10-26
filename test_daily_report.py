#!/usr/bin/env python3
"""Test the daily surf report script without Telegram"""

import sys
sys.path.insert(0, '.')

from daily_surf_report import (
    get_surf_forecast,
    parse_forecast_data,
    has_surfable_waves,
    format_telegram_message
)

def main():
    print("🧪 Testing Daily Surf Report\n")
    
    # Test 1: Fetch forecast
    print("1️⃣ Testing API fetch...")
    api_data = get_surf_forecast()
    if api_data:
        print(f"   ✅ Got API data")
        print(f"   Days in response: {len(api_data.get('dailyForecastList', []))}")
    else:
        print("   ❌ Failed to fetch data")
        return
    
    # Test 2: Parse forecast
    print("\n2️⃣ Testing forecast parsing...")
    forecast_days = parse_forecast_data(api_data)
    if forecast_days:
        print(f"   ✅ Parsed {len(forecast_days)} days")
        for day in forecast_days:
            print(f"   📅 {day['hebrew_day']} {day['date_display']}: {len(day['sessions'])} sessions")
    else:
        print("   ❌ No forecast days parsed")
        return
    
    # Test 3: Check for surfable waves
    print("\n3️⃣ Testing wave detection...")
    has_waves = has_surfable_waves(forecast_days)
    print(f"   Surfable waves (>2ft + 6.5s period): {'✅ Yes' if has_waves else '❌ No'}")
    
    # Show detailed session data
    print("\n   📊 Detailed session data:")
    for day in forecast_days:
        print(f"   📅 {day['hebrew_day']} {day['date_display']}:")
        for session in day['sessions']:
            meets_criteria = session['height_ft'] >= 2.0 and session['period_s'] >= 6.5
            status = "✅" if meets_criteria else "❌"
            print(f"      {status} {session['time']}: {session['height_ft']}ft, {session['period_s']}s period, {session['stars']}")
    
    # Show detailed wave analysis
    print("   📊 Session breakdown:")
    for day in forecast_days:
        print(f"      {day['hebrew_day']} {day['date_display']}:")
        for session in day['sessions']:
            height_ft = session['height_ft']
            period_s = session['period_s']
            meets_criteria = height_ft >= 2.0 and period_s >= 6.5
            status = "✅" if meets_criteria else "❌"
            print(f"         {session['time']}: {height_ft:.1f}ft, {period_s}s period {status}")
    
    # Show current conditions for context
    print("   Current conditions:")
    for day in forecast_days[:1]:  # Just first day
        for session in day['sessions'][:2]:  # Just first 2 sessions
            height = session['height_ft']
            period = session['period_s']
            print(f"     {session['time']}: {height}ft, {period}s period")
    
    # Test 4: Format message
    print("\n4️⃣ Testing message formatting...")
    message = format_telegram_message(forecast_days)
    print("   Message preview:")
    print("   " + "-" * 60)
    for line in message.split('\n')[:15]:  # First 15 lines
        print(f"   {line}")
    print("   " + "-" * 60)
    print(f"   Message length: {len(message)} chars")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    main()
