"""
Autonomous Agent Framework - Agent Executor Mock
Implements the core ReAct (Reason + Act) loop for autonomous agent execution
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional


class AgentExecutor:
    """
    Core executor that implements the ReAct framework:
    1. Reason: Agent thinks about what to do next
    2. Act: Agent executes a tool
    3. Observe: Agent observes the result
    4. Repeat until goal is achieved or max iterations reached
    """
    
    def __init__(self, config: Dict[str, Any], tool_registry: Any, state_manager: Any):
        self.config = config
        self.agent_id = config.get('agent_id', 'AGENT-001')
        self.tools = tool_registry
        self.state = state_manager
        self.max_iterations = config.get('execution', {}).get('max_concurrent_tasks', 5)
        self.timeout = config.get('execution', {}).get('timeout_seconds', 300)
        
        # Execution metrics
        self.metrics = {
            'iterations': 0,
            'tools_executed': 0,
            'reasoning_steps': 0,
            'total_time_ms': 0,
            'success_rate': 0.0
        }
        
        print(f"🤖 AgentExecutor initialized: {self.agent_id}")
        print(f"   Max iterations: {self.max_iterations}, Timeout: {self.timeout}s")
    
    def _reason(self, goal: str, context: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """
        Reasoning step: Agent decides what to do next
        
        In production: This would call an LLM with:
        - Goal/objective
        - Current context
        - Available tools
        - Execution history
        
        Mock: Simulates intelligent reasoning based on goal and available data
        """
        self.metrics['reasoning_steps'] += 1
        
        # Simulate reasoning delay
        time.sleep(0.1)
        
        # Analyze goal and context to decide next action
        available_tools = self.tools.list_tools()
        history = context.get('execution_history', [])
        
        # Simple rule-based reasoning (production would use LLM)
        if iteration == 1:
            # First iteration: gather data
            thought = f"I need to gather initial data to understand '{goal}'"
            selected_tool = next((t for t in available_tools if t['type'] == 'data_source'), available_tools[0])
            confidence = 0.85
        
        elif iteration == 2:
            # Second iteration: analyze or fetch more data
            thought = f"I should fetch additional data or analyze what I have"
            data_tools = [t for t in available_tools if t['type'] in ['data_source', 'external_api']]
            selected_tool = random.choice(data_tools) if data_tools else available_tools[0]
            confidence = 0.78
        
        elif iteration == 3:
            # Third iteration: take action based on data
            thought = f"Based on the data, I should take action to progress toward '{goal}'"
            action_tools = [t for t in available_tools if t['type'] == 'action']
            selected_tool = random.choice(action_tools) if action_tools else available_tools[0]
            confidence = 0.82
        
        else:
            # Further iterations: monitor or finalize
            thought = f"I should monitor the results or finalize the task"
            monitor_tools = [t for t in available_tools if t['type'] in ['monitor', 'action']]
            selected_tool = random.choice(monitor_tools) if monitor_tools else available_tools[0]
            confidence = 0.75
        
        reasoning = {
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'thought': thought,
            'selected_tool': selected_tool['name'],
            'tool_type': selected_tool['type'],
            'confidence': confidence,
            'reasoning_depth': min(3, iteration)  # How deep we're thinking
        }
        
        print(f"\n🧠 REASONING (Iteration {iteration}):")
        print(f"   Thought: {thought}")
        print(f"   Selected tool: {selected_tool['name']} ({selected_tool['type']})")
        print(f"   Confidence: {confidence:.2%}")
        
        return reasoning
    
    def _act(self, tool_name: str, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action step: Execute the selected tool
        
        In production: This would make actual API calls
        Mock: Simulates tool execution with realistic results
        """
        self.metrics['tools_executed'] += 1
        start_time = time.time()
        
        # Execute tool through tool registry
        result = self.tools.execute_tool(tool_name, context)
        
        execution_time_ms = (time.time() - start_time) * 1000
        self.metrics['total_time_ms'] += execution_time_ms
        
        action = {
            'tool': tool_name,
            'timestamp': datetime.now().isoformat(),
            'input': context.get('tool_input', {}),
            'result': result,
            'execution_time_ms': execution_time_ms,
            'success': result.get('success', True)
        }
        
        print(f"⚡ ACTION: Executed {tool_name}")
        print(f"   Time: {execution_time_ms:.0f}ms")
        print(f"   Success: {action['success']}")
        
        return action
    
    def _observe(self, action: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Observation step: Analyze the action result
        
        In production: LLM would interpret results and decide if goal is achieved
        Mock: Simple rule-based observation
        """
        result = action.get('result', {})
        success = action.get('success', False)
        
        # Analyze if we're making progress toward goal
        data_gathered = bool(result.get('data') or result.get('recommendations') or result.get('status'))
        
        # Calculate progress (mock: increases with each successful action)
        current_progress = self.metrics['tools_executed'] / self.max_iterations
        
        observation = {
            'timestamp': datetime.now().isoformat(),
            'action_success': success,
            'data_gathered': data_gathered,
            'progress_toward_goal': current_progress,
            'summary': self._generate_observation_summary(action, goal),
            'goal_achieved': current_progress >= 0.8  # Mock: 80% progress = goal achieved
        }
        
        print(f"👁️  OBSERVATION:")
        print(f"   {observation['summary']}")
        print(f"   Progress: {current_progress:.1%}")
        print(f"   Goal achieved: {observation['goal_achieved']}")
        
        return observation
    
    def _generate_observation_summary(self, action: Dict[str, Any], goal: str) -> str:
        """Generate human-readable observation summary"""
        tool = action['tool']
        result = action.get('result', {})
        success = action.get('success', False)
        
        if not success:
            return f"Tool {tool} failed - need to retry or use alternative approach"
        
        # Generate summary based on tool type and result
        if 'data' in str(result):
            return f"Successfully retrieved data from {tool} - contains useful information for '{goal}'"
        elif 'status' in str(result):
            status = result.get('status', 'unknown')
            return f"Tool {tool} reports status: {status}"
        elif 'recommendations' in str(result):
            return f"Received recommendations from {tool} that can help achieve '{goal}'"
        else:
            return f"Tool {tool} executed successfully - gathered information"
    
    def execute(self, goal: str, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution loop: ReAct framework implementation
        
        Args:
            goal: The objective the agent should achieve
            initial_context: Optional initial context/data
        
        Returns:
            Execution results with history and metrics
        """
        print(f"\n{'='*80}")
        print(f"🎯 STARTING AGENT EXECUTION")
        print(f"   Agent: {self.agent_id}")
        print(f"   Goal: {goal}")
        print(f"{'='*80}\n")
        
        execution_start = time.time()
        context = initial_context or {}
        context['goal'] = goal
        context['execution_history'] = []
        
        # Update state
        self.state.update_state('status', 'executing')
        self.state.update_state('current_task', goal)
        
        iteration = 0
        goal_achieved = False
        
        # ReAct Loop
        while iteration < self.max_iterations and not goal_achieved:
            iteration += 1
            self.metrics['iterations'] = iteration
            
            # Check timeout
            elapsed = time.time() - execution_start
            if elapsed > self.timeout:
                print(f"\n⏱️  TIMEOUT after {elapsed:.1f}s")
                break
            
            # 1. REASON: Decide what to do
            reasoning = self._reason(goal, context, iteration)
            
            # 2. ACT: Execute selected tool
            action = self._act(reasoning['selected_tool'], goal, context)
            
            # 3. OBSERVE: Analyze result
            observation = self._observe(action, goal)
            goal_achieved = observation['goal_achieved']
            
            # Record this iteration
            step = {
                'iteration': iteration,
                'reasoning': reasoning,
                'action': action,
                'observation': observation
            }
            context['execution_history'].append(step)
            
            # Update state
            self.state.add_to_memory('execution_history', step)
            
            # Small delay between iterations
            time.sleep(0.2)
        
        # Final results
        total_time = time.time() - execution_start
        self.metrics['total_time_ms'] = total_time * 1000
        
        # Calculate success rate
        successful_actions = sum(1 for step in context['execution_history'] 
                                if step['action'].get('success', False))
        self.metrics['success_rate'] = successful_actions / self.metrics['iterations'] if self.metrics['iterations'] > 0 else 0
        
        # Update final state
        self.state.update_state('status', 'completed' if goal_achieved else 'incomplete')
        self.state.update_state('current_task', None)
        self.state.update_state('decisions_made', self.metrics['iterations'])
        self.state.update_state('success_rate', self.metrics['success_rate'])
        
        # Print summary
        self._print_summary(goal, goal_achieved, total_time, context)
        
        return {
            'success': goal_achieved,
            'goal': goal,
            'iterations': self.metrics['iterations'],
            'total_time_seconds': total_time,
            'execution_history': context['execution_history'],
            'metrics': self.metrics,
            'final_state': self.state.get_state()
        }
    
    def _print_summary(self, goal: str, achieved: bool, time_seconds: float, context: Dict):
        """Print execution summary"""
        print(f"\n{'='*80}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Goal: {goal}")
        print(f"Status: {'✅ ACHIEVED' if achieved else '❌ INCOMPLETE'}")
        print(f"Iterations: {self.metrics['iterations']}/{self.max_iterations}")
        print(f"Tools executed: {self.metrics['tools_executed']}")
        print(f"Reasoning steps: {self.metrics['reasoning_steps']}")
        print(f"Total time: {time_seconds:.2f}s")
        print(f"Success rate: {self.metrics['success_rate']:.1%}")
        print(f"{'='*80}\n")


def test_agent_executor():
    """Test the agent executor with mock configuration"""
    print("\n🧪 TESTING AGENT EXECUTOR\n")
    
    # Load agent config
    with open('example_agent_config.json', 'r') as f:
        config = json.load(f)
    
    # Import dependencies (mock)
    from tool_registry_mock import ToolRegistry
    from state_manager_mock import StateManager
    
    # Initialize components
    tool_registry = ToolRegistry(config['tools'])
    state_manager = StateManager(config['agent_id'], config.get('memory', {}))
    
    # Create executor
    executor = AgentExecutor(config, tool_registry, state_manager)
    
    # Execute test goal
    goal = "Optimize harvest operations for Field-001 considering weather, crop maturity, and robot availability"
    
    result = executor.execute(goal)
    
    # Validate results
    print("\n✅ TEST RESULTS:")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Tools executed: {result['metrics']['tools_executed']}")
    print(f"   Total time: {result['total_time_seconds']:.2f}s")
    
    return result


if __name__ == '__main__':
    result = test_agent_executor()
    
    # Save execution trace
    with open('execution_trace_test.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print("\n💾 Execution trace saved to execution_trace_test.json")
