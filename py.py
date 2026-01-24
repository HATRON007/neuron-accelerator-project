import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE_NAME = "data.csv"
SCALING_FACTOR = 4096.0

IDS_TO_PLOT = [0, 150, 300, 499] 

DT  = 2**-7
TAU = 2.0
A   = 0.7
B   = 0.5

def get_pow2_approx(x):
    def hw_pow2(val):
        val_int = np.floor(val)
        val_frac = val - val_int
        return (1.0 + val_frac) * (2.0 ** val_int)
    term_neg = hw_pow2(-x)
    term_pos = hw_pow2(x)
    return term_neg - term_pos

def run_ideal_model(stimulus_array):
    steps = len(stimulus_array)
    v_out = np.zeros(steps)
    v = -1.19
    w = -0.625
    threshold = 450.0 / SCALING_FACTOR

    for k in range(steps):
        I = stimulus_array[k]
        g_v = 3.0 * get_pow2_approx(v)
        linear_v = 5.0 * v
        force = linear_v + g_v - w + I
        
        if -threshold < force < threshold:
            force = 0.0
            
        dv = DT * force
        dw = (DT / TAU) * (v + A - B * w)
        v = v + dv
        w = w + dw
        v_out[k] = v
        
    return v_out

print(f"Loading {FILE_NAME}...")
df = pd.read_csv(FILE_NAME)

print("Generating 4 separate windows...")

for n_id in IDS_TO_PLOT:
    subset = df[df['neuron_id'] == n_id].reset_index(drop=True)
    
    if subset.empty:
        print(f"Skipping Neuron {n_id} (No data).")
        continue

    v_hw = subset['v_float'].values
    t_axis = subset['time_ns'].values

    if n_id == 0 or n_id == 150:
        i_stim = np.full(len(v_hw), 1.0)
    else:
        i_stim = np.zeros(len(v_hw))

    v_model = run_ideal_model(i_stim)

    limit = min(len(v_hw), len(v_model))
    error = v_hw[:limit] - v_model[:limit]
    rmse = np.sqrt(np.mean(error**2))

    plt.figure(figsize=(10, 6))
    
    plt.plot(t_axis[:limit], v_model[:limit], 'r--', linewidth=2, label='Python Math Model')
    plt.plot(t_axis[:limit], v_hw[:limit], 'b-', alpha=0.6, label='Verilog Hardware')
    
    plt.title(f"Neuron ID: {n_id} (RMSE: {rmse:.4f})")
    plt.xlabel("Simulation Time (ns)")
    plt.ylabel("Membrane Potential (V)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    filename = f"neuron_{n_id}_validation.png"
    plt.savefig(filename)
    print(f"Saved {filename}")

    plt.show()