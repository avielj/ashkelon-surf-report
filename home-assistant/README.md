# Ashkelon Surf Forecast for Home Assistant 🏄‍♂️🌊

Simple Home Assistant custom sensor that shows surf conditions for Ashkelon beach using the same API as the Scriptable widget.

## ✨ Features

- **3 Sensors**: Today, Tomorrow, Day After Tomorrow
- **Real-time Data**: From 4surfers.co.il API
- **Wave Heights**: Displayed in feet (ft)
- **Hebrew Support**: Wave descriptions in Hebrew
- **Auto-refresh**: Updates every 30 minutes
- **Time-specific Data**: Morning (06:00), Noon (12:00), Evening (18:00)

## 📦 Quick Installation

### Method 1: Manual Installation (Easiest)

1. **Create custom component directory:**
   ```bash
   mkdir -p /config/custom_components/ashkelon_surf
   ```

2. **Copy the sensor file:**
   ```bash
   cp ashkelon_surf_sensor.py /config/custom_components/ashkelon_surf/sensor.py
   ```

3. **Create manifest file:**
   ```bash
   cat > /config/custom_components/ashkelon_surf/manifest.json << 'EOF'
   {
     "domain": "ashkelon_surf",
     "name": "Ashkelon Surf Forecast",
     "documentation": "https://github.com/avielj/ashkelon-surf-report",
     "requirements": [],
     "codeowners": [],
     "version": "1.0.0",
     "iot_class": "cloud_polling"
   }
   EOF
   ```

4. **Add to configuration.yaml:**
   ```yaml
   sensor:
     - platform: ashkelon_surf
   ```

5. **Restart Home Assistant**

### Method 2: HACS (If you use it)

1. Add custom repository in HACS
2. Search for "Ashkelon Surf"
3. Install
4. Add to configuration.yaml
5. Restart

## 📊 Available Sensors

After installation, you'll have 3 sensors:

| Sensor | Entity ID | Description |
|--------|-----------|-------------|
| **Ashkelon Surf Today** | `sensor.ashkelon_surf_today` | Today's forecast |
| **Ashkelon Surf Tomorrow** | `sensor.ashkelon_surf_tomorrow` | Tomorrow's forecast |
| **Ashkelon Surf Day After** | `sensor.ashkelon_surf_day_after` | Day after tomorrow |

### Sensor State
- **Value**: Average wave height in feet (ft)
- **Example**: `2.3` (2.3 feet)

### Sensor Attributes

Each sensor has these attributes:

```yaml
morning_height_ft: 1.3        # Morning wave height
noon_height_ft: 2.0           # Noon wave height  
evening_height_ft: 2.3        # Evening wave height
morning_hebrew: "קרסול"       # Hebrew description
noon_hebrew: "ברך"            # Hebrew description
evening_hebrew: "ברך"         # Hebrew description
morning_time: "06:00"         # Time slot
noon_time: "12:00"            # Time slot
evening_time: "18:00"         # Time slot
surf_quality: "Fair"          # Overall quality
surf_quality_hebrew: "בסדר"  # Hebrew quality
forecast_date: "2025-10-20"   # Date
beach: "Ashkelon"             # Beach name
beach_hebrew: "אשקלון"        # Hebrew beach name
```

## 🎨 Lovelace Card Examples

### Simple Entity Card

```yaml
type: entity
entity: sensor.ashkelon_surf_today
name: Ashkelon Surf Today
icon: mdi:surfing
```

### Detailed Card with Multiple Days

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # 🌊 Ashkelon Surf Forecast
      
  - type: entities
    entities:
      - entity: sensor.ashkelon_surf_today
        name: Today
        secondary_info: attribute
        attribute: surf_quality
        icon: mdi:waves
      - entity: sensor.ashkelon_surf_tomorrow
        name: Tomorrow
        secondary_info: attribute
        attribute: surf_quality
        icon: mdi:waves
      - entity: sensor.ashkelon_surf_day_after
        name: Day After
        secondary_info: attribute
        attribute: surf_quality
        icon: mdi:waves
```

### Beautiful Card with Time Breakdown

```yaml
type: custom:mushroom-chips-card
chips:
  - type: template
    entity: sensor.ashkelon_surf_today
    content: "🌊 {{ states('sensor.ashkelon_surf_today') }}ft"
    icon: mdi:surfing
    tap_action:
      action: more-info
  - type: template
    entity: sensor.ashkelon_surf_today
    content: "Morning: {{ state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') }}ft"
  - type: template
    entity: sensor.ashkelon_surf_today
    content: "Noon: {{ state_attr('sensor.ashkelon_surf_today', 'noon_height_ft') }}ft"
  - type: template
    entity: sensor.ashkelon_surf_today
    content: "Evening: {{ state_attr('sensor.ashkelon_surf_today', 'evening_height_ft') }}ft"
```

### Gauge Card (Visual)

```yaml
type: gauge
entity: sensor.ashkelon_surf_today
name: Wave Height Today
unit: ft
min: 0
max: 10
severity:
  green: 0
  yellow: 3
  red: 6
```

### Grid Card with Hebrew

```yaml
type: grid
columns: 3
square: false
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.ashkelon_surf_today
    name: היום
    icon: mdi:waves
    primary_info: state
    secondary_info: attribute
    attribute: surf_quality_hebrew
  - type: custom:mushroom-entity-card
    entity: sensor.ashkelon_surf_tomorrow
    name: מחר
    icon: mdi:surfing
    primary_info: state
    secondary_info: attribute
    attribute: surf_quality_hebrew
  - type: custom:mushroom-entity-card
    entity: sensor.ashkelon_surf_day_after
    name: מחרתיים
    icon: mdi:water
    primary_info: state
    secondary_info: attribute
    attribute: surf_quality_hebrew
```

## 🤖 Automation Examples

### Morning Surf Alert

```yaml
automation:
  - alias: "Good Surf Alert Morning"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.ashkelon_surf_today
        above: 2.6  # Good conditions (above 2.6ft)
    action:
      - service: notify.mobile_app
        data:
          title: "🏄‍♂️ Good Surf Conditions!"
          message: >
            Waves are {{ states('sensor.ashkelon_surf_today') }}ft today!
            Morning: {{ state_attr('sensor.ashkelon_surf_today', 'morning_hebrew') }}
            Perfect for surfing! 🌊
```

### Tomorrow's Forecast Notification

```yaml
automation:
  - alias: "Tomorrow Surf Forecast"
    trigger:
      - platform: time
        at: "20:00:00"  # 8 PM
    action:
      - service: notify.mobile_app
        data:
          title: "🌊 Tomorrow's Surf Forecast"
          message: >
            Ashkelon: {{ states('sensor.ashkelon_surf_tomorrow') }}ft
            Quality: {{ state_attr('sensor.ashkelon_surf_tomorrow', 'surf_quality') }}
            Morning: {{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') }}ft
            Noon: {{ state_attr('sensor.ashkelon_surf_tomorrow', 'noon_height_ft') }}ft
            Evening: {{ state_attr('sensor.ashkelon_surf_tomorrow', 'evening_height_ft') }}ft
```

### Best Surf Day Alert (3-day scan)

```yaml
automation:
  - alias: "Best Surf Day This Week"
    trigger:
      - platform: state
        entity_id:
          - sensor.ashkelon_surf_today
          - sensor.ashkelon_surf_tomorrow
          - sensor.ashkelon_surf_day_after
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Surf Forecast Update"
          message: >
            {% set today = states('sensor.ashkelon_surf_today') | float %}
            {% set tomorrow = states('sensor.ashkelon_surf_tomorrow') | float %}
            {% set day_after = states('sensor.ashkelon_surf_day_after') | float %}
            {% if today >= tomorrow and today >= day_after %}
              Best day: TODAY ({{ today }}ft) 🎉
            {% elif tomorrow >= today and tomorrow >= day_after %}
              Best day: TOMORROW ({{ tomorrow }}ft) 🌊
            {% else %}
              Best day: DAY AFTER ({{ day_after }}ft) 🏄‍♂️
            {% endif %}
```

## 📱 iOS Companion

This sensor works great alongside the iOS Scriptable widget! You can:

1. Use the **Scriptable widget** on your iPhone home screen for quick glances
2. Use **Home Assistant** for automations, notifications, and detailed tracking
3. Ask **Siri** using the Siri Shortcut script

All three use the same API and data format! 🎯

## 🔧 Customization

### Change Update Frequency

Edit `SCAN_INTERVAL` in the sensor file:

```python
SCAN_INTERVAL = timedelta(minutes=15)  # Update every 15 minutes
```

### Change Beach

To monitor a different beach, change `BEACH_AREA_ID`:

```python
BEACH_AREA_ID = "60"  # Tel Aviv
# Other options: 50 (Netanya), 30 (Haifa), 80 (Ashkelon)
```

### Use Meters Instead of Feet

In the `meters_to_feet` function, change:

```python
def meters_to_feet(m):
    if m is None:
        return None
    return round(m, 1)  # Just return meters as-is
```

And change `unit_of_measurement`:

```python
@property
def unit_of_measurement(self):
    return "m"  # meters
```

## 🐛 Troubleshooting

### Sensors not appearing

1. Check Home Assistant logs: Settings → System → Logs
2. Make sure files are in `/config/custom_components/ashkelon_surf/`
3. Verify `configuration.yaml` has the sensor platform entry
4. Restart Home Assistant

### "Unavailable" State

- Check your internet connection
- API might be temporarily down
- Check logs for error messages

### Wrong Data

- Wait 30 minutes for next update
- Restart Home Assistant to force immediate update
- Check if 4surfers.co.il website is accessible

## 📚 Related Files

- **Scriptable Widget**: `COMPLETE_SCRIPTABLE_WIDGET.js` - iOS home screen widget
- **Siri Integration**: `SIRI_SHORTCUT.js` - Voice commands with Siri
- **Setup Guide**: `SIRI_SETUP_GUIDE.md` - How to set up Siri shortcuts

## 🎉 That's It!

You now have surf forecast data directly in Home Assistant. Create beautiful dashboards, set up smart automations, and never miss good surf conditions again! 🏄‍♂️

---

**Questions?** Check the logs or open an issue on GitHub.
**Want more features?** PRs welcome! 🌊
