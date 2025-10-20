# 🌊 Vercel Deployment Instructions

## 🚀 Deploy to Vercel in 2 Minutes

### Step 1: Prepare Repository
```bash
# In your standalone-widget directory
git add .
git commit -m "Add Vercel deployment files"
git push origin main
```

### Step 2: Deploy to Vercel
1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Import your repository**: `ashkelon-surf-report`
5. **Set root directory**: `standalone-widget`
6. **Click "Deploy"**

### Step 3: Your URLs
After deployment, you'll get:
- **Main App**: `https://your-app.vercel.app/`
- **Widget View**: `https://your-app.vercel.app/widget`
- **JSON API**: `https://your-app.vercel.app/api/widget`

## 📱 Update iOS Widget

Once deployed, update your iOS Scriptable widget:

```javascript
// Change this line in your iOS widget script:
const API_BASE_URL = 'https://your-vercel-app.vercel.app';
```

## 🔧 Vercel Configuration

The deployment includes:
- ✅ **Serverless Functions**: Optimized for Vercel
- ✅ **Template Support**: Jinja2 templates included
- ✅ **API Endpoints**: JSON API for widget integration
- ✅ **Health Checks**: `/health` endpoint for monitoring

## 📁 File Structure for Vercel

```
standalone-widget/
├── api/
│   ├── index.py          # Main serverless function
│   ├── requirements.txt  # Python dependencies
│   └── templates/        # HTML templates
├── vercel.json          # Vercel configuration
└── runtime.txt          # Python version
```

## ⚡ Features

- **Fast Deploy**: Ready-to-deploy configuration
- **Serverless**: No server management needed
- **Global CDN**: Fast worldwide access
- **Auto-scaling**: Handles traffic spikes
- **HTTPS**: SSL certificate included
- **Custom Domain**: Add your own domain easily

## 🎯 Next Steps

1. **Deploy to Vercel** using the instructions above
2. **Get your Vercel URL** from the deployment dashboard
3. **Update iOS widget** with your new URL
4. **Test the widget** - it should now pull from your Vercel deployment!

## 💡 Tips

- **Custom Domain**: Add a custom domain in Vercel settings
- **Environment Variables**: Add any secrets in Vercel dashboard
- **Analytics**: Enable Vercel Analytics for usage insights
- **Monitoring**: Use the `/health` endpoint for uptime monitoring

**Your surf forecast is now deployed globally! 🏄‍♂️**