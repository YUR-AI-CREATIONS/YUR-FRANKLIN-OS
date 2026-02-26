# SOVEREIGN AI - Frontend + Backend Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  SOVEREIGN AI v4.2.0                     │
│              React Frontend + Python FastAPI            │
└─────────────────────────────────────────────────────────┘

Frontend (React/TypeScript)
  ├─ UI: Dark theme with yellow accents
  ├─ State: Zustand store
  ├─ API Client: Axios with WebSocket support
  ├─ Port: http://localhost:5173

Backend (FastAPI/Python)
  ├─ xAI Grok Integration
  ├─ User Authentication
  ├─ WebSocket Chat (real-time)
  ├─ File Upload/Processing
  ├─ Port: http://localhost:8000

Integration
  ├─ CORS enabled
  ├─ Proxy routing (dev)
  ├─ JWT authentication ready
```

---

## Backend Setup (Python FastAPI)

### 1. Install Backend Dependencies

```powershell
cd C:\XAI_GROK_GENESIS\sovereign-api
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` in `sovereign-api/`:
```
XAI_API_KEY=xai-IraELamvOAkhJGrUOoLQSJJ5JmRRsMb2CorODPs040qenCsRAsrGxTQOSMWPSkXKmsvwSSDfVuy2lLkf
```

### 3. Run Backend Server

```powershell
cd C:\XAI_GROK_GENESIS\sovereign-api
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ API will be at `http://localhost:8000`  
📚 Docs at `http://localhost:8000/docs` (Swagger UI)

---

## Frontend Setup (React + Vite)

### 1. Install Node.js Dependencies

You'll need Node.js 18+. Check: `node --version`

```powershell
cd C:\XAI_GROK_GENESIS\sovereign-frontend
npm install
```

### 2. Configure Environment

Create `.env` in `sovereign-frontend/`:
```
REACT_APP_API_URL=http://localhost:8000
```

### 3. Run Development Server

```powershell
cd C:\XAI_GROK_GENESIS\sovereign-frontend
npm run dev
```

✅ Frontend will be at `http://localhost:5173`

---

## Running Both Services Together

### Terminal 1 - Start Backend:
```powershell
cd C:\XAI_GROK_GENESIS\sovereign-api
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m uvicorn main:app --reload
```

### Terminal 2 - Start Frontend:
```powershell
cd C:\XAI_GROK_GENESIS\sovereign-frontend
npm run dev
```

### Open Browser:
Navigate to `http://localhost:5173`

---

## API Endpoints

### Health & Status
- `GET /health` - System status

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /user/profile/{token}` - Get user profile

### Chat
- `POST /chat` - Send message to Oracle
- `GET /models` - Get available AI models
- `WebSocket /ws/chat/{client_id}` - Real-time chat

### Files
- `POST /upload` - Upload blueprints/documents

### Subscription
- `POST /subscription/sync/{token}` - Sync subscription status

---

## Frontend Components Architecture

```
src/
├── App.tsx                    # Main component
├── App.css                    # Global styles
├── main.tsx                   # Entry point
├── context/
│   └── NeuralStore.ts        # Zustand state management
├── services/
│   └── apiService.ts         # Axios client + WebSocket
├── types/
│   └── index.ts              # TypeScript interfaces
└── components/               # (Extensible for complex UIs)
```

---

## State Management (Zustand)

### Core State (`NeuralStore`)
```typescript
{
  user: User | null;
  activeNode: {
    history: ChatMessage[];
    model: string;
  };
  windows: WindowConfig[];    // For future window management
  activeWindowId: string;
  neonTheme: { color: string; name: string };
  logs: string[];
  centralBrainDNA: string;
}
```

### Usage in Components
```typescript
const store = useNeuralStore();
store.addLog('MESSAGE_HERE');
store.dispatch({ type: 'ADD_MESSAGE', payload: msg });
```

---

## Key Features

✅ **xAI Grok Integration** - Direct API calls to xAI  
✅ **Real-time Chat** - WebSocket support for live responses  
✅ **User Authentication** - Token-based auth system  
✅ **File Upload** - Support for blueprints (ZIP, PDF, DWG)  
✅ **Responsive UI** - Dark theme optimized for long sessions  
✅ **CORS Enabled** - Cross-origin requests ready  
✅ **Production Ready** - FastAPI + Vite production builds  

---

## Development Workflow

### Making API Changes
1. Edit `sovereign-api/main.py`
2. FastAPI auto-reloads on save
3. Check `http://localhost:8000/docs`

### Making UI Changes
1. Edit `sovereign-frontend/src/App.tsx` or components
2. Vite HMR auto-refreshes browser
3. Changes visible instantly

### Adding New Endpoints
```python
# In sovereign-api/main.py
@app.post("/your-endpoint")
async def your_endpoint(req: YourModel):
    # Your logic here
    return {"result": "success"}
```

### Calling New Endpoints
```typescript
// In sovereign-frontend/src/services/apiService.ts
async yourMethod(params: any) {
  const res = await apiClient.post('/your-endpoint', params);
  return res.data;
}

// Use in component:
const data = await apiService.yourMethod(stuff);
```

---

## Troubleshooting

### Frontend can't connect to backend
- ✅ Check backend is running on `http://localhost:8000`
- ✅ Check `.env` has correct `REACT_APP_API_URL`
- ✅ Check CORS is enabled in `sovereign-api/main.py`

### API Key not working
- ✅ Verify `XAI_API_KEY` in `.env`
- ✅ Check key hasn't expired in xAI dashboard
- ✅ Monitor logs: `http://localhost:8000/docs` > Try it out

### Node/npm not found
- ✅ Install Node.js from https://nodejs.org/ (LTS recommended)
- ✅ Restart terminal after install
- ✅ Verify: `node --version` && `npm --version`

---

## Building for Production

### Backend
```powershell
# Create production binary
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m pip install gunicorn
gunicorn sovereign-api.main:app -w 4 -b 0.0.0.0:8000
```

### Frontend
```powershell
cd C:\XAI_GROK_GENESIS\sovereign-frontend
npm run build
# Output in dist/
```

---

## Next Steps

1. ✅ Run both servers locally
2. ✅ Test chat with Oracle
3. ✅ Add user registration/login UI
4. ✅ Integrate file upload component
5. ✅ Add window management (draggable, resizable)
6. ✅ Deploy to production

---

**Status:** MVP Ready  
**Version:** 4.2.0-STABLE  
**Last Updated:** February 5, 2026
