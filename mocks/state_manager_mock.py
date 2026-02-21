"""
Autonomous Agent Framework - State Manager Mock
Manages agent state, memory (short-term and long-term), and context
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque


class StateManager:
    """
    Manages agent state and memory:
    - Current state (status, task, metrics)
    - Short-term memory (recent observations, < 1 hour TTL)
    - Long-term memory (persistent knowledge, days/weeks retention)
    - Working memory (current execution context)
    """
    
    def __init__(self, agent_id: str, memory_config: Dict[str, Any]):
        self.agent_id = agent_id
        self.memory_config = memory_config
        
        # Current agent state
        self.state = {
            'agent_id': agent_id,
            'status': 'ready',  # ready, executing, paused, error, completed
            'current_task': None,
            'decisions_made': 0,
            'success_rate': 0.0,
            'uptime_hours': 0.0,
            'last_decision_at': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Short-term memory (working memory for current task)
        short_term_config = memory_config.get('short_term', {})
        self.short_term_enabled = short_term_config.get('enabled', True)
        self.short_term_capacity = short_term_config.get('max_messages', 10)
        self.short_term_ttl = short_term_config.get('ttl_seconds', 3600)
        self.short_term_memory = deque(maxlen=self.short_term_capacity)
        
        # Long-term memory (persistent knowledge)
        long_term_config = memory_config.get('long_term', {})
        self.long_term_enabled = long_term_config.get('enabled', True)
        self.long_term_retention_days = long_term_config.get('retention_days', 30)
        self.long_term_memory = []
        
        # Embeddings config (for similarity search in production)
        embeddings_config = memory_config.get('embeddings', {})
        self.embeddings_enabled = embeddings_config.get('enabled', False)
        self.similarity_threshold = embeddings_config.get('similarity_threshold', 0.8)
        
        # Working memory (current execution context)
        self.working_memory = {
            'execution_history': [],
            'data_cache': {},
            'partial_results': {},
            'insights': []
        }
        
        print(f"💾 StateManager initialized for {agent_id}")
        print(f"   Short-term memory: {'enabled' if self.short_term_enabled else 'disabled'} (capacity: {self.short_term_capacity})")
        print(f"   Long-term memory: {'enabled' if self.long_term_enabled else 'disabled'} (retention: {self.long_term_retention_days} days)")
    
    # ===== STATE MANAGEMENT =====
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self.state.copy()
    
    def update_state(self, key: str, value: Any):
        """Update a specific state field"""
        if key in self.state:
            self.state[key] = value
            self.state['updated_at'] = datetime.now().isoformat()
            
            # Special handling for certain state changes
            if key == 'status':
                print(f"📌 State updated: status = {value}")
            elif key == 'current_task':
                print(f"📌 State updated: task = {value if value else 'None'}")
    
    def set_state(self, new_state: Dict[str, Any]):
        """Replace entire state (preserves agent_id and timestamps)"""
        agent_id = self.state['agent_id']
        created_at = self.state['created_at']
        
        self.state = {
            **new_state,
            'agent_id': agent_id,
            'created_at': created_at,
            'updated_at': datetime.now().isoformat()
        }
    
    # ===== SHORT-TERM MEMORY =====
    
    def add_to_short_term(self, item: Dict[str, Any]):
        """
        Add item to short-term memory
        Automatically enforces capacity limit (FIFO eviction)
        """
        if not self.short_term_enabled:
            return
        
        memory_item = {
            **item,
            'timestamp': datetime.now().isoformat(),
            'ttl_expires_at': (datetime.now() + timedelta(seconds=self.short_term_ttl)).isoformat()
        }
        
        self.short_term_memory.append(memory_item)
    
    def get_short_term_memory(self, max_items: Optional[int] = None) -> List[Dict]:
        """
        Get recent short-term memory items
        Automatically filters out expired items
        """
        if not self.short_term_enabled:
            return []
        
        now = datetime.now()
        valid_items = []
        
        for item in self.short_term_memory:
            expires_at = datetime.fromisoformat(item['ttl_expires_at'])
            if expires_at > now:
                valid_items.append(item)
        
        if max_items:
            valid_items = valid_items[-max_items:]
        
        return valid_items
    
    def clear_short_term(self):
        """Clear all short-term memory"""
        self.short_term_memory.clear()
        print("🧹 Short-term memory cleared")
    
    # ===== LONG-TERM MEMORY =====
    
    def add_to_long_term(self, item: Dict[str, Any], category: str = 'general'):
        """
        Add item to long-term memory with category
        In production: Would store in vector database for similarity search
        """
        if not self.long_term_enabled:
            return
        
        memory_item = {
            **item,
            'category': category,
            'stored_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=self.long_term_retention_days)).isoformat(),
            'access_count': 0,
            'last_accessed': None
        }
        
        self.long_term_memory.append(memory_item)
        print(f"💽 Stored to long-term memory: {category}")
    
    def query_long_term(self, category: Optional[str] = None, keywords: Optional[List [str]] = None) -> List[Dict]:
        """
        Query long-term memory by category or keywords
        In production: Would use vector similarity search
        """
        if not self.long_term_enabled:
            return []
        
        now = datetime.now()
        results = []
        
        for item in self.long_term_memory:
            # Filter expired items
            expires_at = datetime.fromisoformat(item['expires_at'])
            if expires_at <= now:
                continue
            
            # Filter by category
            if category and item.get('category') != category:
                continue
            
            # Filter by keywords (simple mock - production would use embeddings)
            if keywords:
                item_text = json.dumps(item).lower()
                if not any(keyword.lower() in item_text for keyword in keywords):
                    continue
            
            # Update access tracking
            item['access_count'] += 1
            item['last_accessed'] = datetime.now().isoformat()
            
            results.append(item)
        
        return results
    
    def clear_long_term(self, category: Optional[str] = None):
        """Clear long-term memory, optionally by category"""
        if category:
            self.long_term_memory = [item for item in self.long_term_memory if item.get('category') != category]
            print(f"🧹 Long-term memory cleared: category={category}")
        else:
            self.long_term_memory.clear()
            print("🧹 All long-term memory cleared")
    
    # ===== WORKING MEMORY =====
    
    def add_to_memory(self, key: str, value: Any):
        """Add or update item in working memory"""
        if key not in self.working_memory:
            self.working_memory[key] = value
        elif isinstance(self.working_memory[key], list):
            self.working_memory[key].append(value)
        else:
            self.working_memory[key] = value
    
    def get_from_memory(self, key: str, default: Any = None) -> Any:
        """Get item from working memory"""
        return self.working_memory.get(key, default)
    
    def clear_working_memory(self):
        """Clear working memory (fresh start for new task)"""
        self.working_memory = {
            'execution_history': [],
            'data_cache': {},
            'partial_results': {},
            'insights': []
        }
        print("🧹 Working memory cleared")
    
    # ===== PERSISTENCE =====
    
    def save_to_file(self, filepath: str):
        """Save complete state and memory to JSON file"""
        snapshot = {
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'state': self.state,
            'short_term_memory': list(self.short_term_memory),
            'long_term_memory': self.long_term_memory,
            'working_memory': self.working_memory,
            'config': self.memory_config
        }
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        print(f"💾 State saved to {filepath}")
    
    def load_from_file(self, filepath: str):
        """Load state and memory from JSON file"""
        with open(filepath, 'r') as f:
            snapshot = json.load(f)
        
        self.state = snapshot.get('state', self.state)
        self.short_term_memory = deque(snapshot.get('short_term_memory', []), maxlen=self.short_term_capacity)
        self.long_term_memory = snapshot.get('long_term_memory', [])
        self.working_memory = snapshot.get('working_memory', self.working_memory)
        
        print(f"💾 State loaded from {filepath}")
    
    # ===== STATISTICS =====
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            'short_term': {
                'enabled': self.short_term_enabled,
                'capacity': self.short_term_capacity,
                'used': len(self.short_term_memory),
                'available': self.short_term_capacity - len(self.short_term_memory)
            },
            'long_term': {
                'enabled': self.long_term_enabled,
                'total_items': len(self.long_term_memory),
                'retention_days': self.long_term_retention_days
            },
            'working_memory': {
                'execution_history_items': len(self.working_memory.get('execution_history', [])),
                'cached_data_keys': len(self.working_memory.get('data_cache', {})),
                'insights_count': len(self.working_memory.get('insights', []))
            }
        }
    
    def print_stats(self):
        """Print formatted memory statistics"""
        stats = self.get_memory_stats()
        
        print(f"\n{'='*80}")
        print("📊 MEMORY STATISTICS")
        print(f"{'='*80}")
        
        # Short-term memory
        st = stats['short_term']
        print(f"Short-term memory: {st['used']}/{st['capacity']} used ({st['available']} available)")
        
        # Long-term memory
        lt = stats['long_term']
        print(f"Long-term memory: {lt['total_items']} items (retention: {lt['retention_days']} days)")
        
        # Working memory
        wm = stats['working_memory']
        print(f"Working memory:")
        print(f"   Execution history: {wm['execution_history_items']} items")
        print(f"   Cached data: {wm['cached_data_keys']} keys")
        print(f"   Insights: {wm['insights_count']} items")
        
        print(f"{'='*80}\n")


def test_state_manager():
    """Test the state manager"""
    print("\n🧪 TESTING STATE MANAGER\n")
    
    # Config
    memory_config = {
        'short_term': {
            'enabled': True,
            'max_messages': 10,
            'ttl_seconds': 3600
        },
        'long_term': {
            'enabled': True,
            'retention_days': 30
        }
    }
    
    # Initialize
    manager = StateManager('AGENT-TEST-001', memory_config)
    
    # Test state updates
    print("\n📝 Testing state updates:")
    manager.update_state('status', 'executing')
    manager.update_state('current_task', 'Test harvest optimization')
    
    # Test short-term memory
    print("\n📝 Testing short-term memory:")
    for i in range(12):  # Exceed capacity to test eviction
        manager.add_to_short_term({
            'type': 'observation',
            'content': f'Observation {i+1}',
            'confidence': 0.8 + (i * 0.01)
        })
    
    recent_memory = manager.get_short_term_memory(max_items=5)
    print(f"   Recent memories: {len(recent_memory)} (requested last 5)")
    
    # Test long-term memory
    print("\n📝 Testing long-term memory:")
    manager.add_to_long_term({
        'learning': 'Hungarian algorithm optimal for batch task allocation',
        'success_rate': 0.95
    }, category='algorithms')
    
    manager.add_to_long_term({
        'learning': 'Weather forecast critical for harvest scheduling',
        'importance': 'high'
    }, category='planning')
    
    results = manager.query_long_term(keywords=['algorithm', 'allocation'])
    print(f"   Query results: {len(results)} items found")
    
    # Test working memory
    print("\n📝 Testing working memory:")
    manager.add_to_memory('execution_history', {'step': 1, 'action': 'gather_data'})
    manager.add_to_memory('data_cache', {'field_001': 'data_value'})
    manager.add_to_memory('insights', 'Crop maturity optimal in Zone A')
    
    # Print statistics
    manager.print_stats()
    
    # Test persistence
    print("📝 Testing persistence:")
    manager.save_to_file('state_snapshot_test.json')
    
    return manager


if __name__ == '__main__':
    manager = test_state_manager()
