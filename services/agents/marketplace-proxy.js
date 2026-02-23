const axios = require('axios');

const MARKETPLACE_URL = process.env.MARKETPLACE_URL || 'http://localhost:8080';

/**
 * Marketplace Proxy - Routes requests to Python marketplace service
 */
class MarketplaceProxy {
  constructor(baseUrl = MARKETPLACE_URL) {
    this.baseUrl = baseUrl;
    this.retryAttempts = 3;
    this.retryDelay = 1000;
  }

  /**
   * Make a request with retry logic
   */
  async makeRequest(method, path, data = null, retries = this.retryAttempts) {
    try {
      const config = {
        method,
        url: `${this.baseUrl}${path}`,
        timeout: 5000,
      };

      if (data) {
        config.data = data;
        config.headers = { 'Content-Type': 'application/json' };
      }

      console.log(`[Marketplace Proxy] ${method} ${path}`);
      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error(`[Marketplace Proxy] Error: ${error.message}`);

      if (retries > 0 && this.shouldRetry(error)) {
        console.log(`[Marketplace Proxy] Retrying... (${retries} attempts left)`);
        await this.sleep(this.retryDelay);
        return this.makeRequest(method, path, data, retries - 1);
      }

      throw error;
    }
  }

  /**
   * Determine if request should be retried
   */
  shouldRetry(error) {
    return error.code === 'ECONNREFUSED' ||
           error.code === 'ETIMEDOUT' ||
           (error.response && error.response.status >= 500);
  }

  /**
   * Sleep utility for retry delays
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get all available agents
   */
  async getAgents() {
    return this.makeRequest('GET', '/api/agents');
  }

  /**
   * Get specific agent details
   */
  async getAgent(agentId) {
    return this.makeRequest('GET', `/api/agent/${agentId}`);
  }

  /**
   * Purchase an agent
   */
  async purchaseAgent(agentId, userId) {
    return this.makeRequest('POST', '/api/purchase', {
      agent_id: agentId,
      user_id: userId
    });
  }

  /**
   * Rent an agent
   */
  async rentAgent(agentId, userId, hours) {
    return this.makeRequest('POST', '/api/rent', {
      agent_id: agentId,
      user_id: userId,
      hours: hours
    });
  }

  /**
   * Get academy programs
   */
  async getAcademyPrograms() {
    return this.makeRequest('GET', '/api/academy/programs');
  }

  /**
   * Enroll agent in academy program
   */
  async enrollAgent(agentId, program) {
    return this.makeRequest('POST', '/api/academy/enroll', {
      agent_id: agentId,
      program: program
    });
  }

  /**
   * Certify agent
   */
  async certifyAgent(agentId, program) {
    return this.makeRequest('POST', '/api/academy/certify', {
      agent_id: agentId,
      program: program
    });
  }
}

module.exports = MarketplaceProxy;
