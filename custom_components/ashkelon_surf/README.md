# Ashkelon Surf Forecast – Home Assistant Integration

Surf forecast sensors for Home Assistant that mirror the exact logic of the iOS Scriptable widget: same API endpoint, time slots (06:00, 09:00, 12:00, 18:00), star ratings, Hebrew descriptions, and wave heights converted to feet.

## Highlights
- ⏱ Updates every 3 hours with shared caching to avoid duplicate API calls
- 🌊 Uses `SurfHeightFrom`/`SurfHeightTo` averages from the official 4surfers.co.il API
- ⭐ Produces star ratings identical to the Scriptable widget thresholds
- 🗓 Three sensors: Today, Tomorrow, Day After Tomorrow
- 📋 Rich attributes including all four sessions, missing slots, best session, and last refresh timestamp
- 🪄 Compatible with HACS (add this repository as a custom integration)

## Installation

### Via HACS (recommended)
1. In HACS → Integrations → three-dot menu → *Custom repositories* → add:
   - **Repository:** `https://github.com/avielj/ashkelon-surf-report`
   - **Category:** `Integration`
2. Search for **Ashkelon Surf Forecast** inside HACS and install it.
3. Restart Home Assistant.
4. Add the platform to `configuration.yaml`:
   ```yaml
   sensor:
     - platform: ashkelon_surf
   ```
5. Restart Home Assistant once more; the sensors will appear automatically.

### Manual install
1. Copy the folder `custom_components/ashkelon_surf` into `/config/custom_components/` on your Home Assistant instance.
2. Ensure the final structure is:
   ```text
   /config/custom_components/ashkelon_surf/
     ├── __init__.py
     ├── manifest.json
     ├── sensor.py
     └── README.md
   ```
3. Add the snippet from the HACS section to `configuration.yaml` and restart Home Assistant.

## Entities & Attributes
You will see three sensors:
- `sensor.ashkelon_surf_today`
- `sensor.ashkelon_surf_tomorrow`
- `sensor.ashkelon_surf_day_after`

Each sensor state is the average wave height (feet) across all available sessions for that day. Attributes include:

| Attribute | Description |
|-----------|-------------|
| `sessions` | List of the available time slots. Each session contains `time`, `height_m`, `height_ft`, `period_s`, `stars`, `surf_rank`, `hebrew_height`, `wind_kts`. |
| `missing_times` | Array of time slots that the API did not provide (helps spot gaps). |
| `average_height_ft` / `_m` | Average of all available sessions. |
| `stars` | Star rating derived from the average height (identical to the widget). |
| `best_session` | The session with the highest wave height, or `null` if missing. |
| `last_refreshed` | ISO timestamp of the fetch. |
| `beach` / `beach_hebrew` | Static metadata for Ashkelon. |

Because `sessions` is a list of dictionaries you can create templated Lovelace cards or automations that mimic the Scriptable widget layout.

## Automations Example
Notify when the evening session crosses 3 ft:
```yaml
alias: Evening Surf Alert
trigger:
  - platform: time
    at: "17:30:00"
condition:
  - condition: template
    value_template: >-
      {% set sessions = state_attr('sensor.ashkelon_surf_today', 'sessions') %}
      {% if not sessions %}
        false
      {% else %}
        {% set evening = sessions | selectattr('time', 'equalto', '18:00') | list %}
        {% if evening %}
          {{ evening[0].height_ft | float(0) >= 3.0 }}
        {% else %}
          false
        {% endif %}
      {% endif %}
action:
  - service: notify.mobile_app
    data:
      title: "🌊 Ashkelon Evening Session"
      message: >-
        Surf at 18:00 is {{ evening[0].height_ft }} ft ({{ evening[0].hebrew_height }}), winds {{ evening[0].wind_kts }} kts.
```

## Troubleshooting
- Enable debug logs if you need to inspect the raw data:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.ashkelon_surf: debug
  ```
- The integration honours a 1-hour throttle internally; repeated manual updates faster than that will reuse cached data.
- If 4surfers returns fewer than three days the extra sensors will show as unavailable until the API resumes normal output.

## Development Notes
- Uses built-in `asyncio.timeout` for predictable request handling.
- Converts heights to feet with one decimal place (`round(m * 3.28084, 1)`).
- Hebrew day labels follow the Scriptable widget (`"א'"`, `"ב'"`, …, `"שבת"`).

Feel free to open issues or PRs if you want support for additional beaches or more attributes.
