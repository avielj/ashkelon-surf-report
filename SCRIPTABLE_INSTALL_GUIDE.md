# 🌊 Complete Scriptable Surf Widget - Installation Guide

## ✨ What This Widget Does

- **✅ Fetches REAL data** from 4surfers.co.il API
- **✅ Shows today's forecast** (morning, noon, evening)
- **✅ Beautiful Aguacatec-style design**
- **✅ Auto-refreshes every 30 minutes**
- **✅ Works 100% offline** (with cached/mock data)
- **✅ No server needed!** Everything runs on your iPhone

## 📱 Installation (2 Minutes)

### Step 1: Install Scriptable App
1. Download **Scriptable** from the App Store (FREE)
2. Open the app

### Step 2: Create New Script
1. Tap the **+** button (top right)
2. Tap on "Untitled Script"
3. Give it a name: **"Ashkelon Surf"**

### Step 3: Copy the Code
1. Open the file: `COMPLETE_SCRIPTABLE_WIDGET.js`
2. **Select ALL** the code (Cmd+A)
3. **Copy** it (Cmd+C)
4. Go back to Scriptable
5. **Paste** the code into your new script
6. Tap **Done**

### Step 4: Test It
1. Tap the ▶️ **Run** button
2. You should see a beautiful surf forecast!

### Step 5: Add to Home Screen
1. Go to your iPhone **Home Screen**
2. **Long press** anywhere to enter edit mode
3. Tap the **+** button (top left)
4. Search for **"Scriptable"**
5. Choose **Medium** size widget
6. Add to home screen
7. **Tap on the widget** to configure
8. Select **"Ashkelon Surf"** script
9. Tap outside to save

## 🎨 Features

### Live Data
- Connects to 4surfers.co.il API
- Shows real wave heights
- Hebrew surf quality terms
- Wave period information

### Beautiful Design
- Ocean gradient background
- Aguacatec-style cards
- Hebrew text (RTL)
- Material Design icons
- Responsive layout

### Smart Fallback
- If API fails, shows demo data
- Works without internet
- Auto-refreshes when online

## 🔧 Customization

Edit these values at the top of the script:

```javascript
const BEACH_NAME = "אשקלון"  // Change beach name
const BEACH_NAME_EN = "Ashkelon"  // English name
const REFRESH_INTERVAL = 30  // Minutes between updates
```

## 📊 Widget Sizes

### Medium Widget (Recommended)
- Shows 3 sessions: morning, noon, evening
- Best for home screen
- Beautiful card layout

### Small Widget
The code can be adapted for small widget by showing only current session.

### Large Widget
Can be extended to show multiple days.

## 🌊 What You'll See

```
🌊 אשקלון                    🔴 LIVE
   ה' • 20/10

┌─────────┬─────────┬─────────┐
│  בוקר   │  צהרים  │   ערב   │
│ 0.5מ'   │ 0.7מ'   │ 0.4מ'   │
│ קרסול   │  ברך    │ קרסול   │
│   8s    │   9s    │   7s    │
└─────────┴─────────┴─────────┘

⏰ 15:30              📊 4surfers
```

## 🆘 Troubleshooting

### Widget shows error
- Check internet connection
- Widget will show demo data if API fails
- Tap the widget to refresh

### Widget not updating
- Long press widget → Edit Widget → Done
- This forces a refresh

### Code not working
- Make sure you copied ALL the code
- Check for any copy/paste errors
- Try running in Scriptable app first

## 🎯 Advantages Over Web Version

1. **✅ No server needed** - Runs entirely on iPhone
2. **✅ Faster** - No waiting for server response
3. **✅ Works offline** - Caches last data
4. **✅ Free forever** - No hosting costs
5. **✅ More reliable** - No server downtime
6. **✅ Native iOS** - Smooth animations
7. **✅ Better battery** - Scriptable is optimized

## 📝 Notes

- Widget auto-refreshes every 30 minutes
- Tap widget to open Scriptable for manual refresh
- Data comes directly from 4surfers.co.il
- All processing happens on your device
- Zero privacy concerns - no data sent anywhere

## 🚀 This is the BEST Solution!

No need for Vercel, Railway, or any hosting service. Everything runs natively on your iPhone with real-time data from 4surfers.co.il!

Enjoy your beautiful Ashkelon surf forecast! 🏄‍♂️🌊
