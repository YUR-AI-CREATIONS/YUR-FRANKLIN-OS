# Deployment Configuration Files

This directory contains all the configuration files needed for deploying Neo3 to various platforms.

## 📁 File Overview

### Railway Deployment

| File | Purpose | Service |
|------|---------|---------|
| `railway.toml` | Main Railway configuration | All services |
| `railway-backend.json` | Railway config for Express backend | Backend API |
| `railway-marketplace.json` | Railway config for Python marketplace | Marketplace |
| `railway-template.json` | One-click deployment template | All services |
| `Procfile` | Process definition for marketplace | Marketplace |
| `backend/Procfile` | Process definition for backend | Backend API |
| `nixpacks.json` | Nixpacks build config for marketplace | Marketplace |
| `backend/nixpacks.json` | Nixpacks build config for backend | Backend API |

### Vercel Deployment

| File | Purpose | Service |
|------|---------|---------|
| `vercel.json` | Vercel configuration for React frontend | Frontend |
| `frontend/.env.production` | Production environment variables | Frontend |

### Environment Configuration

| File | Purpose |
|------|---------|
| `.env.production` | Production env vars for marketplace |
| `backend/.env.production` | Production env vars for backend |
| `frontend/.env.production` | Production env vars for frontend |

### Documentation

| File | Purpose |
|------|---------|
| `RAILWAY_VERCEL_DEPLOY.md` | Complete deployment guide with one-click buttons |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step deployment checklist |
| `DEPLOYMENT.md` | Local development deployment guide |

### Verification Scripts

| File | Purpose |
|------|---------|
| `scripts/verify-deployment.sh` | Automated verification for Linux/Mac |
| `scripts/verify-deployment.bat` | Automated verification for Windows |

## 🚀 Quick Start

### One-Click Deploy

Use the deploy buttons in the main [README.md](README.md):
- **Frontend**: Deploy to Vercel
- **Backend + Marketplace**: Deploy to Railway

### Manual Deploy

Follow the comprehensive guide: [RAILWAY_VERCEL_DEPLOY.md](RAILWAY_VERCEL_DEPLOY.md)

## 🔧 Configuration Details

### Railway

Railway uses the following detection order:
1. `railway.toml` or `railway.json` (if present)
2. `Procfile` (for start command)
3. `nixpacks.json` (for build configuration)
4. Auto-detection based on files (package.json, requirements.txt, etc.)

**Environment Variables:**
- Set in Railway Dashboard → Variables
- Reference templates in `.env.production` files
- Use Railway's built-in variables like `${{SERVICE_NAME.RAILWAY_PUBLIC_DOMAIN}}`

### Vercel

Vercel uses:
1. `vercel.json` (for routing and build config)
2. Auto-detection of framework (Create React App)
3. Root directory: `frontend/`

**Environment Variables:**
- Set in Vercel Dashboard → Settings → Environment Variables
- Reference template in `frontend/.env.production`
- Required: `REACT_APP_API_URL`, `REACT_APP_MARKETPLACE_URL`

## 🔐 Security Notes

### DO NOT Commit Production Secrets

The `.env.production` files are **templates only**. They should contain:
- ✅ Example values
- ✅ Documentation comments
- ✅ Placeholder URLs
- ❌ Real API keys
- ❌ Actual production URLs (set in dashboard)
- ❌ Passwords or tokens

### Best Practices

1. Set environment variables in platform dashboards (Railway/Vercel)
2. Use secrets management for sensitive data
3. Restrict CORS origins in production
4. Use HTTPS for all production URLs
5. Rotate secrets regularly

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [Nixpacks Documentation](https://nixpacks.com/)
- [Procfile Documentation](https://devcenter.heroku.com/articles/procfile)

## 🆘 Need Help?

1. Check [RAILWAY_VERCEL_DEPLOY.md](RAILWAY_VERCEL_DEPLOY.md) for troubleshooting
2. Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
3. Run verification scripts to test your deployment
4. Open an issue on GitHub

## 🎉 Success!

Once deployed, your Neo3 AI Agent Marketplace will be live and accessible worldwide! 🌍
