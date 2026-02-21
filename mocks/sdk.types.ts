/**
 * Autonomous Agent Framework - TypeScript SDK
 * Type definitions for building autonomous multi-tool agents
 */

// ============================================================================
// Core Types
// ============================================================================

export interface AgentConfig {
  name: string;
  description?: string;
  capabilities: Capability[];
  decision_model: DecisionModel;
  tools?: Tool[];
  memory?: MemoryConfig;
  planning?: PlanningConfig;
  execution?: ExecutionConfig;
  monitoring?: MonitoringConfig;
  goals?: Goal[];
}

export type Capability = 
  | 'data_analysis'
  | 'decision_making'
  | 'task_planning'
  | 'resource_optimization'
  | 'pattern_recognition'
  | 'anomaly_detection'
  | 'forecasting';

export type AgentStatus = 'active' | 'paused' | 'stopped' | 'error';

// ============================================================================
// Decision Model
// ============================================================================

export interface DecisionModel {
  type: 'llm' | 'rule_based' | 'ml_model' | 'hybrid';
  provider?: LLMProvider;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  system_prompt?: string;
  few_shot_examples?: FewShotExample[];
  output_schema?: Record<string, any>;
}

export type LLMProvider = 'openai' | 'anthropic' | 'azure' | 'local';

export interface FewShotExample {
  input: string;
  output: string;
}

// ============================================================================
// Tools
// ============================================================================

export interface Tool {
  name: string;
  type: ToolType;
  endpoint: string;
  method: HTTPMethod;
  parameters: Record<string, ParameterDefinition>;
  description: string;
  authentication?: Authentication;
  retry_policy?: RetryPolicy;
  timeout_ms?: number;
}

export type ToolType = 
  | 'data_source'
  | 'action'
  | 'monitor'
  | 'external_api'
  | 'database'
  | 'webhook';

export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface ParameterDefinition {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'float' | 'integer';
  required: boolean;
  default?: any;
  description?: string;
  enum?: any[];
  min?: number;
  max?: number;
}

export interface Authentication {
  type: 'bearer' | 'api_key' | 'basic' | 'oauth' | 'query';
  token_env_var?: string;
  header_name?: string;
  param?: string;
  value_env_var?: string;
}

export interface RetryPolicy {
  max_attempts: number;
  backoff_seconds: number;
  exponential: boolean;
  retry_on_status?: number[];
}

// ============================================================================
// Memory
// ============================================================================

export interface MemoryConfig {
  short_term: ShortTermMemoryConfig;
  long_term: LongTermMemoryConfig;
  embeddings?: EmbeddingsConfig;
}

export interface ShortTermMemoryConfig {
  enabled: boolean;
  max_messages: number;
  ttl_seconds: number;
  storage?: 'memory' | 'redis';
}

export interface LongTermMemoryConfig {
  enabled: boolean;
  storage: 'redis' | 'postgres' | 'mongodb';
  key_prefix?: string;
  retention_days: number;
}

export interface EmbeddingsConfig {
  enabled: boolean;
  model: string;
  dimensions: number;
  similarity_threshold: number;
  vector_db?: 'pinecone' | 'qdrant' | 'weaviate' | 'milvus';
}

export interface MemoryEntry {
  memory_id: string;
  type: 'fact' | 'observation' | 'decision' | 'outcome';
  content: string;
  metadata: Record<string, any>;
  embedding?: number[];
  stored_at: string;
  ttl_days?: number;
}

export interface MemorySearchResult {
  memory_id: string;
  content: string;
  similarity: number;
  metadata: Record<string, any>;
  stored_at: string;
}

// ============================================================================
// Planning & Execution
// ============================================================================

export interface PlanningConfig {
  strategy: 'reactive' | 'deliberative' | 'reactive_deliberative' | 'hierarchical';
  horizon_hours: number;
  replanning_interval_minutes: number;
  constraints?: Record<string, any>;
}

export interface ExecutionConfig {
  mode: 'autonomous' | 'semi_autonomous' | 'manual';
  approval_required: boolean;
  max_concurrent_tasks: number;
  timeout_seconds: number;
  retry_policy?: RetryPolicy;
}

export interface ExecutionTrigger {
  type: 'scheduled' | 'manual' | 'event' | 'conditional';
  reason: string;
  context: Record<string, any>;
}

export interface ExecutionResult {
  execution_id: string;
  agent_id: string;
  status: ExecutionStatus;
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  steps: ExecutionStep[];
  decision_made?: Decision;
  outcome?: ExecutionOutcome;
  metrics: ExecutionMetrics;
  logs: LogEntry[];
}

export type ExecutionStatus = 
  | 'started'
  | 'gathering_data'
  | 'analyzing'
  | 'executing'
  | 'completed_success'
  | 'completed_partial'
  | 'failed'
  | 'cancelled';

export interface ExecutionStep {
  step: number;
  timestamp: string;
  action: string;
  description: string;
  tool_calls?: ToolCall[];
  llm_call?: LLMCall;
  memory_operations?: MemoryOperation[];
  status: 'success' | 'failed' | 'skipped';
  duration_ms: number;
  error?: string;
}

export interface ToolCall {
  tool: string;
  params: Record<string, any>;
  response: {
    status: number;
    data: any;
  };
  latency_ms: number;
}

export interface LLMCall {
  model: string;
  prompt: {
    system: string;
    user: string;
  };
  response: any;
  tokens_used: number;
  latency_ms: number;
}

export interface MemoryOperation {
  type: 'store' | 'retrieve' | 'search' | 'embed';
  key?: string;
  data?: any;
  query?: string;
  results?: any[];
}

export interface Decision {
  decision: string;
  reasoning: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence?: number;
  alternatives?: string[];
  risks?: string[];
  expected_outcome?: Record<string, any>;
  [key: string]: any; // LLM can return additional fields
}

export interface ExecutionOutcome {
  success: boolean;
  actions_executed: number;
  errors?: string[];
  estimated_impact?: Record<string, any>;
  [key: string]: any;
}

export interface ExecutionMetrics {
  total_tool_calls: number;
  total_latency_ms: number;
  llm_latency_ms: number;
  llm_tokens_used: number;
  memory_operations: number;
}

// ============================================================================
// Goals & Metrics
// ============================================================================

export interface Goal {
  name: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  metrics: string[];
  target: Record<string, any>;
  description?: string;
  deadline?: string;
}

export interface GoalProgress {
  goal_id: string;
  name: string;
  status: 'active' | 'achieved' | 'failed' | 'paused';
  progress: number; // 0.0 to 1.0
  current_value: any;
  target_value: any;
  last_updated: string;
}

export interface AgentMetrics {
  period: {
    from: string;
    to: string;
  };
  metrics: {
    executions_count: number;
    success_rate: number;
    avg_decision_latency_ms: number;
    total_decisions_made: number;
    goals_achieved: number;
    estimated_roi_usd?: number;
    [key: string]: any;
  };
  time_series?: TimeSeriesData[];
}

export interface TimeSeriesData {
  timestamp: string;
  [key: string]: any;
}

// ============================================================================
// Scheduling
// ============================================================================

export interface Schedule {
  name: string;
  cron: string;
  enabled: boolean;
  context?: Record<string, any>;
  timezone?: string;
}

export interface ScheduleInfo {
  schedule_id: string;
  name: string;
  cron: string;
  enabled: boolean;
  next_execution_at: string;
  last_execution_at?: string;
  executions_count: number;
}

// ============================================================================
// Monitoring
// ============================================================================

export interface MonitoringConfig {
  logging: LoggingConfig;
  metrics: MetricsConfig;
  alerts: AlertsConfig;
}

export interface LoggingConfig {
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  destination: 'file' | 'console' | 'remote';
  path?: string;
  rotation?: 'daily' | 'weekly' | 'size';
  max_size_mb?: number;
}

export interface MetricsConfig {
  enabled: boolean;
  interval_seconds: number;
  push_endpoint?: string;
  retention_days?: number;
}

export interface AlertsConfig {
  enabled: boolean;
  channels: AlertChannel[];
  severity_threshold: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  rate_limit_per_hour?: number;
}

export type AlertChannel = 'email' | 'slack' | 'webhook' | 'sms';

export interface LogEntry {
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' | 'SUCCESS';
  timestamp: string;
  message: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// Webhooks
// ============================================================================

export interface WebhookConfig {
  event: WebhookEvent;
  url: string;
  headers?: Record<string, string>;
  retry_policy?: RetryPolicy;
}

export type WebhookEvent = 
  | 'execution.started'
  | 'execution.completed'
  | 'execution.failed'
  | 'decision.made'
  | 'goal.achieved'
  | 'alert.triggered'
  | 'tool.failed';

export interface WebhookPayload {
  event: WebhookEvent;
  timestamp: string;
  agent_id: string;
  data: Record<string, any>;
}

// ============================================================================
// SDK Client
// ============================================================================

export class AgentFramework {
  constructor(config: {
    apiKey: string;
    baseUrl?: string;
    timeout?: number;
  });

  // Agent Management
  createAgent(config: AgentConfig): Promise<Agent>;
  getAgent(agentId: string): Promise<Agent>;
  listAgents(): Promise<Agent[]>;
  deleteAgent(agentId: string): Promise<void>;

  // Executions
  getExecution(executionId: string): Promise<ExecutionResult>;
  listExecutions(agentId: string, params?: {
    status?: ExecutionStatus;
    limit?: number;
    offset?: number;
  }): Promise<ExecutionResult[]>;
}

export class Agent {
  readonly agent_id: string;
  readonly name: string;
  status: AgentStatus;
  readonly created_at: string;

  // Tool Management
  registerTool(tool: Tool): Promise<string>;
  listTools(): Promise<Tool[]>;
  getTool(toolId: string): Promise<Tool>;
  unregisterTool(toolId: string): Promise<void>;

  // Execution
  execute(params: {
    trigger_reason?: string;
    context?: Record<string, any>;
    async_mode?: boolean;
  }): Promise<ExecutionResult>;
  
  cancelExecution(executionId: string): Promise<void>;

  // Memory
  storeMemory(memory: Omit<MemoryEntry, 'memory_id' | 'stored_at'>): Promise<string>;
  searchMemory(params: {
    query: string;
    limit?: number;
    threshold?: number;
  }): Promise<MemorySearchResult[]>;
  deleteMemory(memoryId: string): Promise<void>;

  // Goals
  setGoal(goal: Goal): Promise<string>;
  getGoals(): Promise<GoalProgress[]>;
  getGoal(goalId: string): Promise<GoalProgress>;
  deleteGoal(goalId: string): Promise<void>;

  // Metrics
  getMetrics(params: {
    from_date: Date | string;
    to_date: Date | string;
    granularity?: 'hour' | 'day' | 'week';
  }): Promise<AgentMetrics>;

  // Scheduling
  createSchedule(schedule: Schedule): Promise<ScheduleInfo>;
  listSchedules(): Promise<ScheduleInfo[]>;
  updateSchedule(scheduleId: string, updates: Partial<Schedule>): Promise<ScheduleInfo>;
  deleteSchedule(scheduleId: string): Promise<void>;

  // Webhooks
  registerWebhook(webhook: WebhookConfig): Promise<string>;
  listWebhooks(): Promise<WebhookConfig[]>;
  deleteWebhook(webhookId: string): Promise<void>;

  // Configuration
  update(updates: Partial<AgentConfig>): Promise<void>;
  pause(): Promise<void>;
  resume(): Promise<void>;
}

// ============================================================================
// Error Types
// ============================================================================

export class AgentError extends Error {
  readonly code: string;
  readonly statusCode: number;
  readonly details?: Record<string, any>;
  
  constructor(code: string, message: string, statusCode: number, details?: Record<string, any>);
}

export class ToolError extends AgentError {
  readonly toolName: string;
  
  constructor(toolName: string, message: string, details?: Record<string, any>);
}

export class ExecutionError extends AgentError {
  readonly executionId: string;
  readonly step?: number;
  
  constructor(executionId: string, message: string, step?: number, details?: Record<string, any>);
}

// ============================================================================
// Utility Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: string;
}
