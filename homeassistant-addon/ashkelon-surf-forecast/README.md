# Ashkelon Surf Forecast - Home Assistant Addon

🌊 Beautiful Home Assistant addon displaying surf forecast for Ashkelon beach from 4surfers.co.il

## Features

- 📱 **Beautiful Web Interface** - Responsive design with Hebrew and English support
- 🌊 **Real-time Surf Data** - Fetches live data from 4surfers.co.il API
- ⏰ **Automatic Updates** - Configurable update intervals (5 minutes to 24 hours)
- 🏄‍♂️ **Hebrew Support** - Full RTL layout with Hebrew surf terminology
- 📊 **7-Day Forecast** - Shows morning, noon, and evening surf sessions
- 🎨 **Surf-themed Design** - Ocean-inspired colors and animations

## Installation

### Method 1: Home Assistant Add-on Store (Recommended)

1. In Home Assistant, go to **Supervisor** > **Add-on Store**
2. Click the menu (⋮) and select **Repositories**
3. Add this repository URL: `https://github.com/avielj/ashkelon-surf-report`
4. Find "Ashkelon Surf Forecast" in the store and click **Install**
5. Configure the addon and click **Start**

### Method 2: Manual Installation

1. Copy the `homeassistant-addon` folder to your Home Assistant addons directory
2. Restart Home Assistant
3. Go to **Supervisor** > **Add-on Store** > **Local Add-ons**
4. Install the "Ashkelon Surf Forecast" addon

## Configuration

The addon supports the following configuration options:

```yaml
update_interval: 3600    # Update interval in seconds (300-86400)
timezone: "Asia/Jerusalem"  # Timezone for display
show_hebrew: true        # Show Hebrew text and RTL layout
show_chart: true         # Enable chart generation (future feature)
```

## Usage

After installation and configuration:

1. **Start the addon** - The web server will start on port 8099
2. **Access the interface** - Navigate to `http://[your-ha-ip]:8099`
3. **Add to Home Assistant** - Use the iframe integration to embed in your dashboard

### Adding to Home Assistant Dashboard

Add an iframe card to your dashboard:

```yaml
type: iframe
url: http://192.168.1.100:8099
title: Ashkelon Surf Forecast
aspect_ratio: 70%
```

Replace `192.168.1.100` with your Home Assistant IP address.

## API Endpoints

The addon provides REST API endpoints for integration:

- **`GET /`** - Main web interface
- **`GET /api/forecast`** - JSON forecast data
- **`GET /api/status`** - Addon status and configuration
- **`GET /health`** - Health check endpoint

### Example API Response

```json
{
  "success": true,
  "last_update": "2024-01-15T12:00:00",
  "data": {
    "beach": "Ashkelon",
    "daily_forecasts": {
      "2024-01-15": {
        "hebrew_day": "שני",
        "english_day": "Monday",
        "times": {
          "06:00": {
            "wave_height": 0.7,
            "surf_quality": "ברך (knee_high)"
          }
        }
      }
    }
  }
}
```

## Home Assistant Sensors

You can create sensors to track surf conditions:

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "Ashkelon Waves Today"
    resource: "http://192.168.1.100:8099/api/forecast"
    value_template: "{{ value_json.data.daily_forecasts | list | length }}"
    json_attributes_path: "$.data"
    json_attributes:
      - daily_forecasts
      - last_update
    scan_interval: 1800  # 30 minutes
```

## Automation Examples

### Notify when good waves are coming:

```yaml
# automations.yaml
- alias: "Good Waves Alert"
  trigger:
    platform: state
    entity_id: sensor.ashkelon_waves_today
  condition:
    # Add conditions based on wave height/quality
  action:
    service: notify.mobile_app
    data:
      message: "🌊 Good waves detected at Ashkelon!"
```

## Technical Details

- **Base Image**: Python 3.11 slim
- **Web Framework**: Flask
- **Browser Automation**: Playwright with Chromium
- **Data Source**: 4surfers.co.il extended API
- **Update Mechanism**: Background threading
- **Port**: 8099
- **Supported Architectures**: amd64, aarch64, armv7, armhf, i386

## Troubleshooting

### Common Issues

1. **Addon won't start**
   - Check the logs in Home Assistant
   - Ensure port 8099 is not used by another service
   - Verify internet connectivity for 4surfers.co.il

2. **No forecast data**
   - Check if 4surfers.co.il is accessible
   - Increase update_interval if getting rate limited
   - Review addon logs for API errors

3. **Hebrew text not displaying**
   - Ensure your browser supports Hebrew fonts
   - Try refreshing the page
   - Check browser developer console for errors

### Logs

View addon logs in Home Assistant:
**Supervisor** > **Ashkelon Surf Forecast** > **Log**

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source. See the main repository for license details.

## Credits

- **Data Source**: [4surfers.co.il](https://4surfers.co.il) - Israeli surf forecast website
- **Developer**: [@avielj](https://github.com/avielj)
- **Inspired by**: The Israeli surf community

---

🏄‍♂️ **Enjoy the waves!** 🌊