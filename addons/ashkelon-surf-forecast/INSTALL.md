#!/bin/bash

# Quick Setup Guide for Ashkelon Surf Forecast Home Assistant Addon

echo "🌊 Ashkelon Surf Forecast - Home Assistant Addon Setup"
echo "======================================================"
echo ""

echo "📋 Prerequisites:"
echo "✅ Home Assistant OS/Supervised installation"
echo "✅ Add-ons feature enabled"
echo "✅ Internet connection for 4surfers.co.il"
echo ""

echo "📥 Installation Options:"
echo ""
echo "1️⃣ Home Assistant Add-on Store (Recommended):"
echo "   • Go to Settings > Add-ons > Add-on Store"
echo "   • Click ⋮ menu > Repositories"
echo "   • Add: https://github.com/avielj/ashkelon-surf-report"
echo "   • Find 'Ashkelon Surf Forecast' and install"
echo ""

echo "2️⃣ Manual Installation:"
echo "   • Copy this folder to: /usr/share/hassio/addons/"
echo "   • Restart Home Assistant"
echo "   • Install from 'Local Add-ons' section"
echo ""

echo "⚙️  Basic Configuration:"
echo "   update_interval: 3600    # 1 hour (300-86400 seconds)"
echo "   timezone: 'Asia/Jerusalem'"
echo "   show_hebrew: true"
echo "   show_chart: true"
echo ""

echo "🌐 Access after installation:"
echo "   Web Interface: http://[your-ha-ip]:8099"
echo "   API Endpoint:  http://[your-ha-ip]:8099/api/forecast"
echo ""

echo "📱 Add to Dashboard:"
echo "   type: iframe"
echo "   url: http://192.168.1.100:8099"
echo "   title: Ashkelon Surf Forecast"
echo "   aspect_ratio: 70%"
echo ""

echo "🔧 Troubleshooting:"
echo "   • Check addon logs in Home Assistant"
echo "   • Verify port 8099 is not in use"
echo "   • Ensure internet access to 4surfers.co.il"
echo "   • Try increasing update_interval if rate limited"
echo ""

echo "🏄‍♂️ Ready to surf! Check the waves and enjoy! 🌊"