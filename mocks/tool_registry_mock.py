"""
Autonomous Agent Framework - Tool Registry Mock
Manages tool registration, discovery, and execution
"""

import json
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime


class ToolRegistry:
    """
    Central registry for all tools available to agents
    Handles tool registration, discovery, validation, and execution
    """
    
    def __init__(self, tools_config: List[Dict[str, Any]]):
        self.tools = {}
        self.execution_stats = {}
        
        # Register all configured tools
        for tool_config in tools_config:
            self.register_tool(tool_config)
        
        print(f"🔧 ToolRegistry initialized with {len(self.tools)} tools")
    
    def register_tool(self, tool_config: Dict[str, Any]):
        """Register a new tool"""
        tool_name = tool_config.get('name')
        if not tool_name:
            raise ValueError("Tool must have a 'name' field")
        
        self.tools[tool_name] = {
            **tool_config,
            'registered_at': datetime.now().isoformat(),
            'execution_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_execution_time_ms': 0
        }
        
        self.execution_stats[tool_name] = {
            'executions': 0,
            'successes': 0,
            'failures': 0,
            'avg_time_ms': 0
        }
        
        print(f"   ✓ Registered tool: {tool_name} ({tool_config.get('type', 'unknown')})")
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self, tool_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered tools, optionally filtered by type"""
        tools = list(self.tools.values())
        
        if tool_type:
            tools = [t for t in tools if t.get('type') == tool_type]
        
        return tools
    
    def execute_tool(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given context
        
        In production: This would make actual HTTP requests to endpoints
        Mock: Simulates tool execution with realistic responses
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f"Tool {tool_name} not found",
                'timestamp': datetime.now().isoformat()
            }
        
        # Record execution attempt
        tool['execution_count'] += 1
        self.execution_stats[tool_name]['executions'] += 1
        
        start_time = time.time()
        
        # Simulate network delay
        time.sleep(random.uniform(0.05, 0.15))
        
        # Execute based on tool type
        result = self._mock_execute(tool, context)
        
        # Record execution time
        execution_time_ms = (time.time() - start_time) * 1000
        tool['total_execution_time_ms'] += execution_time_ms
        
        # Update stats
        if result.get('success', True):
            tool['success_count'] += 1
            self.execution_stats[tool_name]['successes'] += 1
        else:
            tool['failure_count'] += 1
            self.execution_stats[tool_name]['failures'] += 1
        
        self.execution_stats[tool_name]['avg_time_ms'] = (
            tool['total_execution_time_ms'] / tool['execution_count']
        )
        
        # Add metadata to result
        result['tool_name'] = tool_name
        result['execution_time_ms'] = execution_time_ms
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    def _mock_execute(self, tool: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock execution of tool based on its type
        Simulates realistic responses from each tool
        """
        tool_type = tool.get('type', 'unknown')
        tool_name = tool.get('name', 'unknown')
        
        # Simulate 95% success rate (some tools might fail)
        success = random.random() < 0.95
        
        if not success:
            return {
                'success': False,
                'error': f"Tool {tool_name} execution failed (network timeout)",
                'retry_recommended': True
            }
        
        # Generate response based on tool type
        if tool_type == 'data_source':
            return self._mock_data_source(tool_name, context)
        
        elif tool_type == 'action':
            return self._mock_action(tool_name, context)
        
        elif tool_type == 'monitor':
            return self._mock_monitor(tool_name, context)
        
        elif tool_type == 'external_api':
            return self._mock_external_api(tool_name, context)
        
        else:
            return {
                'success': True,
                'message': f"Tool {tool_name} executed successfully",
                'data': {}
            }
    
    def _mock_data_source(self, tool_name: str, context: Dict) -> Dict:
        """Mock data source tool execution"""
        if 'precision' in tool_name.lower():
            return {
                'success': True,
                'source': 'Precision Agriculture Platform',
                'data': {
                    'field_id': context.get('field_id', 'FIELD-001'),
                    'recommendations': [
                        {
                            'zone_id': 'ZONE-A',
                            'crop_maturity': 94.5,
                            'soil_moisture': 68.2,
                            'harvest_priority': 'HIGH',
                            'estimated_yield_ton_per_ha': 85.3
                        },
                        {
                            'zone_id': 'ZONE-B',
                            'crop_maturity': 88.1,
                            'soil_moisture': 72.5,
                            'harvest_priority': 'MEDIUM',
                            'estimated_yield_ton_per_ha': 79.8
                        }
                    ],
                    'optimal_harvest_window': {
                        'start': '2026-02-21T06:00:00Z',
                        'end': '2026-02-23T18:00:00Z',
                        'confidence': 0.87
                    }
                }
            }
        
        elif 'vision' in tool_name.lower() or 'ai' in tool_name.lower():
            return {
                'success': True,
                'source': 'AI Vision Agriculture',
                'data': {
                    'field_id': context.get('field_id', 'FIELD-001'),
                    'maturity_analysis': {
                        'average_maturity': 92.3,
                        'maturity_distribution': {
                            'underripe': 8.2,
                            'optimal': 76.5,
                            'overripe': 15.3
                        },
                        'harvest_recommendation': 'IMMEDIATE',
                        'quality_score': 0.89
                    },
                    'detections': {
                        'healthy_plants': 8752,
                        'stressed_plants': 431,
                        'diseased_plants': 28
                    }
                }
            }
        
        else:
            return {
                'success': True,
                'source': tool_name,
                'data': {
                    'records_found': random.randint(50, 500),
                    'status': 'data_retrieved',
                    'quality': random.choice(['high', 'high', 'medium'])
                }
            }
    
    def _mock_action(self, tool_name: str, context: Dict) -> Dict:
        """Mock action tool execution"""
        if 'swarm' in tool_name.lower() or 'coordinator' in tool_name.lower():
            return {
                'success': True,
                'action': 'task_allocation',
                'data': {
                    'tasks_allocated': 3,
                    'robots_assigned': ['ROB-001', 'ROB-002', 'ROB-003'],
                    'allocation_method': 'hungarian_algorithm',
                    'estimated_completion_hours': 4.5,
                    'total_area_ha': 12.3,
                    'assignments': [
                        {
                            'robot_id': 'ROB-001',
                            'zone_id': 'ZONE-A',
                            'task_type': 'harvest',
                            'priority': 'HIGH',
                            'estimated_duration_min': 85
                        },
                        {
                            'robot_id': 'ROB-002',
                            'zone_id': 'ZONE-B',
                            'task_type': 'harvest',
                            'priority': 'MEDIUM',
                            'estimated_duration_min': 92
                        },
                        {
                            'robot_id': 'ROB-003',
                            'zone_id': 'ZONE-C',
                            'task_type': 'transport',
                            'priority': 'MEDIUM',
                            'estimated_duration_min': 45
                        }
                    ]
                }
            }
        
        else:
            return {
                'success': True,
                'action': 'executed',
                'status': 'completed',
                'affected_resources': random.randint(1, 5)
            }
    
    def _mock_monitor(self, tool_name: str, context: Dict) -> Dict:
        """Mock monitoring tool execution"""
        if 'telemetry' in tool_name.lower():
            return {
                'success': True,
                'monitor': 'robot_fleet_telemetry',
                'data': {
                    'timestamp': datetime.now().isoformat(),
                    'robots': [
                        {
                            'robot_id': 'ROB-001',
                            'status': 'WORKING',
                            'battery_soc': 78.5,
                            'current_task': 'HARVEST_ZONE_A',
                            'progress_percent': 45.2,
                            'location': {'lat': -22.7145, 'lon': -47.6505}
                        },
                        {
                            'robot_id': 'ROB-002',
                            'status': 'WORKING',
                            'battery_soc': 82.1,
                            'current_task': 'HARVEST_ZONE_B',
                            'progress_percent': 38.7,
                            'location': {'lat': -22.7152, 'lon': -47.6512}
                        },
                        {
                            'robot_id': 'ROB-003',
                            'status': 'IDLE',
                            'battery_soc': 95.3,
                            'current_task': None,
                            'progress_percent': 0,
                            'location': {'lat': -22.7140, 'lon': -47.6500}
                        }
                    ],
                    'fleet_summary': {
                        'total_robots': 3,
                        'working': 2,
                        'idle': 1,
                        'charging': 0,
                        'avg_battery': 85.3
                    }
                }
            }
        
        else:
            return {
                'success': True,
                'monitor': 'system_health',
                'status': 'healthy',
                'metrics': {
                    'cpu_usage': random.uniform(20, 60),
                    'memory_usage': random.uniform(30, 70),
                    'uptime_hours': random.uniform(10, 100)
                }
            }
    
    def _mock_external_api(self, tool_name: str, context: Dict) -> Dict:
        """Mock external API tool execution"""
        if 'weather' in tool_name.lower():
            return {
                'success': True,
                'source': 'Weather API',
                'data': {
                    'location': {
                        'lat': context.get('lat', -22.71),
                        'lon': context.get('lon', -47.65)
                    },
                    'current': {
                        'temperature_c': 24.5,
                        'humidity_percent': 68,
                        'wind_speed_kmh': 12.3,
                        'conditions': 'partly_cloudy'
                    },
                    'forecast_48h': [
                        {
                            'datetime': '2026-02-21T12:00:00Z',
                            'temperature_c': 26.8,
                            'precipitation_mm': 0,
                            'wind_speed_kmh': 15.2,
                            'conditions': 'sunny'
                        },
                        {
                            'datetime': '2026-02-22T12:00:00Z',
                            'temperature_c': 25.3,
                            'precipitation_mm': 2.5,
                            'wind_speed_kmh': 18.7,
                            'conditions': 'light_rain'
                        }
                    ],
                    'harvest_suitability': {
                        'next_24h': 'EXCELLENT',
                        'next_48h': 'GOOD',
                        'confidence': 0.82
                    }
                }
            }
        
        else:
            return {
                'success': True,
                'source': 'External API',
                'data': {
                    'response_code': 200,
                    'data_available': True
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics for all tools"""
        return {
            'total_tools': len(self.tools),
            'total_executions': sum(s['executions'] for s in self.execution_stats.values()),
            'tools': self.execution_stats
        }
    
    def print_stats(self):
        """Print formatted statistics"""
        print(f"\n{'='*80}")
        print("📊 TOOL REGISTRY STATISTICS")
        print(f"{'='*80}")
        
        stats = self.get_stats()
        print(f"Total tools: {stats['total_tools']}")
        print(f"Total executions: {stats['total_executions']}\n")
        
        for tool_name, tool_stats in stats['tools'].items():
            if tool_stats['executions'] > 0:
                success_rate = (tool_stats['successes'] / tool_stats['executions']) * 100
                print(f"🔧 {tool_name}:")
                print(f"   Executions: {tool_stats['executions']}")
                print(f"   Success rate: {success_rate:.1f}%")
                print(f"   Avg time: {tool_stats['avg_time_ms']:.0f}ms")


def test_tool_registry():
    """Test the tool registry"""
    print("\n🧪 TESTING TOOL REGISTRY\n")
    
    # Sample tools config
    tools_config = [
        {
            'name': 'precision_data',
            'type': 'data_source',
            'description': 'Fetch precision agriculture data'
        },
        {
            'name': 'ai_vision',
            'type': 'data_source',
            'description': 'AI vision maturity analysis'
        },
        {
            'name': 'swarm_coordinator',
            'type': 'action',
            'description': 'Coordinate robot swarm tasks'
        },
        {
            'name': 'telemetry',
            'type': 'monitor',
            'description': 'Monitor robot telemetry'
        },
        {
            'name': 'weather_forecast',
            'type': 'external_api',
            'description': 'Get weather forecast'
        }
    ]
    
    # Initialize registry
    registry = ToolRegistry(tools_config)
    
    # Test tool execution
    print("\n📝 Testing tool execution:\n")
    
    tools_to_test = ['precision_data', 'ai_vision', 'swarm_coordinator', 'telemetry', 'weather_forecast']
    
    for tool_name in tools_to_test:
        result = registry.execute_tool(tool_name, {'field_id': 'FIELD-001'})
        print(f"✓ {tool_name}: {'SUCCESS' if result.get('success') else 'FAILED'} ({result.get('execution_time_ms', 0):.0f}ms)")
    
    # Print stats
    registry.print_stats()
    
    return registry


if __name__ == '__main__':
    registry = test_tool_registry()
