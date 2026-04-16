import { useEffect, useState } from "react";
import { useAppStore } from "../../store/appStore";
import { getParameters, updateParameters, resetParameters } from "../../services/api";
import type { Parameters, GridSystem } from "../../types";

const GRIDS: { value: GridSystem; label: string; maxBus: number }[] = [
  { value: "ieee14",  label: "IEEE 14",  maxBus: 14  },
  { value: "ieee24",  label: "IEEE 24",  maxBus: 24  },
  { value: "ieee30",  label: "IEEE 30",  maxBus: 30  },
  { value: "ieee39",  label: "IEEE 39",  maxBus: 39  },
  { value: "ieee57",  label: "IEEE 57",  maxBus: 57  },
  { value: "ieee118", label: "IEEE 118", maxBus: 118 },
  { value: "ieee300", label: "IEEE 300", maxBus: 300 },
];

type Errors = Partial<Record<keyof Parameters, string>>;

function validate(draft: Parameters): Errors {
  const errors: Errors = {};
  const grid = GRIDS.find((g) => g.value === draft.grid);
  if (grid && (draft.bus_id < 1 || draft.bus_id > grid.maxBus)) {
    errors.bus_id = `Bus must be 1–${grid.maxBus} for ${grid.label}`;
  }
  if (draft.step_size <= 0 || draft.step_size > 0.1) {
    errors.step_size = "Step size must be 0.001–0.1";
  }
  if (draft.max_scale <= 1 || draft.max_scale > 10) {
    errors.max_scale = "Max scale must be 1.0–10.0";
  }
  if (draft.power_factor <= 0 || draft.power_factor > 1) {
    errors.power_factor = "Power factor must be 0–1";
  }
  if (draft.voltage_limit <= 0 || draft.voltage_limit > 1) {
    errors.voltage_limit = "Voltage limit must be 0–1 pu";
  }
  return errors;
}

interface Props {
  className?: string;
}

export default function ParameterPanel({ className = "" }: Props) {
  const sessionId = useAppStore((s) => s.sessionId);
  const storeParams = useAppStore((s) => s.parameters);
  const setParameters = useAppStore((s) => s.setParameters);

  const [draft, setDraft] = useState<Parameters | null>(storeParams);
  const [errors, setErrors] = useState<Errors>({});
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  // Fetch parameters from backend when session is available
  useEffect(() => {
    if (!sessionId) return;
    getParameters(sessionId)
      .then((p) => { setDraft(p); setParameters(p); })
      .catch(() => {/* backend not ready yet */});
  }, [sessionId]);

  // Sync draft if store changes from outside (e.g. LLM updated params; websocket refetched GET /parameters)
  useEffect(() => {
    if (storeParams && !isDirty) setDraft(storeParams);
  }, [storeParams, isDirty]);

  function patch<K extends keyof Parameters>(key: K, value: Parameters[K]) {
    setDraft((prev) => {
      if (!prev) return prev;
      const next = { ...prev, [key]: value };
      const errs = validate(next);
      setErrors(errs);
      setIsDirty(true);
      setSaved(false);
      return next;
    });
  }

  async function apply() {
    if (!draft || !sessionId) return;
    const errs = validate(draft);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setSaving(true);
    setSaveError(null);
    try {
      const updated = await updateParameters(sessionId, draft);
      setParameters(updated);
      setDraft(updated);
      setIsDirty(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  async function reset() {
    if (!sessionId) return;
    setSaving(true);
    try {
      const defaults = await resetParameters(sessionId);
      setParameters(defaults);
      setDraft(defaults);
      setErrors({});
      setIsDirty(false);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  if (!draft) {
    return (
      <div className={`p-4 text-sm text-gray-400 dark:text-gray-500 ${className}`}>
        Loading parameters…
      </div>
    );
  }

  const hasErrors = Object.keys(errors).length > 0;

  return (
    <div className={`overflow-y-auto p-4 space-y-5 text-sm ${className}`}>
      <h3 className="font-semibold text-gray-800 dark:text-gray-200 text-base">
        Parameters
      </h3>

      {/* ── Grid System ─────────────────────────────────────────────── */}
      <Field label="Grid System">
        <select
          value={draft.grid}
          onChange={(e) => {
            const g = e.target.value as GridSystem;
            const maxBus = GRIDS.find((x) => x.value === g)?.maxBus ?? 300;
            const bus = Math.min(draft.bus_id, maxBus);
            setDraft((p) => p ? { ...p, grid: g, bus_id: bus } : p);
            setIsDirty(true);
            setSaved(false);
          }}
          className={selectCls}
        >
          {GRIDS.map((g) => (
            <option key={g.value} value={g.value}>{g.label}</option>
          ))}
        </select>
      </Field>

      {/* ── Bus ID ───────────────────────────────────────────────────── */}
      <Field label="Bus ID" error={errors.bus_id}
        hint={`1–${GRIDS.find(g => g.value === draft.grid)?.maxBus}`}>
        <input
          type="number"
          value={draft.bus_id}
          min={1}
          max={GRIDS.find(g => g.value === draft.grid)?.maxBus ?? 300}
          onChange={(e) => patch("bus_id", parseInt(e.target.value) || 1)}
          className={inputCls(!!errors.bus_id)}
        />
      </Field>

      {/* ── Power Factor ─────────────────────────────────────────────── */}
      <Field label={`Power Factor: ${draft.power_factor.toFixed(2)}`} error={errors.power_factor}
        hint="How much of load is real power (0–1)">
        <div className="flex items-center gap-3">
          <input
            type="range" min={0.01} max={1} step={0.01}
            value={draft.power_factor}
            onChange={(e) => patch("power_factor", parseFloat(e.target.value))}
            className={rangeCls}
          />
          <input
            type="number" min={0.01} max={1} step={0.01}
            value={draft.power_factor}
            onChange={(e) => patch("power_factor", parseFloat(e.target.value) || 0.01)}
            className={`w-20 ${inputCls(!!errors.power_factor)}`}
          />
        </div>
      </Field>

      {/* ── Load Type ─────────────────────────────────────────────────── */}
      <Field label="Load Type" hint="Capacitive loads improve stability margin">
        <div className="flex gap-4">
          {[{ label: "Inductive", value: false }, { label: "Capacitive", value: true }].map((opt) => {
            const selected = draft.capacitive === opt.value;
            return (
              <button
                key={String(opt.value)}
                type="button"
                onClick={() => patch("capacitive", opt.value)}
                className="flex items-center gap-2 cursor-pointer"
              >
                {/* outer ring */}
                <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors ${
                  selected
                    ? "border-indigo-500"
                    : "border-gray-400 dark:border-gray-500"
                }`}>
                  {/* inner filled dot — only shown when selected */}
                  {selected && (
                    <div className="w-2 h-2 rounded-full bg-indigo-500" />
                  )}
                </div>
                <span className={`text-sm ${selected ? "text-gray-900 dark:text-gray-100" : "text-gray-500 dark:text-gray-400"}`}>
                  {opt.label}
                </span>
              </button>
            );
          })}
        </div>
      </Field>

      {/* ── Step Size ──────────────────────────────────────────────────── */}
      <Field label="Step Size" error={errors.step_size}
        hint="Load increment per iteration (smaller = more accurate)">
        <input
          type="number" min={0.001} max={0.1} step={0.001}
          value={draft.step_size}
          onChange={(e) => patch("step_size", parseFloat(e.target.value) || 0.001)}
          className={inputCls(!!errors.step_size)}
        />
      </Field>

      {/* ── Max Scale ──────────────────────────────────────────────────── */}
      <Field label={`Max Load Multiplier: ${draft.max_scale.toFixed(1)}×`} error={errors.max_scale}
        hint="How far to scale the base load (1–10)">
        <div className="flex items-center gap-3">
          <input
            type="range" min={1.1} max={10} step={0.1}
            value={draft.max_scale}
            onChange={(e) => patch("max_scale", parseFloat(e.target.value))}
            className={rangeCls}
          />
          <input
            type="number" min={1.1} max={10} step={0.1}
            value={draft.max_scale}
            onChange={(e) => patch("max_scale", parseFloat(e.target.value) || 1.1)}
            className={`w-20 ${inputCls(!!errors.max_scale)}`}
          />
        </div>
      </Field>

      {/* ── Voltage Limit ───────────────────────────────────────────────── */}
      <Field label={`Voltage Limit: ${draft.voltage_limit.toFixed(2)} pu`} error={errors.voltage_limit}
        hint="Stop simulation when voltage drops below this threshold">
        <div className="flex items-center gap-3">
          <input
            type="range" min={0.01} max={1} step={0.01}
            value={draft.voltage_limit}
            onChange={(e) => patch("voltage_limit", parseFloat(e.target.value))}
            className={rangeCls}
          />
          <input
            type="number" min={0.01} max={1} step={0.01}
            value={draft.voltage_limit}
            onChange={(e) => patch("voltage_limit", parseFloat(e.target.value) || 0.01)}
            className={`w-20 ${inputCls(!!errors.voltage_limit)}`}
          />
        </div>
      </Field>

      {/* ── Continuation ─────────────────────────────────────────────────── */}
      <Field label="Continuation Method"
        hint="Uses predictor-corrector for better accuracy near nose point">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={draft.continuation}
            onChange={(e) => patch("continuation", e.target.checked)}
            className="w-4 h-4 accent-indigo-600"
          />
          <span>{draft.continuation ? "Enabled" : "Disabled"}</span>
        </label>
      </Field>

      {/* ── Transmission line ─────────────────────────────────────────────── */}
      <Field
        label="Transmission line(s) out"
        hint="N-1/N-k: which lines are out of service before the sweep (1-based bus ends)"
      >
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 px-3 py-2 font-mono text-xs text-gray-800 dark:text-gray-200">
          {formatTransmissionLinesOut(draft.contingency_lines)}
        </div>
      </Field>

      {/* ── Generator voltage setpoints ─────────────────────────────────────── */}
      <Field
        label="Generator voltage setpoints"
        hint="1-based generator index → voltage magnitude in pu before the sweep"
      >
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 px-3 py-2 font-mono text-xs text-gray-800 dark:text-gray-200">
          {formatGenVoltageSetpoints(draft.gen_voltage_setpoints)}
        </div>
      </Field>

      {/* ── Action buttons ──────────────────────────────────────────────── */}
      {saveError && (
        <p className="text-red-500 text-xs">{saveError}</p>
      )}

      <div className="flex gap-2 pt-1">
        <button
          onClick={apply}
          disabled={saving || hasErrors || !isDirty}
          className="flex-1 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? "Saving…" : saved ? "✓ Saved" : "Apply Changes"}
        </button>
        <button
          onClick={reset}
          disabled={saving}
          title="Reset all parameters to defaults"
          className="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm transition-colors disabled:opacity-40"
        >
          Reset
        </button>
      </div>

      {isDirty && !hasErrors && (
        <p className="text-[11px] text-amber-500 dark:text-amber-400">
          ⚠ Unsaved changes — click Apply to confirm
        </p>
      )}
    </div>
  );
}

// ─── Small helpers ─────────────────────────────────────────────────────────────

/** Same idea as CLI / agent/utils/display.py: "None" or "Bus a – Bus b", … */
function formatTransmissionLinesOut(lines: Parameters["contingency_lines"]): string {
  if (!lines || lines.length === 0) return "None";
  return lines.map(([a, b]) => `Bus ${a} – Bus ${b}`).join(", ");
}

/** Same idea as CLI: "None" or "Gen 1: 1.2 pu", … */
function formatGenVoltageSetpoints(sp: Parameters["gen_voltage_setpoints"]): string {
  if (!sp || Object.keys(sp).length === 0) return "None";
  return Object.entries(sp)
    .map(([g, pu]) => [Number(g), pu] as const)
    .sort(([a], [b]) => a - b)
    .map(([g, pu]) => `Gen ${g}: ${pu} pu`)
    .join(", ");
}

interface FieldProps {
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}

function Field({ label, hint, error, children }: FieldProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-gray-700 dark:text-gray-300 leading-none">
          {label}
        </label>
        {hint && (
          <span title={hint} className="cursor-help text-gray-400 dark:text-gray-600 text-xs select-none">ⓘ</span>
        )}
      </div>
      {children}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

const selectCls =
  "w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";

function inputCls(hasError: boolean) {
  return (
    "w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-800 " +
    (hasError
      ? "border-red-400 dark:border-red-500"
      : "border-gray-200 dark:border-gray-700")
  );
}

const rangeCls =
  "flex-1 accent-indigo-600 cursor-pointer";
