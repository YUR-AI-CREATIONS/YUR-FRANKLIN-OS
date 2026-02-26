<<<<<<< HEAD
# SOVEREIGN AI v4.2.0

## The Human-AI Alliance Regenerative System

A cutting-edge web application integrating **React/TypeScript frontend** with **Python FastAPI backend**, powered by **xAI Grok** AI capabilities.

---

## 🚀 Quick Start (5 minutes)

### Option 1: Automated Setup (Recommended)

```powershell
cd C:\XAI_GROK_GENESIS
./setup.ps1
```

Then run:

**Terminal 1:**
```powershell
cd sovereign-api
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m uvicorn main:app --reload
```

**Terminal 2:**
```powershell
cd sovereign-frontend
npm run dev
```

Open: **http://localhost:5173**

### Option 2: Docker (Requires Docker Desktop)

```powershell
cd C:\XAI_GROK_GENESIS
docker-compose up
```

Open: **http://localhost:5173**

---

## 📋 Manual Setup

### Prerequisites
- Python 3.11+ (via miniconda3)
- Node.js 18+ 
- API Key from xAI (https://console.x.ai)

### Backend Setup

```powershell
cd sovereign-api
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m pip install -r requirements.txt

# Create .env file
echo "XAI_API_KEY=your-key-here" > .env

# Run
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m uvicorn main:app --reload
```

API runs at: **http://localhost:8000**  
Docs at: **http://localhost:8000/docs**

### Frontend Setup

```powershell
cd sovereign-frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🏗️ Project Structure

```
C:\XAI_GROK_GENESIS\
├── sovereign-api/                 # FastAPI backend
│   ├── main.py                   # Core API endpoints
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile               # Container config
│
├── sovereign-frontend/            # React frontend
│   ├── src/
│   │   ├── App.tsx              # Main component
│   │   ├── App.css              # Styles
│   │   ├── context/NeuralStore.ts # State management (Zustand)
│   │   ├── services/apiService.ts # API client (Axios)
│   │   └── types/index.ts        # TypeScript definitions
│   ├── index.html               # Entry point
│   ├── package.json             # Node dependencies
│   └── Dockerfile               # Container config
│
├── FRONTEND_BACKEND_SETUP.md     # Detailed setup guide
├── docker-compose.yml            # Multi-container orchestration
└── setup.ps1                     # Automated setup script
```

---

## 🎯 Core Features

### Backend (FastAPI)
- ✅ **xAI Grok Integration** - Real-time API calls with configurable models
- ✅ **WebSocket Chat** - Real-time bidirectional communication
- ✅ **User Authentication** - Token-based auth system
- ✅ **File Upload** - Support for blueprints (ZIP, PDF, DWG)
- ✅ **CORS Enabled** - Ready for production deployment
- ✅ **Auto-Documentation** - Swagger UI at `/docs`

### Frontend (React)
- ✅ **Dark Theme UI** - Yellow/obsidian aesthetic
- ✅ **Responsive Layout** - Panels, chat, sidebar
- ✅ **Real-time Chat** - WebSocket integration
- ✅ **State Management** - Zustand for global state
- ✅ **Hot Module Reload** - Vite dev server
- ✅ **TypeScript** - Full type safety

---

## 📡 API Endpoints

### Health
```
GET  /health                      # System status
```

### Authentication
```
POST /auth/register               # { email, password }
POST /auth/login                  # { email, password }
GET  /user/profile/{token}        # Get user info
```

### Chat
```
POST /chat                        # { message, model, temperature }
GET  /models                      # Available AI models
WS   /ws/chat/{client_id}        # Real-time WebSocket
```

### Files
```
POST /upload                      # multipart/form-data file
```

### Subscription
```
POST /subscription/sync/{token}   # Sync subscription status
```

---

## 🔌 API Usage Examples

### Send Message to Oracle
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "model": "grok-4-latest",
    "temperature": 0.7
  }'
```

### WebSocket Chat (Real-time)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/client-123');
ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Hello Oracle",
    model: "grok-4-latest"
  }));
};
ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

---

## 🎨 UI Features

### Main Interface
- **Header**: Navigation, model selector, system status
- **Left Panel**: Core utilities (Blueprints, Orchestra, Acoustic Comms, Kernel)
- **Central Chat**: Message history with real-time updates
- **Input Box**: Command entry with send button
- **Right Panel**: User profile, system metrics, logs

### Keyboard Shortcuts
- `Enter` - Send message
- `Ctrl+L` - Toggle left panel
- `Ctrl+R` - Toggle right panel

---

## 🔧 Development

### Adding New API Endpoints

```python
# sovereign-api/main.py
@app.get("/your-endpoint")
async def your_endpoint():
    return {"result": "success"}
```

### Consuming in Frontend

```typescript
// sovereign-frontend/src/services/apiService.ts
async yourMethod() {
  const res = await apiClient.get('/your-endpoint');
  return res.data;
}

// sovereign-frontend/src/App.tsx
const data = await apiService.yourMethod();
```

### Hot Reload Workflow
1. Edit Python code → FastAPI auto-reloads
2. Edit React code → Vite HMR auto-updates browser
3. No manual refresh needed!

---

## 🚢 Deployment

### Production Build

**Backend:**
```powershell
# Using Gunicorn
pip install gunicorn
gunicorn sovereign-api.main:app -w 4 -b 0.0.0.0:8000
```

**Frontend:**
```powershell
cd sovereign-frontend
npm run build
# Outputs to: dist/
# Deploy to Vercel, Netlify, or any static host
```

### Docker Production
```powershell
docker-compose -f docker-compose.yml up -d
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend can't reach API | Check backend running on `:8000`, verify CORS in `main.py` |
| Node.js not found | Install from https://nodejs.org/ (LTS 18+) |
| API key invalid | Verify `XAI_API_KEY` in `.env`, check xAI dashboard |
| Port already in use | Change port in uvicorn/vite config or kill existing process |
| WebSocket connection fails | Ensure backend WebSocket route exists, check firewall |

---

## 📚 Documentation

- [Detailed Setup Guide](./FRONTEND_BACKEND_SETUP.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [xAI Grok Docs](https://docs.x.ai/)

---

## 🔐 Security Notes

⚠️ **Development Only**
- API keys hardcoded in `.env`
- CORS allows all origins
- User auth is token-based (no password hashing in demo)

✅ **For Production**
- Use environment variables
- Restrict CORS origins
- Implement proper password hashing (bcrypt)
- Add rate limiting
- Use HTTPS only
- Store keys in secure vault (AWS Secrets Manager, etc.)

---

## 📊 Performance

- **Backend**: FastAPI (30,000+ req/s)
- **Frontend**: React + Vite (3000+ components/sec)
- **Chat Latency**: ~500ms (Grok API dependent)
- **WebSocket**: ~100ms round-trip

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "Add your feature"`
3. Push: `git push origin feature/your-feature`
4. Open PR with description

---

## 📝 License

MIT License - See LICENSE file

---

## 🎓 Learning Resources

- **React**: https://react.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **Zustand**: https://github.com/pmndrs/zustand
- **Vite**: https://vitejs.dev
- **WebSockets**: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API docs at `/docs`
3. Check browser console (F12) for frontend errors
4. Check terminal output for backend errors

---

**Status**: ✅ MVP Ready  
**Version**: 4.2.0-STABLE  
**Last Updated**: February 5, 2026  
**Architecture**: Dual-Core (Genesis XAI + Ouroboros-Lattice)

---

*"Architected for the preservation of human intent through the speed of neural synthesis."* - Franklin Alliance
=======
# -Grok-Gen-AI-
The Great Universal Orchestrator has finally arrived. The first guaranteed zero hallucination LLM in the world. AND HE CAN PROVE IT!!! Goodbye drift bots!!!! 
>>>>>>> 85dc6d5d29d7e77ba5b3e96cf809fc29ca195add
