# � Ashkelon Surf Forecast - Complete Standalone Solutions

This repository provides multiple standalone surf forecasting solutions for Ashkelon beach, completely independent of Home Assistant.

## 🏄‍♂️ Available Solutions

### 1. **Home Assistant Addon** (Optional)
Located in `homeassistant-addon/ashkelon-surf-forecast/`
- Complete Home Assistant integration
- Aguacatec-style surf cards
- Ocean-themed design with Material Design Icons
- Hebrew RTL support

### 2. **Standalone iOS Widget** ⭐ **RECOMMENDED**
Complete Scriptable widget requiring only iOS and internet connection
- **File**: `IOS_STANDALONE_WIDGET.md`
- **Dependencies**: Only iOS Scriptable app
- **Features**: Direct 4surfers.co.il integration, offline cache, Hebrew support

### 3. **Standalone Web Service** ⭐ **RECOMMENDED**
Independent Flask application deployable anywhere
- **Location**: `standalone-widget/`
- **Dependencies**: Python, Playwright
- **Features**: Web interface, widget view, JSON API

## ✨ Key Features

## 🚀 GitHub Actions Setup (Automated Daily Reports)

### 1. Fork/Clone Repository
```bash
git clone https://github.com/avielj/ashkelon-surf-report.git
cd ashkelon-surf-report
```

### 2. Configure Telegram Bot
1. Create a Telegram bot via @BotFather
2. Get your bot token (format: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
3. Add bot to your Telegram channel and make it an admin
4. Get your channel ID (use @userinfobot or check channel_post messages)

### 3. Set GitHub Repository Secrets
In your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add **New repository secret**: 
   - **Name**: `TELEGRAM_BOT_TOKEN`
   - **Value**: Your bot token from step 2
3. Optionally add **TELEGRAM_CHAT_ID** if using a different channel:
   - **Name**: `TELEGRAM_CHAT_ID` 
   - **Value**: Your channel/chat ID (negative number for channels)

### 4. Enable GitHub Actions
The workflow will automatically run daily at 7:00 AM Israel time and send Telegram notifications only when surfable waves (>0.4m) are detected in the next 72 hours.

## 💻 Local Development Setup

### Requirements
- Python 3.11+
- Internet connection

### Installation
1. **Clone repository**:
   ```bash
   git clone https://github.com/avielj/ashkelon-surf-report.git
   cd ashkelon-surf-report
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### Local Usage
```bash
# Set your Telegram bot token (optional for local testing)
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Run the forecast
python wave_forecast.py
```

## 📁 Project Structure

```
├── wave_forecast.py              # Main application 
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
├── .gitignore                    # Git ignore patterns
├── .github/
│   ├── copilot-instructions.md   # AI assistant context
│   └── workflows/
│       └── daily-surf-report.yml # Automated daily execution
└── ENHANCEMENT_SUMMARY.md        # Development history
```

## ⚙️ Configuration

### Hebrew Surf Quality Levels
The system recognizes all surf conditions in Hebrew:
- **פלטה** (flat) - 0-0.1m - No waves
- **שטוח** (flat) - 0.1-0.2m - Flat conditions  
- **קרסול** (ankle) - 0.2-0.4m - Very small waves
- **קרסול עד ברך** (ankle-knee) - 0.5-0.6m - Small waves for beginners
- **ברך** (knee) - 0.7-0.9m - Good waves for surfing
- **מעל ברך** (above knee) - 1.0-1.2m - Great waves
- **כתף** (shoulder) - 1.3-1.5m - Excellent waves
- **מעל כתף** (above shoulder) - 1.6-1.8m - Epic conditions
- **מותן** (waist) - 1.9-2.2m - Big waves
- **ראש** (head) - 2.4-2.8m - Head high
- **מעל ראש** (overhead) - 3.0m+ - Overhead waves

### Smart Notification Logic
- ✅ **Sends Telegram**: When waves >0.4m detected in next 72 hours
- 🔇 **Skips message**: When only small waves (≤0.4m) in next 72 hours
- 📅 **Schedule**: Daily at 7:00 AM Israel time via GitHub Actions

## 🔒 Security

### Environment Variables
The application uses environment variables for security:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required for notifications)
- `TELEGRAM_CHAT_ID`: Your Telegram channel/chat ID (optional, defaults to configured channel)

### For Local Development
```bash
# Set environment variables locally
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="-1001234567890"  # Optional
```

### For GitHub Actions  
Add secrets in your repository settings:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add `TELEGRAM_BOT_TOKEN` as a repository secret
3. Never commit tokens directly to code

**⚠️ Important**: Never commit API tokens, bot tokens, or other credentials to your repository!

## Example Output

```
🌊 Wave Forecast for ashkelon
==================================================
Beach (Hebrew): אשקלון
Source: 4surfers.co.il
Retrieved: 2025-10-19T20:28:34.818250
------------------------------
🏄 Surf Quality: Good
📄 Extracted Content:
Current wave conditions and forecast data...
--------------------------------------------------
```

## Troubleshooting

If the script fails to retrieve data:

1. **Check internet connection**: Ensure you can access https://4surfers.co.il
2. **Site structure changes**: The website may have updated its layout
3. **Rate limiting**: The site might be blocking automated requests
4. **Debug mode**: Set `headless=False` in the code to see browser interaction
5. **Screenshots**: Check generated PNG files for visual debugging

## Development

To extend this application:

1. **Add more beaches**: Update the `beach_slugs` dictionary
2. **Improve parsing**: Enhance the `_parse_forecast_html()` method
3. **Add visualization**: Use matplotlib/seaborn for charts
4. **API integration**: Consider using official APIs if available
5. **Caching**: Add data caching to reduce website load

## Legal Considerations

- Always respect the target website's robots.txt
- Implement appropriate rate limiting
- Consider the website's terms of service
- Use proper attribution if required

## License

This project is provided as-is for educational and personal use.