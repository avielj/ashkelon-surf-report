# GitHub Actions Setup Guide

## Overview
The repository includes a GitHub Actions workflow that automatically sends daily surf reports via Telegram at 7:00 AM GMT+2.

## Required GitHub Secrets

You need to configure two secrets in your GitHub repository:

### 1. TELEGRAM_BOT_TOKEN
This is your Telegram bot token from BotFather.

**To get your bot token:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to create a new bot (or use existing bot)
3. Follow the instructions to name your bot
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. TELEGRAM_CHAT_ID
This is the chat/channel ID where messages will be sent.

**Current default value:** `-1002522870307` (your channel)

**To find your chat ID (if needed):**
1. Add your bot to the channel/group
2. Send a message in the channel
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":-1001234567890,...}`

## Adding Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add both secrets:
   - Name: `TELEGRAM_BOT_TOKEN`, Value: your bot token
   - Name: `TELEGRAM_CHAT_ID`, Value: your chat ID

## Testing the Workflow

### Manual Test (Recommended)
1. Go to **Actions** tab in GitHub
2. Click **Daily Surf Report** workflow
3. Click **Run workflow** → **Run workflow**
4. Check the workflow run for errors
5. Verify message received in Telegram

### Automatic Schedule
- Runs daily at **5:00 AM UTC** = **7:00 AM Israel time (GMT+2 in winter)**
- Note: During daylight saving time (GMT+3), this will be 8:00 AM

## Message Logic

The script checks the next 72 hours (3 days) of forecasts:

### If waves exist (≥1.0ft):
```
🏄‍♂️ תחזית גלים - אשקלון 🌊

📅 רביעי 22/10
  🕐 06:00: ⭐⭐ 2.3ft (ברך) ⏱️ 7s 💨 12kts
  🕐 09:00: ⭐ 1.8ft (קרסול) ⏱️ 6s 💨 10kts
  ...

📊 מקור: 4surfers.co.il
```

### If no waves (<1.0ft):
```
אין גלים בימים הקרובים 🏖️
```

## Troubleshooting

### Check workflow logs:
1. Go to **Actions** tab
2. Click on the failed workflow run
3. Click on **surf-report** job
4. Expand **Run daily surf report** step

### Common issues:

**"TELEGRAM_BOT_TOKEN environment variable not set"**
- Secret not configured in GitHub
- Secret name has typo (must be exact)

**"403 Forbidden" from API**
- API might be blocking GitHub Actions IPs
- Usually temporary - retry will work

**"Message send failed"**
- Bot not added to channel
- Bot doesn't have post permission
- Wrong chat ID

## Files Used by Workflow

- `.github/workflows/daily-surf-report.yml` - Workflow definition
- `daily_surf_report.py` - Main script
- `requirements.txt` - Python dependencies (only `requests`)

## How It Works

1. **Fetch Forecast**: GET request to 4surfers.co.il API
2. **Parse Data**: Extract next 3 days, 4 time slots each (06:00, 09:00, 12:00, 18:00)
3. **Check Waves**: Look for any session with waves ≥1.0ft
4. **Format Message**: Generate Hebrew message with surf conditions
5. **Send Telegram**: POST to Telegram Bot API

## Script Output Example

When workflow runs successfully:
```
🏄‍♂️ Daily Surf Report - Ashkelon
==================================================
📡 Fetching forecast from 4surfers.co.il...
📊 Parsing forecast data...
✅ Got 3 days of forecast

📝 Message to send:
--------------------------------------------------
אין גלים בימים הקרובים 🏖️
--------------------------------------------------

📱 Sending to Telegram...
✅ Telegram message sent successfully!
✅ Daily report completed successfully!
```

## Manual Testing Locally

To test without Telegram:
```bash
python3 test_daily_report.py
```

To test with Telegram (requires bot token):
```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
export TELEGRAM_CHAT_ID="-1002522870307"
python3 daily_surf_report.py
```
