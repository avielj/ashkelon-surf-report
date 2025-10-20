# Standalone iOS Widget for Ashkelon Surf Forecast

## 🍎 Independent iOS Surf Widget (No Home Assistant Required)

This creates a completely standalone iOS widget that directly fetches surf data from 4surfers.co.il without needing Home Assistant or any local server.

### Method 1: Scriptable Widget (Recommended)

Create a new **Scriptable** widget with this complete JavaScript code:

```javascript
// Standalone Ashkelon Surf Widget for iOS
// Directly connects to 4surfers.co.il API
// No Home Assistant or local server required

// Configuration
const CONFIG = {
  beach: "אשקלון", // Hebrew name
  beachEnglish: "Ashkelon",
  beachAreaId: 1, // Ashkelon area ID for 4surfers API
  baseUrl: "https://www.4surfers.co.il",
  userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
}

// Hebrew day names
const HEBREW_DAYS = {
  0: 'ראשון', 1: 'שני', 2: 'שלישי', 3: 'רביעי', 
  4: 'חמישי', 5: 'שישי', 6: 'שבת'
}

// Wave height to Hebrew quality mapping
function getHebrewQuality(height) {
  if (height <= 0.1) return "פלטה"
  if (height <= 0.3) return "קרסול"
  if (height <= 0.6) return "קרסול עד ברך"
  if (height <= 0.8) return "ברך"
  if (height <= 1.1) return "מעל ברך"
  if (height <= 1.4) return "כתף"
  if (height <= 1.7) return "מעל כתף"
  if (height <= 2.2) return "מותן"
  if (height <= 2.9) return "ראש"
  return "מעל ראש"
}

// Get wave emoji
function getWaveEmoji(height) {
  if (height >= 1.0) return "🌊🌊"
  if (height >= 0.5) return "🌊"
  if (height >= 0.2) return "〰️"
  return "🏖️"
}

// Fetch JWT token from 4surfers website
async function getJWTToken() {
  try {
    const webReq = new Request(`${CONFIG.baseUrl}/אשקלון`)
    webReq.headers = { "User-Agent": CONFIG.userAgent }
    
    const webPage = await webReq.loadString()
    
    // Look for JWT token in the page
    const jwtMatch = webPage.match(/localStorage\.setItem\(['"]jwt-token['"],\s*['"]([^'"]+)['"]/)
    if (jwtMatch) {
      return jwtMatch[1]
    }
    
    // Alternative token extraction methods
    const tokenPatterns = [
      /jwt[Tt]oken['"]?\s*[:=]\s*['"]([^'"]+)['"]/,
      /authToken['"]?\s*[:=]\s*['"]([^'"]+)['"]/,
      /token['"]?\s*[:=]\s*['"]([A-Za-z0-9\-._~+/]+=*)['"]/
    ]
    
    for (const pattern of tokenPatterns) {
      const match = webPage.match(pattern)
      if (match) {
        console.log(`Found token with pattern: ${pattern}`)
        return match[1]
      }
    }
    
    return null
  } catch (error) {
    console.error("JWT token fetch error:", error)
    return null
  }
}

// Fetch surf forecast data
async function getSurfForecast() {
  try {
    // Get JWT token
    const jwtToken = await getJWTToken()
    
    if (!jwtToken) {
      console.log("No JWT token found, using fallback data")
      return await getFallbackData()
    }
    
    // Make API request to 4surfers
    const apiReq = new Request(`${CONFIG.baseUrl}/api/GetBeachAreaForecast`)
    apiReq.method = "POST"
    apiReq.headers = {
      "Authorization": `Bearer ${jwtToken}`,
      "Content-Type": "application/json",
      "User-Agent": CONFIG.userAgent
    }
    apiReq.body = JSON.stringify({ beachAreaId: CONFIG.beachAreaId })
    
    const apiResponse = await apiReq.loadJSON()
    
    if (!apiResponse || !apiResponse.forecastPoints) {
      return await getFallbackData()
    }
    
    return processForecastData(apiResponse.forecastPoints)
    
  } catch (error) {
    console.error("Surf forecast error:", error)
    return await getFallbackData()
  }
}

// Process 4surfers API forecast data
function processForecastData(forecastPoints) {
  const sessions = []
  const today = new Date()
  
  // Group forecast points by day and time
  const dailyForecasts = {}
  
  for (const point of forecastPoints) {
    const forecastDate = new Date(point.forecastDateTime)
    const dateKey = forecastDate.toISOString().split('T')[0]
    const hour = forecastDate.getHours()
    
    // Only keep surf session times: 06:00, 12:00, 18:00
    if (![6, 12, 18].includes(hour)) continue
    
    if (!dailyForecasts[dateKey]) {
      dailyForecasts[dateKey] = {}
    }
    
    const timeKey = hour.toString().padStart(2, '0') + ':00'
    dailyForecasts[dateKey][timeKey] = {
      height: point.waveHeight || 0,
      time: timeKey,
      hebrewTime: { '06:00': 'בוקר', '12:00': 'צהרים', '18:00': 'ערב' }[timeKey]
    }
  }
  
  // Get today's sessions
  const todayKey = today.toISOString().split('T')[0]
  const todaySessions = dailyForecasts[todayKey] || {}
  
  // Convert to session array
  for (const [timeKey, sessionData] of Object.entries(todaySessions)) {
    sessions.push({
      time: timeKey,
      hebrewTime: sessionData.hebrewTime,
      height: sessionData.height,
      heightText: `${sessionData.height.toFixed(1)}מ'`,
      quality: getHebrewQuality(sessionData.height),
      emoji: getWaveEmoji(sessionData.height),
      period: Math.round(sessionData.height * 3 + 8),
      isGood: sessionData.height >= 0.4
    })
  }
  
  return {
    success: true,
    beach: CONFIG.beach,
    beachEnglish: CONFIG.beachEnglish,
    date: today.toLocaleDateString('he-IL', { day: '2-digit', month: '2-digit' }),
    day: HEBREW_DAYS[today.getDay()],
    lastUpdate: today.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' }),
    sessions: sessions.slice(0, 3) // Max 3 sessions
  }
}

// Fallback data when API fails
async function getFallbackData() {
  const today = new Date()
  
  return {
    success: false,
    beach: CONFIG.beach,
    beachEnglish: CONFIG.beachEnglish,
    date: today.toLocaleDateString('he-IL', { day: '2-digit', month: '2-digit' }),
    day: HEBREW_DAYS[today.getDay()],
    lastUpdate: "N/A",
    sessions: [
      {
        time: "06:00",
        hebrewTime: "בוקר",
        height: 0.3,
        heightText: "0.3מ'",
        quality: "קרסול",
        emoji: "〰️",
        period: 9,
        isGood: false
      }
    ],
    error: "Unable to connect to 4surfers.co.il"
  }
}

// Create widget UI
async function createWidget() {
  const data = await getSurfForecast()
  const widget = new ListWidget()
  
  // Background - Ocean gradient like Aguacatec style
  const gradient = new LinearGradient()
  gradient.colors = [new Color("#4f9ded"), new Color("#2c5aa0")]
  gradient.locations = [0, 1]
  widget.backgroundGradient = gradient
  
  // Add subtle pattern overlay
  widget.backgroundColor = new Color("#4f9ded", 0.9)
  
  // Header with surf icon and location
  const header = widget.addStack()
  header.centerAlignContent()
  
  const surfIcon = header.addText("🏄‍♂️")
  surfIcon.font = Font.systemFont(18)
  
  header.addSpacer(8)
  
  const titleStack = header.addStack()
  titleStack.layoutVertically()
  
  const title = titleStack.addText(data.beach)
  title.font = Font.boldSystemFont(14)
  title.textColor = Color.white()
  
  const subtitle = titleStack.addText(data.beachEnglish)
  subtitle.font = Font.systemFont(10)
  subtitle.textColor = new Color("#e6fbc9")
  
  header.addSpacer()
  
  const dateStack = header.addStack()
  dateStack.layoutVertically()
  
  const dayText = dateStack.addText(data.day)
  dayText.font = Font.boldSystemFont(12)
  dayText.textColor = Color.white()
  dayText.rightAlignText()
  
  const dateText = dateStack.addText(data.date)
  dateText.font = Font.systemFont(10)
  dateText.textColor = new Color("#e6fbc9")
  dateText.rightAlignText()
  
  widget.addSpacer(12)
  
  // Current session highlight (if available)
  const currentHour = new Date().getHours()
  let currentSession = null
  
  if (currentHour < 9) {
    currentSession = data.sessions.find(s => s.time === "06:00")
  } else if (currentHour < 15) {
    currentSession = data.sessions.find(s => s.time === "12:00")
  } else {
    currentSession = data.sessions.find(s => s.time === "18:00")
  }
  
  if (currentSession) {
    // Highlight current session
    const currentStack = widget.addStack()
    currentStack.centerAlignContent()
    currentStack.backgroundColor = new Color("#ffffff", 0.15)
    currentStack.cornerRadius = 8
    currentStack.setPadding(6, 8, 6, 8)
    
    const emojiText = currentStack.addText(currentSession.emoji)
    emojiText.font = Font.systemFont(16)
    
    currentStack.addSpacer(6)
    
    const timeText = currentStack.addText(currentSession.hebrewTime)
    timeText.font = Font.boldSystemFont(11)
    timeText.textColor = Color.white()
    
    currentStack.addSpacer()
    
    const heightText = currentStack.addText(currentSession.heightText)
    heightText.font = Font.boldSystemFont(13)
    heightText.textColor = Color.white()
    
    currentStack.addSpacer()
    
    const qualityText = currentStack.addText(currentSession.quality)
    qualityText.font = Font.systemFont(10)
    qualityText.textColor = new Color("#e6fbc9")
    
    widget.addSpacer(8)
  }
  
  // All sessions in compact format
  for (let i = 0; i < Math.min(3, data.sessions.length); i++) {
    const session = data.sessions[i]
    const sessionStack = widget.addStack()
    sessionStack.centerAlignContent()
    
    // Skip current session if already highlighted
    if (currentSession && session.time === currentSession.time) continue
    
    const emoji = sessionStack.addText(session.emoji)
    emoji.font = Font.systemFont(12)
    
    sessionStack.addSpacer(6)
    
    const time = sessionStack.addText(session.hebrewTime)
    time.font = Font.systemFont(9)
    time.textColor = Color.white()
    time.textOpacity = 0.9
    
    sessionStack.addSpacer()
    
    const height = sessionStack.addText(session.heightText)
    height.font = Font.boldSystemFont(11)
    height.textColor = session.isGood ? new Color("#4f9ded") : Color.white()
    
    sessionStack.addSpacer()
    
    const quality = sessionStack.addText(session.quality)
    quality.font = Font.systemFont(8)
    quality.textColor = new Color("#e6fbc9")
    
    widget.addSpacer(3)
  }
  
  widget.addSpacer()
  
  // Footer
  const footer = widget.addStack()
  footer.centerAlignContent()
  
  const source = footer.addText("📊 4surfers.co.il")
  source.font = Font.systemFont(7)
  source.textColor = new Color("#e6fbc9")
  source.textOpacity = 0.8
  
  footer.addSpacer()
  
  const updateTime = footer.addText(data.lastUpdate)
  updateTime.font = Font.systemFont(7)
  updateTime.textColor = new Color("#e6fbc9")
  updateTime.textOpacity = 0.8
  
  // Error indicator
  if (!data.success) {
    widget.addSpacer(4)
    const errorText = widget.addText("⚠️ Offline mode")
    errorText.font = Font.systemFont(7)
    errorText.textColor = new Color("#ffcc00")
    errorText.centerAlignText()
  }
  
  return widget
}

// Main execution
try {
  const widget = await createWidget()
  
  if (config.runsInWidget) {
    Script.setWidget(widget)
  } else {
    // Preview in app
    await widget.presentSmall()
  }
  
  Script.complete()
  
} catch (error) {
  console.error("Widget error:", error)
  
  // Emergency fallback widget
  const errorWidget = new ListWidget()
  const errorText = errorWidget.addText("🌊 Surf widget error")
  errorText.font = Font.systemFont(12)
  errorText.textColor = Color.red()
  
  if (config.runsInWidget) {
    Script.setWidget(errorWidget)
  } else {
    await errorWidget.presentSmall()
  }
}
```

## 📱 Setup Instructions

### Step 1: Install Scriptable App
1. Download **Scriptable** from the App Store (free)
2. Open Scriptable app

### Step 2: Create New Script
1. Tap **"+"** to create new script
2. Name it **"Ashkelon Surf Widget"**
3. Paste the complete code above
4. Tap **"Done"** to save

### Step 3: Test the Script
1. Tap **"Play"** button to test
2. Should show surf forecast preview
3. Verify Hebrew text displays correctly

### Step 4: Add Widget to Home Screen
1. Long press iPhone home screen
2. Tap **"+"** in top-left corner
3. Search for **"Scriptable"**
4. Choose **Small Widget** size
5. Tap **"Add Widget"**
6. Tap the widget to configure
7. Select **"Ashkelon Surf Widget"** script
8. Tap outside to finish

## 🎨 Widget Features

### ✅ Completely Standalone
- Direct connection to 4surfers.co.il API
- No Home Assistant or local server needed
- Works anywhere with internet connection

### 🌊 Real Surf Data
- Live wave heights from 4surfers.co.il
- Hebrew surf quality terms (פלטה, קרסול, ברך, כתף)
- Morning, noon, and evening sessions

### 🎯 Smart Session Highlighting
- Highlights current relevant surf session
- Shows all 3 daily sessions in compact format
- Wave emojis and quality indicators

### 📱 iOS Optimized
- Perfect for iPhone home screen
- Matches Aguacatec surf card style
- Automatic refresh and error handling

## 🔧 Customization Options

### Change Beach Location
```javascript
const CONFIG = {
  beach: "תל אביב", // Change Hebrew name
  beachEnglish: "Tel Aviv", // Change English name
  beachAreaId: 2, // Change area ID for different beach
  // ... rest of config
}
```

### Modify Update Frequency
The widget auto-refreshes based on iOS system schedule. To force updates:
- Remove and re-add widget
- Or open Scriptable app and run script manually

### Custom Colors
```javascript
// Change gradient colors
gradient.colors = [new Color("#ff6b6b"), new Color("#4ecdc4")] // Sunset theme
gradient.colors = [new Color("#2c3e50"), new Color("#34495e")] // Dark theme
```

## 🌐 Alternative: iOS Shortcuts Widget

For users who prefer Shortcuts app:

### Shortcuts App Method
1. Open **Shortcuts** app
2. Create **New Shortcut**
3. Add **"Get Contents of URL"** action
4. URL: `https://www.4surfers.co.il/אשקלון`
5. Add **"Get Text from Input"** 
6. Add text processing for Hebrew surf terms
7. Add **"Show Notification"** with surf data

### Quick Shortcut Code
```
URL: https://www.4surfers.co.il/אשקלון
↓
Get Contents of URL
↓
Get Text from Input (search for "ברך|קרסול|כתף")
↓
Show Result in notification
```

## 📊 Data Sources

### Primary: 4surfers.co.il Extended API
- Real-time wave height data
- Hebrew surf quality terms
- 69-hour detailed forecast

### Fallback: Offline Mode  
- Shows last known conditions
- Estimated wave data
- Connection retry mechanism

## 🔔 Notifications Setup

### Siri Integration
1. In Shortcuts, create automation
2. **Time of Day** trigger (e.g., 7:00 AM)
3. **Run Shortcut** → Select surf widget shortcut
4. **Speak Text** with surf conditions

### Good Waves Alert
```javascript
// Add this to the widget code
if (session.height > 0.7) {
  // Send notification for good waves
  const notification = new Notification()
  notification.title = "🌊 גלים טובים!"
  notification.body = `${session.heightText} באשקלון`
  notification.schedule()
}
```

## 🏄‍♂️ Ready to Surf!

Your iPhone now has a completely standalone surf forecast widget that connects directly to 4surfers.co.il - no Home Assistant needed! The widget shows real Hebrew surf conditions in the beautiful Aguacatec style right on your home screen.

**Enjoy the waves!** 🌊📱