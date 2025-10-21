// Quick test to see all API fields
// Run this in Scriptable to see what fields are available

async function testAPI() {
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
  request.body = JSON.stringify({ beachAreaId: "80" })
  
  const response = await request.loadJSON()
  
  if (response && response.dailyForecastList && response.dailyForecastList[0]) {
    const firstDay = response.dailyForecastList[0]
    const firstHour = firstDay.forecastHours ? firstDay.forecastHours[0] : null
    
    if (firstHour) {
      console.log("=== ALL FIELDS IN FORECAST HOUR ===")
      console.log(JSON.stringify(firstHour, null, 2))
      console.log("\n=== FIELD NAMES ===")
      console.log(Object.keys(firstHour).join("\n"))
      
      // Show the forecast data
      const alert = new Alert()
      alert.title = "API Fields Found"
      alert.message = "Fields:\n" + Object.keys(firstHour).join("\n")
      await alert.present()
    }
  }
}

await testAPI()
