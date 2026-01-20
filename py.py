import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE_NAME = "data.csv"
SCALING_FACTOR = 4096.0

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

df = pd.read_csv(FILE_NAME)

t_hw = df['time_step'].values
v_hw = df['v_float'].values
i_raw = df['i_raw'].values
i_stim = i_raw / SCALING_FACTOR

num_steps = len(df)
v_py = np.zeros(num_steps)
w_py = np.zeros(num_steps)

v_py[0] = -1.19
w_py[0] = -0.625

v = v_py[0]
w = w_py[0]

print(f"Running Python Model for {num_steps} cycles...")

threshold_voltage = 450.0 / 4096.0

for k in range(1, num_steps):
    I = i_stim[k-1]
    g_v = 3.0 * get_pow2_approx(v)
    linear_v = 5.0 * v
    force = linear_v + g_v - w + I
    if force > -threshold_voltage and force < threshold_voltage:
        force = 0.0
    dv = DT * force
    dw = (DT / TAU) * (v + A - B * w)
    v = v + dv
    w = w + dw
    v_py[k] = v
    w_py[k] = w

error = v_hw - v_py
mse = np.mean(error**2)
rmse = np.sqrt(mse)

print(f"Validation Complete.")
print(f"RMSE: {rmse:.5f}")

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
