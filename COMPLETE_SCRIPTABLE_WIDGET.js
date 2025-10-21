// Ashkelon Surf Forecast - Complete Scriptable Widget
// No server needed! Everything runs directly in Scriptable

// =======================
// VERSION & AUTO-UPDATE
// =======================
const SCRIPT_VERSION = "1.1.0"
const SCRIPT_NAME = "Ashkelon Surf Widget"
const GITHUB_RAW_URL = "https://raw.githubusercontent.com/avielj/ashkelon-surf-report/main/COMPLETE_SCRIPTABLE_WIDGET.js"
const CHECK_UPDATE_DAYS = 7 // Check for updates every 7 days

// =======================
// CONFIGURATION
// =======================
const BEACH_NAME = "אשקלון"
const BEACH_NAME_EN = "Ashkelon"
const REFRESH_INTERVAL = 30 // minutes

// =======================
// MAIN WIDGET
// =======================
async function createWidget() {
  const widget = new ListWidget()
  
  try {
    // Fetch surf data
    const forecast = await fetchSurfForecast()
    
    // Style widget with ocean gradient
    const gradient = new LinearGradient()
    gradient.locations = [0, 1]
    gradient.colors = [
      new Color("#4f9ded"),
      new Color("#2c5aa0")
    ]
    widget.backgroundGradient = gradient
    
    // Add content
    addHeader(widget, forecast)
    widget.addSpacer(8)
    addSessions(widget, forecast)
    widget.addSpacer(4)
    addFooter(widget, forecast)
    
    // Refresh timer
    widget.refreshAfterDate = new Date(Date.now() + REFRESH_INTERVAL * 60 * 1000)
    
  } catch (error) {
    // Error state
    widget.backgroundColor = new Color("#d32f2f")
    const errorText = widget.addText("❌ שגיאה")
    errorText.font = Font.boldSystemFont(16)
    errorText.textColor = Color.white()
    errorText.centerAlignText()
    
    const errorMsg = widget.addText(error.message || "לא ניתן לטעון נתונים")
    errorMsg.font = Font.systemFont(12)
    errorMsg.textColor = Color.white()
    errorMsg.centerAlignText()
  }
  
  return widget
}

// =======================
// FETCH SURF DATA (72 HOURS)
// =======================
async function fetchSurfForecast() {
  try {
    // Use the working 4surfers API endpoint
    const url = "https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast"
    const request = new Request(url)
    request.method = "POST"
    request.headers = {
      "Accept": "application/json, text/plain, */*",
      "Content-Type": "application/json;charset=UTF-8",
      "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
      "Origin": "https://4surfers.co.il",
      "Referer": "https://4surfers.co.il/"
    }
    request.body = JSON.stringify({ beachAreaId: "80" }) // Ashkelon ID
    request.timeoutInterval = 20
    
    const response = await request.loadJSON()
    
    if (response && response.dailyForecastList) {
      console.log("✅ API Success: Got forecast data")
      return parseForecastData(response)
    } else {
      console.log("API returned no forecast data, using mock")
      return getMockData()
    }
    
  } catch (error) {
    console.log("API error, using mock data: " + error.message)
    return getMockData()
  }
}

function parseForecastData(data) {
  const today = new Date()
  const timeSlots = []
  
  // Parse time-based forecasts (6 AM, 9 AM, 12 PM, 6 PM)
  const times = [
    { hour: 6, label: "06:00" },
    { hour: 9, label: "09:00" },
    { hour: 12, label: "12:00" },
    { hour: 18, label: "18:00" }
  ]
  
  // Parse real API response format
  if (data && data.dailyForecastList && data.dailyForecastList.length > 0) {
    console.log(`Parsing ${data.dailyForecastList.length} days of forecast`)
    
    for (let dayIndex = 0; dayIndex < Math.min(3, data.dailyForecastList.length); dayIndex++) {
      const dayData = data.dailyForecastList[dayIndex]
      const forecastHours = dayData.forecastHours || []
      
      // Get the date for this forecast day
      const forecastDate = new Date(dayData.forecastLocalTime)
      const dayName = getDayName(forecastDate)
      const dateStr = formatDate(forecastDate)
      
      const dayLabel = dayIndex === 0 
        ? "Today" 
        : `${dayName} ${dateStr}`
      
      // Extract data for specific hours
      for (const time of times) {
        // Find the forecast hour that matches this time
        const hourData = forecastHours.find(h => {
          if (h.forecastLocalHour) {
            const hourMatch = h.forecastLocalHour.match(/T(\d{2}):/)
            return hourMatch && parseInt(hourMatch[1]) === time.hour
          }
          return false
        })
        
        if (hourData) {
          const height = hourData.waveHeight || 0.5
          const period = hourData.WavePeriod || 9
          const surfRank = hourData.surfRankMark || ""
          const hebrewHeight = hourData.surfHeightDesc || ""
          
          timeSlots.push({
            time: time.label,
            day: dayLabel,
            stars: heightToStars(height),
            height: height,
            period: period,
            surfRank: surfRank,
            hebrewHeight: hebrewHeight
          })
        } else {
          // No data for this hour, use estimate
        const avgHeight = forecastHours.length > 0
            ? forecastHours.reduce((sum, h) => sum + (h.waveHeight || 0), 0) / forecastHours.length
            : 0.5
          
          timeSlots.push({
            time: time.label,
            day: dayLabel,
            stars: heightToStars(avgHeight),
            height: avgHeight,
            period: 9,
            surfRank: "",
            hebrewHeight: waveHeightToQuality(avgHeight)
          })
        }
      }
    }
  }
  
  // If no data or parsing failed, generate mock data
  if (timeSlots.length === 0) {
    console.log("No data parsed, generating mock data")
    for (let dayIndex = 0; dayIndex < 3; dayIndex++) {
      const mockDate = new Date(today)
      mockDate.setDate(today.getDate() + dayIndex)
      const dayName = getDayName(mockDate)
      const dateStr = formatDate(mockDate)
      const dayLabel = dayIndex === 0 ? "Today" : `${dayName} ${dateStr}`
      
      for (const time of times) {
        const height = 0.5 + Math.random() * 2.5
        timeSlots.push({
          time: time.label,
          day: dayLabel,
          stars: heightToStars(height),
          height: height,
          period: 8 + Math.floor(Math.random() * 4)
        })
      }
    }
  }
  
  return {
    beach: BEACH_NAME_EN,
    timeSlots: timeSlots,
    lastUpdate: formatTime(today),
    isLive: data && data.dailyForecastList
  }
}

function getMockData() {
  const today = new Date()
  const timeSlots = []
  const times = [
    { hour: 6, label: "06:00" },
    { hour: 9, label: "09:00" },
    { hour: 12, label: "12:00" },
    { hour: 18, label: "18:00" }
  ]
  
  // Generate 3 days × 4 times = 12 time slots
  for (let dayIndex = 0; dayIndex < 3; dayIndex++) {
    const mockDate = new Date(today)
    mockDate.setDate(today.getDate() + dayIndex)
    const dayName = getDayName(mockDate)
    const dateStr = formatDate(mockDate)
    const dayLabel = dayIndex === 0 ? "Today" : `${dayName} ${dateStr}`
    
    for (const time of times) {
      const height = 1.2 + Math.random() * 1.8 // 1.2ft - 3.0ft (converted from meters in API)
      timeSlots.push({
        time: time.label,
        day: dayLabel,
        stars: heightToStars(height),
        height: height,
        period: 9 + Math.floor(Math.random() * 3), // 9-11 seconds
        surfRank: "b05",
        hebrewHeight: waveHeightToQuality(height)
      })
    }
  }
  
  return {
    beach: BEACH_NAME_EN,
    timeSlots: timeSlots,
    lastUpdate: formatTime(today),
    isLive: false
  }
}

// =======================
// WIDGET UI BUILDERS
// =======================
function addHeader(widget, forecast) {
  const header = widget.addStack()
  header.layoutHorizontally()
  header.centerAlignContent()
  
  // Beach name
  const textStack = header.addStack()
  textStack.layoutVertically()
  
  const beachText = textStack.addText(`🏖️ ${forecast.beach}`)
  beachText.font = Font.boldSystemFont(16)
  beachText.textColor = Color.white()
  
  // Live indicator
  if (forecast.isLive) {
    header.addSpacer()
    const liveText = header.addText("●")
    liveText.font = Font.systemFont(14)
    liveText.textColor = new Color("#22c55e")
  }
}

function addSessions(widget, forecast) {
  // Group by day
  const days = {}
  forecast.timeSlots.forEach(slot => {
    if (!days[slot.day]) days[slot.day] = []
    days[slot.day].push(slot)
  })
  
  // Display each day (use actual day labels from data)
  const dayKeys = Object.keys(days)
  for (let i = 0; i < dayKeys.length; i++) {
    const dayKey = dayKeys[i]
    const slots = days[dayKey] || []
    
    if (slots.length === 0) continue
    
    // Day label
    const dayLabel = widget.addText(dayKey)
    dayLabel.font = Font.semiboldSystemFont(11)
    dayLabel.textColor = new Color("#e6fbc9")
    
    widget.addSpacer(3)
    
    // Time slots row
    const row = widget.addStack()
    row.layoutHorizontally()
    row.spacing = 5
    
    for (const slot of slots) {
      const card = row.addStack()
      card.layoutVertically()
      card.backgroundColor = new Color("#ffffff", 0.15)
      card.cornerRadius = 8
      card.setPadding(6, 8, 6, 8)
      card.spacing = 2
      
      // Time with clock icon
      const timeRow = card.addStack()
      timeRow.layoutHorizontally()
      timeRow.spacing = 2
      const clockIcon = timeRow.addText("⏰")
      clockIcon.font = Font.systemFont(9)
      const timeText = timeRow.addText(slot.time)
      timeText.font = Font.mediumSystemFont(9)
      timeText.textColor = new Color("#ffffff", 0.9)
      
      // Stars rating
      const starsText = card.addText(slot.stars)
      starsText.font = Font.systemFont(11)
      starsText.centerAlignText()
      
      // Wave height in feet
      const heightRow = card.addStack()
      heightRow.layoutHorizontally()
      heightRow.spacing = 2
      const waveIcon = heightRow.addText("🌊")
      waveIcon.font = Font.systemFont(9)
      const heightFeet = (slot.height * 3.28084).toFixed(1)
      const heightText = heightRow.addText(`${heightFeet}ft`)
      heightText.font = Font.boldSystemFont(11)
      heightText.textColor = Color.white()
      
      // Hebrew height description
      if (slot.hebrewHeight) {
        const hebrewText = card.addText(slot.hebrewHeight)
        hebrewText.font = Font.systemFont(8)
        hebrewText.textColor = new Color("#e6fbc9")
        hebrewText.centerAlignText()
        hebrewText.lineLimit = 1
        hebrewText.minimumScaleFactor = 0.7
      }
      
      // Period
      const periodRow = card.addStack()
      periodRow.layoutHorizontally()
      periodRow.spacing = 2
      const periodIcon = periodRow.addText("⏱️")
      periodIcon.font = Font.systemFont(7)
      const periodText = periodRow.addText(`${slot.period}s`)
      periodText.font = Font.systemFont(8)
      periodText.textColor = new Color("#ffffff", 0.7)
    }
    
    // Spacing between days
    if (i < dayKeys.length - 1) {
      widget.addSpacer(6)
    }
  }
}

function addFooter(widget, forecast) {
  const footer = widget.addStack()
  footer.layoutHorizontally()
  footer.centerAlignContent()
  
  footer.addSpacer()
  
  const updateText = footer.addText(`⏰ עודכן ${forecast.lastUpdate}`)
  updateText.font = Font.systemFont(9)
  updateText.textColor = new Color("#ffffff", 0.5)
  
  footer.addSpacer()
}

// =======================
// HELPER FUNCTIONS
// =======================
function heightToStars(height) {
  // Convert wave height to star rating (0-5 stars)
  if (height <= 0.5) return "☆☆☆☆☆" // 0 stars - flat
  if (height <= 1.0) return "⭐☆☆☆☆" // 1 star - small
  if (height <= 1.5) return "⭐⭐☆☆☆" // 2 stars - decent
  if (height <= 2.0) return "⭐⭐⭐☆☆" // 3 stars - good
  if (height <= 2.5) return "⭐⭐⭐⭐☆" // 4 stars - great
  return "⭐⭐⭐⭐⭐" // 5 stars - excellent
}

function waveHeightToQuality(height) {
  if (height <= 0.1) return "פלטה"
  if (height <= 0.2) return "שטוח"
  if (height <= 0.4) return "קרסול"
  if (height <= 0.6) return "קרסול עד ברך"
  if (height <= 0.9) return "ברך"
  if (height <= 1.2) return "מעל ברך"
  if (height <= 1.5) return "כתף"
  if (height <= 1.8) return "מעל כתף"
  if (height <= 2.2) return "מותן"
  if (height <= 2.8) return "ראש"
  return "מעל ראש"
}

function getDayName(date) {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
  return days[date.getDay()]
}

function getHebrewDay(dayIndex) {
  const days = ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "שבת"]
  return days[dayIndex]
}

function formatDate(date) {
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}`
}

function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

// =======================
// AUTO-UPDATE FUNCTIONS
// =======================
async function checkForUpdates() {
  try {
    const fm = FileManager.iCloud()
    const updateCheckFile = fm.joinPath(fm.documentsDirectory(), "ashkelon_widget_update_check.json")
    
    // Check if we should check for updates
    let shouldCheck = true
    if (fm.fileExists(updateCheckFile)) {
      const data = JSON.parse(fm.readString(updateCheckFile))
      const daysSinceLastCheck = (Date.now() - data.lastCheck) / (1000 * 60 * 60 * 24)
      shouldCheck = daysSinceLastCheck >= CHECK_UPDATE_DAYS
    }
    
    if (!shouldCheck) {
      console.log("⏭️ Skipping update check (checked recently)")
      return false
    }
    
    console.log("🔍 Checking for updates...")
    
    // Fetch latest version from GitHub
    const req = new Request(GITHUB_RAW_URL)
    const content = await req.loadString()
    
    // Extract version from downloaded content
    const versionMatch = content.match(/const SCRIPT_VERSION = "([^"]+)"/)
    const latestVersion = versionMatch ? versionMatch[1] : null
    
    // Save check time
    fm.writeString(updateCheckFile, JSON.stringify({
      lastCheck: Date.now(),
      latestVersion: latestVersion,
      currentVersion: SCRIPT_VERSION
    }))
    
    if (!latestVersion) {
      console.log("⚠️ Could not determine latest version")
      return false
    }
    
    console.log(`📦 Current: v${SCRIPT_VERSION}, Latest: v${latestVersion}`)
    
    if (latestVersion !== SCRIPT_VERSION) {
      console.log("🎉 New version available!")
      return {
        available: true,
        currentVersion: SCRIPT_VERSION,
        latestVersion: latestVersion,
        content: content
      }
    } else {
      console.log("✅ Already on latest version")
      return false
    }
    
  } catch (error) {
    console.error("❌ Error checking for updates:", error)
    return false
  }
}

async function performUpdate(updateContent) {
  try {
    console.log("📥 Installing update...")
    
    const fm = FileManager.iCloud()
    const scriptPath = module.filename
    
    // Backup current version
    const backupPath = scriptPath.replace('.js', '_backup.js')
    if (fm.fileExists(scriptPath)) {
      fm.copy(scriptPath, backupPath)
      console.log("💾 Backup created")
    }
    
    // Write new version
    fm.writeString(scriptPath, updateContent)
    console.log("✅ Update installed successfully!")
    
    // Show notification
    const notification = new Notification()
    notification.title = SCRIPT_NAME
    notification.body = `Updated to latest version! Widget will refresh.`
    notification.sound = "default"
    await notification.schedule()
    
    return true
    
  } catch (error) {
    console.error("❌ Error installing update:", error)
    
    const notification = new Notification()
    notification.title = SCRIPT_NAME
    notification.body = `Update failed: ${error.message}`
    await notification.schedule()
    
    return false
  }
}

async function showUpdatePrompt(updateInfo) {
  const alert = new Alert()
  alert.title = "🌊 Update Available"
  alert.message = `A new version of ${SCRIPT_NAME} is available!\n\nCurrent: v${updateInfo.currentVersion}\nLatest: v${updateInfo.latestVersion}\n\nWould you like to update now?`
  alert.addAction("Update Now")
  alert.addAction("Later")
  alert.addCancelAction("Skip This Version")
  
  const response = await alert.presentAlert()
  
  if (response === 0) {
    // Update now
    const success = await performUpdate(updateInfo.content)
    if (success) {
      // Reload script
      const alert2 = new Alert()
      alert2.title = "✅ Update Complete"
      alert2.message = "The widget has been updated. Please rerun the script or wait for the next refresh."
      alert2.addAction("OK")
      await alert2.present()
    }
  } else if (response === 2) {
    // Skip this version
    const fm = FileManager.iCloud()
    const skipFile = fm.joinPath(fm.documentsDirectory(), "ashkelon_widget_skip_version.txt")
    fm.writeString(skipFile, updateInfo.latestVersion)
  }
}

// =======================
// RUN WIDGET
// =======================
const widget = await createWidget()

// Check for updates when running in app (not in widget)
if (!config.runsInWidget) {
  const updateInfo = await checkForUpdates()
  if (updateInfo && updateInfo.available) {
    await showUpdatePrompt(updateInfo)
  }
}

if (config.runsInWidget) {
  Script.setWidget(widget)
} else {
  // Preview in app
  await widget.presentMedium()
}

Script.complete()
