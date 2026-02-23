# 🚀 Quick Deploy Reference

## One-Click Deployment (Recommended)

### Step 1: Deploy to Railway (Backend Services)
Click here → [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/jag0414/Neo3)

This deploys:
- ✅ Python Marketplace (Port 8080)
- ✅ Express Backend (Port 3000)

**After deployment:**
1. Copy the Railway URLs from your dashboard
2. Note: You'll get 2 services with URLs like:
   - Backend: `https://neo3-backend-xxx.up.railway.app`
   - Marketplace: `https://neo3-marketplace-xxx.up.railway.app`

### Step 2: Deploy to Vercel (Frontend)
Click here → [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/jag0414/Neo3&project-name=neo3-frontend&repository-name=neo3-frontend&root-directory=frontend)

This deploys:
- ✅ React Frontend

**During setup, add these environment variables:**
```
REACT_APP_API_URL=https://neo3-backend-xxx.up.railway.app
REACT_APP_MARKETPLACE_URL=https://neo3-marketplace-xxx.up.railway.app
```

### Step 3: Test Your Deployment
Run the verification script:
```bash
./scripts/verify-deployment.sh  # Linux/Mac
scripts\verify-deployment.bat    # Windows
```

---

## Manual Deployment

### Railway

1. Go to [railway.app](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub"
3. Select `Neo3` repository
4. Create two services:
   - **Service 1 (Marketplace)**: Root directory = `.` (Python auto-detected)
   - **Service 2 (Backend)**: Root directory = `backend` (Node.js auto-detected)
5. Set environment variables in Railway dashboard
6. Copy the public URLs

### Vercel

1. Go to [vercel.com](https://vercel.com/)
2. Click "Add New" → "Project"
3. Import `Neo3` repository
4. Configure:
   - Root Directory: `frontend`
   - Framework: Create React App
   - Environment Variables: Add Railway URLs
5. Click "Deploy"

---

## Environment Variables Quick Reference

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend.up.railway.app
REACT_APP_MARKETPLACE_URL=https://your-marketplace.up.railway.app
```

### Backend (Railway)
```
NODE_ENV=production
MARKETPLACE_URL=https://your-marketplace.up.railway.app
CORS_ORIGIN=*
```

### Marketplace (Railway)
```
# No environment variables required
# Railway auto-assigns PORT
```

---

## Common Issues & Quick Fixes

### ❌ Frontend shows "Service Unavailable"
**Fix:** Check environment variables in Vercel have correct Railway URLs

### ❌ CORS Errors in Browser
**Fix:** Verify `CORS_ORIGIN=*` is set in Railway backend variables

### ❌ Backend can't reach Marketplace
**Fix:** Ensure `MARKETPLACE_URL` in backend points to marketplace Railway URL (no trailing slash)

### ❌ 404 on Frontend Routes
**Fix:** Vercel should auto-configure SPA routing. Check `vercel.json` is present

---

## Testing Checklist

After deployment, test:
- [ ] Frontend loads: `https://your-app.vercel.app`
- [ ] Dashboard shows all services healthy
- [ ] Can view agents in Marketplace tab
- [ ] Can view programs in Academy tab
- [ ] Purchase/Rent modals work
- [ ] No errors in browser console

---

## Cost

### Free Tier Limits

**Railway:**
- $5 free credit/month
- No credit card required
- ~100 hours runtime/service/month

**Vercel:**
- Free forever for hobby projects
- 100GB bandwidth/month
- Unlimited deployments

**Total: $0/month** for small-scale projects! 🎉

---

## Need More Help?

📖 **Detailed Guides:**
- [Complete Deployment Guide](RAILWAY_VERCEL_DEPLOY.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Deployment Files Reference](DEPLOYMENT_FILES.md)
- [Local Development](DEPLOYMENT.md)

🔧 **Tools:**
- [Verification Script](scripts/verify-deployment.sh)
- [GitHub Actions Template](.github/workflows/ci-cd.yml.template)

💬 **Support:**
- [GitHub Issues](https://github.com/jag0414/Neo3/issues)
- [Railway Docs](https://docs.railway.app/)
- [Vercel Docs](https://vercel.com/docs)

---

## Success! 🎊

Your Neo3 AI Agent Marketplace is now live at:
- 🌐 **Frontend:** https://your-app.vercel.app
- ⚙️ **Backend:** https://your-backend.up.railway.app
- 🛒 **Marketplace:** https://your-marketplace.up.railway.app

Share it with the world! 🚀
