# 🚀 Quick Start Guide - Autonomous Agent Framework

## What You'll Build

An autonomous agent that optimizes sugarcane harvest operations by:
- Monitoring crop maturity via AI vision
- Checking weather forecasts
- Analyzing robot fleet availability
- Making autonomous decisions about harvest timing
- Allocating tasks to robot swarm

**Time to complete**: ~15 minutes

---

## Prerequisites

- Python 3.10+ or Node.js 16+
- API keys for:
  - OpenAI (for GPT-4)
  - Weather API (OpenWeatherMap)
- Running instances of (or use mocks):
  - Precision Agriculture Platform (port 5000)
  - AI-Vision System (port 5001)
  - Swarm Coordinator (port 5002)
  - Telemetry Service (port 5003)

---

## Step 1: Installation

### Python
```bash
pip install autonomous-agent-sdk
```

### TypeScript
```bash
npm install @agro/autonomous-agent-sdk
```

---

## Step 2: Set Environment Variables

```bash
# Agent Framework
export AGENT_FRAMEWORK_API_KEY="your_framework_api_key"

# LLM Provider
export OPENAI_API_KEY="sk-..."

# External Services
export PRECISION_API_KEY="your_precision_key"
export AI_VISION_API_KEY="your_vision_key"
export SWARM_API_KEY="your_swarm_key"
export TELEMETRY_API_KEY="your_telemetry_key"
export OPENWEATHER_API_KEY="your_weather_key"

# Optional: Webhook Authentication
export WEBHOOK_SECRET="your_webhook_secret"
```

---

## Step 3: Create Your First Agent

### Python

```python
from autonomous_agent import AgentFramework, DecisionModel

# Initialize
framework = AgentFramework(api_key="your_api_key")

# Create agent
agent = framework.create_agent(
    name="My Harvest Agent",
    decision_model=DecisionModel(
        type="llm",
        provider="openai",
        model="gpt-4",
        system_prompt="""
        You are a harvest optimization agent.
        Analyze field data, weather, and robot availability.
        Decide if harvest should start now, wait, or postpone.
        Output JSON: {"decision": "START_HARVEST_NOW|WAIT|POSTPONE", "reasoning": "..."}
        """
    )
)

print(f"✅ Agent created: {agent.agent_id}")
```

### TypeScript

```typescript
import { AgentFramework } from '@agro/autonomous-agent-sdk';

const framework = new AgentFramework({ 
  apiKey: 'your_api_key' 
});

const agent = await framework.createAgent({
  name: 'My Harvest Agent',
  decision_model: {
    type: 'llm',
    provider: 'openai',
    model: 'gpt-4',
    system_prompt: `
      You are a harvest optimization agent.
      Analyze field data, weather, and robot availability.
      Decide if harvest should start now, wait, or postpone.
      Output JSON: {"decision": "START_HARVEST_NOW|WAIT|POSTPONE", "reasoning": "..."}
    `
  }
});

console.log(`✅ Agent created: ${agent.agent_id}`);
```

---

## Step 4: Register Tools

Tools are the APIs/services your agent can call to gather data or execute actions.

### Python

```python
from autonomous_agent import Tool

# Register field data source
precision_tool = Tool(
    name="field_data",
    type="data_source",
    endpoint="http://localhost:5000/api/v1/recommendations",
    method="GET",
    parameters={
        "field_id": {"type": "string", "required": True}
    },
    description="Get field readiness and productivity data"
)

agent.register_tool(precision_tool)

# Register weather API
weather_tool = Tool(
    name="weather",
    type="external_api",
    endpoint="https://api.openweathermap.org/data/2.5/forecast",
    method="GET",
    parameters={
        "lat": {"type": "float", "required": True},
        "lon": {"type": "float", "required": True}
    },
    description="Get 5-day weather forecast",
    authentication={
        "type": "query",
        "param": "appid",
        "value_env_var": "OPENWEATHER_API_KEY"
    }
)

agent.register_tool(weather_tool)

# Register action tool (allocate tasks to robots)
swarm_tool = Tool(
    name="allocate_robots",
    type="action",
    endpoint="http://localhost:5002/api/v1/allocate",
    method="POST",
    parameters={
        "tasks": {"type": "array", "required": True},
        "robots": {"type": "array", "required": True}
    },
    description="Allocate harvest tasks to robot swarm"
)

agent.register_tool(swarm_tool)

print("✅ Tools registered")
```

### TypeScript

```typescript
await agent.registerTool({
  name: 'field_data',
  type: 'data_source',
  endpoint: 'http://localhost:5000/api/v1/recommendations',
  method: 'GET',
  parameters: {
    field_id: { type: 'string', required: true }
  },
  description: 'Get field readiness data'
});

await agent.registerTool({
  name: 'weather',
  type: 'external_api',
  endpoint: 'https://api.openweathermap.org/data/2.5/forecast',
  method: 'GET',
  parameters: {
    lat: { type: 'float', required: true },
    lon: { type: 'float', required: true }
  },
  description: 'Get weather forecast',
  authentication: {
    type: 'query',
    param: 'appid',
    value_env_var: 'OPENWEATHER_API_KEY'
  }
});

await agent.registerTool({
  name: 'allocate_robots',
  type: 'action',
  endpoint: 'http://localhost:5002/api/v1/allocate',
  method: 'POST',
  parameters: {
    tasks: { type: 'array', required: true },
    robots: { type: 'array', required: true }
  },
  description: 'Allocate tasks to robot swarm'
});

console.log('✅ Tools registered');
```

---

## Step 5: Execute Agent

Now trigger the agent to analyze data and make a decision.

### Python

```python
# Execute synchronously
result = agent.execute(
    trigger_reason="Manual harvest check",
    context={
        "field_id": "FIELD-01",
        "priority": "HIGH"
    },
    async_mode=False  # Wait for completion
)

# Display results
print(f"Decision: {result.decision_made['decision']}")
print(f"Reasoning: {result.decision_made['reasoning']}")
print(f"Duration: {result.duration_seconds}s")

if result.outcome['success']:
    print(f"✅ Success! Impact: {result.outcome['estimated_impact']}")
```

### TypeScript

```typescript
const result = await agent.execute({
  trigger_reason: 'Manual harvest check',
  context: {
    field_id: 'FIELD-01',
    priority: 'HIGH'
  },
  async_mode: false
});

console.log(`Decision: ${result.decision_made.decision}`);
console.log(`Reasoning: ${result.decision_made.reasoning}`);
console.log(`Duration: ${result.duration_seconds}s`);

if (result.outcome?.success) {
  console.log(`✅ Success! Impact:`, result.outcome.estimated_impact);
}
```

---

## Step 6: Schedule Periodic Execution

Set the agent to run automatically every 30 minutes.

### Python

```python
schedule = agent.create_schedule(
    name="Periodic Harvest Check",
    cron="0 */30 * * *",  # Every 30 minutes
    enabled=True,
    context={"check_type": "automated"}
)

print(f"✅ Schedule created. Next run: {schedule.next_execution_at}")
```

### TypeScript

```typescript
const schedule = await agent.createSchedule({
  name: 'Periodic Harvest Check',
  cron: '0 */30 * * *',
  enabled: true,
  context: { check_type: 'automated' }
});

console.log(`✅ Schedule created. Next run: ${schedule.next_execution_at}`);
```

---

## Step 7: Add Long-Term Memory

Give your agent historical knowledge to improve decisions.

### Python

```python
# Store fact about optimal harvest timing
agent.store_memory(
    type="fact",
    content="Morning harvests (6am-10am) result in 8% higher juice quality",
    metadata={"timing": "morning", "impact": "quality"},
    ttl_days=365
)

# Store operational knowledge
agent.store_memory(
    type="fact",
    content="FIELD-01 typically requires 6.5 hours to harvest with 3 robots",
    metadata={"field_id": "FIELD-01", "source": "historical_data"},
    ttl_days=365
)

print("✅ Knowledge stored")
```

### TypeScript

```typescript
await agent.storeMemory({
  type: 'fact',
  content: 'Morning harvests (6am-10am) result in 8% higher juice quality',
  metadata: { timing: 'morning', impact: 'quality' },
  ttl_days: 365
});

await agent.storeMemory({
  type: 'fact',
  content: 'FIELD-01 typically requires 6.5 hours to harvest with 3 robots',
  metadata: { field_id: 'FIELD-01', source: 'historical_data' },
  ttl_days: 365
});

console.log('✅ Knowledge stored');
```

---

## Step 8: Set Goals

Define what the agent should optimize for.

### Python

```python
from autonomous_agent import Goal

# Goal: Minimize crop loss
agent.set_goal(Goal(
    name="minimize_crop_loss",
    priority="critical",
    metrics=["overripe_percentage", "harvest_delay_hours"],
    target={
        "overripe_percentage": "< 5%",
        "harvest_delay_hours": "< 24"
    }
))

# Goal: Maximize efficiency
agent.set_goal(Goal(
    name="maximize_efficiency",
    priority="high",
    metrics=["ha_per_hour"],
    target={"ha_per_hour": 10}
))

print("✅ Goals set")
```

### TypeScript

```typescript
await agent.setGoal({
  name: 'minimize_crop_loss',
  priority: 'critical',
  metrics: ['overripe_percentage', 'harvest_delay_hours'],
  target: {
    overripe_percentage: '< 5%',
    harvest_delay_hours: '< 24'
  }
});

await agent.setGoal({
  name: 'maximize_efficiency',
  priority: 'high',
  metrics: ['ha_per_hour'],
  target: { ha_per_hour: 10 }
});

console.log('✅ Goals set');
```

---

## Step 9: Monitor Performance

Check agent metrics and goal progress.

### Python

```python
from datetime import datetime, timedelta

# Get last 7 days of metrics
metrics = agent.get_metrics(
    from_date=datetime.now() - timedelta(days=7),
    to_date=datetime.now(),
    granularity="day"
)

print(f"Executions: {metrics.metrics['executions_count']}")
print(f"Success rate: {metrics.metrics['success_rate']*100:.1f}%")
print(f"Avg latency: {metrics.metrics['avg_decision_latency_ms']}ms")

# Check goal progress
goals = agent.get_goals()
for goal in goals:
    print(f"{goal.name}: {goal.progress*100:.0f}% complete")
```

### TypeScript

```typescript
const now = new Date();
const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

const metrics = await agent.getMetrics({
  from_date: weekAgo,
  to_date: now,
  granularity: 'day'
});

console.log(`Executions: ${metrics.metrics.executions_count}`);
console.log(`Success rate: ${(metrics.metrics.success_rate * 100).toFixed(1)}%`);
console.log(`Avg latency: ${metrics.metrics.avg_decision_latency_ms}ms`);

const goals = await agent.getGoals();
goals.forEach(goal => {
  console.log(`${goal.name}: ${(goal.progress * 100).toFixed(0)}% complete`);
});
```

---

## What's Next?

### Advanced Features

1. **Multi-Agent Coordination**: Create multiple specialized agents that coordinate
2. **Custom Decision Models**: Train your own ML models instead of using LLMs
3. **Advanced Memory**: Use RAG (Retrieval-Augmented Generation) for complex reasoning
4. **Webhooks**: Get real-time notifications when decisions are made
5. **A/B Testing**: Compare different decision strategies

### Example Projects

- **Energy Optimization**: Agent that coordinates solar panels, batteries, and grid
- **Maintenance Scheduler**: Predictive maintenance for robot fleet
- **Quality Control**: Agent that monitors product quality and adjusts processes
- **Supply Chain**: Optimize logistics and inventory based on demand forecasts

### Resources

- 📖 [Full Documentation](mocks/api_spec.md)
- 🎨 [Architecture Diagrams](mocks/architecture_diagrams.md)
- 💻 [Complete Examples](mocks/)
- 💬 [Community Discord](https://discord.gg/autonomous-agents)
- 📧 [Enterprise Support](mailto:enterprise@autonomous-agent.dev)

---

## Troubleshooting

### Agent not making decisions?
- Check LLM API key is valid
- Verify tools are responding (check logs)
- Ensure system prompt is clear and structured

### Tools timing out?
- Increase `timeout_ms` in tool configuration
- Check network connectivity to external services
- Implement retry policies

### High latency?
- Use faster LLM models (gpt-3.5-turbo vs gpt-4)
- Reduce number of tool calls
- Enable response caching
- Use parallel tool calls when possible

### Memory not working?
- Verify Redis/PostgreSQL connections
- Check embedding model is loaded
- Ensure similarity threshold isn't too high (try 0.7)

---

## Example Output

When you run your agent, you'll see output like:

```
🚀 Autonomous Agent Framework - Execution Started
====================================================================

📊 Execution ID: exec-harvest-20260220-143025
   Status: gathering_data

🔧 Calling tools:
   ✅ field_data: 124ms
   ✅ weather: 342ms
   ✅ robot_status: 98ms

🧠 Analyzing with GPT-4...

🤖 DECISION: START_HARVEST_NOW
   Priority: HIGH
   Reasoning: Field FIELD-01 is at 94% maturity with overripe zones 
              detected. Weather forecast shows rain probability increasing 
              to 70% tomorrow. Three robots available with good battery 
              levels (87%, 92%, 78%).
   
   Recommended robots: ROB-001, ROB-003, ROB-005
   Target zones: zone_3, zone_7 (overripe areas)
   Duration: 6.5 hours

⚡ Executing action: allocate_robots
   ✅ Tasks allocated to swarm coordinator

✅ OUTCOME:
   Success: true
   Robots allocated: 3
   Estimated crop saved: 25.8 tons
   Estimated revenue increase: $12,500.00

📈 Execution completed in 3.2s
====================================================================
```

---

## 🎉 Congratulations!

You've built your first autonomous agent! It can now:
- ✅ Gather data from multiple sources
- ✅ Make intelligent decisions using AI
- ✅ Execute actions automatically
- ✅ Learn from historical patterns
- ✅ Optimize towards defined goals

**Next Steps**: Explore the [complete example code](mocks/example_usage.py) for more advanced features!
