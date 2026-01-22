import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE_NAME = "data.csv"
SCALING_FACTOR = 4096.0

DT = 2**-7
TAU = 2.0
A = 0.7
B = 0.5

def get_pow2_approx(x):
    def hw_pow2(val):
        val_int = np.floor(val)
        val_frac = val - val_int
        return (1.0 + val_frac) * (2.0 ** val_int)
    term_neg = hw_pow2(-x)
    term_pos = hw_pow2(x)
    return term_neg - term_pos

df = pd.read_csv(FILE_NAME)
v_hw = df['v_float'].values
i_raw = df['i_raw'].values
i_stim = i_raw / SCALING_FACTOR

num_hw_steps = len(df)
num_py_steps = num_hw_steps // 4

v_py = np.zeros(num_py_steps)
w_py = np.zeros(num_py_steps)

v_py[0] = -1.19
w_py[0] = -0.625

v = v_py[0]
w = w_py[0]

i_stim_decimated = i_stim[::4]
threshold_voltage = 450.0 / 4096.0

for k in range(1, num_py_steps):
    I = i_stim_decimated[k-1] if k-1 < len(i_stim_decimated) else 0
    g_v = 3.0 * get_pow2_approx(v)
    linear_v = 5.0 * v
    force = linear_v + g_v - w + I
    if -threshold_voltage < force < threshold_voltage:
        force = 0.0
    dv = DT * force
    dw = (DT / TAU) * (v + A - B * w)
    v = v + dv
    w = w + dw
    v_py[k] = v
    w_py[k] = w

v_py_stretched = np.repeat(v_py, 4)

limit = min(len(v_hw), len(v_py_stretched))
v_hw_plot = v_hw[:limit]
v_py_plot = v_py_stretched[:limit]
t_axis = np.arange(limit)

error = v_hw_plot - v_py_plot
rmse = np.sqrt(np.mean(error**2))

print("Validation Complete.")
print(f"RMSE (Aligned): {rmse:.5f}")

plt.figure(figsize=(12, 6))
plt.plot(t_axis, v_py_plot, 'r--', linewidth=2, label='Python (Stretched 4x)')
plt.plot(t_axis, v_hw_plot, 'b-', alpha=0.6, label='Verilog Hardware (Pipelined)')
plt.title(f"Pipeline Validation: Hardware vs Python (RMSE: {rmse:.4f})")
plt.xlabel("Simulation Clock Cycles")
plt.ylabel("Membrane Potential (V)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("validation_pipeline.png")
plt.show()
