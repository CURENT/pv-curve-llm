/**
 * Axios-based REST client for the FastAPI backend.
 *
 * All requests go to /api/v1/... which Vite proxies to http://localhost:8000.
 */
import axios from "axios";
import type {
  Parameters,
  LLMConfigRequest,
  LLMConfigResponse,
  LLMTestResponse,
  ConversationSummary,
  ConversationDetail,
} from "../types";

const http = axios.create({
  baseURL: "/api/v1",
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// ─── Parameters ──────────────────────────────────────────────────────────────

export async function getParameters(sessionId: string): Promise<Parameters> {
  const { data } = await http.get("/parameters", { params: { session_id: sessionId } });
  return data.parameters as Parameters;
}

export async function updateParameters(
  sessionId: string,
  updates: Partial<Parameters>
): Promise<Parameters> {
  const { data } = await http.post("/parameters", { session_id: sessionId, ...updates });
  return data.parameters as Parameters;
}

export async function resetParameters(sessionId: string): Promise<Parameters> {
  const { data } = await http.post("/parameters/reset", null, {
    params: { session_id: sessionId },
  });
  return data.parameters as Parameters;
}

// ─── LLM Settings ─────────────────────────────────────────────────────────────

export async function getLLMConfig(sessionId: string): Promise<LLMConfigResponse> {
  const { data } = await http.get("/settings/llm", { params: { session_id: sessionId } });
  return data as LLMConfigResponse;
}

export async function saveLLMConfig(
  body: LLMConfigRequest
): Promise<LLMConfigResponse> {
  const { data } = await http.post("/settings/llm", body);
  return data as LLMConfigResponse;
}

export async function testLLMConnection(
  body: LLMConfigRequest
): Promise<LLMTestResponse> {
  const { data } = await http.post("/settings/llm/test", body);
  return data as LLMTestResponse;
}

// ─── Conversation history ─────────────────────────────────────────────────────

export async function listConversations(
  sessionId: string
): Promise<ConversationSummary[]> {
  const { data } = await http.get("/conversations", { params: { session_id: sessionId } });
  return data as ConversationSummary[];
}

export async function getConversation(
  conversationId: string
): Promise<ConversationDetail> {
  const { data } = await http.get(`/conversations/${conversationId}`);
  return data as ConversationDetail;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await http.delete(`/conversations/${conversationId}`);
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function healthCheck(): Promise<boolean> {
  try {
    await axios.get("/health", { timeout: 3_000 });
    return true;
  } catch {
    return false;
  }
}
