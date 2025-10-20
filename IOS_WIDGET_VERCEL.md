# 📱 iOS Scriptable Widget for Vercel Deployment

## 🌊 Ashkelon Surf Widget - Connect to Your Vercel Deployment

This widget connects directly to your deployed Vercel surf forecast service.

### 🚀 Quick Setup

1. **Deploy to Vercel** (see VERCEL_DEPLOY.md)
2. **Install Scriptable** app from App Store
3. **Create new script** in Scriptable
4. **Copy the code below**
5. **Update API_BASE_URL** with your Vercel URL
6. **Add widget to home screen**

### 📱 Complete Widget Code

```javascript
// 🌊 Ashkelon Surf Forecast Widget - Vercel Integration
// Connect to your deployed Vercel surf forecast service

// ⚡ CONFIGURATION - UPDATE WITH YOUR VERCEL URL
const API_BASE_URL = 'https://YOUR-APP-NAME.vercel.app'; // 👈 CHANGE THIS!

// Widget configuration
const CACHE_KEY = 'ashkelon_surf_widget_data';
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes
const TIMEOUT = 8000; // 8 second timeout

// Hebrew surf quality colors
const QUALITY_COLORS = {
  'פלטה': new Color('#6B7280'),        // Gray - Flat
  'שטוח': new Color('#6B7280'),        // Gray - Flat
  'קרסול': new Color('#F59E0B'),       // Amber - Ankle
  'קרסול עד ברך': new Color('#F59E0B'), // Amber - Ankle to knee
  'ברך': new Color('#10B981'),         // Green - Knee
  'מעל ברך': new Color('#10B981'),     // Green - Above knee
  'כתף': new Color('#3B82F6'),         // Blue - Shoulder
  'מעל כתף': new Color('#3B82F6'),     // Blue - Above shoulder
  'מותן': new Color('#8B5CF6'),        // Purple - Waist
  'ראש': new Color('#EF4444'),         // Red - Head
  'מעל ראש': new Color('#DC2626')      // Dark red - Overhead
};

// Main widget creation function
async function createWidget() {
  const widget = new ListWidget();
  
  try {
    // Get forecast data from your Vercel deployment
    const data = await fetchSurfData();
    
    if (data && data.success) {
      await setupSuccessWidget(widget, data);
    } else {
      await setupErrorWidget(widget, data?.error || 'No data available');
    }
  } catch (error) {
    console.error('Widget error:', error);
    await setupErrorWidget(widget, 'Connection failed');
  }
  
  return widget;
}

// Fetch surf data from Vercel API
async function fetchSurfData() {
  try {
    console.log('Fetching from:', `${API_BASE_URL}/api/widget`);
    
    const request = new Request(`${API_BASE_URL}/api/widget`);
    request.timeoutInterval = TIMEOUT / 1000;
    request.headers = {
      'User-Agent': 'Ashkelon-Surf-Widget/1.0',
      'Accept': 'application/json'
    };
    
    const response = await request.loadJSON();
    
    if (response) {
      // Cache the successful response
      await cacheData(response);
      return response;
    }
    
    throw new Error('Empty response');
    
  } catch (error) {
    console.error('API fetch failed:', error);
    
    // Try to load from cache
    const cachedData = await loadCachedData();
    if (cachedData) {
      cachedData.offline_mode = true;
      return cachedData;
    }
    
    return null;
  }
}

// Setup successful widget display
async function setupSuccessWidget(widget, data) {
  // Ocean gradient background
  const gradient = new LinearGradient();
  gradient.locations = [0, 1];
  gradient.colors = [new Color('#4f9ded'), new Color('#2c5aa0')];
  widget.backgroundGradient = gradient;
  
  // Header with beach name and date
  const headerStack = widget.addStack();
  headerStack.layoutHorizontally();
  headerStack.centerAlignContent();
  
  // Surf emoji and location
  const locationStack = headerStack.addStack();
  locationStack.layoutHorizontally();
  locationStack.centerAlignContent();
  
  const surfEmoji = locationStack.addText('🏄‍♂️');
  surfEmoji.font = Font.systemFont(20);
  
  locationStack.addSpacer(6);
  
  const beachText = locationStack.addText('אשקלון');
  beachText.font = Font.boldSystemFont(16);
  beachText.textColor = Color.white();
  beachText.rightAlignText();
  
  headerStack.addSpacer();
  
  // Date info
  const dateText = headerStack.addText(data.day || 'היום');
  dateText.font = Font.systemFont(12);
  dateText.textColor = new Color('#E6FBC9');
  dateText.leftAlignText();
  
  widget.addSpacer(12);
  
  // Sessions display
  if (data.sessions && data.sessions.length > 0) {
    const currentSession = data.sessions[0]; // Current/next session
    
    // Current session info
    const sessionStack = widget.addStack();
    sessionStack.layoutHorizontally();
    sessionStack.centerAlignContent();
    
    // Time
    const timeText = sessionStack.addText(currentSession.hebrew_time || currentSession.time);
    timeText.font = Font.boldSystemFont(14);
    timeText.textColor = Color.white();
    
    sessionStack.addSpacer(8);
    
    // Quality with color
    const qualityText = sessionStack.addText(currentSession.quality_hebrew || 'N/A');
    qualityText.font = Font.boldSystemFont(14);
    qualityText.textColor = QUALITY_COLORS[currentSession.quality_hebrew] || Color.white();
    
    sessionStack.addSpacer();
    
    // Wave height
    const heightText = sessionStack.addText(currentSession.height_text || '0.0מ\'');
    heightText.font = Font.boldSystemFont(14);
    heightText.textColor = Color.white();
    
    widget.addSpacer(8);
    
    // Next sessions preview (if available)
    if (data.sessions.length > 1) {
      const nextStack = widget.addStack();
      nextStack.layoutHorizontally();
      nextStack.centerAlignContent();
      
      const nextLabel = nextStack.addText('בהמשך: ');
      nextLabel.font = Font.systemFont(10);
      nextLabel.textColor = new Color('#E6FBC9');
      
      for (let i = 1; i < Math.min(data.sessions.length, 3); i++) {
        const session = data.sessions[i];
        
        if (i > 1) {
          const separator = nextStack.addText(' • ');
          separator.font = Font.systemFont(10);
          separator.textColor = new Color('#E6FBC9');
        }
        
        const sessionInfo = nextStack.addText(`${session.hebrew_time}: ${session.quality_hebrew}`);
        sessionInfo.font = Font.systemFont(10);
        sessionInfo.textColor = QUALITY_COLORS[session.quality_hebrew] || new Color('#E6FBC9');
      }
    }
  } else {
    const noDataText = widget.addText('אין נתונים זמינים');
    noDataText.font = Font.systemFont(14);
    noDataText.textColor = Color.white();
    noDataText.centerAlignText();
  }
  
  widget.addSpacer();
  
  // Footer with update time and offline indicator
  const footerStack = widget.addStack();
  footerStack.layoutHorizontally();
  footerStack.centerAlignContent();
  
  const sourceText = footerStack.addText('📊 4surfers');
  sourceText.font = Font.systemFont(8);
  sourceText.textColor = new Color('#E6FBC9');
  
  footerStack.addSpacer();
  
  if (data.offline_mode) {
    const offlineText = footerStack.addText('⚠️ לא מקוון');
    offlineText.font = Font.systemFont(8);
    offlineText.textColor = new Color('#FCD34D');
  }
  
  const updateText = footerStack.addText(`⏰ ${data.last_update || 'N/A'}`);
  updateText.font = Font.systemFont(8);
  updateText.textColor = new Color('#E6FBC9');
}

// Setup error widget display
async function setupErrorWidget(widget, errorMessage) {
  // Ocean gradient background (same as success)
  const gradient = new LinearGradient();
  gradient.locations = [0, 1];
  gradient.colors = [new Color('#4f9ded'), new Color('#2c5aa0')];
  widget.backgroundGradient = gradient;
  
  widget.addSpacer();
  
  // Error icon
  const errorIcon = widget.addText('⚠️');
  errorIcon.font = Font.systemFont(32);
  errorIcon.centerAlignText();
  
  widget.addSpacer(8);
  
  // Error message
  const errorText = widget.addText('חיבור נכשל');
  errorText.font = Font.boldSystemFont(14);
  errorText.textColor = Color.white();
  errorText.centerAlignText();
  
  widget.addSpacer(4);
  
  const detailText = widget.addText(errorMessage);
  detailText.font = Font.systemFont(10);
  detailText.textColor = new Color('#E6FBC9');
  detailText.centerAlignText();
  
  widget.addSpacer();
  
  // Retry instructions
  const retryText = widget.addText('יתעדכן באופן אוטומטי');
  retryText.font = Font.systemFont(8);
  retryText.textColor = new Color('#E6FBC9');
  retryText.centerAlignText();
}

// Cache management functions
async function cacheData(data) {
  try {
    const cacheData = {
      data: data,
      timestamp: Date.now()
    };
    
    const fm = FileManager.local();
    const cacheFile = fm.joinPath(fm.documentsDirectory(), `${CACHE_KEY}.json`);
    fm.writeString(cacheFile, JSON.stringify(cacheData));
    
    console.log('Data cached successfully');
  } catch (error) {
    console.error('Cache write error:', error);
  }
}

async function loadCachedData() {
  try {
    const fm = FileManager.local();
    const cacheFile = fm.joinPath(fm.documentsDirectory(), `${CACHE_KEY}.json`);
    
    if (!fm.fileExists(cacheFile)) {
      return null;
    }
    
    const cacheContent = fm.readString(cacheFile);
    const cacheData = JSON.parse(cacheContent);
    
    // Check if cache is still valid (30 minutes)
    const age = Date.now() - cacheData.timestamp;
    if (age < CACHE_DURATION) {
      console.log('Using cached data');
      return cacheData.data;
    }
    
    console.log('Cache expired');
    return null;
    
  } catch (error) {
    console.error('Cache read error:', error);
    return null;
  }
}

// Widget presentation logic
if (config.runsInWidget) {
  // Running as a widget
  const widget = await createWidget();
  Script.setWidget(widget);
} else if (config.runsInApp) {
  // Running in the Scriptable app for testing
  const widget = await createWidget();
  
  if (config.widgetFamily === 'small') {
    widget.presentSmall();
  } else if (config.widgetFamily === 'medium') {
    widget.presentMedium();
  } else {
    widget.presentLarge();
  }
} else {
  // Running in Siri or other context
  const data = await fetchSurfData();
  
  if (data && data.success && data.sessions.length > 0) {
    const session = data.sessions[0];
    const speech = `גלים באשקלון: ${session.quality_hebrew}, גובה ${session.height_text}`;
    Speech.speak(speech, 'he-IL');
  } else {
    Speech.speak('אין נתוני גלים זמינים עבור אשקלון', 'he-IL');
  }
}

Script.complete();
```

## 🔧 Setup Instructions

### 1. Deploy Your Vercel App First
Follow the instructions in `VERCEL_DEPLOY.md`

### 2. Get Your Vercel URL
After deployment, copy your Vercel app URL (e.g., `https://my-surf-app.vercel.app`)

### 3. Update Widget Code
Replace `YOUR-APP-NAME.vercel.app` with your actual Vercel URL:
```javascript
const API_BASE_URL = 'https://your-actual-app.vercel.app';
```

### 4. Add to iOS
1. **Open Scriptable app**
2. **Create new script** (tap "+")
3. **Name it**: "Ashkelon Surf"
4. **Paste the updated code**
5. **Save the script**

### 5. Add Widget to Home Screen
1. **Long press** on home screen
2. **Tap "+" (top left)**
3. **Search "Scriptable"**
4. **Choose widget size** (Small recommended)
5. **Add Widget**
6. **Edit widget** → **Script** → Select "Ashkelon Surf"

## ✨ Widget Features

- 🌊 **Real-time data** from your Vercel deployment
- 📱 **Offline support** with local caching
- 🇮🇱 **Hebrew interface** with RTL support
- 🎨 **Beautiful ocean theme** matching Aguacatec style
- ⚡ **Fast updates** every 30 minutes
- 🏄‍♂️ **Surf-optimized** display with quality colors

## 🎯 Benefits of Vercel Integration

✅ **Global CDN**: Fast loading worldwide  
✅ **99.9% Uptime**: Reliable service  
✅ **Auto-scaling**: Handles traffic spikes  
✅ **HTTPS Security**: Secure data transfer  
✅ **No Server Management**: Serverless deployment  
✅ **Custom Domain**: Add your own domain  

Your iOS widget now pulls surf data from your own deployed Vercel service! 🏄‍♂️