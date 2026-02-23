# 🚀 One-Click Deployment Guide for Neo3

Deploy Neo3 to production with just one click! This guide walks you through deploying the complete Neo3 AI Agent Marketplace to Railway and Vercel.

## 🎯 Quick Deploy Overview

Neo3 consists of three deployable services:
1. **Frontend (React)** → Deploy to Vercel ✅
2. **Backend (Express)** → Deploy to Railway ✅
3. **Marketplace (Python)** → Deploy to Railway ✅

## 📦 What You'll Deploy

- **React Frontend**: Modern UI for marketplace and academy (Port 3000)
- **Express Backend**: API gateway with CORS and proxy capabilities (Port 3000)
- **Python Marketplace**: Core backend with 7 AI agents and 6 training programs (Port 8080)

---

## 🚀 One-Click Deployment

### Step 1: Deploy Python Marketplace to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/jag0414/Neo3&referralCode=neo3)

**What this does:**
- Deploys the Python marketplace service (`web_interface.py`)
- Automatically detects Python and installs dependencies
- Sets up health checks at `/api/agents`
- Provides a public URL (e.g., `https://neo3-marketplace.up.railway.app`)

**Environment Variables (Auto-configured):**
- `MARKETPLACE_PORT`: 8080
- `PORT`: Auto-assigned by Railway

**After deployment:**
1. Copy the Railway URL (e.g., `https://neo3-marketplace-xxx.up.railway.app`)
2. Save it for Step 3

---

### Step 2: Deploy Express Backend to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/jag0414/Neo3/tree/main/backend&referralCode=neo3)

**What this does:**
- Deploys the Express API gateway (`backend/index.js`)
- Automatically installs Node.js dependencies
- Sets up health checks at `/health`
- Configures CORS for frontend communication
- Provides a public URL (e.g., `https://neo3-backend.up.railway.app`)

**Required Environment Variables:**
After deployment, add these in Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | Auto-set | Railway provides this automatically |
| `NODE_ENV` | `production` | Sets Node to production mode |
| `MARKETPLACE_URL` | `https://your-marketplace-url.up.railway.app` | URL from Step 1 |
| `CORS_ORIGIN` | `*` | Allow all origins (or restrict to your Vercel domain) |

**After deployment:**
1. Copy the Railway URL (e.g., `https://neo3-backend-xxx.up.railway.app`)
2. Update the `MARKETPLACE_URL` environment variable with URL from Step 1
3. Trigger a redeploy
4. Save the backend URL for Step 3

---

### Step 3: Deploy React Frontend to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/jag0414/Neo3&project-name=neo3-frontend&repository-name=neo3-frontend&root-directory=frontend&env=REACT_APP_API_URL,REACT_APP_MARKETPLACE_URL&envDescription=API%20URLs%20from%20Railway%20deployments&envLink=https://github.com/jag0414/Neo3/blob/main/RAILWAY_VERCEL_DEPLOY.md)

**What this does:**
- Deploys the React frontend from the `frontend/` directory
- Automatically runs `npm install` and `npm run build`
- Serves the optimized production build
- Provides a public URL (e.g., `https://neo3.vercel.app`)

**Required Environment Variables:**
During Vercel setup, you'll be prompted to enter:

| Variable | Value | Example |
|----------|-------|---------|
| `REACT_APP_API_URL` | Backend URL from Step 2 | `https://neo3-backend-xxx.up.railway.app` |
| `REACT_APP_MARKETPLACE_URL` | Marketplace URL from Step 1 | `https://neo3-marketplace-xxx.up.railway.app` |
| `REACT_APP_PYQMC_URL` | (Optional) PyQMC service URL | `https://neo3-pyqmc-xxx.up.railway.app` |

**After deployment:**
1. Visit your Vercel URL
2. Verify all services are connected (Dashboard should show "healthy" status)
3. Update CORS_ORIGIN in Railway backend to your Vercel domain for security

---

## 🔧 Manual Deployment (Alternative)

If you prefer manual control, follow these steps:

### Railway - Python Marketplace

1. **Go to [Railway](https://railway.app/)**
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your forked `Neo3` repository
4. Railway will auto-detect Python
5. Add environment variables:
   - `PORT`: Leave blank (Railway auto-assigns)
   - `MARKETPLACE_PORT`: `8080`
6. Deploy!

### Railway - Express Backend

1. **Create a second Railway service**
2. Select the same repository
3. Set **Root Directory**: `backend`
4. Railway will auto-detect Node.js
5. Add environment variables:
   - `PORT`: Leave blank (Railway auto-assigns)
   - `NODE_ENV`: `production`
   - `MARKETPLACE_URL`: URL from marketplace deployment
   - `CORS_ORIGIN`: `*`
6. Deploy!

### Vercel - React Frontend

1. **Go to [Vercel](https://vercel.com/)**
2. Click "Add New Project" → "Import Git Repository"
3. Select your forked `Neo3` repository
4. Set **Root Directory**: `frontend`
5. Set **Framework Preset**: `Create React App`
6. Add environment variables:
   - `REACT_APP_API_URL`: Backend Railway URL
   - `REACT_APP_MARKETPLACE_URL`: Marketplace Railway URL
7. Click "Deploy"!

---

## 🔐 Post-Deployment Configuration

### 1. Update CORS Settings (Security)

After all services are deployed, update the backend's CORS settings:

**Railway Backend Dashboard:**
1. Go to your backend service
2. Navigate to "Variables"
3. Update `CORS_ORIGIN` from `*` to your Vercel domain:
   ```
   CORS_ORIGIN=https://your-app.vercel.app
   ```
4. Redeploy the service

### 2. Verify All Services

Visit your Vercel frontend URL and check:
- ✅ Dashboard shows all services as "healthy"
- ✅ Marketplace tab loads agent cards
- ✅ Academy tab loads program cards
- ✅ Purchase/Rent functionality works
- ✅ No CORS errors in browser console

### 3. Test the Deployment

Use the automated verification script:

```bash
# Linux/Mac/WSL
./scripts/verify-deployment.sh

# Windows
scripts\verify-deployment.bat
```

Or test manually:

```bash
# Test frontend (Vercel)
curl https://your-app.vercel.app

# Test backend (Railway)
curl https://your-backend.up.railway.app/health

# Test marketplace (Railway)
curl https://your-marketplace.up.railway.app/api/agents
```

---

## 🔄 Continuous Deployment

Both Railway and Vercel support automatic deployments:

### Railway
- **Auto-deploys** on every push to `main` branch
- Configure in Railway dashboard → Settings → Deployments
- Can set up custom branches or PR deployments

### Vercel
- **Auto-deploys** on every push to `main` branch
- Preview deployments for all PRs
- Configure in Vercel dashboard → Settings → Git

---

## 📊 Monitoring & Logs

### Railway Logs

View logs in real-time:
1. Go to Railway dashboard
2. Select your service
3. Click "Deployments" → Select active deployment
4. View logs in the terminal section

### Vercel Logs

View deployment and runtime logs:
1. Go to Vercel dashboard
2. Select your project
3. Click "Deployments" → Select deployment
4. View build logs and runtime logs

---

## 🚨 Troubleshooting

### Issue: Frontend can't connect to backend

**Solution:**
1. Check `REACT_APP_API_URL` in Vercel env vars
2. Verify Railway backend is running: `curl https://backend-url/health`
3. Check CORS settings in backend
4. Redeploy frontend after fixing env vars

### Issue: Backend can't connect to marketplace

**Solution:**
1. Check `MARKETPLACE_URL` in Railway backend env vars
2. Verify marketplace is running: `curl https://marketplace-url/api/agents`
3. Ensure URLs don't have trailing slashes
4. Redeploy backend after fixing env vars

### Issue: Build fails on Railway

**Solution:**
1. Check build logs in Railway dashboard
2. Verify `package.json` has correct dependencies
3. For Python: Ensure `requirements.txt` is present (even if empty)
4. Try manual build locally: `npm install` or `pip install -r requirements.txt`

### Issue: Build fails on Vercel

**Solution:**
1. Check build logs in Vercel dashboard
2. Verify root directory is set to `frontend`
3. Ensure `package.json` has `build` script
4. Check environment variables are set correctly

---

## 💰 Cost Estimation

### Railway (Free Tier)
- **$5 free credit/month** (no credit card required)
- Sufficient for:
  - 2 small services (backend + marketplace)
  - ~100 hours of uptime/month per service
  - 1GB RAM per service

### Vercel (Hobby Tier)
- **Free forever** for personal projects
- Includes:
  - Unlimited deployments
  - 100GB bandwidth/month
  - Automatic HTTPS
  - Global CDN

**Total Cost: $0/month** for small projects! 🎉

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Neo3 Full Deployment Guide](./DEPLOYMENT.md)
- [Neo3 Testing Guide](./TESTING_GUIDE.md)

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Production-ready Neo3 marketplace
- ✅ Automatic deployments on git push
- ✅ HTTPS with custom domains (optional)
- ✅ Global CDN for frontend
- ✅ Health monitoring and logs
- ✅ Zero-downtime deployments

**Your Neo3 AI Agent Marketplace is now live!** 🚀

Share your deployment URL with the world! 🌍

---

## 🤝 Need Help?

- Check the main [README.md](./README.md)
- Review [DEPLOYMENT.md](./DEPLOYMENT.md) for local development
- Open an issue on [GitHub](https://github.com/jag0414/Neo3/issues)

Happy deploying! 🎊
