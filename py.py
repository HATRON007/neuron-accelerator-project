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
    return 2.0**(-x) - 2.0**(x)

# --- 2. LOAD DATA ---
# Reads the CSV. If Verilog wrote consistent columns, this will be perfect.
df = pd.read_csv(FILE_NAME)

# Extract columns
t_hw = df['time_step'].values
v_hw = df['v_float'].values
i_raw = df['i_raw'].values

# Convert Stimulus to float (e.g. 4096 -> 1.0)
i_stim = i_raw / SCALING_FACTOR

# Setup Python Arrays
num_steps = len(df)
v_py = np.zeros(num_steps)
w_py = np.zeros(num_steps)

# --- 3. INITIAL CONDITIONS ---
# Matches Verilog reset values: v = 0xECE1 (-1.19), w = 0xF600 (-0.625)
v_py[0] = -1.19
w_py[0] = -0.625

v = v_py[0]
w = w_py[0]

# --- 4. SIMULATION LOOP ---
print(f"Running Python Model for {num_steps} cycles...")

for k in range(1, num_steps):
    # Get current input current (from previous timestep)
    I = i_stim[k-1]
    
    # --- MATH CORE (Matches Hardware Logic) ---
    
    # Nonlinear term: g(v) = 3 * (2^-v - 2^v)
    g_v = 3.0 * get_pow2_approx(v)
    
    # Linear term: 5 * v
    linear_v = 5.0 * v
    
    # Slope calculation
    dv = DT * (linear_v + g_v - w + I)
    
    # Recovery calculation
    dw = (DT / TAU) * (v + A - B * w)
    
    # Update State (Euler Integration)
    v = v + dv
    w = w + dw
    
    # Store result
    v_py[k] = v
    w_py[k] = w

# --- 5. ERROR ANALYSIS ---
# Calculate RMSE
error = v_hw - v_py
mse = np.mean(error**2)
rmse = np.sqrt(mse)

print(f"Validation Complete.")
print(f"RMSE: {rmse:.5f}")

# --- 6. PLOTTING ---
plt.figure(figsize=(12, 6))

# Plot Python Model (Reference)
plt.plot(t_hw, v_py, 'r--', linewidth=2, label='Python Ideal')

# Plot Hardware Output
plt.plot(t_hw, v_hw, 'b-', alpha=0.6, label='Verilog Hardware')

plt.title(f"Validation: Hardware vs Python (RMSE: {rmse:.4f})")
plt.xlabel("Simulation Time (ns)")
plt.ylabel("Membrane Potential (V)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("validation_full.png")
plt.show()