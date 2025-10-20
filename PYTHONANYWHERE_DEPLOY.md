# Deploy to PythonAnywhere

## Why PythonAnywhere?
- ✅ **100% FREE tier (forever)**
- ✅ **Specifically designed for Python web apps**
- ✅ **Simple web-based interface**
- ✅ **No credit card required**
- ✅ **Perfect for Flask apps**

## Quick Setup (10 minutes)

### Step 1: Sign Up
1. Go to: https://www.pythonanywhere.com
2. Create a **free account** (no credit card needed)
3. Username becomes your URL: `username.pythonanywhere.com`

### Step 2: Clone Your Repo
1. Open a **Bash console** (from dashboard)
2. Run:
```bash
git clone https://github.com/avielj/ashkelon-surf-report.git
cd ashkelon-surf-report
```

### Step 3: Install Dependencies
```bash
cd standalone-widget
pip3 install --user -r requirements.txt
pip3 install --user playwright
playwright install
```

### Step 4: Setup Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**
5. Configure:
   - **Source code**: `/home/username/ashkelon-surf-report/standalone-widget`
   - **Working directory**: same
   - **WSGI file**: Edit and add:

```python
import sys
path = '/home/username/ashkelon-surf-report/standalone-widget'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

6. Click **Reload** and visit your URL!

## Your app will be live at:
`https://username.pythonanywhere.com`

## Free Tier Limits
- ✅ One web app
- ✅ Always running (doesn't spin down)
- ✅ 512MB storage
- ✅ Good enough for this project!

## Upgrade ($5/month)
- Custom domain
- More CPU time
- HTTPS on custom domains
