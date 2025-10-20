# Setting Up Siri Voice Commands for Surf Forecast 🎤🌊

This guide will help you set up Siri to answer questions about surf conditions in Hebrew.

## 📱 Step 1: Install the Script in Scriptable

1. Open **Scriptable** app
2. Tap **+** to create a new script
3. Copy and paste the entire content from `SIRI_SHORTCUT.js`
4. Rename it to **"Surf Forecast Siri"**
5. Save the script

## 🎙️ Step 2: Create Siri Shortcuts

### Option A: Create Individual Shortcuts (Recommended)

#### Shortcut 1: "מה התחזית למחר?" (What's the forecast tomorrow?)

1. Open **Shortcuts** app
2. Tap **+** to create new shortcut
3. Search for and add **"Run Script"** action
4. Select **"Surf Forecast Siri"** script
5. Under "Text", enter: `מחר`
6. Add **"Show Result"** action
7. Add **"Speak Text"** action and connect the result from the script
8. Tap the settings icon (⚙️) and name it: **"תחזית גלים מחר"**
9. Tap **"Add to Siri"**
10. Record your phrase: **"מה התחזית למחר"** or **"מה גובה הגלים מחר"**

#### Shortcut 2: "מה התחזית היום?" (What's the forecast today?)

1. Create new shortcut
2. Add **"Run Script"** → Select **"Surf Forecast Siri"**
3. Enter text: `היום`
4. Add **"Speak Text"** action
5. Name it: **"תחזית גלים היום"**
6. Add to Siri with phrase: **"מה התחזית היום"** or **"מה גובה הגלים היום"**

#### Shortcut 3: "מה התחזית מחרתיים?" (What's the forecast day after tomorrow?)

1. Create new shortcut
2. Add **"Run Script"** → Select **"Surf Forecast Siri"**
3. Enter text: `מחרתיים`
4. Add **"Speak Text"** action
5. Name it: **"תחזית גלים מחרתיים"**
6. Add to Siri with phrase: **"מה התחזית מחרתיים"**

### Option B: Smart Shortcut with Ask Input (Advanced)

1. Create new shortcut
2. Add **"Ask for Input"** action
   - Prompt: "איזה יום? (היום/מחר/מחרתיים)"
3. Add **"Run Script"** → Select **"Surf Forecast Siri"**
   - Pass "Provided Input" as text
4. Add **"Speak Text"** action with the result
5. Name: **"תחזית גלים"**
6. Add to Siri: **"תחזית גלים"**

## 🗣️ Siri Phrases You Can Use

Once set up, you can say:

### Hebrew Commands:
- **"היי סירי, מה התחזית למחר?"** → "Hey Siri, what's the forecast tomorrow?"
- **"היי סירי, מה גובה הגלים מחר?"** → "Hey Siri, what's the wave height tomorrow?"
- **"היי סירי, מה התחזית היום?"** → "Hey Siri, what's the forecast today?"
- **"היי סירי, תחזית גלים"** → "Hey Siri, surf forecast"
- **"היי סירי, כדאי לגלוש מחר?"** → "Hey Siri, should I surf tomorrow?"

## 📊 What Siri Will Say

Example response in Hebrew:
```
מחר באשקלון, 
בבוקר הגלים קרסול, גובה 0.4 מטר. 
בצהריים הגלים ברך, גובה 0.6 מטר. 
בערב הגלים ברך, גובה 0.7 מטר. 
ממוצע גובה הגלים 0.6 מטר.
תנאים בסדר לגלישה.
```

Translation:
```
Tomorrow in Ashkelon,
In the morning the waves are ankle high, 0.4 meters.
At noon the waves are knee high, 0.6 meters.
In the evening the waves are knee high, 0.7 meters.
Average wave height is 0.6 meters.
Conditions are okay for surfing.
```

## 🎯 Quick Setup Tips

### For Quick Access:
1. Add shortcuts to your **Home Screen**:
   - Long press shortcut → Share → Add to Home Screen
   
2. Add shortcuts to **Back Tap**:
   - Settings → Accessibility → Touch → Back Tap
   - Assign double/triple tap to run the shortcut

3. Add to **Control Center**:
   - Settings → Control Center → Add Shortcuts

### Widget Setup:
You can also add a Shortcuts widget to your home screen that shows your surf forecast shortcuts!

## 🔧 Customization

### Change the Beach:
In `SIRI_SHORTCUT.js`, change:
```javascript
const BEACH_AREA_ID = "80" // Ashkelon
```

Other beach IDs:
- Tel Aviv: "60"
- Netanya: "50"
- Haifa: "30"

### Adjust Response Detail:
Edit the `createHebrewResponse()` function to add/remove information like:
- Wind conditions
- Wave period
- Surf quality ratings

## ❗ Troubleshooting

**Problem**: Siri doesn't recognize Hebrew
- **Solution**: Make sure Hebrew is enabled in Settings → Siri & Search → Language

**Problem**: Script times out
- **Solution**: Check your internet connection, the API needs network access

**Problem**: No data returned
- **Solution**: The API might be down, the script will fall back to a friendly error message

**Problem**: Siri doesn't activate shortcut
- **Solution**: Try re-recording the phrase, make sure Hebrew is the primary language

## 🌟 Advanced Features

You can enhance the script to:
- Send notifications at specific times
- Add weather conditions (from another API)
- Compare multiple beaches
- Track surf conditions over time
- Send to Apple Watch

## 📱 iOS Automation

### Auto Morning Briefing:
1. Open **Shortcuts** app
2. Go to **Automation** tab
3. Create **Personal Automation**
4. Choose **Time of Day** (e.g., 7:00 AM)
5. Add action: **Run Shortcut** → Select your surf forecast shortcut
6. Enable **Run Immediately** (no confirmation needed)

Now Siri will automatically tell you the surf forecast every morning! ☀️🏄‍♂️

## 📚 More Examples

### Family Integration:
Create shortcuts for different family members:
- "Should dad surf tomorrow?" → Checks if conditions are good for experienced surfers
- "Is it safe for kids?" → Checks if conditions are calm

### Planning Shortcuts:
- "Best surf day this week" → Analyzes all 7 days and recommends the best day
- "When should I go?" → Suggests optimal time slots

Enjoy your voice-controlled surf forecasting! 🎤🌊
