// Ashkelon Surf Forecast - Siri Shortcut Script
// This script can be called from Siri Shortcuts to get voice responses about surf conditions

// =======================
// CONFIGURATION
// =======================
const BEACH_AREA_ID = "80" // Ashkelon

// =======================
// MAIN FUNCTION
// =======================
async function getSurfForecast(dayOffset = 0) {
  try {
    // Fetch data from 4surfers API
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
    request.body = JSON.stringify({ beachAreaId: BEACH_AREA_ID })
    request.timeoutInterval = 20
    
    const response = await request.loadJSON()
    
    if (response && response.dailyForecastList && response.dailyForecastList.length > dayOffset) {
      const dayData = response.dailyForecastList[dayOffset]
      return createHebrewResponse(dayData, dayOffset)
    } else {
      return "מצטער, לא הצלחתי למצוא מידע על הגלים"
    }
    
  } catch (error) {
    console.log("Error: " + error.message)
    return "מצטער, יש בעיה בקבלת המידע"
  }
}

function createHebrewResponse(dayData, dayOffset) {
  const forecastHours = dayData.forecastHours || []
  
  // Get key times
  const morning = forecastHours.find(h => h.forecastLocalHour?.includes("T06:00"))
  const noon = forecastHours.find(h => h.forecastLocalHour?.includes("T12:00"))
  const evening = forecastHours.find(h => h.forecastLocalHour?.includes("T18:00"))
  
  // Convert meters to feet (1 meter = 3.28084 feet)
  const metersToFeet = (meters) => (meters * 3.28084).toFixed(1)
  
  // Calculate average height
  const heights = []
  if (morning) heights.push(morning.waveHeight)
  if (noon) heights.push(noon.waveHeight)
  if (evening) heights.push(evening.waveHeight)
  
  const avgHeightMeters = heights.length > 0 
    ? heights.reduce((a, b) => a + b, 0) / heights.length
    : 0.5
  
  const avgHeightFeet = metersToFeet(avgHeightMeters)
  
  // Get Hebrew quality
  const hebrewQuality = morning?.surfHeightDesc || noon?.surfHeightDesc || "לא ידוע"
  
  // Build response based on day
  let dayText = ""
  if (dayOffset === 0) {
    dayText = "היום"
  } else if (dayOffset === 1) {
    dayText = "מחר"
  } else if (dayOffset === 2) {
    dayText = "מחרתיים"
  } else {
    const date = new Date(dayData.forecastLocalTime)
    dayText = `ב${getHebrewDayName(date.getDay())}`
  }
  
  // Create response
  let response = `${dayText} באשקלון, `
  
  // Add morning info if available
  if (morning) {
    response += `בבוקר הגלים ${morning.surfHeightDesc}, גובה ${metersToFeet(morning.waveHeight)} רגל. `
  }
  
  // Add noon info if available
  if (noon) {
    response += `בצהריים ${noon.surfHeightDesc}, גובה ${metersToFeet(noon.waveHeight)} רגל. `
  }
  
  // Add evening info if available
  if (evening) {
    response += `בערב ${evening.surfHeightDesc}, גובה ${metersToFeet(evening.waveHeight)} רגל. `
  }
  
  // Add summary
  response += `ממוצע גובה הגלים ${avgHeightFeet} רגל.`
  
  // Add surf quality assessment (converted thresholds to feet)
  if (avgHeightMeters < 0.4) {
    response += " תנאים לא טובים לגלישה."
  } else if (avgHeightMeters < 0.8) {
    response += " תנאים בסדר לגלישה."
  } else if (avgHeightMeters < 1.5) {
    response += " תנאים טובים לגלישה!"
  } else {
    response += " תנאים מעולים לגלישה!"
  }
  
  return response
}

function getHebrewDayName(dayIndex) {
  const days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
  return days[dayIndex]
}

// =======================
// SHORTCUT INTEGRATION
// =======================

// Check if running as shortcut with parameters
if (args.shortcutParameter) {
  const param = args.shortcutParameter
  let dayOffset = 0
  
  // Parse Hebrew input
  if (param.includes("מחר")) {
    dayOffset = 1
  } else if (param.includes("מחרתיים")) {
    dayOffset = 2
  } else if (param.includes("היום")) {
    dayOffset = 0
  } else {
    // Try to extract day offset from number
    const match = param.match(/\d+/)
    if (match) {
      dayOffset = parseInt(match[0])
    }
  }
  
  const response = await getSurfForecast(dayOffset)
  Script.setShortcutOutput(response)
  Script.complete()
  
} else {
  // Running directly - default to tomorrow
  const response = await getSurfForecast(1)
  console.log(response)
  
  // Show as notification
  const notification = new Notification()
  notification.title = "תחזית גלים למחר"
  notification.body = response
  notification.sound = "default"
  await notification.schedule()
  
  Script.complete()
}
