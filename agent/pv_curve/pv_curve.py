import numpy as np
import matplotlib.pyplot as plt
import pandapower as pp
import pandapower.networks as pn
import pandapower.topology as top
from datetime import datetime
import os

# This function creates a P–V curve to show how bus voltage drops as the system load increases
def generate_pv_curve(
    grid="ieee39",             # Which test system to use (e.g., IEEE 39-bus system)
    target_bus_idx=5,          # Bus number where we monitor voltage
    step_size=0.01,            # Increment size for load increase (e.g., 1% per step)
    max_scale=3.0,             # Maximum multiplier for load (e.g., 3 = 300% load)
    power_factor=0.95,         # Assumed constant power factor (relationship between real and reactive power)
    voltage_limit=0.4,         # Minimum acceptable voltage limit (in pu) before we stop
    capacitive=False,         # Whether the power factor is capacitive or inductive (default is inductive)
    skip_plot=False,          # Skip visual graph generation (for analysis-only mode)
    contingency_lines=None,    # It should be [1, 2] means cut the line between bus 1 and 2 instead of 2 and 3(It starts from 0 in pp)
    gen_voltage_setpoints=None,  # Dict of {gen_index: vm_pu} to override generator voltage setpoints before the sweep
                                 # e.g. {1: 1.05} — set generator 1 to 1.05 pu
):
    net_map = {
        "ieee14": pn.case14,
        "ieee24": pn.case24_ieee_rts,
        "ieee30": pn.case30,
        "ieee39": pn.case39,
        "ieee57": pn.case57,
        "ieee118": pn.case118,
        "ieee300": pn.case300,
    }

    if grid not in net_map:
        raise ValueError(f"Unsupported grid '{grid}'. Choose from {list(net_map)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Choose output directory:
    # 1) If PV_CURVE_OUTPUT_DIR is set, use that
    # 2) Otherwise fall back to "generated" (CLI behavior stays the same)
    output_dir = os.getenv("PV_CURVE_OUTPUT_DIR") or "generated"
    os.makedirs(output_dir, exist_ok=True)

    save_path = os.path.join(output_dir, f"pv_curve_{grid}_{timestamp}.png")

    net = net_map[grid]()

    # Convert target_bus_idx from 1-based (user input) to 0-based (pandapower index)
    target_bus_idx -= 1
    if target_bus_idx not in net.bus.index:
        raise ValueError(f"Bus {target_bus_idx + 1} not found in grid '{grid}'. Valid range: 1 to {len(net.bus)}.")

    # Apply line contingencies (N-1 / N-k): disable specified lines and verify connectivity
    if contingency_lines:
        for (fb, tb) in contingency_lines:
            fb -= 1
            tb -= 1
            line_mask = (
                ((net.line["from_bus"] == fb) & (net.line["to_bus"] == tb)) |
                ((net.line["from_bus"] == tb) & (net.line["to_bus"] == fb))
            )
            trafo_mask = (
                ((net.trafo["hv_bus"] == fb) & (net.trafo["lv_bus"] == tb)) |
                ((net.trafo["hv_bus"] == tb) & (net.trafo["lv_bus"] == fb))
            ) if not net.trafo.empty else None

            if not line_mask.any() and (trafo_mask is None or not trafo_mask.any()):
                raise ValueError(f"No line or transformer found between bus {fb+1} and bus {tb+1} in grid '{grid}'.")

            if line_mask.any():
                net.line.loc[line_mask, "in_service"] = False
                print(f"Line between bus {fb+1} and bus {tb+1} taken out of service.")
            if trafo_mask is not None and trafo_mask.any():
                net.trafo.loc[trafo_mask, "in_service"] = False
                print(f"Transformer between bus {fb+1} and bus {tb+1} taken out of service.")

        # Verify the network is still fully connected after removing the lines
        mg = top.create_nxgraph(net)
        connected_buses = list(top.connected_components(mg))

        if len(connected_buses) > 1:
            raise ValueError(
                f"Removing lines {contingency_lines} disconnects the network into "
                f"{len(connected_buses)} islands. Choose a different contingency."
            )

    # Override generator voltage setpoints (AVR targets) on generating buses only
    if gen_voltage_setpoints:
        for gen_idx, vm_pu in gen_voltage_setpoints.items():
            gen_idx -= 1
            if gen_idx not in net.gen.index:
                raise ValueError(f"Generator index {gen_idx+1} not found in grid '{grid}'. Valid indices: {list(net.gen.index+1)}")
            net.gen.at[gen_idx, "vm_pu"] = vm_pu
            print(f"Generator {gen_idx+1} voltage setpoint set to {vm_pu} pu.")

    # Save original active (P) and reactive (Q) loads to scale later
    net.load["p_mw_base"] = net.load["p_mw"]
    net.load["q_mvar_base"] = net.load["q_mvar"]

    # List of all buses with loads connected
    scale_buses = list(net.load["bus"].values)

    # Store results for each step (total load and voltage)
    results = []

    # Start from normal load (scale = 1.0)
    scale = 1.0
    converged = True

    # Loop to keep increasing the load step by step
    while scale <= max_scale and converged:
        for idx in net.load.index:
            if net.load.at[idx, "bus"] in scale_buses:
                base_p = net.load.at[idx, "p_mw_base"]
                
                # Increase active power
                net.load.at[idx, "p_mw"] = base_p * scale
                
                # Calculate corresponding reactive power using power factor
                # net.load.at[idx, "q_mvar"] = net.load.at[idx, "p_mw"] * np.tan(np.arccos(power_factor))

                sign = -1 if capacitive else 1
                net.load.at[idx, "q_mvar"] = sign * net.load.at[idx, "p_mw"] * np.tan(np.arccos(power_factor))

        try:
            # Run power flow analysis to solve for voltages
            pp.runpp(net, init="results")
            
            # Get voltage magnitude at the chosen bus
            v_mag = net.res_bus.at[target_bus_idx, "vm_pu"]
            
            # Calculate total system active load
            total_p = net.load["p_mw"].sum()

            # Save the current load and voltage for plotting later
            results.append((total_p, v_mag))

            # Stop if voltage drops below chosen limit (collapse point)
            if v_mag < voltage_limit:
                print("Voltage below limit, stopping.")
                break

        except pp.LoadflowNotConverged:
            # If the solver can't find a valid solution, we have reached the collapse point
            if not skip_plot:
                print("Voltage collapse point successfully identified.")
            converged = False
            break

        # Increase the load multiplier for the next step
        scale += step_size

    # Split saved results into separate lists for plotting
    P_vals, V_vals = zip(*results)

    # Find point with maximum load (approximate nose point of the curve)
    max_p_idx = int(np.argmax(P_vals))  # Convert to Python int for JSON serialization
    nose_p = P_vals[max_p_idx]
    nose_v = V_vals[max_p_idx]
    
    # Only create plot if skip_plot is False
    if not skip_plot:
        # Symmetric lower branch (plot only): reflect upper branch in V around nose voltage
        n = max_p_idx + 1
        P_lower = P_vals[:n]
        V_lower = [2 * nose_v - V_vals[i] for i in range(n)]

        # Create the plot
        plt.figure(figsize=(8, 6))
        # Upper branch (stable) from power-increase sweep
        plt.plot(P_vals, V_vals, marker="o", linestyle="-", color="blue", label="Upper Branch")
        plt.plot(P_lower, V_lower, marker="x", linestyle="-", color="red", label="Lower Branch (symmetric)")
        plt.scatter(nose_p, nose_v, color="red", zorder=5, label="Nose Point")
        plt.annotate(
            f"P={nose_p:.1f} MW\nV={nose_v:.3f} pu",
            xy=(nose_p, nose_v),
            xytext=(nose_p * 1.005, nose_v),
            arrowprops=dict(arrowstyle="->", color="black"),
            fontsize=9
        )
        plt.xlabel("Total Active Load P (MW)")
        plt.ylabel(f"Voltage at Bus {target_bus_idx + 1} (pu)")
        plt.title("System P–V Curve (Voltage Stability Analysis)")
        
        # Set y-axis to include both branches
        y_min = max(0, min(min(V_vals), min(V_lower)) * 0.99)
        y_max = max(max(V_vals), max(V_lower)) * 1.01
        plt.ylim(y_min, y_max)
        
        plt.grid(True)
        plt.legend()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        
        print(f"P-V curve successfully generated and saved at: {save_path}")
        print("Displaying curve preview - close the plot window to continue analysis...")
        
        plt.show()
        plt.close()
    else:
        # When skipping plot, set save_path to None
        save_path = None

    # Add points and details of shape for the LLM to better understand the curve
    curve_points = []
    initial_voltage = float(V_vals[0])
    initial_load = float(P_vals[0])
    
    for i, (load, voltage) in enumerate(zip(P_vals, V_vals)):
        load_scale = load / initial_load if initial_load > 0 else 1.0
        voltage_drop_from_initial = initial_voltage - voltage
        voltage_drop_percent = (voltage_drop_from_initial / initial_voltage) * 100 if initial_voltage > 0 else 0
        
        curve_points.append({
            "step": i + 1,
            "load_mw": float(load),
            "voltage_pu": float(voltage),
            "load_scale_factor": float(load_scale),
            "voltage_drop_from_initial_pu": float(voltage_drop_from_initial),
            "voltage_drop_percent": float(voltage_drop_percent),
            "is_nose_point": bool(i == max_p_idx)  # Convert to Python bool for JSON serialization
        })

    results_summary = {
        "grid_system": grid,
        "target_bus": target_bus_idx + 1,  # Report back as 1-based
        "power_factor": power_factor,
        "capacitive_load": capacitive,
        "contingency_lines": contingency_lines,
        "gen_voltage_setpoints": gen_voltage_setpoints,
        "load_values_mw": list(P_vals),
        "voltage_values_pu": list(V_vals),
        "curve_points": curve_points,
        "nose_point": {
            "load_mw": float(nose_p),
            "voltage_pu": float(nose_v),
            "index": int(max_p_idx)
        },
        "initial_conditions": {
            "load_mw": float(P_vals[0]),
            "voltage_pu": float(V_vals[0])
        },
        "final_conditions": {
            "load_mw": float(P_vals[-1]),
            "voltage_pu": float(V_vals[-1])
        },
        "voltage_drop_total": float(V_vals[0] - V_vals[-1]),
        "voltage_drop_percent_total": float((V_vals[0] - V_vals[-1]) / V_vals[0] * 100) if V_vals[0] > 0 else 0,
        "load_margin_mw": float(nose_p - P_vals[0]),
        "load_margin_percent": float((nose_p - P_vals[0]) / P_vals[0] * 100) if P_vals[0] > 0 else 0,
        "converged_steps": len(results),
        "voltage_limit": voltage_limit,
        "save_path": save_path
    }

    # Analysis details will be handled by the analysis agent
    # Results summary is returned for the LLM to analyze

    return results_summary

if __name__ == "__main__":
    """
    Runs locally using the following parameters.

    Modify the parameters to your liking, then run `python pv_curve.py` in this directory.
    """

    generate_pv_curve(
        grid="ieee39",
        target_bus_idx=5,
        step_size=0.01,
        max_scale=3.0,
        power_factor=0.95,
        voltage_limit=0.4,
        capacitive=False,
        skip_plot=False,
        # contingency_lines=[(2, 3), (3, 4)],
        # gen_voltage_setpoints={1: 2},
    )