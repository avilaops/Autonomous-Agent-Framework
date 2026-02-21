"""
Autonomous Agent Framework - Example Usage
Demonstrates how to create and configure an autonomous agent for harvest optimization
"""

from autonomous_agent import AgentFramework, DecisionModel, Tool, Goal, MemoryConfig
from datetime import datetime, timedelta
import os

# Initialize framework
framework = AgentFramework(
    api_key=os.getenv("AGENT_FRAMEWORK_API_KEY"),
    base_url="http://localhost:6000/api/v1"
)

def create_harvest_optimizer_agent():
    """Create a harvest optimization agent with full configuration"""
    
    # Define decision model (LLM-based)
    decision_model = DecisionModel(
        type="llm",
        provider="openai",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        system_prompt="""
        You are an agricultural optimization agent specialized in harvest operations.
        
        Your role is to:
        1. Analyze data from multiple sources (field sensors, weather, robots, AI vision)
        2. Make decisions about harvest timing and resource allocation
        3. Prioritize crop quality, weather windows, and operational efficiency
        4. Output decisions in structured JSON format
        
        Decision Framework:
        - Consider crop maturity (optimal: 92-96%)
        - Weather windows (avoid rain, high wind)
        - Robot fleet availability and battery levels
        - Overripe zones (high priority)
        - ROI and efficiency metrics
        
        Always provide:
        {
          "decision": "START_HARVEST_NOW|WAIT|POSTPONE",
          "reasoning": "Clear explanation of factors",
          "priority": "HIGH|MEDIUM|LOW",
          "recommended_robots": ["ROB-001", ...],
          "estimated_duration_hours": 0.0,
          "risk_assessment": {...}
        }
        """
    )
    
    # Create agent
    agent = framework.create_agent(
        name="Harvest Optimizer Agent",
        description="Autonomous agent that optimizes harvest timing and resource allocation",
        capabilities=["data_analysis", "decision_making", "task_planning", "resource_optimization"],
        decision_model=decision_model,
        execution={
            "mode": "autonomous",
            "approval_required": False,
            "max_concurrent_tasks": 5,
            "timeout_seconds": 300
        },
        memory=MemoryConfig(
            short_term={"enabled": True, "max_messages": 10, "ttl_seconds": 3600},
            long_term={"enabled": True, "storage": "redis", "retention_days": 30},
            embeddings={"enabled": True, "model": "text-embedding-ada-002", "dimensions": 1536}
        )
    )
    
    print(f"✅ Agent created: {agent.agent_id}")
    return agent


def register_tools(agent):
    """Register all tools the agent will use"""
    
    tools = [
        Tool(
            name="precision_data",
            type="data_source",
            endpoint="http://localhost:5000/api/v1/recommendations",
            method="GET",
            parameters={
                "field_id": {"type": "string", "required": True}
            },
            description="Fetch field recommendations from Precision Agriculture Platform",
            authentication={"type": "bearer", "token_env_var": "PRECISION_API_KEY"}
        ),
        
        Tool(
            name="ai_vision",
            type="data_source",
            endpoint="http://localhost:5001/api/v1/maturity",
            method="GET",
            parameters={
                "field_id": {"type": "string", "required": True}
            },
            description="Get crop maturity analysis from AI-Vision system",
            authentication={"type": "bearer", "token_env_var": "AI_VISION_API_KEY"}
        ),
        
        Tool(
            name="swarm_coordinator",
            type="action",
            endpoint="http://localhost:5002/api/v1/allocate",
            method="POST",
            parameters={
                "tasks": {"type": "array", "required": True},
                "robots": {"type": "array", "required": True}
            },
            description="Allocate tasks to robot swarm",
            authentication={"type": "bearer", "token_env_var": "SWARM_API_KEY"}
        ),
        
        Tool(
            name="telemetry",
            type="monitor",
            endpoint="http://localhost:5003/api/v1/metrics",
            method="GET",
            parameters={
                "robot_ids": {"type": "array", "required": True},
                "metrics": {"type": "array", "required": True}
            },
            description="Monitor robot fleet telemetry",
            authentication={"type": "bearer", "token_env_var": "TELEMETRY_API_KEY"}
        ),
        
        Tool(
            name="weather_forecast",
            type="external_api",
            endpoint="https://api.openweathermap.org/data/2.5/forecast",
            method="GET",
            parameters={
                "lat": {"type": "float", "required": True},
                "lon": {"type": "float", "required": True}
            },
            description="Get 5-day weather forecast",
            authentication={"type": "query", "param": "appid", "value_env_var": "OPENWEATHER_API_KEY"}
        )
    ]
    
    for tool in tools:
        tool_id = agent.register_tool(tool)
        print(f"✅ Tool registered: {tool.name} ({tool_id})")


def set_agent_goals(agent):
    """Define goals for the agent to optimize towards"""
    
    goals = [
        Goal(
            name="maximize_harvest_efficiency",
            priority="high",
            metrics=["ha_per_hour", "fuel_consumption_per_ha"],
            target={
                "ha_per_hour": 10,
                "fuel_efficiency": "increase"
            },
            description="Increase harvest speed while minimizing fuel consumption"
        ),
        
        Goal(
            name="minimize_crop_loss",
            priority="critical",
            metrics=["overripe_percentage", "harvest_delay_hours"],
            target={
                "overripe_percentage": "< 5%",
                "harvest_delay_hours": "< 24"
            },
            description="Prevent crop loss from overripening or weather delays"
        ),
        
        Goal(
            name="optimize_battery_usage",
            priority="medium",
            metrics=["battery_cycles", "solar_utilization"],
            target={
                "solar_utilization": "> 80%",
                "battery_health": "maintain"
            },
            description="Maximize solar energy usage and maintain battery health"
        )
    ]
    
    for goal in goals:
        goal_id = agent.set_goal(goal)
        print(f"✅ Goal set: {goal.name} ({goal_id})")


def create_execution_schedule(agent):
    """Set up periodic execution schedule"""
    
    # Execute every 30 minutes during harvest season
    schedule = agent.create_schedule(
        name="Periodic Harvest Check",
        cron="0 */30 * * *",  # Every 30 minutes
        enabled=True,
        context={
            "check_type": "automated",
            "season": "harvest"
        }
    )
    
    print(f"✅ Schedule created: {schedule.schedule_id}")
    print(f"   Next execution: {schedule.next_execution_at}")


def add_historical_knowledge(agent):
    """Populate agent's long-term memory with historical data"""
    
    knowledge_base = [
        {
            "content": "FIELD-01 typically requires 6.5 hours to harvest completely with 3 robots",
            "metadata": {"field_id": "FIELD-01", "source": "historical_data"}
        },
        {
            "content": "Optimal harvest time for sugarcane is when maturity reaches 92-96% and Brix levels are 18-22",
            "metadata": {"crop": "sugarcane", "source": "agronomic_guidelines"}
        },
        {
            "content": "Heavy rain (>20mm) within 48 hours after harvest reduces juice quality by approximately 12%",
            "metadata": {"factor": "weather", "impact": "quality"}
        },
        {
            "content": "Robot ROB-003 has the highest efficiency on sloped terrain due to upgraded traction system",
            "metadata": {"robot_id": "ROB-003", "specialization": "slopes"}
        },
        {
            "content": "Morning harvests (6am-10am) result in 8% higher juice quality due to lower ambient temperature",
            "metadata": {"timing": "morning", "impact": "quality"}
        }
    ]
    
    for knowledge in knowledge_base:
        memory_id = agent.store_memory(
            type="fact",
            content=knowledge["content"],
            metadata=knowledge["metadata"],
            ttl_days=365
        )
        print(f"✅ Knowledge stored: {memory_id}")


def manual_execution_example(agent):
    """Manually trigger agent execution"""
    
    print("\n" + "="*60)
    print("MANUAL EXECUTION EXAMPLE")
    print("="*60)
    
    # Trigger execution
    execution = agent.execute(
        trigger_reason="Manual harvest check requested by operator",
        context={
            "field_ids": ["FIELD-01", "FIELD-02"],
            "priority": "HIGH",
            "operator": "João Silva"
        },
        async_mode=False  # Wait for completion
    )
    
    print(f"\n📊 Execution ID: {execution.execution_id}")
    print(f"   Status: {execution.status}")
    print(f"   Duration: {execution.duration_seconds}s")
    
    # Display decision
    decision = execution.decision_made
    print(f"\n🤖 DECISION: {decision['decision']}")
    print(f"   Priority: {decision['priority']}")
    print(f"   Reasoning: {decision['reasoning']}")
    
    if decision['decision'] == "START_HARVEST_NOW":
        print(f"   Robots: {', '.join(decision['recommended_robots'])}")
        print(f"   Duration: {decision['estimated_duration_hours']} hours")
    
    # Display outcome
    outcome = execution.outcome
    if outcome['success']:
        print(f"\n✅ OUTCOME:")
        print(f"   Robots allocated: {outcome['robots_allocated']}")
        print(f"   Estimated crop saved: {outcome['estimated_impact']['crop_saved_tons']} tons")
        print(f"   Estimated revenue increase: ${outcome['estimated_impact']['revenue_increase_usd']:,.2f}")
    
    return execution


def query_agent_metrics(agent):
    """Retrieve and display agent performance metrics"""
    
    print("\n" + "="*60)
    print("AGENT PERFORMANCE METRICS")
    print("="*60)
    
    # Get metrics for last 30 days
    metrics = agent.get_metrics(
        from_date=datetime.now() - timedelta(days=30),
        to_date=datetime.now(),
        granularity="day"
    )
    
    print(f"\n📈 Period: {metrics.period['from']} to {metrics.period['to']}")
    print(f"   Total executions: {metrics.metrics['executions_count']}")
    print(f"   Success rate: {metrics.metrics['success_rate']*100:.1f}%")
    print(f"   Avg decision latency: {metrics.metrics['avg_decision_latency_ms']}ms")
    print(f"   Goals achieved: {metrics.metrics['goals_achieved']}")
    print(f"   Estimated ROI: ${metrics.metrics['estimated_roi_usd']:,.2f}")
    
    # Display goal progress
    goals = agent.get_goals()
    print(f"\n🎯 GOAL PROGRESS:")
    for goal in goals:
        progress_bar = "█" * int(goal.progress * 20) + "░" * (20 - int(goal.progress * 20))
        print(f"   {goal.name}: [{progress_bar}] {goal.progress*100:.0f}%")
        print(f"      Current: {goal.current_value} | Target: {goal.target_value}")


def semantic_memory_search(agent):
    """Example of semantic search in agent's memory"""
    
    print("\n" + "="*60)
    print("SEMANTIC MEMORY SEARCH")
    print("="*60)
    
    query = "What factors affect harvest quality?"
    
    results = agent.search_memory(
        query=query,
        limit=3,
        threshold=0.75
    )
    
    print(f"\n🔍 Query: '{query}'")
    print(f"   Found {len(results)} relevant memories:\n")
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. [Similarity: {result.similarity:.2f}]")
        print(f"      {result.content}")
        print()


def setup_webhooks(agent):
    """Configure webhooks for important events"""
    
    webhooks = [
        {
            "event": "decision.made",
            "url": "https://your-server.com/api/webhooks/decision",
            "headers": {"Authorization": "Bearer YOUR_WEBHOOK_SECRET"}
        },
        {
            "event": "execution.failed",
            "url": "https://your-server.com/api/webhooks/failure",
            "headers": {"Authorization": "Bearer YOUR_WEBHOOK_SECRET"}
        },
        {
            "event": "goal.achieved",
            "url": "https://your-server.com/api/webhooks/goal",
            "headers": {"Authorization": "Bearer YOUR_WEBHOOK_SECRET"}
        }
    ]
    
    for webhook in webhooks:
        webhook_id = agent.register_webhook(
            event=webhook["event"],
            url=webhook["url"],
            headers=webhook["headers"]
        )
        print(f"✅ Webhook registered: {webhook['event']} → {webhook_id}")


def main():
    """Main setup and execution flow"""
    
    print("🚀 Autonomous Agent Framework - Setup and Execution")
    print("="*60)
    
    # 1. Create agent
    print("\n1️⃣ Creating agent...")
    agent = create_harvest_optimizer_agent()
    
    # 2. Register tools
    print("\n2️⃣ Registering tools...")
    register_tools(agent)
    
    # 3. Set goals
    print("\n3️⃣ Setting agent goals...")
    set_agent_goals(agent)
    
    # 4. Add historical knowledge
    print("\n4️⃣ Populating knowledge base...")
    add_historical_knowledge(agent)
    
    # 5. Create schedule
    print("\n5️⃣ Creating execution schedule...")
    create_execution_schedule(agent)
    
    # 6. Setup webhooks
    print("\n6️⃣ Configuring webhooks...")
    setup_webhooks(agent)
    
    # 7. Manual execution example
    execution = manual_execution_example(agent)
    
    # 8. Query metrics
    query_agent_metrics(agent)
    
    # 9. Semantic search
    semantic_memory_search(agent)
    
    print("\n" + "="*60)
    print("✅ Agent setup complete and operational!")
    print(f"   Agent ID: {agent.agent_id}")
    print(f"   Status: {agent.status}")
    print(f"   Tools: {agent.tools_count}")
    print("="*60)


if __name__ == "__main__":
    main()
