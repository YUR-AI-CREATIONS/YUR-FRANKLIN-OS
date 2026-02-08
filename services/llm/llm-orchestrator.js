/**
 * Multi-LLM Orchestration Service
 * Intelligently distributes tasks across Gemini, Grok, and GPT
 * Gemini: Primary orchestrator, complex reasoning
 * Grok: Fast real-time tasks, data analysis
 * GPT: Creative tasks, content generation
 */

const axios = require('axios');

class LLMOrchestrator {
  constructor() {
    this.geminiKey = process.env.GEMINI_API_KEY;
    this.grokKey = process.env.GROK_API_KEY || process.env.XAI_API_KEY;
    this.openaiKey = process.env.OPENAI_API_KEY;
    this.anthropicKey = process.env.ANTHROPIC_API_KEY;

    this.primaryLLM = process.env.PRIMARY_LLM || 'grok';
    this.multiLLMEnabled = process.env.ENABLE_MULTI_LLM_ORCHESTRATION === 'true';

    // Task queues for load balancing
    this.taskQueues = {
      gemini: [],
      grok: [],
      gpt: []
    };
  }

  /**
   * Main orchestration method - analyzes and distributes tasks
   */
  async orchestrate(userMessage, agentContext = {}) {
    try {
      // Analyze task complexity and type
      const taskAnalysis = await this.analyzeTask(userMessage);

      if (!this.multiLLMEnabled || taskAnalysis.simple) {
        // Simple task - use primary LLM only
        return await this.callPrimaryLLM(userMessage, agentContext);
      }

      // Complex task - distribute across LLMs
      return await this.distributeTask(userMessage, taskAnalysis, agentContext);
    } catch (error) {
      console.error('Orchestration error:', error.message);
      // Fallback to primary LLM
      return await this.callPrimaryLLM(userMessage, agentContext);
    }
  }

  /**
   * Analyze task to determine complexity and best distribution
   */
  async analyzeTask(message) {
    const lowerMessage = message.toLowerCase();

    return {
      simple: message.length < 100,
      requiresData: lowerMessage.includes('analyze') || lowerMessage.includes('data') || lowerMessage.includes('calculate'),
      requiresCreativity: lowerMessage.includes('create') || lowerMessage.includes('write') || lowerMessage.includes('design'),
      requiresReasoning: lowerMessage.includes('why') || lowerMessage.includes('how') || lowerMessage.includes('explain'),
      complexity: message.length > 500 ? 'high' : message.length > 200 ? 'medium' : 'low'
    };
  }

  /**
   * Distribute complex task across multiple LLMs in parallel
   */
  async distributeTask(message, analysis, agentContext) {
    const subtasks = [];

    // Create subtasks based on analysis
    if (analysis.requiresData) {
      subtasks.push({
        llm: 'grok',
        prompt: `Analyze the data and patterns in this request: ${message}`,
        type: 'analysis'
      });
    }

    if (analysis.requiresCreativity) {
      subtasks.push({
        llm: 'gpt',
        prompt: `Generate creative and engaging content for: ${message}`,
        type: 'creative'
      });
    }

    if (analysis.requiresReasoning) {
      subtasks.push({
        llm: 'gemini',
        prompt: `Provide detailed reasoning and explanation for: ${message}`,
        type: 'reasoning'
      });
    }

    // If no specific subtasks, use general distribution
    if (subtasks.length === 0) {
      subtasks.push(
        { llm: 'grok', prompt: `Quick analysis: ${message}`, type: 'quick' },
        { llm: 'gemini', prompt: `Detailed response: ${message}`, type: 'detailed' }
      );
    }

    // Execute subtasks in parallel
    const results = await Promise.allSettled(
      subtasks.map(task => this.executeSubtask(task, agentContext))
    );

    // Synthesize results using Gemini
    const successfulResults = results
      .filter(r => r.status === 'fulfilled')
      .map(r => r.value);

    if (successfulResults.length === 0) {
      // Fallback if all subtasks failed
      return await this.callPrimaryLLM(message, agentContext);
    }

    return await this.synthesizeResults(message, successfulResults, agentContext);
  }

  /**
   * Execute a single subtask
   */
  async executeSubtask(task, agentContext) {
    try {
      let response;

      switch (task.llm) {
        case 'gemini':
          response = await this.callGemini(task.prompt, agentContext);
          break;
        case 'grok':
          response = await this.callGrok(task.prompt, agentContext);
          break;
        case 'gpt':
          response = await this.callGPT(task.prompt, agentContext);
          break;
        default:
          response = await this.callPrimaryLLM(task.prompt, agentContext);
      }

      return {
        type: task.type,
        llm: task.llm,
        content: response
      };
    } catch (error) {
      console.error(`Subtask error (${task.llm}):`, error.message);
      return {
        type: task.type,
        llm: task.llm,
        content: null,
        error: error.message
      };
    }
  }

  /**
   * Synthesize multiple results into coherent response
   */
  async synthesizeResults(originalMessage, results, agentContext) {
    const synthesisPrompt = `
Original user question: ${originalMessage}

I have received these responses from different AI systems:

${results.map((r, i) => `
[${r.llm.toUpperCase()} - ${r.type}]:
${r.content}
`).join('\n')}

Please synthesize these responses into a single, coherent, comprehensive answer that:
1. Combines the best insights from all responses
2. Maintains consistency and clarity
3. Directly answers the original question
4. Removes any redundancy

Agent context: ${JSON.stringify(agentContext)}
`;

    return await this.callGrok(synthesisPrompt, agentContext);
  }

  /**
   * Call primary LLM (fallback method)
   */
  async callPrimaryLLM(message, agentContext) {
    switch (this.primaryLLM) {
      case 'gemini':
        return await this.callGemini(message, agentContext);
      case 'grok':
        return await this.callGrok(message, agentContext);
      case 'gpt':
        return await this.callGPT(message, agentContext);
      default:
        return await this.callGrok(message, agentContext);
    }
  }

  /**
   * Call Google Gemini API
   */
  async callGemini(message, agentContext) {
    if (!this.geminiKey) {
      throw new Error('Gemini API key not configured');
    }

    try {
      const systemPrompt = this.buildSystemPrompt(agentContext);

      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${this.geminiKey}`,
        {
          contents: [{
            parts: [{
              text: `${systemPrompt}\n\nUser: ${message}`
            }]
          }]
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 30000
        }
      );

      return response.data.candidates[0].content.parts[0].text;
    } catch (error) {
      console.error('Gemini API error:', error.response?.data || error.message);
      throw new Error(`Gemini unavailable: ${error.message}`);
    }
  }

  /**
   * Call xAI Grok API
   */
  async callGrok(message, agentContext) {
    if (!this.grokKey) {
      throw new Error('Grok API key not configured');
    }

    try {
      const systemPrompt = this.buildSystemPrompt(agentContext);

      const response = await axios.post(
        'https://api.x.ai/v1/chat/completions',
        {
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: message }
          ],
          model: 'grok-3',
          stream: false,
          temperature: 0.7
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.grokKey}`
          },
          timeout: 30000
        }
      );

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Grok API error:', error.response?.data || error.message);
      throw new Error(`Grok unavailable: ${error.message}`);
    }
  }

  /**
   * Call OpenAI GPT API
   */
  async callGPT(message, agentContext) {
    if (!this.openaiKey) {
      throw new Error('OpenAI API key not configured');
    }

    try {
      const systemPrompt = this.buildSystemPrompt(agentContext);

      const response = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
          model: 'gpt-4-turbo-preview',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: message }
          ],
          temperature: 0.8,
          max_tokens: 2000
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiKey}`
          },
          timeout: 30000
        }
      );

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('GPT API error:', error.response?.data || error.message);
      throw new Error(`GPT unavailable: ${error.message}`);
    }
  }

  /**
   * Call Anthropic Claude API (backup)
   */
  async callClaude(message, agentContext) {
    if (!this.anthropicKey) {
      throw new Error('Claude API key not configured');
    }

    try {
      const systemPrompt = this.buildSystemPrompt(agentContext);

      const response = await axios.post(
        'https://api.anthropic.com/v1/messages',
        {
          model: 'claude-3-opus-20240229',
          max_tokens: 2000,
          system: systemPrompt,
          messages: [
            { role: 'user', content: message }
          ]
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.anthropicKey,
            'anthropic-version': '2023-06-01'
          },
          timeout: 30000
        }
      );

      return response.data.content[0].text;
    } catch (error) {
      console.error('Claude API error:', error.response?.data || error.message);
      throw new Error(`Claude unavailable: ${error.message}`);
    }
  }

  /**
   * Build system prompt with agent personality
   */
  buildSystemPrompt(agentContext) {
    const { agentName, agentRole, personality, skills } = agentContext;

    if (!agentName) {
      return 'You are a helpful AI assistant in the Neo3 Agent Marketplace system.';
    }

    return `You are ${agentName}, ${agentRole || 'an AI agent'} in the Neo3 Agent Marketplace.

Your personality: ${personality || 'Professional, helpful, and knowledgeable'}

Your skills: ${skills?.join(', ') || 'General assistance'}

Respond in character, using your unique expertise and personality. Be concise, helpful, and actionable.`;
  }

  /**
   * Get orchestrator status
   */
  getStatus() {
    return {
      primaryLLM: this.primaryLLM,
      multiLLMEnabled: this.multiLLMEnabled,
      availableModels: {
        gemini: !!this.geminiKey,
        grok: !!this.grokKey,
        gpt: !!this.openaiKey,
        claude: !!this.anthropicKey
      },
      queueSizes: {
        gemini: this.taskQueues.gemini.length,
        grok: this.taskQueues.grok.length,
        gpt: this.taskQueues.gpt.length
      }
    };
  }
}

module.exports = LLMOrchestrator;
