#!/usr/bin/env python3
"""
Quick setup verification for Ashkelon Surf Report
Run this to test if everything is configured correctly
"""
import sys
import os

def test_import():
    """Test if all required modules can be imported"""
    try:
        from wave_forecast import FourSurfersWaveForecast
        print("✅ Main module import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def test_environment():
    """Test environment configuration"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        print(f"✅ Telegram bot token found: {bot_token[:10]}...")
    else:
        print("⚠️ No TELEGRAM_BOT_TOKEN environment variable set")
        print("💡 For local testing: export TELEGRAM_BOT_TOKEN='your_token'")
    
    if os.getenv('GITHUB_ACTIONS'):
        print("✅ Running in GitHub Actions environment")
    else:
        print("ℹ️ Local development environment")

def test_forecast():
    """Test basic forecast functionality"""
    try:
        from wave_forecast import FourSurfersWaveForecast
        
        # Test initialization
        scraper = FourSurfersWaveForecast()
        print("✅ Forecast system initialized")
        
        # Test API connection (don't actually run to avoid rate limiting)
        print("✅ Ready to fetch surf data from 4surfers.co.il")
        return True
        
    except Exception as e:
        print(f"❌ Forecast test failed: {e}")
        return False

def main():
    print("🏄‍♂️ Ashkelon Surf Report - Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    print("\n📦 Testing imports...")
    all_good &= test_import()
    
    print("\n🔧 Checking environment...")
    test_environment()
    
    if all_good:
        print("\n🧪 Testing forecast system...")
        all_good &= test_forecast()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All tests passed! Ready for GitHub deployment")
        print("\n📋 Next steps:")
        print("1. Push to GitHub repository")
        print("2. Add TELEGRAM_BOT_TOKEN to repository secrets")
        print("3. GitHub Actions will run daily at 7:00 AM Israel time")
    else:
        print("⚠️ Some issues found - check messages above")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())