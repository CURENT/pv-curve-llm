// ─── Parameter types (mirrors agent/schemas/inputs.py) ─────────────────────

export type GridSystem =
  | "ieee14" | "ieee24" | "ieee30" | "ieee39"
  | "ieee57" | "ieee118" | "ieee300";

export interface Parameters {
  grid: GridSystem;
  bus_id: number;
  step_size: number;
  max_scale: number;
  power_factor: number;
  voltage_limit: number;
  capacitive: boolean;
  continuation: boolean;
  contingency_lines: [number, number][] | null;
  gen_voltage_setpoints: Record<number, number> | null;
}

export type ParametersUpdate = Partial<Omit<Parameters, "contingency_lines" | "gen_voltage_setpoints">>;

// ─── Chat / Message types ────────────────────────────────────────────────────

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id?: number;
  role: MessageRole;
  content: string;
  timestamp?: string;
  // client-only streaming fields
  streaming?: boolean;
  node?: string;
}

export interface ConversationSummary {
  id: string;
  session_id: string;
  title: string | null;
  created_at: string | null;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

// ─── PV Curve result ─────────────────────────────────────────────────────────

export interface PVCurveResult {
  load_margin_mw?: number;
  nose_point_voltage?: number;
  convergence_steps?: number;
  grid?: string;
  bus_id?: number;
  power_factor?: number;
  // Raw curve data for Plotly
  voltage_upper?: number[];
  voltage_lower?: number[];
  load_upper?: number[];
  load_lower?: number[];
  nose_load?: number;
  nose_voltage?: number;
  voltage_limit?: number;
  [key: string]: unknown;
}

// ─── WebSocket message types ─────────────────────────────────────────────────

export type WSMessageType =
  | "session"
  | "conversation_created"
  | "node_update"
  | "result"
  | "complete"
  | "error"
  | "pong";

export interface WSOutgoing {
  type: "message" | "ping";
  content?: string;
  session_id?: string;
  conversation_id?: string;
}

export interface WSIncoming {
  type: WSMessageType;
  // session
  session_id?: string;
  // conversation_created
  conversation_id?: string;
  title?: string;
  // node_update / result
  node?: string;
  content?: string;
  results?: PVCurveResult;
  plot_path?: string;
}

// ─── LLM Config ─────────────────────────────────────────────────────────────

export type LLMProvider = "openai" | "ollama";

export interface LLMConfigRequest {
  session_id: string;
  provider: LLMProvider;
  api_key?: string;
  ollama_url?: string;
  ollama_model?: string;
}

export interface LLMConfigResponse {
  session_id: string;
  provider: LLMProvider;
  api_key_set: boolean;
  api_key_masked?: string | null;
  ollama_url?: string | null;
  ollama_model?: string | null;
}

export interface LLMTestResponse {
  success: boolean;
  response?: string | null;
  error?: string | null;
}

// ─── App state ───────────────────────────────────────────────────────────────

export type ConnectionStatus = "connected" | "disconnected" | "connecting";
