# Neo3 Deployment Checklist

Use this checklist when deploying Neo3 to production.

## Pre-Deployment

- [ ] Fork or clone the Neo3 repository
- [ ] Review the [RAILWAY_VERCEL_DEPLOY.md](RAILWAY_VERCEL_DEPLOY.md) guide
- [ ] Create accounts on:
  - [ ] [Railway](https://railway.app/) (for backend services)
  - [ ] [Vercel](https://vercel.com/) (for frontend)

## Deployment Steps

### 1. Deploy Python Marketplace to Railway

- [ ] Click "Deploy on Railway" button or create new Railway project
- [ ] Connect your GitHub repository
- [ ] Railway will auto-detect Python
- [ ] Verify environment variables:
  - [ ] `PORT` - Auto-assigned by Railway ✓
  - [ ] `MARKETPLACE_PORT` - Optional (8080)
- [ ] Wait for deployment to complete
- [ ] Copy the Railway public URL (e.g., `https://neo3-marketplace-xxx.up.railway.app`)
- [ ] Test the endpoint: `curl https://your-url/api/agents`

### 2. Deploy Express Backend to Railway

- [ ] Create a second Railway service
- [ ] Connect the same repository
- [ ] Set **Root Directory** to `backend`
- [ ] Railway will auto-detect Node.js
- [ ] Configure environment variables:
  - [ ] `PORT` - Auto-assigned by Railway ✓
  - [ ] `NODE_ENV` - Set to `production`
  - [ ] `MARKETPLACE_URL` - Use URL from Step 1
  - [ ] `CORS_ORIGIN` - Set to `*` initially
- [ ] Wait for deployment to complete
- [ ] Copy the Railway public URL (e.g., `https://neo3-backend-xxx.up.railway.app`)
- [ ] Test the endpoint: `curl https://your-url/health`

### 3. Deploy React Frontend to Vercel

- [ ] Click "Deploy with Vercel" button or create new Vercel project
- [ ] Connect your GitHub repository
- [ ] Set **Root Directory** to `frontend`
- [ ] Set **Framework Preset** to `Create React App`
- [ ] Configure environment variables:
  - [ ] `REACT_APP_API_URL` - Use URL from Step 2
  - [ ] `REACT_APP_MARKETPLACE_URL` - Use URL from Step 1
  - [ ] `REACT_APP_PYQMC_URL` - Optional
- [ ] Click "Deploy"
- [ ] Wait for build and deployment to complete
- [ ] Copy the Vercel URL (e.g., `https://neo3.vercel.app`)

## Post-Deployment

### Security Configuration

- [ ] Update Railway backend `CORS_ORIGIN` from `*` to your Vercel domain:
  ```
  CORS_ORIGIN=https://your-app.vercel.app
  ```
- [ ] Trigger a redeploy of the backend service
- [ ] Never commit `.env` files with production values

### Verification

- [ ] Visit your Vercel URL
- [ ] Check Dashboard tab:
  - [ ] All services show "healthy" status
  - [ ] No errors in browser console
- [ ] Test Marketplace tab:
  - [ ] Agent cards load successfully
  - [ ] Purchase flow works
  - [ ] Rent flow works
- [ ] Test Academy tab:
  - [ ] Program cards load successfully
  - [ ] Enrollment flow works
- [ ] Run automated verification script:
  ```bash
  # Linux/Mac/WSL
  ./scripts/verify-deployment.sh
  
  # Windows
  scripts\verify-deployment.bat
  ```
- [ ] Or test API endpoints manually:
  ```bash
  # Frontend
  curl https://your-app.vercel.app
  
  # Backend health
  curl https://your-backend.up.railway.app/health
  
  # Marketplace agents
  curl https://your-marketplace.up.railway.app/api/agents
  
  # Backend proxy to marketplace
  curl https://your-backend.up.railway.app/api/marketplace/agents
  ```

### Configure Auto-Deployments

- [ ] Railway: Enable auto-deploy on push to `main` branch
- [ ] Vercel: Enable auto-deploy on push to `main` branch
- [ ] Vercel: Enable preview deployments for PRs

### Monitoring

- [ ] Set up Railway log monitoring
- [ ] Set up Vercel analytics (optional)
- [ ] Configure uptime monitoring (optional):
  - [UptimeRobot](https://uptimerobot.com/)
  - [Pingdom](https://www.pingdom.com/)
  - [Better Uptime](https://betteruptime.com/)

## Custom Domain (Optional)

### Vercel Custom Domain

- [ ] Go to Vercel project settings → Domains
- [ ] Add your custom domain (e.g., `neo3.yourdomain.com`)
- [ ] Follow DNS configuration instructions
- [ ] Wait for SSL certificate provisioning
- [ ] Update Railway backend `CORS_ORIGIN` to new domain

### Railway Custom Domain

- [ ] Go to Railway service settings → Domains
- [ ] Add custom domain for backend (e.g., `api.yourdomain.com`)
- [ ] Add custom domain for marketplace (e.g., `marketplace.yourdomain.com`)
- [ ] Follow DNS configuration instructions
- [ ] Update Vercel environment variables with new domains
- [ ] Redeploy frontend

## Troubleshooting

If issues occur, check:

- [ ] All environment variables are set correctly
- [ ] No trailing slashes in URLs
- [ ] Services are running in Railway dashboard
- [ ] Build logs for any errors
- [ ] CORS configuration is correct
- [ ] URLs are using HTTPS (not HTTP)

## Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Neo3 Deployment Guide](RAILWAY_VERCEL_DEPLOY.md)
- [Neo3 Local Development Guide](DEPLOYMENT.md)

## Success! 🎉

Your Neo3 AI Agent Marketplace is now live in production!

- Frontend: https://your-app.vercel.app
- Backend: https://your-backend.up.railway.app
- Marketplace: https://your-marketplace.up.railway.app

Share your deployment with the world! 🌍
