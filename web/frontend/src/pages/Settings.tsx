import { useState, useEffect } from "react";
import { useAppStore } from "../store/appStore";
import { saveLLMConfig, getLLMConfig, testLLMConnection } from "../services/api";
import type { LLMProvider } from "../types";

export default function SettingsPage() {
  const sessionId = useAppStore((s) => s.sessionId);
  const llmConfig = useAppStore((s) => s.llmConfig);
  const setLLMConfig = useAppStore((s) => s.setLLMConfig);
  const isDark = useAppStore((s) => s.isDark);
  const toggleDark = useAppStore((s) => s.toggleDark);

  const [provider, setProvider] = useState<LLMProvider>(llmConfig?.provider ?? "openai");
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [ollamaUrl, setOllamaUrl] = useState(llmConfig?.ollama_url ?? "http://localhost:11434");
  const [ollamaModel, setOllamaModel] = useState(llmConfig?.ollama_model ?? "llama3");

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  // Load current config from backend
  useEffect(() => {
    if (!sessionId) return;
    getLLMConfig(sessionId).then((c) => {
      setLLMConfig(c);
      setProvider(c.provider);
      setOllamaUrl(c.ollama_url ?? "http://localhost:11434");
      setOllamaModel(c.ollama_model ?? "llama3");
    }).catch(() => {});
  }, [sessionId]);

  async function handleSave() {
    if (!sessionId) return;
    setSaving(true);
    setSaveError(null);
    try {
      const resp = await saveLLMConfig({
        session_id: sessionId,
        provider,
        api_key: provider === "openai" ? apiKey || undefined : undefined,
        ollama_url: provider === "ollama" ? ollamaUrl : undefined,
        ollama_model: provider === "ollama" ? ollamaModel : undefined,
      });
      setLLMConfig(resp);
      setApiKey(""); // clear input after save
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  async function handleTest() {
    if (!sessionId) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testLLMConnection({
        session_id: sessionId,
        provider,
        api_key: provider === "openai" ? apiKey || undefined : undefined,
        ollama_url: provider === "ollama" ? ollamaUrl : undefined,
        ollama_model: provider === "ollama" ? ollamaModel : undefined,
      });
      setTestResult({
        success: res.success,
        message: res.success
          ? (res.response ?? "Connection successful!")
          : (res.error ?? "Connection failed"),
      });
    } catch {
      setTestResult({ success: false, message: "Request failed" });
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-6 max-w-2xl mx-auto w-full space-y-8">
      <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>

      {/* ── LLM Configuration ──────────────────────────────────────────── */}
      <section className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-5 space-y-5">
        <h2 className="font-semibold text-gray-800 dark:text-gray-200">LLM Provider</h2>

        {/* Provider selector */}
        <div className="flex gap-4">
          {(["openai", "ollama"] as LLMProvider[]).map((p) => (
            <label key={p} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="provider"
                checked={provider === p}
                onChange={() => { setProvider(p); setTestResult(null); }}
                className="accent-indigo-600"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                {p === "openai" ? "OpenAI API Key" : "Local Ollama"}
              </span>
            </label>
          ))}
        </div>

        {/* OpenAI fields */}
        {provider === "openai" && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                API Key
                {llmConfig?.api_key_set && (
                  <span className="ml-2 text-green-600 dark:text-green-400">
                    ✓ saved ({llmConfig.api_key_masked})
                  </span>
                )}
              </label>
              <div className="relative">
                <input
                  type={showKey ? "text" : "password"}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={llmConfig?.api_key_set ? "Enter new key to replace" : "sk-…"}
                  autoComplete="off"
                  className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-gray-400 dark:placeholder-gray-500"
                />
                <button
                  onClick={() => setShowKey((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xs"
                  type="button"
                >
                  {showKey ? "Hide" : "Show"}
                </button>
              </div>
            </div>
            <p className="text-[11px] text-gray-400 dark:text-gray-500 flex items-center gap-1">
              🔒 Your key is encrypted before storage and never sent to third parties.
            </p>
          </div>
        )}

        {/* Ollama fields */}
        {provider === "ollama" && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">Ollama URL</label>
              <input
                type="url"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">Model</label>
              <input
                type="text"
                value={ollamaModel}
                onChange={(e) => setOllamaModel(e.target.value)}
                placeholder="llama3"
                className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        )}

        {/* Test connection result */}
        {testResult && (
          <div className={`text-sm rounded-xl px-4 py-3 ${
            testResult.success
              ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800"
              : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800"
          }`}>
            {testResult.success ? "✓ " : "✗ "}{testResult.message}
          </div>
        )}

        {saveError && (
          <p className="text-sm text-red-500">{saveError}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium disabled:opacity-40 transition-colors"
          >
            {saving ? "Saving…" : saved ? "✓ Saved" : "Save"}
          </button>
          <button
            onClick={handleTest}
            disabled={testing}
            className="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-40 transition-colors"
          >
            {testing ? "Testing…" : "Test Connection"}
          </button>
        </div>
      </section>

      {/* ── Appearance ──────────────────────────────────────────────────── */}
      <section className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
        <h2 className="font-semibold text-gray-800 dark:text-gray-200">Appearance</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark mode</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">Toggle light / dark theme</p>
          </div>
          <button
            type="button"
            onClick={toggleDark}
            className={`relative inline-flex shrink-0 w-12 h-6 rounded-full transition-colors ${
              isDark ? "bg-indigo-600" : "bg-gray-300 dark:bg-gray-600"
            }`}
            aria-label="Toggle dark mode"
          >
            <span
              className={`pointer-events-none absolute top-1 left-1 size-4 rounded-full bg-white shadow transition-transform duration-200 ease-out ${
                isDark ? "translate-x-6" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </section>

      {/* ── About ────────────────────────────────────────────────────────── */}
      <section className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-5 space-y-2">
        <h2 className="font-semibold text-gray-800 dark:text-gray-200">About</h2>
        <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <p><span className="font-medium">PV Curve Agent</span> — Version 1.0.0</p>
          <p>Powered by LangGraph, pandapower, and FastAPI.</p>
          <p>
            Users provide their own LLM credentials. No data is sent to any server
            other than the one you configure.
          </p>
        </div>
      </section>
    </div>
  );
}
