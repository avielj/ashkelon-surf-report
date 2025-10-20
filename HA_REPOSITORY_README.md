# 🌊 Ashkelon Surf Forecast - Home Assistant Add-on Repository

![Home Assistant Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-blue?logo=homeassistant)
![Version](https://img.shields.io/badge/version-2.0.0-green)
![Hebrew Support](https://img.shields.io/badge/Hebrew-RTL%20Support-orange)

Beautiful Home Assistant add-on repository providing Ashkelon surf forecast with Aguacatec-style interface and Hebrew support.

## 🏄‍♂️ Add-ons in this Repository

### [🌊 Ashkelon Surf Forecast](./ashkelon-surf-forecast/)

![Supports aarch64][aarch64-shield]
![Supports amd64][amd64-shield]
![Supports armhf][armhf-shield]
![Supports armv7][armv7-shield]
![Supports i386][armv7-shield]

Beautiful surf forecast display for Ashkelon beach with:
- 🎨 **Aguacatec-inspired design** with ocean gradients
- 🇮🇱 **Hebrew RTL interface** with surf terminology
- 📊 **Multiple daily sessions** (morning, noon, evening)
- 🏠 **Full HA integration** with sensors and panels
- 📱 **Mobile-optimized** widget views

## 🚀 Installation

### One-Click Installation

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Favielj%2Fashkelon-surf-report)

### Manual Installation

1. **Add Repository**: In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. **Click Menu** (⋮) → **Repositories** 
3. **Add URL**: `https://github.com/avielj/ashkelon-surf-report`
4. **Install**: Find "Ashkelon Surf Forecast" and click **Install**
5. **Configure**: Set your preferences and click **Start**

## ✨ Features

- 🌊 **Real-time surf data** from 4surfers.co.il
- 🎨 **Beautiful Aguacatec design** with ocean themes
- 🇮🇱 **Hebrew surf terminology** - קרסול, ברך, כתף, מעל ראש
- 📊 **Multi-session forecasts** for morning, noon, evening
- 🏠 **HA panel integration** with sidebar menu
- 📱 **Widget API** for iOS Shortcuts and custom integrations
- ⚙️ **RESTful sensors** for automation and dashboards

## 📱 Usage

### Web Interface
Access your surf forecast at: `http://[your-ha-ip]:8099`

### Dashboard Integration
Add to your Lovelace dashboard:

```yaml
type: iframe
url: "http://localhost:8099/widget"
title: "🌊 Ashkelon Surf"
aspect_ratio: "16:9"
```

### Sensor Integration
Add to `configuration.yaml`:

```yaml
sensor:
  - platform: rest
    resource: "http://localhost:8099/api/ha-sensor"
    name: "Ashkelon Surf Forecast"
    value_template: "{{ value_json.state }}"
    json_attributes_path: "attributes"
    json_attributes:
      - max_wave_height
      - max_wave_height_hebrew
      - hebrew_day
      - forecast_date
    scan_interval: 1800
```

## 🌊 Hebrew Surf Quality Levels

The addon displays Hebrew surf conditions:
- **פלטה** (flat) - 0-0.1m
- **קרסול** (ankle) - 0.2-0.4m  
- **ברך** (knee) - 0.7-0.9m
- **כתף** (shoulder) - 1.3-1.5m
- **מעל ראש** (overhead) - 3.0m+

## 🔌 API Endpoints

- **`/`** - Main Aguacatec-style interface
- **`/widget`** - Compact mobile widget
- **`/api/widget`** - JSON API for iOS Shortcuts
- **`/api/ha-sensor`** - Home Assistant sensor format
- **`/health`** - Health monitoring

## 🛠️ Development & Support

### Alternative Deployment Options
This repository also includes standalone deployment options:

- **[Vercel Deployment](./standalone-widget/)** - Serverless web service
- **[iOS Widget](./IOS_STANDALONE_WIDGET.md)** - Scriptable widget
- **[Deployment Guide](./STANDALONE_DEPLOYMENT_GUIDE.md)** - Multiple platforms

### Support
- 🐛 **Issues**: [GitHub Issues](https://github.com/avielj/ashkelon-surf-report/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/avielj/ashkelon-surf-report/discussions)
- 📖 **Documentation**: [Full addon docs](./ashkelon-surf-forecast/README.md)

## 🏄‍♀️ Acknowledgments

- **Data Source**: [4surfers.co.il](https://4surfers.co.il) - Israeli surf forecasting
- **Design Inspiration**: Aguacatec.es surf card styling
- **Community**: Israeli Home Assistant and surf communities

---

**Ready to catch some waves? Add the repository and start surfing! 🌊🏄‍♂️**

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg