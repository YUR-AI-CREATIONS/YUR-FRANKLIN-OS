/**
 * Franklin OS Services - Main Entry Point
 * 
 * Integrates:
 * - Agent Manager (user agents, sessions, conversations)
 * - Marketplace Proxy (Python service integration)
 * - LLM Orchestrator (multi-LLM distribution)
 * - QMC Integrator (quantum monte carlo)
 */

const express = require('express');
const cors = require('cors');
require('dotenv').config();

const AgentManager = require('./agents/agent-manager');
const MarketplaceProxy = require('./agents/marketplace-proxy');
const LLMOrchestrator = require('./llm/llm-orchestrator');

const app = express();
const PORT = process.env.SERVICES_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize services
const agentManager = new AgentManager();
const marketplaceProxy = new MarketplaceProxy(process.env.MARKETPLACE_URL || 'http://localhost:8001');
const llmOrchestrator = new LLMOrchestrator();

// ============================================================================
// HEALTH & STATUS
// ============================================================================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    services: {
      agentManager: 'active',
      marketplaceProxy: 'active',
      llmOrchestrator: llmOrchestrator.getStatus()
    },
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// AGENT MANAGER ENDPOINTS
// ============================================================================

// Get all agent profiles
app.get('/api/agents/profiles', (req, res) => {
  res.json(agentManager.getAllProfiles());
});

// Get specific agent profile
app.get('/api/agents/profile/:agentId', (req, res) => {
  const profile = agentManager.getAgentProfile(req.params.agentId);
  if (!profile) {
    return res.status(404).json({ error: 'Agent not found' });
  }
  res.json(profile);
});

// Add agent to user (after purchase/rent)
app.post('/api/agents/add', (req, res) => {
  try {
    const { userId, agentId, type, expiresAt } = req.body;
    const agent = agentManager.addUserAgent(userId, agentId, type, expiresAt);
    res.json({ success: true, agent });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Get user's agents
app.get('/api/agents/user/:userId', (req, res) => {
  const agents = agentManager.getUserAgents(req.params.userId);
  res.json(agents);
});

// Create chat session
app.post('/api/sessions/create', (req, res) => {
  try {
    const { userId, agentId } = req.body;
    const session = agentManager.createSession(userId, agentId);
    res.json({ success: true, session });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Get session
app.get('/api/sessions/:sessionId', (req, res) => {
  const session = agentManager.getSession(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  res.json(session);
});

// Get user sessions
app.get('/api/sessions/user/:userId', (req, res) => {
  const sessions = agentManager.getUserSessions(req.params.userId);
  res.json(sessions);
});

// End session
app.delete('/api/sessions/:sessionId', (req, res) => {
  agentManager.endSession(req.params.sessionId);
  res.json({ success: true });
});

// Get conversation history
app.get('/api/conversations/:sessionId', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  const history = agentManager.getHistory(req.params.sessionId, limit);
  res.json(history);
});

// ============================================================================
// MARKETPLACE PROXY ENDPOINTS
// ============================================================================

app.get('/api/marketplace/agents', async (req, res) => {
  try {
    const agents = await marketplaceProxy.getAgents();
    res.json(agents);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/marketplace/agent/:agentId', async (req, res) => {
  try {
    const agent = await marketplaceProxy.getAgent(req.params.agentId);
    res.json(agent);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/marketplace/purchase', async (req, res) => {
  try {
    const { agentId, userId } = req.body;
    const result = await marketplaceProxy.purchaseAgent(agentId, userId);
    
    // Add to user's local agent list
    if (result.success) {
      agentManager.addUserAgent(userId, agentId, 'purchase');
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/marketplace/rent', async (req, res) => {
  try {
    const { agentId, userId, hours } = req.body;
    const result = await marketplaceProxy.rentAgent(agentId, userId, hours);
    
    // Add to user's local agent list with expiration
    if (result.success) {
      const expiresAt = new Date(Date.now() + hours * 60 * 60 * 1000).toISOString();
      agentManager.addUserAgent(userId, agentId, 'rent', expiresAt);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/marketplace/programs', async (req, res) => {
  try {
    const programs = await marketplaceProxy.getAcademyPrograms();
    res.json(programs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/marketplace/enroll', async (req, res) => {
  try {
    const { agentId, program } = req.body;
    const result = await marketplaceProxy.enrollAgent(agentId, program);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/marketplace/certify', async (req, res) => {
  try {
    const { agentId, program } = req.body;
    const result = await marketplaceProxy.certifyAgent(agentId, program);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// LLM ORCHESTRATOR ENDPOINTS
// ============================================================================

app.get('/api/llm/status', (req, res) => {
  res.json(llmOrchestrator.getStatus());
});

// Chat with orchestrated LLM (uses session context)
app.post('/api/llm/chat', async (req, res) => {
  try {
    const { sessionId, message } = req.body;
    
    // Get session context
    const session = agentManager.getSession(sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    // Add user message to history
    agentManager.addMessage(sessionId, 'user', message);
    
    // Get response from orchestrator
    const response = await llmOrchestrator.orchestrate(message, session.agentContext);
    
    // Add assistant response to history
    agentManager.addMessage(sessionId, 'assistant', response);
    
    res.json({
      success: true,
      response,
      sessionId,
      agentContext: session.agentContext
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Direct LLM call (no session)
app.post('/api/llm/direct', async (req, res) => {
  try {
    const { message, agentContext } = req.body;
    const response = await llmOrchestrator.orchestrate(message, agentContext || {});
    res.json({ success: true, response });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 4-STAGE BUTTON ACTION PIPELINE
// ============================================================================

/**
 * Stage 1: Validate button action criteria
 * Stage 2: Route to appropriate service
 * Stage 3: Execute with agent intelligence
 * Stage 4: Return audited result
 */
app.post('/api/action/execute', async (req, res) => {
  try {
    const { actionType, payload, userId, sessionId } = req.body;
    
    // Stage 1: Validate
    const validActions = ['purchase', 'rent', 'enroll', 'certify', 'chat', 'analyze'];
    if (!validActions.includes(actionType)) {
      return res.status(400).json({ 
        error: 'Invalid action type',
        stage: 1,
        validActions 
      });
    }
    
    // Stage 2: Route to service
    let result;
    let service;
    
    switch (actionType) {
      case 'purchase':
        service = 'marketplace';
        result = await marketplaceProxy.purchaseAgent(payload.agentId, userId);
        if (result.success) {
          agentManager.addUserAgent(userId, payload.agentId, 'purchase');
        }
        break;
        
      case 'rent':
        service = 'marketplace';
        result = await marketplaceProxy.rentAgent(payload.agentId, userId, payload.hours);
        if (result.success) {
          const expiresAt = new Date(Date.now() + payload.hours * 60 * 60 * 1000).toISOString();
          agentManager.addUserAgent(userId, payload.agentId, 'rent', expiresAt);
        }
        break;
        
      case 'enroll':
        service = 'academy';
        result = await marketplaceProxy.enrollAgent(payload.agentId, payload.program);
        break;
        
      case 'certify':
        service = 'academy';
        result = await marketplaceProxy.certifyAgent(payload.agentId, payload.program);
        break;
        
      case 'chat':
        service = 'llm';
        const session = agentManager.getSession(sessionId);
        if (!session) {
          return res.status(404).json({ error: 'Session not found', stage: 2 });
        }
        agentManager.addMessage(sessionId, 'user', payload.message);
        const response = await llmOrchestrator.orchestrate(payload.message, session.agentContext);
        agentManager.addMessage(sessionId, 'assistant', response);
        result = { success: true, response };
        break;
        
      case 'analyze':
        service = 'llm';
        result = { 
          success: true, 
          analysis: await llmOrchestrator.analyzeTask(payload.message) 
        };
        break;
        
      default:
        return res.status(400).json({ error: 'Unhandled action type', stage: 2 });
    }
    
    // Stage 3 & 4: Execute and return audited result
    res.json({
      success: true,
      actionType,
      service,
      result,
      audit: {
        timestamp: new Date().toISOString(),
        userId,
        sessionId,
        stage: 4,
        status: 'completed'
      }
    });
    
  } catch (error) {
    res.status(500).json({ 
      error: error.message,
      stage: 'execution_failed'
    });
  }
});

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                     FRANKLIN OS SERVICES STARTED                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                                                   ║
║  Services:                                                                   ║
║    • Agent Manager    - /api/agents/*                                        ║
║    • Sessions         - /api/sessions/*                                      ║
║    • Marketplace      - /api/marketplace/*                                   ║
║    • LLM Orchestrator - /api/llm/*                                           ║
║    • Action Pipeline  - /api/action/execute                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
