# Autonomous Agent Framework - API Specification

## Overview
SDK for building autonomous multi-tool agents that can interact with the agricultural ecosystem.

## Base URL
```
http://localhost:6000/api/v1
```

## Authentication
All endpoints require JWT Bearer token:
```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. Agent Management

#### POST /agents
Create a new autonomous agent.

**Request:**
```json
{
  "name": "Harvest Optimizer Agent",
  "description": "Optimizes harvest timing and resource allocation",
  "capabilities": ["data_analysis", "decision_making", "task_planning"],
  "decision_model": {
    "type": "llm",
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "system_prompt": "You are an agricultural optimization agent..."
  },
  "execution": {
    "mode": "autonomous",
    "approval_required": false
  }
}
```

**Response (201):**
```json
{
  "agent_id": "AGENT-HARVEST-001",
  "status": "created",
  "api_key": "agent_sk_abc123...",
  "created_at": "2026-02-20T21:30:00Z"
}
```

---

#### GET /agents
List all agents owned by the user.

**Response (200):**
```json
{
  "agents": [
    {
      "agent_id": "AGENT-HARVEST-001",
      "name": "Harvest Optimizer Agent",
      "status": "active",
      "executions_count": 142,
      "success_rate": 0.96,
      "uptime_hours": 720.5
    }
  ],
  "total": 1
}
```

---

#### GET /agents/:agent_id
Get agent details.

**Response (200):**
```json
{
  "agent_id": "AGENT-HARVEST-001",
  "name": "Harvest Optimizer Agent",
  "description": "Optimizes harvest timing...",
  "status": "active",
  "capabilities": ["data_analysis", "decision_making"],
  "tools_count": 5,
  "created_at": "2026-02-20T21:30:00Z",
  "metrics": {
    "decisions_made": 142,
    "success_rate": 0.96,
    "avg_latency_ms": 2340,
    "uptime_hours": 720.5
  }
}
```

---

#### PATCH /agents/:agent_id
Update agent configuration.

**Request:**
```json
{
  "status": "paused",
  "decision_model": {
    "temperature": 0.5
  }
}
```

**Response (200):**
```json
{
  "agent_id": "AGENT-HARVEST-001",
  "status": "paused",
  "updated_at": "2026-02-20T22:00:00Z"
}
```

---

#### DELETE /agents/:agent_id
Delete an agent permanently.

**Response (204):** No content

---

### 2. Tool Registry

#### POST /agents/:agent_id/tools
Register a tool for the agent to use.

**Request:**
```json
{
  "name": "precision_data",
  "type": "data_source",
  "endpoint": "http://localhost:5000/api/v1/recommendations",
  "method": "GET",
  "parameters": {
    "field_id": {
      "type": "string",
      "required": true
    }
  },
  "description": "Fetch field recommendations from Precision Platform",
  "authentication": {
    "type": "bearer",
    "token_env_var": "PRECISION_API_KEY"
  }
}
```

**Response (201):**
```json
{
  "tool_id": "TOOL-001",
  "name": "precision_data",
  "status": "registered",
  "registered_at": "2026-02-20T21:35:00Z"
}
```

---

#### GET /agents/:agent_id/tools
List all tools registered for an agent.

**Response (200):**
```json
{
  "tools": [
    {
      "tool_id": "TOOL-001",
      "name": "precision_data",
      "type": "data_source",
      "status": "active",
      "call_count": 847,
      "avg_latency_ms": 124,
      "success_rate": 0.99
    }
  ],
  "total": 5
}
```

---

#### DELETE /agents/:agent_id/tools/:tool_id
Unregister a tool.

**Response (204):** No content

---

### 3. Execution Control

#### POST /agents/:agent_id/execute
Trigger agent execution manually.

**Request:**
```json
{
  "trigger_reason": "Manual harvest check requested by operator",
  "context": {
    "field_ids": ["FIELD-01", "FIELD-02"],
    "priority": "HIGH"
  },
  "async": true
}
```

**Response (202):**
```json
{
  "execution_id": "exec-harvest-20260220-143025",
  "status": "started",
  "async": true,
  "started_at": "2026-02-20T14:30:25Z",
  "check_status_url": "/api/v1/executions/exec-harvest-20260220-143025"
}
```

---

#### GET /executions/:execution_id
Get execution status and results.

**Response (200):**
```json
{
  "execution_id": "exec-harvest-20260220-143025",
  "agent_id": "AGENT-HARVEST-001",
  "status": "completed_success",
  "started_at": "2026-02-20T14:30:25Z",
  "ended_at": "2026-02-20T14:35:42Z",
  "duration_seconds": 317,
  "steps_completed": 5,
  "decision_made": {
    "decision": "START_HARVEST_NOW",
    "priority": "HIGH",
    "reasoning": "Field FIELD-01 is at 94% maturity...",
    "actions_executed": 1
  },
  "outcome": {
    "success": true,
    "robots_allocated": 3,
    "estimated_impact": {
      "crop_saved_tons": 25.8,
      "revenue_increase_usd": 12500.00
    }
  }
}
```

---

#### GET /executions/:execution_id/trace
Get detailed execution trace.

**Response (200):**
```json
{
  "execution_id": "exec-harvest-20260220-143025",
  "steps": [
    {
      "step": 1,
      "action": "gather_data",
      "tool_calls": [
        {
          "tool": "precision_data",
          "params": {"field_id": "FIELD-01"},
          "response": {...},
          "latency_ms": 124
        }
      ],
      "status": "success",
      "duration_ms": 851
    }
  ],
  "logs": [
    {"level": "INFO", "timestamp": "2026-02-20T14:30:25Z", "message": "Agent execution started"}
  ]
}
```

---

#### POST /executions/:execution_id/cancel
Cancel a running execution.

**Response (200):**
```json
{
  "execution_id": "exec-harvest-20260220-143025",
  "status": "cancelled",
  "cancelled_at": "2026-02-20T14:32:00Z"
}
```

---

### 4. Memory Management

#### POST /agents/:agent_id/memory
Store information in agent's long-term memory.

**Request:**
```json
{
  "type": "fact",
  "content": "FIELD-01 typically requires 6.5 hours to harvest completely",
  "metadata": {
    "field_id": "FIELD-01",
    "source": "historical_data"
  },
  "ttl_days": 365
}
```

**Response (201):**
```json
{
  "memory_id": "MEM-001",
  "stored_at": "2026-02-20T21:40:00Z",
  "embedding_generated": true
}
```

---

#### GET /agents/:agent_id/memory/search
Search agent's memory using semantic search.

**Query Parameters:**
- `q` (string): Search query
- `limit` (int): Max results (default: 10)
- `threshold` (float): Similarity threshold (default: 0.8)

**Response (200):**
```json
{
  "results": [
    {
      "memory_id": "MEM-001",
      "content": "FIELD-01 typically requires 6.5 hours to harvest completely",
      "similarity": 0.92,
      "stored_at": "2026-02-20T21:40:00Z"
    }
  ],
  "total": 1
}
```

---

#### DELETE /agents/:agent_id/memory/:memory_id
Delete a memory entry.

**Response (204):** No content

---

### 5. Goals & Metrics

#### POST /agents/:agent_id/goals
Define a goal for the agent.

**Request:**
```json
{
  "name": "maximize_harvest_efficiency",
  "priority": "high",
  "metrics": ["ha_per_hour", "fuel_consumption_per_ha"],
  "target": {
    "ha_per_hour": 10,
    "fuel_efficiency": "increase"
  }
}
```

**Response (201):**
```json
{
  "goal_id": "GOAL-001",
  "status": "active",
  "created_at": "2026-02-20T21:45:00Z"
}
```

---

#### GET /agents/:agent_id/goals
List all goals.

**Response (200):**
```json
{
  "goals": [
    {
      "goal_id": "GOAL-001",
      "name": "maximize_harvest_efficiency",
      "priority": "high",
      "status": "active",
      "progress": 0.67,
      "current_value": 8.5,
      "target_value": 10
    }
  ],
  "total": 3
}
```

---

#### GET /agents/:agent_id/metrics
Get agent performance metrics.

**Query Parameters:**
- `from` (ISO 8601 date): Start date
- `to` (ISO 8601 date): End date
- `granularity` (string): hour, day, week (default: day)

**Response (200):**
```json
{
  "period": {
    "from": "2026-02-01T00:00:00Z",
    "to": "2026-02-20T23:59:59Z"
  },
  "metrics": {
    "executions_count": 142,
    "success_rate": 0.96,
    "avg_decision_latency_ms": 2340,
    "total_decisions_made": 142,
    "goals_achieved": 2,
    "estimated_roi_usd": 178500.00
  },
  "time_series": [
    {
      "timestamp": "2026-02-01T00:00:00Z",
      "executions": 8,
      "success_rate": 0.95
    }
  ]
}
```

---

### 6. Scheduling

#### POST /agents/:agent_id/schedules
Create execution schedule.

**Request:**
```json
{
  "name": "Periodic Harvest Check",
  "cron": "0 */30 * * *",
  "enabled": true,
  "context": {
    "check_type": "automated"
  }
}
```

**Response (201):**
```json
{
  "schedule_id": "SCHED-001",
  "next_execution_at": "2026-02-20T15:00:00Z",
  "created_at": "2026-02-20T21:50:00Z"
}
```

---

#### GET /agents/:agent_id/schedules
List all schedules.

**Response (200):**
```json
{
  "schedules": [
    {
      "schedule_id": "SCHED-001",
      "name": "Periodic Harvest Check",
      "cron": "0 */30 * * *",
      "enabled": true,
      "next_execution_at": "2026-02-20T15:00:00Z",
      "executions_count": 48
    }
  ],
  "total": 1
}
```

---

#### DELETE /agents/:agent_id/schedules/:schedule_id
Delete a schedule.

**Response (204):** No content

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID AGENT-HARVEST-001 not found",
    "details": {},
    "timestamp": "2026-02-20T22:00:00Z"
  }
}
```

### Error Codes
- `AGENT_NOT_FOUND` (404)
- `TOOL_NOT_FOUND` (404)
- `EXECUTION_FAILED` (500)
- `INVALID_CONFIGURATION` (400)
- `UNAUTHORIZED` (401)
- `RATE_LIMIT_EXCEEDED` (429)
- `LLM_PROVIDER_ERROR` (502)

---

## Rate Limits
- 100 requests/minute per agent
- 10 concurrent executions per agent
- 1000 tool calls/hour per agent

---

## Webhooks

Agents can send webhooks on certain events:

### Events
- `execution.started`
- `execution.completed`
- `execution.failed`
- `decision.made`
- `goal.achieved`
- `alert.triggered`

### Webhook Payload Example
```json
{
  "event": "decision.made",
  "timestamp": "2026-02-20T14:30:29Z",
  "agent_id": "AGENT-HARVEST-001",
  "data": {
    "execution_id": "exec-harvest-20260220-143025",
    "decision": "START_HARVEST_NOW",
    "priority": "HIGH"
  }
}
```

---

## SDK Libraries

### Python
```bash
pip install autonomous-agent-sdk
```

```python
from autonomous_agent import AgentFramework

framework = AgentFramework(api_key="your_api_key")

# Create agent
agent = framework.create_agent(
    name="My Agent",
    decision_model={
        "type": "llm",
        "provider": "openai",
        "model": "gpt-4"
    }
)

# Register tool
agent.register_tool(
    name="data_source",
    endpoint="http://api.example.com/data",
    method="GET"
)

# Execute
result = agent.execute(context={"field_id": "FIELD-01"})
print(result.decision)
```

### JavaScript/TypeScript
```bash
npm install @agro/autonomous-agent-sdk
```

```typescript
import { AgentFramework } from '@agro/autonomous-agent-sdk';

const framework = new AgentFramework({ apiKey: 'your_api_key' });

const agent = await framework.createAgent({
  name: 'My Agent',
  decisionModel: {
    type: 'llm',
    provider: 'openai',
    model: 'gpt-4'
  }
});

const result = await agent.execute({ fieldId: 'FIELD-01' });
console.log(result.decision);
```

---

## Best Practices

1. **Tool Registration**: Register only necessary tools to reduce decision latency
2. **Memory Management**: Use TTLs to prevent memory bloat
3. **Goal Setting**: Define clear, measurable goals with realistic targets
4. **Error Handling**: Implement retry policies for transient failures
5. **Monitoring**: Set up alerts for critical failures
6. **Security**: Rotate API keys regularly, use environment variables
7. **Testing**: Test agents in sandbox mode before production deployment

---

## Versioning
API version is included in the URL: `/api/v1/`

Breaking changes will result in a new version: `/api/v2/`
