# Neo3 Complete System Deployment Guide

## Overview

Neo3 is a comprehensive AI Agent Marketplace with three main components:
1. **Python Marketplace Service** (Port 8080) - Backend marketplace with agents and academy programs
2. **Express API Gateway** (Port 3000) - Proxy layer for frontend communication
3. **React Frontend** (Port 3000 dev server) - User interface for marketplace and academy

## Prerequisites

### Required Software
- **Python 3.8+** - For the marketplace service
- **Node.js 16+** - For the Express backend and React frontend
- **npm or yarn** - Package manager for Node.js

### Optional
- **Docker & Docker Compose** - For containerized deployment
- **Git** - For version control

## Quick Start (Development)

### 1. Clone the Repository

```bash
git clone https://github.com/jag0414/Neo3.git
cd Neo3
```

### 2. Configure Environment Variables

```bash
# Copy environment examples
cp .env.example .env
cp frontend/.env.example frontend/.env

# Edit .env files if needed (defaults should work for local development)
```

### 3. Start Python Marketplace Service

```bash
# From the Neo3 root directory
python3 web_interface.py
```

**Expected Output:**
```
======================================================================
🎓 Neo3 AI Agent Academy - Web Interface
======================================================================

✓ Server started on http://localhost:8080
✓ Open your browser and visit: http://localhost:8080

Features:
  • Purchase AI agents
  • Rent agents by the hour
  • Enroll agents in elite training programs
  • View certifications and capabilities

Press Ctrl+C to stop the server
======================================================================
```

The marketplace service will be available at: **http://localhost:8080**

### 4. Start Express Backend (New Terminal)

```bash
cd backend
npm install
npm start
```

**Expected Output:**
```
🚀 Neo3 API running on port 3000
```

The API gateway will be available at: **http://localhost:3000**

### 5. Start React Frontend (New Terminal)

```bash
cd frontend
npm install
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

The React app will automatically open in your browser at: **http://localhost:3000**

### 6. Verify System is Running

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Marketplace API**: http://localhost:8080
- **Express API**: http://localhost:3000/health

You should see:
1. Dashboard with service status indicators
2. Navigation tabs: Dashboard | Marketplace | Academy
3. All services showing "healthy" or "running" status

## Using Startup Scripts

For convenience, you can use the provided startup scripts:

### Linux/Mac/WSL

```bash
# Make the script executable
chmod +x scripts/start-all.sh

# Run all services
./scripts/start-all.sh
```

### Windows

```batch
# Run from command prompt or PowerShell
scripts\start-all.bat
```

**Note**: Startup scripts will open multiple terminal windows. Press Ctrl+C in each window to stop services.

## Testing the System

### Test Agent Marketplace

1. Navigate to http://localhost:3000/marketplace
2. You should see 7 agent cards displayed:
   - Analyst Alpha (Finance)
   - Legal Eagle (Legal)
   - Strategy Sigma (Finance)
   - Builder Beta (Construction)
   - Efficiency Epsilon (Environmental)
   - Aviation Ace (Aviation)
   - Health Guardian (Healthcare)

3. **Test Purchase Flow:**
   - Click "Purchase" button on any agent
   - Modal should appear with agent details
   - Default user ID is pre-filled ("demo_user")
   - Click "Confirm Purchase"
   - You should see a success message

4. **Test Rental Flow:**
   - Click "Rent" button on any agent
   - Modal should appear with hourly rate
   - Adjust the hours slider (1-168 hours)
   - Total cost should update in real-time
   - Click "Confirm Rental"
   - You should see success message with rental ID and cost

### Test Academy Programs

1. Navigate to http://localhost:3000/academy
2. You should see 6 program cards:
   - Elite Finance Program (Harvard, Stanford, Wharton)
   - Advanced Legal AI Program (Yale, Harvard, Stanford)
   - Medical Intelligence Program (Johns Hopkins, Stanford, Mayo Clinic)
   - Environmental Science Program (MIT, Stanford, Cambridge)
   - Infrastructure & Construction Program (MIT, Stanford, Georgia Tech)
   - Aviation & Aerospace Program (MIT, Stanford, Embry-Riddle)

3. **Test Enrollment Flow:**
   - Click "Enroll Agent" on any program
   - Modal should appear with program details
   - Enter an agent ID (e.g., "analyst_alpha")
   - Click "Confirm Enrollment"
   - You should see success message with program details

### Test Backend APIs

```bash
# Check API health
curl http://localhost:3000/health

# Get all agents
curl http://localhost:3000/api/marketplace/agents

# Get academy programs
curl http://localhost:3000/api/marketplace/programs

# Purchase agent (POST)
curl -X POST http://localhost:3000/api/marketplace/purchase \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "analyst_alpha", "user_id": "test_user"}'

# Rent agent (POST)
curl -X POST http://localhost:3000/api/marketplace/rent \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "legal_eagle", "user_id": "test_user", "hours": 8}'

# Enroll in program (POST)
curl -X POST http://localhost:3000/api/marketplace/enroll \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "analyst_alpha", "program": "finance"}'
```

## Production Build

### Build React Frontend for Production

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/build/`.

### Serve Production Build

You can serve the production build using:

```bash
# Using serve package
npm install -g serve
serve -s build -p 3001

# Or configure Express to serve static files
# See backend/index.js for static file serving
```

### Environment Variables for Production

Update your `.env` files for production:

```bash
# Root .env
NODE_ENV=production
MARKETPLACE_URL=http://your-marketplace-domain:8080

# frontend/.env
REACT_APP_API_URL=http://your-api-domain:3000
REACT_APP_MARKETPLACE_URL=http://your-marketplace-domain:8080
```

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Access Services (Docker)

- Frontend: http://localhost:3001
- Express API: http://localhost:3000
- Python Marketplace: http://localhost:8080
- PyQMC Service: http://localhost:5000

## Troubleshooting

### Port Already in Use

If you see "Port already in use" errors:

```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Find and kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

**Windows:**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Marketplace Service Unavailable

If frontend shows "Marketplace service unavailable":

1. Verify Python marketplace is running: `curl http://localhost:8080/api/agents`
2. Check if marketplace process is running: `ps aux | grep web_interface`
3. Restart marketplace: `python3 web_interface.py`

### CORS Errors

If you see CORS errors in browser console:

1. Verify Express backend is running
2. Check CORS configuration in `backend/index.js`
3. Ensure frontend is making requests to `http://localhost:3000` (not `http://localhost:8080` directly)

### Module Not Found Errors

If you see module errors:

```bash
# Backend
cd backend
rm -rf node_modules package-lock.json
npm install

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### React Build Fails

If `npm run build` fails:

1. Check Node.js version: `node --version` (should be 16+)
2. Clear cache: `npm cache clean --force`
3. Reinstall dependencies: `rm -rf node_modules && npm install`
4. Try building again: `npm run build`

## System Architecture

```
┌─────────────────────────────────────────────────┐
│   React Frontend (localhost:3000)               │
│   - AgentMarketplace component                  │
│   - AcademyPrograms component                   │
│   - Purchase/Rent modals                        │
│   - Navigation & routing                        │
└─────────────────┬───────────────────────────────┘
                  │
                  │ HTTP Requests
                  │ (CORS enabled)
                  ▼
┌─────────────────────────────────────────────────┐
│   Express Backend (localhost:3000)              │
│   - Proxy to Python marketplace                 │
│   - Health checks                               │
│   - Error handling                              │
│   - Request logging                             │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ Python           │  │ PyQMC Service    │
│ Marketplace      │  │ (Port 5000)      │
│ (Port 8080)      │  │                  │
│ - 7 Agents       │  │ - QMC compute    │
│ - 6 Programs     │  │ - GPU support    │
│ - Purchase/Rent  │  │ - Health checks  │
│ - Enrollment     │  └──────────────────┘
└──────────────────┘
```

## Performance Tips

1. **Development**: Use `npm start` for hot-reloading during development
2. **Production**: Always use `npm run build` and serve the optimized build
3. **Caching**: Configure proper cache headers in production
4. **CDN**: Consider using a CDN for static assets in production
5. **Database**: Consider adding Redis for session caching in high-traffic scenarios

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **API Keys**: Store sensitive keys in environment variables
3. **CORS**: Configure CORS properly for production (restrict origins)
4. **HTTPS**: Use HTTPS in production with valid SSL certificates
5. **Input Validation**: All user inputs are validated on backend
6. **Rate Limiting**: Consider adding rate limiting in production

## Monitoring

### Health Checks

All services provide health check endpoints:

```bash
# Express API
curl http://localhost:3000/health

# Python Marketplace
curl http://localhost:8080/api/agents

# PyQMC Service
curl http://localhost:5000/health
```

### Logs

```bash
# View Express logs
cd backend && npm start

# View React logs
cd frontend && npm start

# View Python logs
python3 web_interface.py
```

## Support

For issues or questions:
1. Check this deployment guide
2. Review the TESTING_GUIDE.md
3. Check the main README.md
4. Open an issue on GitHub

## Next Steps

After successful deployment:
1. Explore the marketplace and purchase/rent agents
2. Enroll agents in academy programs
3. Review agent certifications
4. Customize agents for your needs
5. Integrate with your existing systems

Happy deploying! 🚀
