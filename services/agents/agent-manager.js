/**
 * Agent Manager Service
 * Manages user's purchased/rented agents and their sessions
 */

class AgentManager {
  constructor() {
    // In-memory storage for demo (would use database in production)
    this.userAgents = new Map(); // userId -> [agents]
    this.agentSessions = new Map(); // sessionId -> session data
    this.conversationHistory = new Map(); // sessionId -> [messages]

    // Agent personality profiles
    this.agentProfiles = {
      'analyst-alpha': {
        name: 'Analyst Alpha',
        role: 'Financial Analyst',
        personality: 'Analytical, precise, data-driven. Speaks in clear financial terms with confidence.',
        skills: ['Financial Analysis', 'Market Research', 'Risk Assessment', 'Portfolio Management'],
        specialty: 'data_analysis'
      },
      'legal-eagle': {
        name: 'Legal Eagle',
        role: 'Legal Expert',
        personality: 'Thorough, detail-oriented, professional. Explains complex legal concepts clearly.',
        skills: ['Contract Review', 'Legal Research', 'Compliance', 'Risk Mitigation'],
        specialty: 'reasoning'
      },
      'strategy-sigma': {
        name: 'Strategy Sigma',
        role: 'Strategic Planner',
        personality: 'Visionary, strategic, big-picture thinker. Provides actionable insights.',
        skills: ['Strategic Planning', 'Business Development', 'Innovation', 'Leadership'],
        specialty: 'reasoning'
      },
      'builder-beta': {
        name: 'Builder Beta',
        role: 'Construction Specialist',
        personality: 'Practical, solution-focused, experienced. Thinks in terms of feasibility and execution.',
        skills: ['Project Management', 'Construction Planning', 'Cost Estimation', 'Quality Control'],
        specialty: 'analysis'
      },
      'efficiency-epsilon': {
        name: 'Efficiency Epsilon',
        role: 'Environmental Optimizer',
        personality: 'Innovative, eco-conscious, efficiency-focused. Balances performance with sustainability.',
        skills: ['Environmental Analysis', 'Sustainability Planning', 'Efficiency Optimization', 'Green Technology'],
        specialty: 'creative'
      },
      'aviation-ace': {
        name: 'Aviation Ace',
        role: 'Aviation Expert',
        personality: 'Safety-first, technically precise, experienced. Thinks systematically about aviation.',
        skills: ['Flight Planning', 'Safety Analysis', 'Aircraft Systems', 'Regulatory Compliance'],
        specialty: 'analysis'
      },
      'health-guardian': {
        name: 'Health Guardian',
        role: 'Healthcare Specialist',
        personality: 'Caring, knowledgeable, patient-focused. Explains medical concepts accessibly.',
        skills: ['Healthcare Analysis', 'Patient Care', 'Medical Research', 'Health Optimization'],
        specialty: 'reasoning'
      }
    };
  }

  /**
   * Add agent to user's collection (after purchase/rent)
   */
  addUserAgent(userId, agentId, type = 'purchase', expiresAt = null) {
    if (!this.userAgents.has(userId)) {
      this.userAgents.set(userId, []);
    }

    const agents = this.userAgents.get(userId);
    const agent = {
      agentId,
      type, // 'purchase' or 'rent'
      acquiredAt: new Date().toISOString(),
      expiresAt,
      active: true,
      ...this.agentProfiles[agentId]
    };

    agents.push(agent);
    return agent;
  }

  /**
   * Get all agents for a user
   */
  getUserAgents(userId) {
    const agents = this.userAgents.get(userId) || [];

    // Filter out expired rentals
    const now = new Date();
    return agents.filter(agent => {
      if (agent.type === 'rent' && agent.expiresAt) {
        return new Date(agent.expiresAt) > now;
      }
      return true;
    });
  }

  /**
   * Get specific agent by ID
   */
  getUserAgent(userId, agentId) {
    const agents = this.getUserAgents(userId);
    return agents.find(a => a.agentId === agentId);
  }

  /**
   * Create chat session with an agent
   */
  createSession(userId, agentId) {
    const agent = this.getUserAgent(userId, agentId);
    if (!agent) {
      throw new Error('Agent not found or not owned by user');
    }

    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const session = {
      sessionId,
      userId,
      agentId,
      agentContext: {
        agentName: agent.name,
        agentRole: agent.role,
        personality: agent.personality,
        skills: agent.skills,
        specialty: agent.specialty
      },
      createdAt: new Date().toISOString(),
      lastActivity: new Date().toISOString()
    };

    this.agentSessions.set(sessionId, session);
    this.conversationHistory.set(sessionId, []);

    return session;
  }

  /**
   * Get session by ID
   */
  getSession(sessionId) {
    return this.agentSessions.get(sessionId);
  }

  /**
   * Add message to conversation history
   */
  addMessage(sessionId, role, content) {
    if (!this.conversationHistory.has(sessionId)) {
      this.conversationHistory.set(sessionId, []);
    }

    const history = this.conversationHistory.get(sessionId);
    history.push({
      role,
      content,
      timestamp: new Date().toISOString()
    });

    // Update session activity
    const session = this.agentSessions.get(sessionId);
    if (session) {
      session.lastActivity = new Date().toISOString();
    }

    return history;
  }

  /**
   * Get conversation history
   */
  getHistory(sessionId, limit = 50) {
    const history = this.conversationHistory.get(sessionId) || [];
    return history.slice(-limit);
  }

  /**
   * End session
   */
  endSession(sessionId) {
    this.agentSessions.delete(sessionId);
    // Keep history for potential review
    return true;
  }

  /**
   * Get all active sessions for a user
   */
  getUserSessions(userId) {
    const sessions = [];
    for (const [sessionId, session] of this.agentSessions.entries()) {
      if (session.userId === userId) {
        sessions.push({
          ...session,
          messageCount: (this.conversationHistory.get(sessionId) || []).length
        });
      }
    }
    return sessions;
  }

  /**
   * Get agent profile
   */
  getAgentProfile(agentId) {
    return this.agentProfiles[agentId] || null;
  }

  /**
   * Get all agent profiles
   */
  getAllProfiles() {
    return this.agentProfiles;
  }
}

module.exports = AgentManager;
