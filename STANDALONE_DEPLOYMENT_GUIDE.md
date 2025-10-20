# 🌊 Standalone Surf Forecast Deployment Guide

Complete guide for deploying the standalone Ashkelon surf forecast application - No Home Assistant required!

## 📋 Overview

This standalone application provides surf forecasting for Ashkelon beach with multiple deployment options:

- **Standalone Web Service**: Independent Flask app deployable anywhere
- **iOS Widget**: Scriptable app widget with direct API integration
- **Widget API**: JSON API for custom integrations

## 🚀 Quick Deployment Options

### Option 1: Local Development Server

1. **Set up Python environment**:
```bash
cd standalone-widget
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install Playwright browsers**:
```bash
playwright install chromium
```

3. **Run the application**:
```bash
python app.py
```

4. **Access the application**:
- Main interface: http://localhost:8080
- Widget view: http://localhost:8080/widget
- JSON API: http://localhost:8080/api/widget

### Option 2: Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
```

2. **Build and run**:
```bash
docker build -t ashkelon-surf-forecast .
docker run -p 8080:8080 ashkelon-surf-forecast
```

### Option 3: Heroku Deployment

1. **Create Procfile**:
```
web: python app.py
```

2. **Create runtime.txt**:
```
python-3.11.4
```

3. **Deploy to Heroku**:
```bash
# Install Heroku CLI first
heroku create your-surf-forecast-app
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/mxschmitt/heroku-playwright-buildpack.git
git push heroku main
```

### Option 4: Railway Deployment

1. **Connect your GitHub repository to Railway**
2. **Add environment variables** (if needed)
3. **Deploy automatically** - Railway will detect the Flask app

### Option 5: Render Deployment

1. **Create render.yaml**:
```yaml
services:
  - type: web
    name: ashkelon-surf-forecast
    env: python
    buildCommand: "pip install -r requirements.txt && playwright install --with-deps chromium"
    startCommand: "python app.py"
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.4"
```

2. **Connect repository and deploy**

## 📱 iOS Widget Setup (Standalone)

### Requirements
- iOS device with Scriptable app installed
- Internet connection

### Installation Steps

1. **Install Scriptable**: Download from the App Store
2. **Create new script**: Open Scriptable → "+" → Name it "Ashkelon Surf"
3. **Copy the code**: Use the complete code from `IOS_STANDALONE_WIDGET.md`
4. **Configure the script**: Update the API endpoint if you deployed to a custom domain
5. **Add to home screen**: Long press home screen → "+" → Search "Scriptable" → Select your script
6. **Configure widget**: Choose small/medium/large size

### Widget Features
- Direct connection to 4surfers.co.il
- No Home Assistant dependency
- Offline capability with cached data
- Hebrew support with RTL layout
- Auto-refresh every hour
- Beautiful ocean-themed design

## 🔧 Configuration Options

### Environment Variables
```bash
# Optional configurations
export FLASK_ENV=production
export HOST=0.0.0.0
export PORT=8080
export CACHE_DURATION=3600  # Cache duration in seconds
export DEBUG_MODE=false
```

### Custom Domains
If you deploy to a custom domain, update the iOS widget script:
```javascript
// Update this line in the iOS widget code
const API_BASE_URL = 'https://your-domain.com';
```

## 📊 API Endpoints

### GET /
Main application interface with Aguacatec-style cards

### GET /widget
Compact widget view optimized for embedding

### GET /api/widget
JSON API endpoint returning:
```json
{
  "status": "success",
  "data": {
    "days": [...],
    "last_update": "...",
    "offline_mode": false
  }
}
```

## 🎨 Customization

### Styling
- Edit `templates/standalone_index.html` for main interface
- Edit `templates/widget.html` for widget view
- Ocean gradient and wave patterns built-in
- Aguacatec-inspired design with Material Design Icons

### Adding More Beaches
Extend the `StandaloneSurfForecast` class in `app.py`:
```python
def get_forecast_for_beach(self, beach_name):
    # Add support for other Israeli beaches
    pass
```

## 🔍 Monitoring & Debugging

### Health Check Endpoint
```bash
curl http://localhost:8080/api/widget
```

### Debug Mode
Set `DEBUG_MODE=true` to enable:
- Verbose logging
- Screenshot capture on errors
- Extended error messages

### Log Monitoring
The application logs all scraping activities and errors for easy debugging.

## 🌐 Production Considerations

### Performance
- Automatic caching (1 hour default)
- Background data updates
- Efficient Playwright browser management
- Graceful error handling

### Security
- No sensitive data exposure
- CORS headers for API access
- Input validation and sanitization

### Reliability
- Fallback to cached data on errors
- Offline mode indicator
- Retry mechanisms for failed requests
- Browser cleanup and resource management

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: Playwright browser not found
**Solution**: Run `playwright install chromium`

**Issue**: Permission denied on deployment
**Solution**: Ensure proper file permissions and dependencies

**Issue**: iOS widget not updating
**Solution**: Check internet connection and API endpoint accessibility

### Getting Help
- Check the application logs for error messages
- Verify API endpoint is accessible: `/api/widget`
- Test the main interface first: `/`
- Ensure Playwright browsers are properly installed

## 🎯 Next Steps

1. **Deploy to your preferred platform**
2. **Set up iOS widget** with your deployment URL
3. **Customize styling** to match your preferences
4. **Add monitoring** for production deployments
5. **Extend functionality** for additional beaches or features

---

## 🏄‍♂️ Features Summary

✅ **Complete Independence**: No Home Assistant required  
✅ **Multiple Deployment Options**: Local, Docker, Heroku, Railway, Render  
✅ **iOS Widget Support**: Direct Scriptable integration  
✅ **Beautiful UI**: Aguacatec-inspired ocean theme  
✅ **Hebrew Support**: Full RTL and Hebrew surf terminology  
✅ **Offline Capability**: Cached data and offline indicators  
✅ **API Access**: JSON endpoints for custom integrations  
✅ **Auto-refresh**: Configurable update intervals  
✅ **Responsive Design**: Works on all screen sizes  

**Ready to surf! 🏄‍♀️ Deploy your standalone Ashkelon surf forecast today!**