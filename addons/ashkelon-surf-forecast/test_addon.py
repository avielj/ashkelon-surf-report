#!/usr/bin/env python3
"""
Test script for Ashkelon Surf Forecast Home Assistant Addon
Tests the web server functionality locally
"""

import os
import sys
import time
import threading
import requests
from datetime import datetime

# Add the addon directory to path
sys.path.insert(0, '/Users/avielj/Library/Mobile Documents/com~apple~CloudDocs/Surfers/homeassistant-addon/ashkelon-surf-forecast')

def test_addon_locally():
    """Test the addon functionality locally"""
    
    print("🧪 Testing Ashkelon Surf Forecast Home Assistant Addon")
    print("=" * 60)
    
    # Set environment variables for testing
    os.environ['UPDATE_INTERVAL'] = '60'  # 1 minute for testing
    os.environ['SHOW_HEBREW'] = 'true'
    os.environ['SHOW_CHART'] = 'true'
    
    try:
        # Import and start the web server in a separate thread
        print("📡 Starting web server...")
        
        import web_server
        
        # Start server in background thread
        server_thread = threading.Thread(
            target=lambda: web_server.app.run(host='127.0.0.1', port=8099, debug=False),
            daemon=True
        )
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        print("✅ Web server started on http://127.0.0.1:8099")
        
        # Test API endpoints
        print("\n🔍 Testing API endpoints...")
        
        # Test health endpoint
        try:
            response = requests.get('http://127.0.0.1:8099/health', timeout=10)
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
        
        # Test status endpoint
        try:
            response = requests.get('http://127.0.0.1:8099/api/status', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Status endpoint working")
                print(f"   Config: {data.get('config', {})}")
                print(f"   Data Available: {data.get('data_available', False)}")
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Status endpoint error: {e}")
        
        # Test main page
        try:
            response = requests.get('http://127.0.0.1:8099/', timeout=15)
            if response.status_code == 200:
                print("✅ Main page loading")
                print(f"   Content length: {len(response.content)} bytes")
            else:
                print(f"❌ Main page failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Main page error: {e}")
        
        # Wait for forecast data to load
        print("\n⏳ Waiting for forecast data to load (this may take a minute)...")
        
        for attempt in range(6):  # Wait up to 30 seconds
            try:
                response = requests.get('http://127.0.0.1:8099/api/forecast', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and data['data'].get('daily_forecasts'):
                        print("✅ Forecast data loaded successfully!")
                        forecast_count = len(data['data']['daily_forecasts'])
                        print(f"   Found {forecast_count} days of forecast data")
                        
                        # Show sample data
                        sample_day = list(data['data']['daily_forecasts'].keys())[0]
                        sample_data = data['data']['daily_forecasts'][sample_day]
                        print(f"   Sample day: {sample_day} ({sample_data.get('hebrew_day', 'N/A')})")
                        break
                    else:
                        print(f"   Attempt {attempt + 1}/6: No forecast data yet...")
                        time.sleep(5)
                else:
                    print(f"❌ Forecast endpoint failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"   Attempt {attempt + 1}/6: {e}")
                time.sleep(5)
        else:
            print("⚠️  Forecast data not loaded within timeout period")
        
        print("\n🎉 Test completed! Visit http://127.0.0.1:8099 to see the interface")
        print("   Press Ctrl+C to stop the server")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_addon_locally()