<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
# Ashkelon Surf Forecast Project

Multi-platform surf forecast solution using 4surfers.co.il API for Israeli beaches, with a focus on Ashkelon.

## Project Status: ✅ COMPLETED & DEPLOYED

- ✅ iOS Scriptable widget (COMPLETE_SCRIPTABLE_WIDGET.js)
- ✅ Siri voice commands in Hebrew (SIRI_SHORTCUT.js)
- ✅ Home Assistant custom sensor integration
- ✅ All measurements in feet (not meters)
- ✅ 4 time slots per day (6, 9, 12, 18)
- ✅ 3-day forecasts across all platforms
- ✅ Hebrew descriptions (קרסול, ברך, כתף)
- ✅ API tested and verified working
- ✅ Git repository cleaned up
- ✅ Documentation complete

## Three Deployment Options

### 1. iOS Widget (Recommended)
**File**: `COMPLETE_SCRIPTABLE_WIDGET.js`
- Native iOS home screen widget
- No server needed
- Auto-refresh every 30 minutes
- Beautiful ocean gradient design
- Star ratings and Hebrew descriptions

### 2. Siri Voice Commands
**File**: `SIRI_SHORTCUT.js`
- Ask Siri in Hebrew: "מה התחזית למחר?"
- Responds with wave heights in feet
- Works with Hebrew day names
- Uses same API as widget

### 3. Home Assistant Integration
**Folder**: `home-assistant/`
- Custom sensor integration
- 3 sensors (Today, Tomorrow, Day After)
- Lovelace card examples
- Morning surf alert automations
- 30-minute refresh interval

## API Details

- **Endpoint**: `https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast`
- **Beach ID**: 80 (Ashkelon)
- **Method**: POST with `{beachAreaId: "80"}`
- **Returns**: 10 days of forecasts with waveHeight (actual breaking waves), swellHeight (ocean swell), WavePeriod, surfRankMark, surfHeightDesc
- **Important**: Use `waveHeight` field (actual wave height at beach), NOT `swellHeight` (ocean swell energy)

## Key Features

- ✅ Real-time data from 4surfers.co.il API
- ✅ Uses `waveHeight` (actual breaking waves), not `swellHeight` (ocean swell)
- ✅ Wave heights in feet (converted from meters)
- ✅ Hebrew descriptions from API
- ✅ 4 time slots: 06:00, 09:00, 12:00, 18:00
- ✅ 3-day forecasts (Today, Tomorrow, Day 3)
- ✅ Star ratings (⭐) for surf quality
- ✅ Wave periods in seconds
- ✅ Cross-platform (iOS, Siri, Home Assistant)

## Files Overview

### Active Files
- `COMPLETE_SCRIPTABLE_WIDGET.js` - iOS widget with full API integration
- `SIRI_SHORTCUT.js` - Siri voice command script
- `SCRIPTABLE_INSTALL_GUIDE.md` - Widget setup instructions
- `SIRI_SETUP_GUIDE.md` - Siri integration guide
- `home-assistant/` - HA custom sensor integration
  - `ashkelon_surf_sensor.py` - Main sensor code
  - `README.md` - HA installation guide
  - `manifest.json` - Integration metadata
  - `__init__.py` - Init file
- `README.md` - Main documentation

### Legacy Files (Optional)
- `addons/ashkelon-surf-forecast/` - Home Assistant addon (complex installation)
- `wave_forecast.py` - Original Python scraper
- Deployment guides for Railway, Render, PythonAnywhere

## Recent Changes (Latest Commit)

✅ Added Home Assistant custom sensor integration
✅ Cleaned up obsolete Vercel/API files
✅ Updated README with 3 platforms comparison
✅ All code uses feet (not meters)
✅ Consistent time slots (6,9,12,18) everywhere
✅ Pushed to GitHub (main branch)

## Current Status
All three platforms fully functional and deployed to GitHub. Users can choose iOS widget, Siri, or Home Assistant based on their needs. All use same 4surfers.co.il API with identical data structure.