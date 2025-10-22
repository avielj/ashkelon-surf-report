# 🌊 Ashkelon Surf Forecast

Complete surf forecast solution for Ashkelon beach (Israel) using data from 4surfers.co.il API.

## 🚀 Three Ways to Use

### 1. 📱 iOS Scriptable Widget (Recommended)
Native iOS widget that shows real-time surf conditions on your home screen.

**File**: `COMPLETE_SCRIPTABLE_WIDGET.js`

**Features**:
- ✅ No server needed - runs directly on your iPhone
- ✅ 3 days forecast (Today, Tomorrow, Day 3)
- ✅ 4 time slots per day (06:00, 09:00, 12:00, 18:00)
- ✅ Wave heights in feet
- ✅ Hebrew wave descriptions (קרסול, ברך, כתף)
- ✅ Star ratings (⭐) based on conditions
- ✅ Auto-refresh every 30 minutes
- ✅ Beautiful ocean gradient design

**Installation**: Copy the script to Scriptable app, add widget to home screen.

---

### 2. 🎤 Siri Voice Commands
Ask Siri about surf conditions in Hebrew!

**File**: `SIRI_SHORTCUT.js`  
**Guide**: `SIRI_SETUP_GUIDE.md`

**Example Commands**:
- "היי סירי, מה התחזית למחר?" (Hey Siri, what's the forecast tomorrow?)
- "היי סירי, מה גובה הגלים היום?" (Hey Siri, what's the wave height today?)

**Siri Response** (in Hebrew):
```
מחר באשקלון, 
בבוקר הגלים קרסול, גובה 1.3 רגל. 
בצהריים הגלים ברך, גובה 2.0 רגל. 
בערב הגלים ברך, גובה 2.3 רגל. 
ממוצע גובה הגלים 1.9 רגל.
תנאים בסדר לגלישה.
```

---

### 3. 🏠 Home Assistant Integration
Custom sensor for Home Assistant with automations and notifications.

**Folder**: `home-assistant/`  
**Guide**: `home-assistant/README.md`

**Features**:
- ✅ 3 sensors (Today, Tomorrow, Day After)
- ✅ Wave heights in feet
- ✅ Hebrew descriptions
- ✅ Auto-refresh every 30 minutes
- ✅ Lovelace card examples
- ✅ Automation templates
- ✅ Morning surf alerts

**Quick Install**:
```bash
# Copy files to Home Assistant
cp -r home-assistant /config/custom_components/ashkelon_surf

# Add to configuration.yaml
echo "sensor:\n  - platform: ashkelon_surf" >> /config/configuration.yaml

# Restart Home Assistant
```

---

### 4. 🤖 Automated Daily Telegram Notifications
Get daily surf reports delivered to your Telegram at 7 AM (GMT+2).

**File**: `daily_surf_report.py`  
**Workflow**: `.github/workflows/daily-surf-report.yml`

**Features**:
- ✅ Runs automatically every day at 7:00 AM (Israel time)
- ✅ Checks next 72 hours for surfable waves
- ✅ Sends Hebrew message to Telegram channel/chat
- ✅ Smart messages:
  - If **no waves** (< 1ft): "אין גלים בימים הקרובים 🏖️"
  - If **waves present**: Full 3-day forecast with times, heights, descriptions

**Example Message** (when there are waves):
```
🏄‍♂️ תחזית גלים - אשקלון 🌊

📅 רביעי 22/10
  🕐 06:00: ⭐⭐ 2.3ft (ברך) ⏱️ 7s 💨 12kts
  🕐 09:00: ⭐⭐ 2.5ft (ברך) ⏱️ 8s 💨 10kts
  🕐 12:00: ⭐⭐⭐ 3.1ft (כתף) ⏱️ 9s 💨 8kts
  🕐 18:00: ⭐⭐ 2.8ft (ברך) ⏱️ 8s 💨 9kts

📅 חמישי 23/10
  🕐 06:00: ⭐⭐ 2.1ft (ברך) ⏱️ 7s 💨 11kts
  ...

📊 מקור: 4surfers.co.il
```

**Setup** (GitHub Actions):
1. Fork this repository
2. Add GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (from @BotFather)
   - `TELEGRAM_CHAT_ID` - Your chat/channel ID (use @userinfobot)
3. Enable GitHub Actions in repository settings
4. Done! Daily reports at 7 AM Israel time

**Manual Trigger**:
Go to Actions → Daily Surf Report → Run workflow

---

## 📊 Data Source

All integrations use the same official API:
- **API**: `https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast`
- **Beach ID**: `80` (Ashkelon)
- **Data**: Real-time wave heights, periods, and Hebrew descriptions
- **Update Frequency**: Every 15-30 minutes

## 🛠️ Features Across All Platforms

| Feature | iOS Widget | Siri | Home Assistant | Telegram Daily |
|---------|-----------|------|----------------|----------------|
| Wave Heights (ft) | ✅ | ✅ | ✅ | ✅ |
| Hebrew Descriptions | ✅ | ✅ | ✅ | ✅ |
| 3-Day Forecast | ✅ | ✅ | ✅ | ✅ |
| Time-specific (6/9/12/18) | ✅ | ✅ | ✅ | ✅ |
| Star Ratings | ✅ | ❌ | ❌ | ✅ |
| Wave Period (seconds) | ✅ | ❌ | ✅ | ✅ |
| Wind Speed | ✅ | ❌ | ✅ | ✅ |
| Voice Commands | ❌ | ✅ | ❌ | ❌ |
| Automations | ❌ | ❌ | ✅ | ✅ |
| Notifications | ❌ | ✅ | ✅ | ✅ |
| No Server Needed | ✅ | ✅ | ❌ | ❌ |
| Runs Automatically | ✅ | ❌ | ✅ | ✅ |

## 📁 Project Structure

```
├── COMPLETE_SCRIPTABLE_WIDGET.js    # iOS widget script
├── SIRI_SHORTCUT.js                 # Siri integration script
├── SIRI_SETUP_GUIDE.md             # Siri setup instructions
├── SCRIPTABLE_INSTALL_GUIDE.md     # Widget installation guide
├── daily_surf_report.py            # Automated daily Telegram reports
├── test_daily_report.py            # Test script for daily automation
├── requirements.txt                # Python dependencies
├── .github/workflows/
│   └── daily-surf-report.yml       # GitHub Actions workflow
├── home-assistant/                  # Home Assistant integration
│   ├── README.md                    # HA installation guide
│   ├── ashkelon_surf_sensor.py     # Custom sensor
│   ├── manifest.json               # Integration manifest
│   └── __init__.py                 # Init file
└── README.md                        # This file
```

## 🚀 Quick Start

### For iPhone Users:
1. Open **Scriptable** app
2. Create new script → paste `COMPLETE_SCRIPTABLE_WIDGET.js`
3. Add widget to home screen
4. Done! 🎉

### For Siri:
1. Install Scriptable script (`SIRI_SHORTCUT.js`)
2. Create Shortcuts automation
3. Add to Siri with Hebrew phrase
4. Say: "היי סירי, מה התחזית למחר?"

### For Home Assistant:
1. Copy files to `/config/custom_components/ashkelon_surf/`
2. Add to `configuration.yaml`
3. Restart Home Assistant
4. Add Lovelace cards

### For Telegram Automation:
1. Fork this repository on GitHub
2. Get Telegram bot token:
   - Message @BotFather on Telegram
   - Create new bot with `/newbot`
   - Copy the token
3. Get your chat/channel ID:
   - For personal: Message @userinfobot, send `/start`
   - For channel: Add bot as admin, forward message to @userinfobot
4. Add GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add `TELEGRAM_BOT_TOKEN` with your bot token
   - Add `TELEGRAM_CHAT_ID` with your chat ID
5. Enable GitHub Actions (Settings → Actions → General)
6. Done! Daily reports at 7 AM Israel time 🤖

## 🌊 Wave Height Reference

| Hebrew | English | Height (ft) | Height (m) |
|--------|---------|-------------|------------|
| פלטה | Flat | 0-0.3 | 0-0.1 |
| שטוח | Flat | 0.3-0.7 | 0.1-0.2 |
| קרסול | Ankle | 0.7-1.3 | 0.2-0.4 |
| קרסול עד ברך | Ankle to Knee | 1.3-2.0 | 0.4-0.6 |
| ברך | Knee | 2.0-3.0 | 0.6-0.9 |
| מעל ברך | Above Knee | 3.0-3.9 | 0.9-1.2 |
| כתף | Shoulder | 3.9-4.9 | 1.2-1.5 |
| מעל כתף | Above Shoulder | 4.9-5.9 | 1.5-1.8 |
| מותן | Waist | 5.9-7.2 | 1.8-2.2 |
| ראש | Head | 7.2-9.2 | 2.2-2.8 |
| מעל ראש | Overhead | 9.2+ | 2.8+ |

## 🔧 Customization

### Change Beach:
All files use `beachAreaId: "80"` for Ashkelon. Change to:
- **60** - Tel Aviv
- **50** - Netanya  
- **30** - Haifa

### Change Units:
Edit the conversion factor `* 3.28084` to use meters instead of feet.

### Change Times:
Modify the time array in each script:
```javascript
const times = [
  { hour: 6, label: "06:00" },
  { hour: 9, label: "09:00" },
  { hour: 12, label: "12:00" },
  { hour: 18, label: "18:00" }
]
```

## 🐛 Troubleshooting

### iOS Widget shows error:
- Check internet connection
- Verify Scriptable has network permissions
- API might be temporarily down

### Siri doesn't respond:
- Make sure Hebrew is enabled in Siri settings
- Re-record the phrase
- Check Scriptable script is saved correctly

### Home Assistant sensors unavailable:
- Check Home Assistant logs
- Verify files are in correct directory
- Restart Home Assistant

## 🎯 Why This Project?

Created to provide Israeli surfers with easy access to Ashkelon surf conditions across multiple platforms:
- **iPhone users** → Widget on home screen
- **Smart home users** → Home Assistant automations
- **Voice users** → Siri commands
- **All platforms** → Same reliable data from 4surfers.co.il

## 🏄‍♂️ Contributing

PRs welcome! Ideas:
- [ ] Apple Watch complication
- [ ] Android widget
- [ ] More Israeli beaches
- [ ] Wind conditions
- [ ] Tide information
- [ ] Best time to surf predictor

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Data from [4surfers.co.il](https://4surfers.co.il)
- Built with love for the Israeli surf community 🇮🇱🌊

---

**Made with 🌊 for surfers in Ashkelon**
