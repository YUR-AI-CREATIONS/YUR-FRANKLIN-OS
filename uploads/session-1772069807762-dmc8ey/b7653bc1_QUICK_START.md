# 🎯 YUR + SOVEREIGN AI Integration - QUICK START

## ⚡ LIVE STATUS
```
✅ Integration Bridge:         http://localhost:8001     (ACTIVE)
✅ SOVEREIGN UI:               http://localhost:5173      (ACTIVE) 
✅ YUR Marketplace:            http://localhost:8080      (ACTIVE)
✅ YUR Backend:                http://localhost:3000      (ACTIVE)
✅ YUR PyQMC:                  http://localhost:5000      (ACTIVE)
```

---

## 🚀 START HERE

### **1. Open the Unified Orchestrator**
```
👉 http://localhost:5173
```

### **2. Navigate to Orchestrator**
- Click **"Unified Orchestrator"** in the left sidebar
- You'll see the Orchestrate, Execute, and Monitor tabs

### **3. Try Your First Multi-Agent Workflow**

#### **Example: Financial Analysis**
```
Primary Agent:      analyst_alpha (Research specialist)
Secondary Agents:   ☐ innovation_lab (Strategy optimizer)
                    ☐ legal_eagle (Compliance checker)
Task Name:          Q1 Financial Review
Description:        Analyze quarterly performance
Grok Enhancement:   Toggle ON for AI insights
```

Click **Execute** → Watch real-time progress → See results with Grok analysis

---

## 📋 Available Agents

| Agent | Icon | Specialties | Task Types |
|-------|------|-------------|-----------|
| **Analyst Alpha** | 💼 | Market analysis, financial data | Research, Analysis |
| **Legal Eagle** | ⚖️ | Compliance, legal review | Compliance, Documentation |
| **Construction Crew** | 🏗️ | Project planning, estimation | Construction Planning |
| **Environmental Inspector** | 🌱 | Environmental impact | Assessment, Metrics |
| **Aviation Authority** | ✈️ | Safety, regulations | Safety Review |
| **Health Guardian** | 🏥 | Health metrics, wellness | Assessment |
| **Innovation Lab** | 🔬 | Optimization, strategy | Optimization |

---

## 🔌 API Quick Reference

### **Health Check**
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "yur_status": "healthy",
  "sovereign_status": "healthy",
  "active_tasks": 0,
  "completed_tasks": 0,
  "system_uptime_seconds": 133.8
}
```

### **Execute Unified Task**
```bash
curl -X POST http://localhost:8001/api/unified/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "primary_agent": "analyst_alpha",
    "secondary_agents": ["legal_eagle"],
    "task_type": "research",
    "task_data": {"query": "AI Market Trends"},
    "use_grok_enhancement": true
  }'
```

### **Get Task Status**
```bash
curl http://localhost:8001/api/unified/tasks?user_id=user123
```

### **Real-time WebSocket Updates**
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/task-updates/user123');
ws.onmessage = (evt) => {
  const metrics = JSON.parse(evt.data);
  console.log('System Health:', metrics);
};
```

---

## 🎮 UI Tabs Explained

### **Orchestrate Tab** 
- Select primary agent and multiple secondary agents
- Configure task parameters
- Enable/disable Grok enhancement
- View routing recommendations

### **Execute Tab**
- Quick task templates
- Real-time progress tracking
- Single-agent execution

### **Monitor Tab**
- System health dashboard
  - YUR status (connected/offline)
  - SOVEREIGN status (connected/offline)
  - Active task count
  - System uptime
  - Average execution time
- Live WebSocket metrics (updates every 5 seconds)
- Task history grid

---

## ✨ Example Workflows

### **Scenario 1: Compliance + Legal Review**
```
Primary:   legal_eagle
Secondary: analyst_alpha
Task:      compliance_check
Input:     {"jurisdiction": "California", "industry": "fintech"}
Output:    ✓ Compliance Score
          ✓ Risk Assessment  
          ✓ Legal Recommendations
          ✨ Grok Enhancement: Regulatory Evolution Insights
```

### **Scenario 2: Project Planning with Optimization**
```
Primary:   construction_crew
Secondary: innovation_lab
Task:      construction_planning
Input:     {"projectName": "Office Building", "location": "NYC"}
Output:    ✓ Project Timeline
          ✓ Budget Estimation
          ✓ Resource Allocation
          ✨ Grok Enhancement: Cost Optimization Strategies
```

### **Scenario 3: Environmental + Health Safety**
```
Primary:   environmental_inspector
Secondary: health_guardian
Task:      environmental_assessment
Input:     {"siteType": "manufacturing", "region": "midwest"}
Output:    ✓ Environmental Impact Score
          ✓ Health Risk Analysis
          ✓ Mitigation Strategies
          ✨ Grok Enhancement: Sustainability Best Practices
```

---

## 🔧 Troubleshooting

### **"Orchestrator Not Showing?"**
- Refresh page: `http://localhost:5173`
- Check console for errors (F12)
- Verify bridge is running: `http://localhost:8001/health`

### **"No Agents Loading?"**
- Verify YUR backend: `http://localhost:3000/api/agents`
- Check YUR marketplace: `http://localhost:8080`
- Wait 5-10 seconds for initial load

### **"Grok Enhancement Not Working?"**
- Set XAI_API_KEY environment variable
- Check bridge logs for API errors
- Results still work without enhancement

### **"WebSocket Not Updating?"**
- Check browser console for connection errors
- Verify port 8001 is accessible
- Reload page to reconnect

---

## 🎓 Pro Tips

1. **Use Secondary Agents** - They execute in parallel for comprehensive analysis
2. **Enable Grok** - Adds intelligent insights to any agent result
3. **Monitor Tab** - Watch real-time metrics while tasks execute
4. **Task History** - Check previous results to compare performance
5. **Batch Execute** - Queue multiple tasks via API endpoint

---

## 📊 Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Single Agent Task | 2-5s | Depends on task complexity |
| Multi-Agent (2-3) | 3-8s | Parallel execution |
| Grok Enhancement | +5-10s | Only if enabled |
| WebSocket Update | <100ms | Real-time metrics |

---

## 🔐 Important Notes

- ✅ Default user: "demo-user" (no auth)
- ✅ Tasks stored in memory (lost on restart)
- ✅ Integration routes to YUR first, falls back to Grok
- ⚠️ Add authentication before production
- ⚠️ Set up persistent database for task history

---

## 📱 Mobile Access

**On Network:**
```
http://<your-computer-ip>:5173
```

Find your IP:
```powershell
ipconfig | findstr /i "ipv4"
```

---

## 🚀 Next Steps

1. **✅ Try the UI** - Spend 5 minutes exploring
2. **✅ Execute a Task** - Test agent workflow
3. **✅ Monitor Results** - Watch real-time updates
4. **📋 Setup XAI Key** - Enable full Grok features
5. **📋 Database** - Persist results long-term
6. **📋 Authentication** - Add user management
7. **🚀 Production** - Deploy via Docker

---

## 📞 Quick Debug Commands

```bash
# Check all services
python verify_orchestration.py

# Restart integration bridge
taskkill /IM python.exe /F
cd C:\XAI_GROK_GENESIS\sovereign-api
python -m uvicorn integration_bridge:app --port 8001

# Check YUR agents
curl http://localhost:3000/api/agents

# View bridge logs
Get-Content integration_bridge.log -Tail 50
```

---

## ✨ What Just Happened

You now have a **unified multi-agent AI system** where:

1. **7 Specialized Agents** execute domain-specific tasks
2. **Integration Bridge** intelligently routes between YUR and Grok
3. **Unified UI** controls agents and monitors execution
4. **WebSocket Updates** provide real-time metrics
5. **Grok Enhancement** adds AI insights to any result
6. **Parallel Execution** coordinates multiple agents simultaneously

🎉 **Next: Visit http://localhost:5173 and click "Unified Orchestrator"**

---

**System Status:** ✅ LIVE & READY
**Last Updated:** 2025-01-30
