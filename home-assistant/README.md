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

1. **Copy the entire folder to Home Assistant:**
   ```bash
   # From the project directory
   cp -r home-assistant /config/custom_components/ashkelon_surf
   ```

   **Or manually create the files:**
   ```bash
   mkdir -p /config/custom_components/ashkelon_surf
   cp home-assistant/__init__.py /config/custom_components/ashkelon_surf/
   cp home-assistant/sensor.py /config/custom_components/ashkelon_surf/
   cp home-assistant/manifest.json /config/custom_components/ashkelon_surf/
   ```

2. **Verify the file structure:**
   ```
   /config/custom_components/ashkelon_surf/
   ├── __init__.py
   ├── sensor.py
   └── manifest.json
   ```

3. **Add to configuration.yaml:**
   ```yaml
   sensor:
     - platform: ashkelon_surf
   ```

4. **Restart Home Assistant completely** (not just reload, full restart!)

5. **Check logs** at Settings → System → Logs for any errors

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

### Sensors Showing "Unavailable"

This is the most common issue. Here's how to fix it:

1. **Check the logs immediately:**
   - Go to Settings → System → Logs
   - Look for errors mentioning "ashkelon_surf" or "4surfers"
   - Common errors and fixes:

2. **Common Issues:**

   **Problem: "async_timeout" error**
   - **Cause**: You're using Home Assistant 2022.9 or newer
   - **Fix**: ✅ Already fixed in latest version (uses `asyncio.timeout`)
   
   **Problem: "API returned status 403" or "Connection refused"**
   - **Cause**: Missing proper browser headers
   - **Fix**: ✅ Already fixed in latest version (uses full browser-like headers)
   - **If still failing**: Make sure you have the latest version from GitHub
     ```bash
     cd /config/custom_components
     rm -rf ashkelon_surf
     # Re-download latest version
     ```
   
   **Problem: "No forecast data in API response"**
   - **Cause**: API changed format or is returning errors
   - **Fix**: Check logs for full error, API might be temporarily down
   
   **Problem: Sensors exist but state is "unknown" or "unavailable"**
   - **Cause**: First update hasn't completed yet, or API is failing
   - **Fix**: 
     1. Wait 5-10 minutes for first update
     2. Check Developer Tools → States to see sensor attributes
     3. Manually trigger update: Developer Tools → Services → `homeassistant.update_entity` with entity_id: `sensor.ashkelon_surf_today`

3. **Force a sensor update:**
   ```yaml
   service: homeassistant.update_entity
   target:
     entity_id: sensor.ashkelon_surf_today
   ```

4. **Test the API manually:**
   ```bash
   curl -X POST https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast \
     -H "Content-Type: application/json" \
     -d '{"beachAreaId":"80"}'
   ```
   Should return JSON with forecast data.

5. **Enable debug logging:**
   Add to `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.ashkelon_surf: debug
   ```
   Then restart and check logs for detailed debug info.

### Sensors Not Appearing at All

1. **Verify file structure:**
   ```bash
   ls -la /config/custom_components/ashkelon_surf/
   ```
   Should show: `__init__.py`, `sensor.py`, `manifest.json`

2. **Check configuration.yaml:**
   ```yaml
   sensor:
     - platform: ashkelon_surf
   ```
   Make sure it's properly indented (2 spaces)

3. **Do a FULL restart** (not just reload):
   - Settings → System → Restart Home Assistant
   - Or: `ha core restart` from CLI

4. **Check if integration loads:**
   - Settings → Devices & Services
   - Look for any error messages about custom components

### Wrong Data or Old Data

- **Wait 30 minutes** for next automatic update
- **Force update** using Developer Tools → Services → `homeassistant.update_entity`
- **Check API directly** with curl command above
- **Verify update interval:** Default is 30 min, you can change in sensor.py

### ⚠️ Important Notes

- **First update takes ~30 seconds** after HA restart
- **Sensors won't update** if API is unreachable
- **Check your HA version**: Requires Home Assistant 2022.9+
- **Internet required**: Sensors fetch data from 4surfers.co.il

## 📚 Related Files

- **Scriptable Widget**: `COMPLETE_SCRIPTABLE_WIDGET.js` - iOS home screen widget
- **Siri Integration**: `SIRI_SHORTCUT.js` - Voice commands with Siri
- **Setup Guide**: `SIRI_SETUP_GUIDE.md` - How to set up Siri shortcuts

## 🎉 That's It!

You now have surf forecast data directly in Home Assistant. Create beautiful dashboards, set up smart automations, and never miss good surf conditions again! 🏄‍♂️

---

**Questions?** Check the logs or open an issue on GitHub.
**Want more features?** PRs welcome! 🌊
