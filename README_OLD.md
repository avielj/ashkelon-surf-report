# 🌊 Ashkelon Surf Forecast Widget

A beautiful, native iOS widget for surf forecasts at Ashkelon beach, Israel. Built with Scriptable and powered by real-time data from 4surfers.co.il.

## 📱 Features

- **Real-time surf data** from 4surfers.co.il API
- **72-hour forecast** (today, tomorrow, and day after)
- **4 time slots per day** (06:00, 09:00, 12:00, 18:00)
- **Hebrew surf descriptions** (קרסול, ברך, כתף, etc.)
- **Star ratings** for wave quality
- **Wave heights in feet** for easy reading
- **Wave periods** for surf planning
- **Ocean gradient design** with Aguacatec styling
- **Auto-refresh** every 30 minutes
- **Siri voice commands** in Hebrew

## 🚀 Quick Start

### iOS Widget Setup

1. Install **Scriptable** app from the App Store (free)
2. Copy the code from `COMPLETE_SCRIPTABLE_WIDGET.js`
3. Create a new script in Scriptable and paste the code
4. Add a Medium-sized Scriptable widget to your home screen
5. Configure it to run the script

📖 **Detailed instructions**: See `SCRIPTABLE_INSTALL_GUIDE.md`

### Siri Voice Commands

Ask Siri in Hebrew about surf conditions!

1. Copy the code from `SIRI_SHORTCUT.js`
2. Create a new script in Scriptable
3. Set up Shortcuts app integration

📖 **Detailed instructions**: See `SIRI_SETUP_GUIDE.md`

**Example commands:**
- "היי סירי, מה התחזית למחר?" (Hey Siri, what's the forecast tomorrow?)
- "היי סירי, מה גובה הגלים מחר?" (Hey Siri, what's the wave height tomorrow?)

## 📂 Project Structure

```
├── COMPLETE_SCRIPTABLE_WIDGET.js  # Main iOS widget
├── SIRI_SHORTCUT.js               # Siri voice command script
├── SCRIPTABLE_INSTALL_GUIDE.md    # Widget installation guide
├── SIRI_SETUP_GUIDE.md            # Siri setup guide
├── addons/                        # Home Assistant addon (optional)
│   └── ashkelon-surf-forecast/
├── requirements.txt               # Python dependencies (for HA addon)
└── README.md                      # This file
```

## 🏄‍♂️ What You'll See

The widget displays:

```
🏖️ Ashkelon                    ●

Today
⏰ 06:00  ⏰ 09:00  ⏰ 12:00  ⏰ 18:00
⭐☆☆☆☆   ⭐☆☆☆☆   ⭐⭐☆☆☆   ⭐⭐☆☆☆
🌊 1.3ft  🌊 1.5ft  🌊 1.8ft  🌊 2.0ft
קרסול     קרסול עד ברך  ברך     ברך
⏱️ 4s     ⏱️ 5s     ⏱️ 5s     ⏱️ 5s

Mon 21/10
...

Tue 22/10
...

⏰ עודכן 15:49
```

## 🔧 Configuration

### Change Beach Location

In both scripts, modify the beach ID:

```javascript
const BEACH_AREA_ID = "80" // Ashkelon
```

**Other beaches:**
- Tel Aviv: `"60"`
- Netanya: `"50"`
- Haifa: `"30"`

### Change Refresh Interval

```javascript
const REFRESH_INTERVAL = 30 // minutes
```

### Change Time Slots

```javascript
const times = [
  { hour: 6, label: "06:00" },
  { hour: 9, label: "09:00" },
  { hour: 12, label: "12:00" },
  { hour: 18, label: "18:00" }
]
```

## 🎨 Design

The widget uses the **Aguacatec** design system:
- Ocean gradient background (#4f9ded → #2c5aa0)
- Clean card-based layout
- Material Design icons
- Hebrew RTL support
- Professional surf aesthetics

## 📊 Data Source

Real-time data from **4surfers.co.il** API:
- Wave heights
- Wave periods
- Hebrew surf descriptions
- Surf quality rankings
- 10-day forecasts available

## 🏠 Home Assistant Integration (Optional)

A Home Assistant addon is also available in the `addons/` directory for smart home integration.

## 📝 Alternative Deployment Guides

For advanced users who want web-based solutions:
- `RAILWAY_DEPLOY.md` - Deploy to Railway.app
- `RENDER_DEPLOY.md` - Deploy to Render.com
- `PYTHONANYWHERE_DEPLOY.md` - Deploy to PythonAnywhere

## 🤝 Contributing

Feel free to open issues or submit pull requests!

## 📄 License

MIT License - Feel free to use and modify

## 🌊 Enjoy Your Surf Sessions!

Made with ❤️ for Israeli surfers - Home Assistant Add-on Repository

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Favielj%2Fashkelon-surf-report)

Home Assistant add-on repository providing surf forecasting for Ashkelon beach with Hebrew support.

## Add-ons

This repository contains the following add-ons:

### 🌊 [Ashkelon Surf Forecast](addons/ashkelon-surf-forecast/)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield] 
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

Beautiful surf forecast display with Aguacatec-style interface, Hebrew support, and Home Assistant integration.

## Installation

1. Click the badge above or add this repository URL to your Home Assistant instance:
   ```
   https://github.com/avielj/ashkelon-surf-report
   ```

2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Find "Ashkelon Surf Forecast" and click **Install**
4. Configure and start the add-on

## Features

- 🌊 Real-time surf data from 4surfers.co.il
- 🎨 Beautiful Aguacatec-style interface 
- 🇮🇱 Hebrew language support with RTL layout
- 📊 Multi-session forecasts (morning, noon, evening)
- 🏠 Full Home Assistant integration
- 📱 Mobile-optimized widget views

## Support

- 📖 [Documentation](addons/ashkelon-surf-forecast/README.md)
- 🐛 [Issues](https://github.com/avielj/ashkelon-surf-report/issues)
- 💬 [Discussions](https://github.com/avielj/ashkelon-surf-report/discussions)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg