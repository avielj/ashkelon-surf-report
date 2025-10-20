# Home Assistant Add-on Repository: Ashkelon Surf Forecast

![Ashkelon Surf Forecast](https://raw.githubusercontent.com/avielj/ashkelon-surf-report/main/.github/assets/addon-banner.png)

## Add-ons

This repository contains the following add-ons:

### [🌊 Ashkelon Surf Forecast](./ashkelon-surf-forecast)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

Beautiful Home Assistant add-on that displays surf forecast for Ashkelon beach from 4surfers.co.il with Hebrew support.

## Installation

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Favielj%2Fashkelon-surf-report)

1. Click the badge above, or manually add the repository URL to your Home Assistant instance:
   ```
   https://github.com/avielj/ashkelon-surf-report
   ```

2. Go to **Settings** > **Add-ons** > **Add-on Store**
3. Find "Ashkelon Surf Forecast" and click **Install**
4. Configure the add-on and click **Start**

## Features

- 🌊 **Real-time Surf Data** - Live data from 4surfers.co.il API
- 📱 **Beautiful Interface** - Responsive design with Hebrew support  
- ⏰ **Auto Updates** - Configurable update intervals
- 🏄‍♂️ **Hebrew Integration** - Full RTL layout and surf terminology
- 📊 **7-Day Forecast** - Morning, noon, and evening sessions
- 🎨 **Ocean Theme** - Surf-inspired design and animations

## Usage

After installation, access the forecast at: `http://[your-ha-ip]:8099`

Add to your dashboard using an iframe card:

```yaml
type: iframe
url: http://192.168.1.100:8099
title: Ashkelon Surf Forecast
aspect_ratio: 70%
```

## Support

- 📖 [Documentation](https://github.com/avielj/ashkelon-surf-report)
- 🐛 [Issue Tracker](https://github.com/avielj/ashkelon-surf-report/issues)
- 💬 [Discussions](https://github.com/avielj/ashkelon-surf-report/discussions)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg