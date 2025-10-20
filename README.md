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

## 📊 Data Source

All integrations use the same official API:
- **API**: `https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast`
- **Beach ID**: `80` (Ashkelon)
- **Data**: Real-time wave heights, periods, and Hebrew descriptions
- **Update Frequency**: Every 15-30 minutes

## 🛠️ Features Across All Platforms

| Feature | iOS Widget | Siri | Home Assistant |
|---------|-----------|------|----------------|
| Wave Heights (ft) | ✅ | ✅ | ✅ |
| Hebrew Descriptions | ✅ | ✅ | ✅ |
| 3-Day Forecast | ✅ | ✅ | ✅ |
| Time-specific (6/9/12/18) | ✅ | ✅ | ✅ |
| Star Ratings | ✅ | ❌ | ❌ |
| Voice Commands | ❌ | ✅ | ❌ |
| Automations | ❌ | ❌ | ✅ |
| Notifications | ❌ | ✅ | ✅ |

## 📁 Project Structure

```
├── COMPLETE_SCRIPTABLE_WIDGET.js    # iOS widget script
├── SIRI_SHORTCUT.js                 # Siri integration script
├── SIRI_SETUP_GUIDE.md             # Siri setup instructions
├── SCRIPTABLE_INSTALL_GUIDE.md     # Widget installation guide
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
