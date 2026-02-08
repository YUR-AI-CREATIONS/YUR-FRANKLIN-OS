/**
 * PyQMC Service Integration
 * Bridge between Node.js and Python PyQMC service
 */

import axios from 'axios';

class PyQMCService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.PYQMC_SERVICE_URL || 'http://localhost:5000';
  }

  /**
   * Optimize cognitive policy using VMC
   */
  async optimizeCognitivePolicy(params: {
    relationshipScore: number;
    recentSentiment: number[];
    interactionFrequency: number;
    taskSuccessRate: number;
    responseTime?: number;
    rewardHistory?: number[];
    n_steps?: number;
  }): Promise<any> {
    try {
      console.log('🧠 Calling PyQMC VMC optimization...');

      const response = await axios.post(
        `${this.baseURL}/vmc/optimize-cognitive`,
        params,
        { timeout: 60000 }
      );

      console.log('✅ PyQMC VMC optimization complete');
      return response.data;
    } catch (error: any) {
      console.error('❌ PyQMC VMC optimization failed:', error.message);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/health`, {
        timeout: 5000
      });

      console.log('📋 PyQMC Service Health:', response.data);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('❌ PyQMC service unreachable');
      return false;
    }
  }
}

export default new PyQMCService();
