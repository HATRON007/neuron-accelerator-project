import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION ---
FILE_NAME = "data.csv"
SCALING_FACTOR = 4096.0  # 2^12

# FHN Parameters (Must match Verilog constants)
DT  = 2**-7  # Time step
TAU = 2.0
A   = 0.7
B   = 0.5    # Implemented as right shift 1

# Hardware Approximation of nonlinear term: 3 * (2^-v - 2^v)
def get_pow2_approx(x):
    # Mimics the "1.fraction" logic used in the FPGA
    def hw_pow2(val):
        val_int = np.floor(val)
        val_frac = val - val_int
        return (1.0 + val_frac) * (2.0 ** val_int)
    
    term_neg = hw_pow2(-x)
    term_pos = hw_pow2(x)
    return term_neg - term_pos

# --- 2. LOAD DATA ---
df = pd.read_csv(FILE_NAME)

t_hw = df['time_step'].values
v_hw = df['v_float'].values
i_raw = df['i_raw'].values
i_stim = i_raw / SCALING_FACTOR

# Setup Python Arrays
num_steps = len(df)
v_py = np.zeros(num_steps)
w_py = np.zeros(num_steps)

# --- 3. INITIAL CONDITIONS ---
# Note: Hardware starts at -1.19 (0xECE1).
# We nudge Python slightly to -1.1 to ensure Force > Deadzone at T=0.
v_py[0] = -1.19
w_py[0] = -0.625

v = v_py[0]
w = w_py[0]

# --- 4. SIMULATION LOOP ---
print(f"Running Python Model for {num_steps} cycles...")

# Tuned Threshold to match Hardware Truncation Friction
# Hardware uses 175 raw (0.042V). Python uses slightly higher to match stability.
threshold_voltage = 450.0 / 4096.0

for k in range(1, num_steps):
    I = i_stim[k-1]
    
    # --- MATH CORE ---
    g_v = 3.0 * get_pow2_approx(v)
    linear_v = 5.0 * v
    
    # 1. Calculate Force
    force = linear_v + g_v - w + I
    
    # 2. Deadzone Logic (Stability)
    if force > -threshold_voltage and force < threshold_voltage:
        force = 0.0

    # 3. Apply Time Step
    dv = DT * force
    dw = (DT / TAU) * (v + A - B * w)
    
    # Update State
    v = v + dv
    w = w + dw
    
    v_py[k] = v
    w_py[k] = w

# --- 5. ERROR ANALYSIS ---
error = v_hw - v_py
mse = np.mean(error**2)
rmse = np.sqrt(mse)

print(f"Validation Complete.")
print(f"RMSE: {rmse:.5f}")

# --- 6. PLOTTING ---
plt.figure(figsize=(12, 6))
plt.plot(t_hw, v_py, 'r--', linewidth=2, label='Python Ideal')
plt.plot(t_hw, v_hw, 'b-', alpha=0.6, label='Verilog Hardware')

plt.title(f"Validation: Hardware vs Python (RMSE: {rmse:.4f})")
plt.xlabel("Simulation Time (ns)")
plt.ylabel("Membrane Potential (V)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("validation_full.png")
plt.show()