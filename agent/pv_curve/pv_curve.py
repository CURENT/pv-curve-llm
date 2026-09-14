"""P–V curve generation using ANDES continuation power flow (CPF)."""

import os
from datetime import datetime

import andes
import matplotlib
import numpy as np

# FastAPI/web runs this code in a thread pool; macOS GUI backend (macosx) only works on the main thread.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE_MAP = {
    "ieee14": "ieee14/ieee14.json",
    "ieee39": "ieee39/ieee39_full.xlsx",
    "ieee118": "matpower/case118.m",
    "ieee300": "matpower/case300.m",
}


def _get_output_path(grid: str) -> str:
    """Build the filesystem path for a saved P–V plot PNG.

    Args:
        grid: Case name key (e.g. ``ieee39``) used in the output filename.

    Returns:
        Full path under ``PV_CURVE_OUTPUT_DIR`` or ``generated``.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.getenv("PV_CURVE_OUTPUT_DIR") or "generated"
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"pv_curve_{grid}_{timestamp}.png")


def _apply_contingencies(ss, contingency_lines):
    """Take transmission lines out of service before ``ss.setup()``.

    Args:
        ss: ANDES system loaded with ``setup=False``.
        contingency_lines: List of ``(from_bus, to_bus)`` pairs using **bus indices**
            as in the case file (same convention as ANDES ``Bus.idx``).

    Raises:
        ValueError: If no line exists for a given pair.
    """
    if not contingency_lines:
        return

    for fb, tb in contingency_lines:
        found = False
        for uid in range(len(ss.Line.bus1.v)):
            b1 = int(ss.Line.bus1.v[uid])
            b2 = int(ss.Line.bus2.v[uid])
            if {b1, b2} == {int(fb), int(tb)}:
                ss.Line.u.v[uid] = 0
                found = True
        if not found:
            raise ValueError(f"No line found between bus {fb} and bus {tb} in grid.")


def _apply_gen_voltage_setpoints(ss, gen_voltage_setpoints):
    """Override PV generator voltage setpoints before ``ss.setup()``.

    Args:
        ss: ANDES system loaded with ``setup=False``.
        gen_voltage_setpoints: Mapping **PV device index** -> voltage magnitude in pu
            (keys must match ``ss.PV.idx``).

    Raises:
        ValueError: If a key is not a valid PV index in this case.
    """
    if not gen_voltage_setpoints:
        return

    valid_indices = set(int(idx) for idx in ss.PV.idx.v)
    for gen_idx, vm_pu in gen_voltage_setpoints.items():
        gen_idx = int(gen_idx)
        if gen_idx not in valid_indices:
            raise ValueError(
                f"Generator index {gen_idx} not found in grid. Valid indices: {sorted(valid_indices)}"
            )
        uid = ss.PV.idx2uid(gen_idx)
        ss.PV.v0.v[uid] = float(vm_pu)


def _build_targets(ss, max_scale, power_factor, capacitive):
    """Build per-load P and Q targets for CPF from base-case PQ ``p0``.

    Args:
        ss: ANDES system after ``setup()`` (PQ ``p0`` available).
        max_scale: Active-power multiplier applied uniformly to all PQ ``p0`` (target load level).
        power_factor: Assumed constant |PF| for loads when building ``q0`` from ``p0``.
        capacitive: If True, reactive target uses leading (capacitive) sign; else lagging.

    Returns:
        Tuple ``(p0_base, p0_target, q0_target)`` as arrays suitable for ``ss.CPF.run``.
    """
    p0_base = ss.PQ.p0.v.copy()
    p0_target = p0_base * float(max_scale)
    sign = -1 if capacitive else 1
    q0_target = sign * p0_target * np.tan(np.arccos(float(power_factor)))
    return p0_base, p0_target, q0_target


def _build_plot(P_vals, V_vals, nose_idx, target_bus_idx, save_path):
    """Save a P–V figure (MW vs pu voltage) for the monitored bus.

    Args:
        P_vals: Sequence of total active load (MW) at each CPF point.
        V_vals: Sequence of voltage magnitude (pu) at the monitored bus.
        nose_idx: Index into ``P_vals`` / ``V_vals`` of the nose (max load) point.
        target_bus_idx: Bus index (same numbering as inputs) for axis label.
        save_path: Output PNG path.
    """
    plt.figure(figsize=(8, 6))

    # If CPF traced full curve, split into upper/lower around the nose.
    if 0 < nose_idx < len(P_vals) - 1:
        plt.plot(P_vals[: nose_idx + 1], V_vals[: nose_idx + 1], marker="o", linestyle="-", color="blue", label="Upper Branch")
        plt.plot(P_vals[nose_idx:], V_vals[nose_idx:], marker="x", linestyle="-", color="red", label="Lower Branch")
    else:
        plt.plot(P_vals, V_vals, marker="o", linestyle="-", color="blue", label="PV Curve")

    nose_p = P_vals[nose_idx]
    nose_v = V_vals[nose_idx]
    plt.scatter(nose_p, nose_v, color="red", zorder=5, label="Nose Point")
    plt.annotate(
        f"P={nose_p:.1f} MW\nV={nose_v:.3f} pu",
        xy=(nose_p, nose_v),
        xytext=(nose_p * 1.005, nose_v),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=9,
    )

    plt.xlabel("Total Active Load P (MW)")
    plt.ylabel(f"Voltage at Bus {target_bus_idx} (pu)")
    plt.title("System P–V Curve (Voltage Stability Analysis)")
    plt.grid(True)
    plt.legend()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_pv_curve(
    grid="ieee39",
    target_bus_idx=5,
    step_size=0.1,
    max_scale=3.0,
    power_factor=0.95,
    voltage_limit=0.4,
    capacitive=False,
    skip_plot=False,
    contingency_lines=None,
    gen_voltage_setpoints=None,
    continuation=True,
):
    """Run ANDES CPF and return a summary dict plus optional P–V plot.

    Uses uniform PQ scaling toward ``p0 * max_scale`` with Q derived from
    ``power_factor`` and ``capacitive``, per ANDES CPF ``p0_target`` / ``q0_target``.

    Args:
        grid: Built-in case key; must exist in ``CASE_MAP``.
        target_bus_idx: Bus whose |V| is traced (same index convention as the case).
        step_size: Initial CPF continuation step; mapped to ``ss.CPF.config.step``.
        max_scale: Load growth factor toward ``p0 * max_scale`` (uniform PQ).
        power_factor: Constant power-factor magnitude in (0, 1] for Q from P.
        voltage_limit: Results are truncated after voltage first drops below this (pu).
        capacitive: If True, leading reactive convention for Q targets.
        skip_plot: If True, do not write a PNG; ``save_path`` in the result is None.
        contingency_lines: Optional list of ``(from_bus, to_bus)`` line outages before setup.
        gen_voltage_setpoints: Optional ``{pv_idx: vm_pu}`` before setup.
        continuation: If True, ``stop_at='FULL'``; else ``stop_at='NOSE'``.

    Returns:
        Dict with curve arrays, nose metadata, limits, and ``save_path``.

    Raises:
        ValueError: Unknown grid, invalid bus, no CPF points, or invalid contingencies / setpoints.
    """
    if grid not in CASE_MAP:
        raise ValueError(f"Unsupported grid '{grid}'. Choose from {list(CASE_MAP)}")

    ss = andes.load(andes.get_case(CASE_MAP[grid]), setup=False)

    bus_indices = set(int(idx) for idx in ss.Bus.idx.v)
    if int(target_bus_idx) not in bus_indices:
        raise ValueError(
            f"Bus {target_bus_idx} not found in grid '{grid}'. Valid range: {min(bus_indices)} to {max(bus_indices)}."
        )

    _apply_contingencies(ss, contingency_lines)
    _apply_gen_voltage_setpoints(ss, gen_voltage_setpoints)

    ss.setup()
    ss.PFlow.run()

    p0_base, p0_target, q0_target = _build_targets(ss, max_scale, power_factor, capacitive)

    ss.CPF.config.step = float(step_size)
    ss.CPF.config.stop_at = "FULL" if continuation else "NOSE"
    ss.CPF.run(p0_target=p0_target, q0_target=q0_target)

    bus_uid = ss.Bus.idx2uid(int(target_bus_idx))
    lam = np.array(ss.CPF.lam, dtype=float)
    voltages = np.array(ss.CPF.V[bus_uid, :], dtype=float)
    # print(f"bus_uid: {bus_uid}\n, lam: {lam}\n, voltages: {voltages}\n")

    # convert p.u. base load into MV
    base_mva = float(getattr(getattr(ss, "config", object()), "mva", 100.0))
    base_p_mw = float(np.sum(p0_base) * base_mva)
    loads_mw = base_p_mw * (1.0 + lam * (float(max_scale) - 1.0))
    print(f"base_mva: {base_mva},\n base_p_mw: {base_p_mw},\n loads_mw: {loads_mw}\n")

    # stop tracking when voltage goes below the limit.
    below_limit_idx = np.where(voltages < float(voltage_limit))[0]
    if below_limit_idx.size > 0:
        end_idx = int(below_limit_idx[0]) + 1
        loads_mw = loads_mw[:end_idx]
        voltages = voltages[:end_idx]
        lam = lam[:end_idx]
        # print(end_idx)

    if len(loads_mw) == 0:
        raise ValueError("No CPF result points were produced.")

    P_vals = [float(v) for v in loads_mw.tolist()]
    V_vals = [float(v) for v in voltages.tolist()]
    max_p_idx = int(np.argmax(P_vals))
    nose_p = P_vals[max_p_idx]
    nose_v = V_vals[max_p_idx]
    # print(bus_uid, lam, voltages)
    save_path = None
    if not skip_plot:
        save_path = _get_output_path(grid)
        _build_plot(P_vals, V_vals, max_p_idx, int(target_bus_idx), save_path)

    curve_points = []
    initial_voltage = float(V_vals[0])
    initial_load = float(P_vals[0])

    for i, (load, voltage) in enumerate(zip(P_vals, V_vals)):
        load_scale = load / initial_load if initial_load > 0 else 1.0
        voltage_drop_from_initial = initial_voltage - voltage
        voltage_drop_percent = (voltage_drop_from_initial / initial_voltage) * 100 if initial_voltage > 0 else 0
        curve_points.append(
            {
                "step": i + 1,
                "load_mw": float(load),
                "voltage_pu": float(voltage),
                "load_scale_factor": float(load_scale),
                "voltage_drop_from_initial_pu": float(voltage_drop_from_initial),
                "voltage_drop_percent": float(voltage_drop_percent),
                "is_nose_point": bool(i == max_p_idx),
            }
        )

    return {
        "grid_system": grid,
        "target_bus": int(target_bus_idx),
        "power_factor": power_factor,
        "capacitive_load": capacitive,
        "contingency_lines": contingency_lines,
        "gen_voltage_setpoints": gen_voltage_setpoints,
        "load_values_mw": P_vals,
        "voltage_values_pu": V_vals,
        "curve_points": curve_points,
        "nose_point": {
            "load_mw": float(nose_p),
            "voltage_pu": float(nose_v),
            "index": int(max_p_idx),
        },
        "initial_conditions": {
            "load_mw": float(P_vals[0]),
            "voltage_pu": float(V_vals[0]),
        },
        "final_conditions": {
            "load_mw": float(P_vals[-1]),
            "voltage_pu": float(V_vals[-1]),
        },
        "voltage_drop_total": float(V_vals[0] - V_vals[-1]),
        "voltage_drop_percent_total": float((V_vals[0] - V_vals[-1]) / V_vals[0] * 100) if V_vals[0] > 0 else 0,
        "load_margin_mw": float(nose_p - P_vals[0]),
        "load_margin_percent": float((nose_p - P_vals[0]) / P_vals[0] * 100) if P_vals[0] > 0 else 0,
        "converged_steps": len(P_vals),
        "voltage_limit": voltage_limit,
        "save_path": save_path,
    }


if __name__ == "__main__":
    generate_pv_curve(
        grid="ieee39",
        target_bus_idx=5,
        step_size=0.1,
        max_scale=3.0,
        power_factor=0.95,
        voltage_limit=0.4,
        capacitive=False,
        skip_plot=False,
        continuation=True,
        # contingency_lines=[(1, 3), (3, 4)],
        # gen_voltage_setpoints={1: 2},
    )