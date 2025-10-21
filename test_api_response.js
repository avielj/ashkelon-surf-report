// Test script to fetch and display complete API response
// Run this in Scriptable to see all available fields

async function testAPI() {
  try {
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
    request.timeoutInterval = 20
    
    console.log("🔍 Fetching API data...")
    const response = await request.loadJSON()
    
    console.log("✅ API Response received!")
    console.log("\n📦 FULL API RESPONSE:")
    console.log(JSON.stringify(response, null, 2))
    
    // Also check first day's first hour in detail
    if (response.dailyForecastList && response.dailyForecastList.length > 0) {
      const firstDay = response.dailyForecastList[0]
      console.log("\n\n🔍 FIRST DAY DATA:")
      console.log(JSON.stringify(firstDay, null, 2))
      
      if (firstDay.forecastHours && firstDay.forecastHours.length > 0) {
        console.log("\n\n🔍 FIRST HOUR DATA (06:00):")
        const firstHour = firstDay.forecastHours.find(h => h.forecastLocalHour && h.forecastLocalHour.includes("06:00"))
        if (firstHour) {
          console.log(JSON.stringify(firstHour, null, 2))
          
          console.log("\n\n📋 ALL FIELD NAMES IN FIRST HOUR:")
          for (let key in firstHour) {
            if (firstHour.hasOwnProperty(key)) {
              console.log(`  ${key}: ${firstHour[key]} (${typeof firstHour[key]})`)
            }
          }
        }
        
        // Check tomorrow's 06:00
        if (response.dailyForecastList.length > 1) {
          const secondDay = response.dailyForecastList[1]
          console.log("\n\n🔍 TOMORROW'S 06:00 DATA:")
          const tomorrowHour = secondDay.forecastHours.find(h => h.forecastLocalHour && h.forecastLocalHour.includes("06:00"))
          if (tomorrowHour) {
            console.log(JSON.stringify(tomorrowHour, null, 2))
            
            console.log("\n\n📋 ALL FIELD NAMES IN TOMORROW'S 06:00:")
            for (let key in tomorrowHour) {
              if (tomorrowHour.hasOwnProperty(key)) {
                console.log(`  ${key}: ${tomorrowHour[key]} (${typeof tomorrowHour[key]})`)
              }
            }
          }
        }
      }
    }
    
    console.log("\n\n✅ Test complete! Look for the field with 0.6m for today and 0.4m for tomorrow")
    
  } catch (error) {
    console.error("❌ Error:", error)
  }
}

await testAPI()
Script.complete()
