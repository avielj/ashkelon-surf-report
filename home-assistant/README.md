# Ashkelon Surf Forecast for Home Assistant 🏄‍♂️🌊

Simple Home Assistant custom sensor that shows surf conditions for Ashkelon beach using the same API as the Scriptable widget.

## ✨ Features

- **3 Sensors**: Today, Tomorrow, Day After Tomorrow
- **Real-time Data**: From 4surfers.co.il API
- **Wave Heights**: Uses actual `waveHeight` (breaking waves), not `swellHeight` (ocean swell)
- **Measurements in Feet**: Displayed in feet (ft), converted from meters
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

## 🔄 Auto-Update from GitHub

Keep your integration up-to-date automatically!

### Option 1: Using Python Script (Recommended)

```bash
# Download the update script
cd /config
curl -O https://raw.githubusercontent.com/avielj/ashkelon-surf-report/main/home-assistant/update_from_github.py

# Run the update
python3 update_from_github.py

# Restart Home Assistant
ha core restart
```

### Option 2: Using Bash Script

```bash
# Download the update script
cd /config
curl -O https://raw.githubusercontent.com/avielj/ashkelon-surf-report/main/home-assistant/update_from_github.sh

# Make it executable
chmod +x update_from_github.sh

# Run the update
bash update_from_github.sh

# Restart Home Assistant
ha core restart
```

### Option 3: One-Line Update

```bash
curl -sS https://raw.githubusercontent.com/avielj/ashkelon-surf-report/main/home-assistant/update_from_github.py | python3 && ha core restart
```

**Features of auto-update:**
- ✅ Automatic backup before update
- ✅ Downloads latest version from GitHub
- ✅ Rollback on failure
- ✅ Safe and tested

### Set up Automatic Updates (Optional)

Create an automation to update weekly:

```yaml
automation:
  - alias: "Update Ashkelon Surf Sensor"
    trigger:
      - platform: time
        at: "03:00:00"  # 3 AM
    condition:
      - condition: time
        weekday:
          - sun  # Every Sunday
    action:
      - service: shell_command.update_ashkelon_surf
      - delay: "00:00:30"
      - service: homeassistant.restart
```

Add to `configuration.yaml`:
```yaml
shell_command:
  update_ashkelon_surf: "python3 /config/update_from_github.py"
```

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

**Preview:**
```
┌─────────────────────────────────┐
│ 🏄 Ashkelon Surf Today          │
│ 2.3 ft                          │
└─────────────────────────────────┘
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

**Preview:**
```
┌────────────────────────────────────┐
│ 🌊 Ashkelon Surf Forecast         │
├────────────────────────────────────┤
│ 🌊 Today             2.3ft         │
│    Fair                            │
├────────────────────────────────────┤
│ 🌊 Tomorrow          2.7ft         │
│    Good                            │
├────────────────────────────────────┤
│ 🌊 Day After         1.9ft         │
│    Fair                            │
└────────────────────────────────────┘
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

**Preview:**
```
┌────────────────────────────────────┐
│ 🌊 2.3ft                           │
│ Morning: 1.3ft                     │
│ Noon: 2.0ft                        │
│ Evening: 2.3ft                     │
└────────────────────────────────────┘
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

**Preview:**
```
┌────────────────────────────────────┐
│    Wave Height Today               │
│                                    │
│         ╭─────────╮               │
│        ╱   2.3ft   ╲              │
│       │      │      │             │
│       │      ●      │             │
│       ╰──────┴──────╯             │
│    0              10               │
│   ■■■■■□□□□□                      │
│  Green  Yellow  Red                │
└────────────────────────────────────┘
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

**Preview:**
```
┌───────────┬───────────┬───────────┐
│ 🌊 היום   │ 🏄 מחר    │ 💧 מחרתיים │
│           │           │           │
│  2.3 ft   │  2.7 ft   │  1.9 ft   │
│  טוב      │  טוב      │  בסדר     │
└───────────┴───────────┴───────────┘
```

### 🌊 iOS Widget Style Card (Recommended!)

This card replicates the iOS Scriptable widget design with 4 times per day and Hebrew descriptions:

```yaml
type: vertical-stack
cards:
  # Header
  - type: markdown
    content: >
      # 🏖️ אשקלון

      **Ashkelon Surf Forecast**
    card_mod:
      style: |
        ha-card {
          background: linear-gradient(135deg, #4f9ded 0%, #2c5aa0 100%);
          color: white;
          text-align: center;
          padding: 5px;
        }
  
  # Today
  - type: markdown
    content: "## 📅 היום (Today)"
    card_mod:
      style: |
        ha-card {
          text-align: center;
          color: #2c5aa0;
          padding: 5px;
        }
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
  
  # Tomorrow
  - type: markdown
    content: "## 📅 מחר (Tomorrow)"
    card_mod:
      style: |
        ha-card {
          text-align: center;
          color: #2c5aa0;
          padding: 5px;
        }
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
  
  # Day After
  - type: markdown
    content: "## 📅 מחרתיים (Day After)"
    card_mod:
      style: |
        ha-card {
          text-align: center;
          color: #2c5aa0;
          padding: 5px;
        }
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              background: #f5f5f5;
              padding: 10px;
            }
  
  # Footer
  - type: markdown
    content: |
      ⏰ Last updated: {{ as_timestamp(states.sensor.ashkelon_surf_today.last_updated) | timestamp_custom('%H:%M') }}
    card_mod:
      style: |
        ha-card {
          text-align: center;
          padding: 10px;
          font-size: 12px;
          color: #666;
        }
```

**Preview with card-mod:**
```
╔═══════════════════════════════════════╗
║  [Ocean Gradient Background 🌊]       ║
║      🏖️ אשקלון                        ║
║   Ashkelon Surf Forecast              ║
╚═══════════════════════════════════════╝

         📅 היום (Today)

┌────────┬────────┬────────┬────────┐
│ 06:00  │ 09:00  │ 12:00  │ 18:00  │
│        │        │        │        │
│ 1.3ft  │ 1.3ft  │ 2.0ft  │ 2.3ft  │
│ קרסול  │ קרסול  │ ברך    │ ברך    │
└────────┴────────┴────────┴────────┘

         📅 מחר (Tomorrow)

┌────────┬────────┬────────┬────────┐
│ 06:00  │ 09:00  │ 12:00  │ 18:00  │
│        │        │        │        │
│ 1.9ft  │ 1.9ft  │ 2.7ft  │ 2.9ft  │
│ ברך    │ ברך    │ ברך    │ כתף    │
└────────┴────────┴────────┴────────┘

        📅 מחרתיים (Day After)

┌────────┬────────┬────────┬────────┐
│ 06:00  │ 09:00  │ 12:00  │ 18:00  │
│        │        │        │        │
│ 2.3ft  │ 2.3ft  │ 1.9ft  │ 2.6ft  │
│קרסול עד│קרסול עד│קרסול עד│קרסול עד│
│  ברך   │  ברך   │  ברך   │  ברך   │
└────────┴────────┴────────┴────────┘

    ⏰ Last updated: 19:00
```

**Note:** This requires the `card-mod` integration. Install it via HACS if you don't have it.

**Alternative without card-mod (Simple Version):**

```yaml
type: vertical-stack
cards:
  # Header
  - type: markdown
    content: |
      # 🏖️ אשקלון
      **Ashkelon Surf Forecast**
  
  # Today
  - type: markdown
    content: "### 📅 היום (Today)"
  
  - type: horizontal-stack
    cards:
      - type: button
        entity: sensor.ashkelon_surf_today
        name: "06:00"
        icon: mdi:waves
        show_state: false
        tap_action:
          action: none
        card_mod:
          style: |
            ha-card {
              text-align: center;
            }
        hold_action:
          action: more-info
      - type: button  
        entity: sensor.ashkelon_surf_today
        name: "09:00"
        icon: mdi:waves
        show_state: false
        tap_action:
          action: none
      - type: button
        entity: sensor.ashkelon_surf_today
        name: "12:00"
        icon: mdi:surfing
        show_state: false
        tap_action:
          action: none
      - type: button
        entity: sensor.ashkelon_surf_today
        name: "18:00"
        icon: mdi:surfing
        show_state: false
        tap_action:
          action: none
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_today', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_today', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_today', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
  
  # Tomorrow
  - type: markdown
    content: "### 📅 מחר (Tomorrow)"
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_tomorrow', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_tomorrow', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_tomorrow', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
  
  # Day After
  - type: markdown
    content: "### 📅 מחרתיים (Day After)"
  
  - type: horizontal-stack
    cards:
      - type: markdown
        content: |
          **⏰ 06:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 09:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'morning_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'morning_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 12:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'noon_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'noon_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'noon_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
      - type: markdown
        content: |
          **⏰ 18:00**
          
          ## 🌊 {{ state_attr('sensor.ashkelon_surf_day_after', 'evening_height_ft') }}ft
          
          **{{ state_attr('sensor.ashkelon_surf_day_after', 'evening_hebrew') }}**
          
          {% set h = state_attr('sensor.ashkelon_surf_day_after', 'evening_height_ft') | float %}
          {% if h >= 3.0 %}⭐⭐⭐⭐⭐{% elif h >= 2.6 %}⭐⭐⭐⭐{% elif h >= 2.0 %}⭐⭐⭐{% elif h >= 1.3 %}⭐⭐{% else %}⭐{% endif %}
  
  # Footer
  - type: markdown
    content: |
      *⏰ Last updated: {{ as_timestamp(states.sensor.ashkelon_surf_today.last_updated) | timestamp_custom('%H:%M') }}*
```

**Preview (Simple version without card-mod):**
```
╔═══════════════════════════════════════╗
║ 🏖️ אשקלון                             ║
║ Ashkelon Surf Forecast                ║
╚═══════════════════════════════════════╝

           📅 היום (Today)

┌─────────┬─────────┬─────────┬─────────┐
│ ⏰ 06:00│ ⏰ 09:00│ ⏰ 12:00│ ⏰ 18:00│
│         │         │         │         │
│  1.3ft  │  1.3ft  │  2.0ft  │  2.3ft  │
│ קרסול   │ קרסול   │  ברך    │  ברך    │
└─────────┴─────────┴─────────┴─────────┘

           📅 מחר (Tomorrow)

┌─────────┬─────────┬─────────┬─────────┐
│ ⏰ 06:00│ ⏰ 09:00│ ⏰ 12:00│ ⏰ 18:00│
│         │         │         │         │
│  1.9ft  │  1.9ft  │  2.7ft  │  2.9ft  │
│  ברך    │  ברך    │  ברך    │  כתף    │
└─────────┴─────────┴─────────┴─────────┘

          📅 מחרתיים (Day After)

┌─────────┬─────────┬─────────┬─────────┐
│ ⏰ 06:00│ ⏰ 09:00│ ⏰ 12:00│ ⏰ 18:00│
│         │         │         │         │
│  2.3ft  │  2.3ft  │  1.9ft  │  2.6ft  │
│קרסול עד │קרסול עד │קרסול עד │קרסול עד │
│  ברך    │  ברך    │  ברך    │  ברך    │
└─────────┴─────────┴─────────┴─────────┘

     ⏰ Last updated: 19:00
```

**Features:**
- 🌊 Ocean gradient header (same as iOS widget)
- 📅 3 days: Today, Tomorrow, Day After
- ⏰ 4 time slots: 06:00, 09:00, 12:00, 18:00
- 🇮🇱 Hebrew wave descriptions (קרסול, ברך, כתף, etc.)
- 📏 Wave heights in feet
- 📱 Card-based responsive design
- 🎨 Clean, modern styling

**Preview:**
```
┌─────────────────────────────────────┐
│     🏖️ אשקלון                       │
│     Ashkelon Surf Forecast          │
├─────────────────────────────────────┤
│ 📅 היום (Today)                     │
│ ┌──────┬──────┬──────┬──────┐      │
│ │06:00 │09:00 │12:00 │18:00 │      │
│ │1.3ft │1.3ft │2.0ft │2.3ft │      │
│ │קרסול │קרסול │ברך   │ברך   │      │
│ └──────┴──────┴──────┴──────┘      │
│                                     │
│ 📅 מחר (Tomorrow)                   │
│ ┌──────┬──────┬──────┬──────┐      │
│ │06:00 │09:00 │12:00 │18:00 │      │
│ │1.5ft │1.5ft │2.2ft │2.5ft │      │
│ │קרסול │קרסול │ברך   │ברך   │      │
│ └──────┴──────┴──────┴──────┘      │
│                                     │
│ 📅 מחרתיים (Day After)              │
│ ┌──────┬──────┬──────┬──────┐      │
│ │06:00 │09:00 │12:00 │18:00 │      │
│ │1.7ft │1.7ft │2.4ft │2.7ft │      │
│ │ברך   │ברך   │ברך   │כתף   │      │
│ └──────┴──────┴──────┴──────┘      │
└─────────────────────────────────────┘
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
