import numpy as np
import matplotlib.pyplot as plt
import pandapower as pp
import pandapower.networks as pn
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
    save_path = f"generated/pv_curve_{grid}_{timestamp}.png"
    
    os.makedirs("generated", exist_ok=True)

    net = net_map[grid]()

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
    max_p_idx = np.argmax(P_vals)
    nose_p = P_vals[max_p_idx]
    nose_v = V_vals[max_p_idx]
    
    # Only create plot if skip_plot is False
    if not skip_plot:
        # Create the plot
        plt.figure(figsize=(8, 6))
        # Upper branch (stable) from power-increase sweep
        plt.plot(P_vals, V_vals, marker="o", linestyle="-", color="blue", label="Upper Branch")
        plt.scatter(nose_p, nose_v, color="red", zorder=5, label="Nose Point")
        plt.annotate(
            f"P={nose_p:.1f} MW\nV={nose_v:.3f} pu",
            xy=(nose_p, nose_v),
            xytext=(nose_p * 0.9, nose_v + 0.05),
            arrowprops=dict(arrowstyle="->", color="black"),
            fontsize=9
        )
        plt.xlabel("Total Active Load P (MW)")
        plt.ylabel(f"Voltage at Bus {target_bus_idx} (pu)")
        plt.title("System P–V Curve (Voltage Stability Analysis)")
        
        # Set y-axis ticks every 0.05 for more precision
        y_min_candidates = [min(V_vals)]
        y_max_candidates = [max(V_vals)]
        y_min = max(0, min(y_min_candidates) - 0.05)
        y_max = max(y_max_candidates) + 0.05
        y_ticks = np.arange(np.floor(y_min * 20) / 20, np.ceil(y_max * 20) / 20 + 0.05, 0.05)
        plt.yticks(y_ticks)
        
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
            "is_nose_point": i == max_p_idx
        })

    results_summary = {
        "grid_system": grid,
        "target_bus": target_bus_idx,
        "power_factor": power_factor,
        "capacitive_load": capacitive,
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
        step_size=0.005,
        max_scale=3.0,
        power_factor=0.95,
        voltage_limit=0.2,
        capacitive=True
    )
