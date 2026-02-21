/**
 * Autonomous Agent Framework - TypeScript Usage Example
 * Example: Harvest Optimization Agent
 */

import { 
  AgentFramework, 
  Agent,
  AgentConfig,
  Tool,
  Goal,
  ExecutionResult 
} from '@agro/autonomous-agent-sdk';

// ============================================================================
// Configuration
// ============================================================================

const config = {
  apiKey: process.env.AGENT_FRAMEWORK_API_KEY!,
  baseUrl: 'http://localhost:6000/api/v1',
  timeout: 30000
};

const framework = new AgentFramework(config);

// ============================================================================
// Agent Creation
// ============================================================================

async function createHarvestOptimizerAgent(): Promise<Agent> {
  const agentConfig: AgentConfig = {
    name: 'Harvest Optimizer Agent',
    description: 'Autonomous agent that optimizes harvest timing and resource allocation',
    
    capabilities: [
      'data_analysis',
      'decision_making',
      'task_planning',
      'resource_optimization'
    ],
    
    decision_model: {
      type: 'llm',
      provider: 'openai',
      model: 'gpt-4',
      temperature: 0.7,
      max_tokens: 1000,
      system_prompt: `
        You are an agricultural optimization agent specialized in harvest operations.
        
        Analyze data from:
        - Field productivity sensors
        - AI vision maturity detection
        - Weather forecasts
        - Robot fleet telemetry
        
        Make decisions about:
        - Harvest timing (optimal maturity window)
        - Resource allocation (which robots to deploy)
        - Zone prioritization (overripe areas first)
        
        Output format:
        {
          "decision": "START_HARVEST_NOW|WAIT|POSTPONE",
          "reasoning": "Clear explanation",
          "priority": "HIGH|MEDIUM|LOW",
          "recommended_robots": ["ROB-001", ...],
          "target_zones": ["zone_3", ...],
          "estimated_duration_hours": 0.0,
          "risk_assessment": {
            "weather_risk": "LOW|MEDIUM|HIGH",
            "crop_loss_risk": "LOW|MEDIUM|HIGH"
          }
        }
      `
    },
    
    memory: {
      short_term: {
        enabled: true,
        max_messages: 10,
        ttl_seconds: 3600,
        storage: 'redis'
      },
      long_term: {
        enabled: true,
        storage: 'postgres',
        retention_days: 30
      },
      embeddings: {
        enabled: true,
        model: 'text-embedding-ada-002',
        dimensions: 1536,
        similarity_threshold: 0.8,
        vector_db: 'pinecone'
      }
    },
    
    planning: {
      strategy: 'reactive_deliberative',
      horizon_hours: 48,
      replanning_interval_minutes: 30,
      constraints: {
        weather: {
          min_temp_celsius: 5,
          max_wind_kmh: 40,
          no_heavy_rain: true
        },
        battery: {
          min_soc_percent: 30,
          reserve_kwh: 50
        },
        daylight: {
          prefer_daylight: true,
          min_solar_elevation: 15
        }
      }
    },
    
    execution: {
      mode: 'autonomous',
      approval_required: false,
      max_concurrent_tasks: 5,
      timeout_seconds: 300,
      retry_policy: {
        max_attempts: 3,
        backoff_seconds: 10,
        exponential: true,
        retry_on_status: [500, 502, 503, 504]
      }
    },
    
    monitoring: {
      logging: {
        level: 'INFO',
        destination: 'file',
        path: '/var/log/agents/harvest_optimizer.log',
        rotation: 'daily'
      },
      metrics: {
        enabled: true,
        interval_seconds: 60,
        push_endpoint: 'http://localhost:5003/api/v1/agent_metrics',
        retention_days: 90
      },
      alerts: {
        enabled: true,
        channels: ['email', 'slack'],
        severity_threshold: 'WARNING',
        rate_limit_per_hour: 10
      }
    }
  };
  
  const agent = await framework.createAgent(agentConfig);
  console.log(`✅ Agent created: ${agent.agent_id}`);
  
  return agent;
}

// ============================================================================
// Tool Registration
// ============================================================================

async function registerTools(agent: Agent): Promise<void> {
  const tools: Tool[] = [
    {
      name: 'precision_data',
      type: 'data_source',
      endpoint: 'http://localhost:5000/api/v1/recommendations',
      method: 'GET',
      parameters: {
        field_id: { type: 'string', required: true }
      },
      description: 'Fetch field productivity and readiness data',
      authentication: {
        type: 'bearer',
        token_env_var: 'PRECISION_API_KEY'
      },
      timeout_ms: 5000
    },
    
    {
      name: 'ai_vision',
      type: 'data_source',
      endpoint: 'http://localhost:5001/api/v1/maturity',
      method: 'GET',
      parameters: {
        field_id: { type: 'string', required: true }
      },
      description: 'Get crop maturity analysis from AI vision',
      authentication: {
        type: 'bearer',
        token_env_var: 'AI_VISION_API_KEY'
      },
      timeout_ms: 10000
    },
    
    {
      name: 'telemetry',
      type: 'monitor',
      endpoint: 'http://localhost:5003/api/v1/metrics',
      method: 'GET',
      parameters: {
        robot_ids: { type: 'array', required: true },
        metrics: { type: 'array', required: true }
      },
      description: 'Monitor robot fleet status and telemetry',
      authentication: {
        type: 'bearer',
        token_env_var: 'TELEMETRY_API_KEY'
      },
      timeout_ms: 3000
    },
    
    {
      name: 'swarm_coordinator',
      type: 'action',
      endpoint: 'http://localhost:5002/api/v1/allocate',
      method: 'POST',
      parameters: {
        tasks: { type: 'array', required: true },
        robots: { type: 'array', required: true }
      },
      description: 'Allocate harvest tasks to robot swarm',
      authentication: {
        type: 'bearer',
        token_env_var: 'SWARM_API_KEY'
      },
      retry_policy: {
        max_attempts: 3,
        backoff_seconds: 5,
        exponential: true
      },
      timeout_ms: 15000
    },
    
    {
      name: 'weather_forecast',
      type: 'external_api',
      endpoint: 'https://api.openweathermap.org/data/2.5/forecast',
      method: 'GET',
      parameters: {
        lat: { type: 'float', required: true },
        lon: { type: 'float', required: true }
      },
      description: 'Get 5-day weather forecast',
      authentication: {
        type: 'query',
        param: 'appid',
        value_env_var: 'OPENWEATHER_API_KEY'
      },
      timeout_ms: 8000
    }
  ];
  
  for (const tool of tools) {
    const toolId = await agent.registerTool(tool);
    console.log(`✅ Tool registered: ${tool.name} (${toolId})`);
  }
}

// ============================================================================
// Goal Setting
// ============================================================================

async function setAgentGoals(agent: Agent): Promise<void> {
  const goals: Goal[] = [
    {
      name: 'maximize_harvest_efficiency',
      priority: 'high',
      metrics: ['ha_per_hour', 'fuel_consumption_per_ha'],
      target: {
        ha_per_hour: 10,
        fuel_efficiency: 'increase'
      },
      description: 'Increase harvest speed while minimizing fuel consumption'
    },
    
    {
      name: 'minimize_crop_loss',
      priority: 'critical',
      metrics: ['overripe_percentage', 'harvest_delay_hours'],
      target: {
        overripe_percentage: '< 5%',
        harvest_delay_hours: '< 24'
      },
      description: 'Prevent crop loss from overripening or delays'
    },
    
    {
      name: 'optimize_battery_usage',
      priority: 'medium',
      metrics: ['battery_cycles', 'solar_utilization'],
      target: {
        solar_utilization: '> 80%'
      },
      description: 'Maximize solar energy usage'
    }
  ];
  
  for (const goal of goals) {
    const goalId = await agent.setGoal(goal);
    console.log(`✅ Goal set: ${goal.name} (${goalId})`);
  }
}

// ============================================================================
// Knowledge Base Population
// ============================================================================

async function populateKnowledgeBase(agent: Agent): Promise<void> {
  const knowledge = [
    {
      type: 'fact' as const,
      content: 'FIELD-01 typically requires 6.5 hours to harvest with 3 robots',
      metadata: { field_id: 'FIELD-01', source: 'historical_data' },
      ttl_days: 365
    },
    {
      type: 'fact' as const,
      content: 'Optimal sugarcane maturity is 92-96% with Brix levels 18-22',
      metadata: { crop: 'sugarcane', source: 'agronomic_guidelines' },
      ttl_days: 730
    },
    {
      type: 'fact' as const,
      content: 'Heavy rain within 48h after harvest reduces juice quality by ~12%',
      metadata: { factor: 'weather', impact: 'quality' },
      ttl_days: 365
    },
    {
      type: 'fact' as const,
      content: 'ROB-003 has highest efficiency on sloped terrain',
      metadata: { robot_id: 'ROB-003', specialization: 'slopes' },
      ttl_days: 180
    },
    {
      type: 'fact' as const,
      content: 'Morning harvests (6am-10am) result in 8% higher juice quality',
      metadata: { timing: 'morning', impact: 'quality' },
      ttl_days: 365
    }
  ];
  
  for (const item of knowledge) {
    const memoryId = await agent.storeMemory(item);
    console.log(`✅ Knowledge stored: ${memoryId}`);
  }
}

// ============================================================================
// Scheduling
// ============================================================================

async function setupSchedule(agent: Agent): Promise<void> {
  const schedule = await agent.createSchedule({
    name: 'Periodic Harvest Check',
    cron: '0 */30 * * *', // Every 30 minutes
    enabled: true,
    context: {
      check_type: 'automated',
      season: 'harvest'
    },
    timezone: 'America/Sao_Paulo'
  });
  
  console.log(`✅ Schedule created: ${schedule.schedule_id}`);
  console.log(`   Next execution: ${schedule.next_execution_at}`);
}

// ============================================================================
// Manual Execution
// ============================================================================

async function executeAgent(agent: Agent): Promise<ExecutionResult> {
  console.log('\n' + '='.repeat(60));
  console.log('TRIGGERING MANUAL EXECUTION');
  console.log('='.repeat(60));
  
  const result = await agent.execute({
    trigger_reason: 'Manual harvest check requested by operator',
    context: {
      field_ids: ['FIELD-01', 'FIELD-02'],
      priority: 'HIGH',
      operator: 'João Silva'
    },
    async_mode: false // Wait for completion
  });
  
  console.log(`\n📊 Execution ID: ${result.execution_id}`);
  console.log(`   Status: ${result.status}`);
  console.log(`   Duration: ${result.duration_seconds}s`);
  
  if (result.decision_made) {
    const decision = result.decision_made;
    console.log(`\n🤖 DECISION: ${decision.decision}`);
    console.log(`   Priority: ${decision.priority}`);
    console.log(`   Reasoning: ${decision.reasoning}`);
    
    if ('recommended_robots' in decision) {
      console.log(`   Robots: ${decision.recommended_robots.join(', ')}`);
    }
    
    if ('estimated_duration_hours' in decision) {
      console.log(`   Duration: ${decision.estimated_duration_hours} hours`);
    }
  }
  
  if (result.outcome?.success) {
    console.log(`\n✅ OUTCOME:`);
    console.log(`   Success: ${result.outcome.success}`);
    if (result.outcome.estimated_impact) {
      const impact = result.outcome.estimated_impact;
      if (impact.crop_saved_tons) {
        console.log(`   Crop saved: ${impact.crop_saved_tons} tons`);
      }
      if (impact.revenue_increase_usd) {
        console.log(`   Revenue increase: $${impact.revenue_increase_usd.toLocaleString()}`);
      }
    }
  }
  
  return result;
}

// ============================================================================
// Metrics & Analytics
// ============================================================================

async function displayMetrics(agent: Agent): Promise<void> {
  console.log('\n' + '='.repeat(60));
  console.log('AGENT PERFORMANCE METRICS');
  console.log('='.repeat(60));
  
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  
  const metrics = await agent.getMetrics({
    from_date: thirtyDaysAgo,
    to_date: now,
    granularity: 'day'
  });
  
  console.log(`\n📈 Period: ${metrics.period.from} to ${metrics.period.to}`);
  console.log(`   Total executions: ${metrics.metrics.executions_count}`);
  console.log(`   Success rate: ${(metrics.metrics.success_rate * 100).toFixed(1)}%`);
  console.log(`   Avg decision latency: ${metrics.metrics.avg_decision_latency_ms}ms`);
  console.log(`   Goals achieved: ${metrics.metrics.goals_achieved}`);
  
  if (metrics.metrics.estimated_roi_usd) {
    console.log(`   Estimated ROI: $${metrics.metrics.estimated_roi_usd.toLocaleString()}`);
  }
  
  // Display goal progress
  const goals = await agent.getGoals();
  console.log(`\n🎯 GOAL PROGRESS:`);
  
  for (const goal of goals) {
    const barLength = 20;
    const filled = Math.floor(goal.progress * barLength);
    const empty = barLength - filled;
    const progressBar = '█'.repeat(filled) + '░'.repeat(empty);
    
    console.log(`   ${goal.name}:`);
    console.log(`   [${progressBar}] ${(goal.progress * 100).toFixed(0)}%`);
    console.log(`   Current: ${goal.current_value} | Target: ${goal.target_value}\n`);
  }
}

// ============================================================================
// Memory Search
// ============================================================================

async function searchMemory(agent: Agent, query: string): Promise<void> {
  console.log('\n' + '='.repeat(60));
  console.log('SEMANTIC MEMORY SEARCH');
  console.log('='.repeat(60));
  
  const results = await agent.searchMemory({
    query,
    limit: 3,
    threshold: 0.75
  });
  
  console.log(`\n🔍 Query: "${query}"`);
  console.log(`   Found ${results.length} relevant memories:\n`);
  
  results.forEach((result, index) => {
    console.log(`   ${index + 1}. [Similarity: ${result.similarity.toFixed(2)}]`);
    console.log(`      ${result.content}\n`);
  });
}

// ============================================================================
// Webhook Setup
// ============================================================================

async function setupWebhooks(agent: Agent): Promise<void> {
  const webhooks = [
    {
      event: 'decision.made' as const,
      url: 'https://your-server.com/api/webhooks/decision',
      headers: {
        'Authorization': `Bearer ${process.env.WEBHOOK_SECRET}`,
        'Content-Type': 'application/json'
      }
    },
    {
      event: 'execution.failed' as const,
      url: 'https://your-server.com/api/webhooks/failure',
      headers: {
        'Authorization': `Bearer ${process.env.WEBHOOK_SECRET}`,
        'Content-Type': 'application/json'
      }
    },
    {
      event: 'goal.achieved' as const,
      url: 'https://your-server.com/api/webhooks/goal',
      headers: {
        'Authorization': `Bearer ${process.env.WEBHOOK_SECRET}`,
        'Content-Type': 'application/json'
      }
    }
  ];
  
  for (const webhook of webhooks) {
    const webhookId = await agent.registerWebhook(webhook);
    console.log(`✅ Webhook registered: ${webhook.event} → ${webhookId}`);
  }
}

// ============================================================================
// Main Execution
// ============================================================================

async function main(): Promise<void> {
  try {
    console.log('🚀 Autonomous Agent Framework - TypeScript Example');
    console.log('='.repeat(60));
    
    // 1. Create agent
    console.log('\n1️⃣ Creating agent...');
    const agent = await createHarvestOptimizerAgent();
    
    // 2. Register tools
    console.log('\n2️⃣ Registering tools...');
    await registerTools(agent);
    
    // 3. Set goals
    console.log('\n3️⃣ Setting goals...');
    await setAgentGoals(agent);
    
    // 4. Populate knowledge base
    console.log('\n4️⃣ Populating knowledge base...');
    await populateKnowledgeBase(agent);
    
    // 5. Setup schedule
    console.log('\n5️⃣ Setting up schedule...');
    await setupSchedule(agent);
    
    // 6. Setup webhooks
    console.log('\n6️⃣ Configuring webhooks...');
    await setupWebhooks(agent);
    
    // 7. Execute agent
    await executeAgent(agent);
    
    // 8. Display metrics
    await displayMetrics(agent);
    
    // 9. Search memory
    await searchMemory(agent, 'What affects harvest quality?');
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ Setup complete! Agent is operational.');
    console.log(`   Agent ID: ${agent.agent_id}`);
    console.log(`   Status: ${agent.status}`);
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

// Run
main();
