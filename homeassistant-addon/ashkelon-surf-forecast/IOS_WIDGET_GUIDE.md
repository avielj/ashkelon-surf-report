# iOS Widget Setup Guide for Ashkelon Surf Forecast

## 🍎 iOS Shortcuts App Configuration

### Method 1: Web Widget (Recommended)

1. **Open Shortcuts App** on your iPhone
2. **Create New Shortcut** → Name it "Ashkelon Surf Widget"
3. **Add Actions:**
   - **Get Contents of URL**
     - URL: `http://192.168.1.100:8099/widget`
     - Replace `192.168.1.100` with your Home Assistant IP
   - **Show Web Page**
     - Pass the web page content from previous action

4. **Save Shortcut**
5. **Add to Home Screen:**
   - Long press home screen → Add Widget
   - Search for "Shortcuts" 
   - Choose "Shortcut" widget size
   - Select your "Ashkelon Surf Widget" shortcut

### Method 2: JSON Data Widget (Advanced)

1. **Create New Shortcut** → Name it "Ashkelon Surf Data"
2. **Add Actions:**
   ```
   Get Contents of URL
   ├── URL: http://192.168.1.100:8099/api/widget
   └── Method: GET
   
   Get Value for "sessions" in Contents of URL
   
   Repeat with Each Item in sessions
   ├── Get Value for "height_text" in Repeat Item
   ├── Get Value for "hebrew_time" in Repeat Item  
   ├── Text Action: "[hebrew_time]: [height_text]"
   └── Add to Variable "surf_sessions"
   
   Show Notification
   ├── Title: "🌊 אשקלון Surf"
   └── Body: surf_sessions
   ```

3. **Test the shortcut** to ensure it works
4. **Add Widget to Home Screen**

### Method 3: Scriptable Widget (iOS Advanced Users)

Create a **Scriptable** widget with this JavaScript:

```javascript
// Ashkelon Surf Widget for Scriptable
const url = "http://192.168.1.100:8099/api/widget"

try {
  const req = new Request(url)
  const json = await req.loadJSON()
  
  if (!json.success) {
    throw new Error("No data available")
  }
  
  // Create widget
  const widget = new ListWidget()
  
  // Background gradient
  const gradient = new LinearGradient()
  gradient.colors = [new Color("#4f9ded"), new Color("#2c5aa0")]
  gradient.locations = [0, 1]
  widget.backgroundGradient = gradient
  
  // Header
  const header = widget.addStack()
  header.centerAlignContent()
  
  const surfIcon = header.addText("🏄‍♂️")
  surfIcon.font = Font.systemFont(20)
  
  header.addSpacer(8)
  
  const titleStack = header.addStack()
  titleStack.layoutVertically()
  
  const title = titleStack.addText("אשקלון")
  title.font = Font.boldSystemFont(16)
  title.textColor = Color.white()
  
  const subtitle = titleStack.addText("Ashkelon")
  subtitle.font = Font.systemFont(12)
  subtitle.textColor = new Color("#e6fbc9")
  
  header.addSpacer()
  
  const dateText = header.addText(json.date)
  dateText.font = Font.systemFont(12)
  dateText.textColor = new Color("#e6fbc9")
  
  widget.addSpacer(12)
  
  // Sessions
  for (const session of json.sessions.slice(0, 3)) {
    const sessionStack = widget.addStack()
    sessionStack.centerAlignContent()
    
    // Time
    const timeText = sessionStack.addText(session.hebrew_time)
    timeText.font = Font.systemFont(11)
    timeText.textColor = Color.white()
    timeText.textOpacity = 0.9
    
    sessionStack.addSpacer()
    
    // Height
    const heightText = sessionStack.addText(session.height_text)
    heightText.font = Font.boldSystemFont(13)
    heightText.textColor = new Color("#4f9ded")
    
    sessionStack.addSpacer()
    
    // Quality
    const qualityText = sessionStack.addText(session.quality_hebrew)
    qualityText.font = Font.systemFont(10)
    qualityText.textColor = new Color("#e6fbc9")
    
    if (session !== json.sessions[json.sessions.length - 1]) {
      widget.addSpacer(4)
    }
  }
  
  widget.addSpacer()
  
  // Footer
  const footer = widget.addText(`📊 4surfers.co.il • ${json.last_update}`)
  footer.font = Font.systemFont(8)
  footer.textColor = new Color("#e6fbc9")
  footer.textOpacity = 0.7
  footer.centerAlignText()
  
  // Set widget
  if (config.runsInWidget) {
    Script.setWidget(widget)
  } else {
    widget.presentSmall()
  }
  
  Script.complete()
  
} catch (error) {
  // Error widget
  const errorWidget = new ListWidget()
  const errorText = errorWidget.addText("🌊 Surf data unavailable")
  errorText.font = Font.systemFont(12)
  errorText.textColor = Color.red()
  
  if (config.runsInWidget) {
    Script.setWidget(errorWidget)
  } else {
    errorWidget.presentSmall()
  }
}
```

## 📱 Widget Setup Instructions

### Small Widget (2x2)
- Perfect for current surf session
- Shows time, height, and quality
- Tap to open full forecast

### Medium Widget (4x2)  
- Shows all 3 surf sessions
- Includes Hebrew day and date
- More detailed information

### Large Widget (4x4)
- Full forecast with multiple days
- Detailed session information
- Weather icons and conditions

## 🔧 Customization Options

### Change Background Image
Add a surf background image to your widget by:
1. Save surf image to Photos app
2. In Shortcuts, use "Select Photos" action
3. Set as widget background

### Notification Alerts
Set up notifications for good surf conditions:
```
If wave_height > 0.7 meters
└── Show Notification: "🌊 Good waves at Ashkelon!"
```

### Siri Integration
Enable Siri voice commands:
- "Hey Siri, Ashkelon surf"
- "Hey Siri, check the waves"
- "Hey Siri, surf forecast"

## 📊 Widget Data Available

The `/api/widget` endpoint provides:
```json
{
  "success": true,
  "beach": "אשקלון",
  "beach_english": "Ashkelon", 
  "date": "20/10",
  "day": "ראשון",
  "last_update": "14:30",
  "sessions": [
    {
      "time": "06:00",
      "hebrew_time": "בוקר",
      "height": 0.7,
      "height_text": "0.7מ'",
      "quality_hebrew": "ברך",
      "quality_english": "knee_high",
      "period": 10,
      "rating_stars": "⭐⭐",
      "is_good": true
    }
  ]
}
```

## 🏠 Home Assistant Integration

### Add Widget Card to Dashboard:
```yaml
type: iframe
url: http://192.168.1.100:8099/widget
title: Ashkelon Surf Widget
aspect_ratio: 70%
```

### Create Sensor for Widget Data:
```yaml
sensor:
  - platform: rest
    name: "Ashkelon Widget Data"
    resource: "http://192.168.1.100:8099/api/widget"
    value_template: "{{ value_json.success }}"
    json_attributes_path: "$"
    json_attributes:
      - beach
      - date
      - day
      - sessions
```

## 🔔 Automation Examples

### Good Waves Push Notification:
```yaml
automation:
  - alias: "iOS Surf Alert"
    trigger:
      platform: webhook
      webhook_id: surf_alert
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "🌊 גלים טובים!"
          message: "Good waves at Ashkelon - {{ trigger.json.height }}m"
          data:
            url: "shortcuts://run-shortcut?name=Ashkelon%20Surf%20Widget"
```

## 📱 Widget Screenshots

- **Small Widget**: Current session with height and quality
- **Medium Widget**: 3 sessions (morning, noon, evening)  
- **Large Widget**: Multi-day forecast with detailed info

## 🔧 Troubleshooting

### Widget Not Loading:
1. Check Home Assistant IP address
2. Ensure addon is running on port 8099
3. Verify network connectivity
4. Test URL in browser first

### Data Not Updating:
1. Check addon logs in Home Assistant
2. Verify 4surfers.co.il is accessible
3. Restart the addon
4. Clear iOS widget cache (remove and re-add)

### Hebrew Text Issues:
1. Ensure iOS supports Hebrew fonts
2. Update iOS to latest version
3. Test in browser first
4. Use fallback English if needed

## 🌊 Enjoy Your Surf Widget!

Your iPhone will now show real-time Ashkelon surf conditions right on your home screen! 🏄‍♂️📱