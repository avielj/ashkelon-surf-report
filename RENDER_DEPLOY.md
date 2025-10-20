# Deploy to Render.com

## Why Render?
- ✅ **100% FREE tier available**
- ✅ **Excellent Python support**
- ✅ **Auto-deploys from GitHub**
- ✅ **Simple configuration**
- ✅ **Better documentation than Vercel**

## Quick Setup (5 minutes)

1. **Go to**: https://render.com
2. **Sign up** with GitHub
3. **New** → **Web Service**
4. **Connect** your `ashkelon-surf-report` repository
5. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python standalone-widget/app.py` or `gunicorn standalone-widget.app:app`
   - **Environment**: Python 3

## Free Tier
- ✅ **Completely FREE** (spins down after 15 min of inactivity)
- Spins back up in ~30 seconds when accessed
- Perfect for demos and personal projects

## Paid Tier ($7/month)
- Always running
- Faster response times
- Custom domains

## Your app will be live at:
`https://ashkelon-surf.onrender.com`

## Configuration File (Optional)

Create `render.yaml` for automatic setup:

```yaml
services:
  - type: web
    name: ashkelon-surf-forecast
    env: python
    buildCommand: pip install -r standalone-widget/requirements.txt
    startCommand: python standalone-widget/app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.4
```
