import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# --- CONFIGURATION ---
FILE_NAME = "data.csv"
SCALING_FACTOR = 4096.0 
DT = 2**-7
TAU = 2.0
A = 0.7
B = 0.5 

def get_pow2_approx(x):
    return 2.0**(-x) - 2.0**(x)

# --- 1. LOAD & SIMULATE ---
print("Loading data...")
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

v, w = v_py[0], w_py[0]

print(f"Running Python Reference Model for {num_steps} cycles...")
for k in range(1, num_steps):
    I = i_stim[k-1]
    g_v = 3.0 * get_pow2_approx(v)
    linear_v = 5.0 * v
    dv = DT * (linear_v + g_v - w + I)
    dw = (DT / TAU) * (v + A - B * w)
    v = v + dv
    w = w + dw
    v_py[k] = v
    w_py[k] = w

# --- 2. SPIKE ANALYSIS ---
print("Analyzing Spikes...")

# Find peaks (spikes) where voltage > 0.0V
# distance=100 ensures we don't count the same spike twice
peaks_hw, _ = find_peaks(v_hw, height=0.0, distance=100)
peaks_py, _ = find_peaks(v_py, height=0.0, distance=100)

# Calculate Inter-Spike Intervals (ISI)
# ISI = Time difference between consecutive spikes
isi_hw = np.diff(peaks_hw)
isi_py = np.diff(peaks_py)

# Calculate Average ISI
avg_isi_hw = np.mean(isi_hw) if len(isi_hw) > 0 else 0
avg_isi_py = np.mean(isi_py) if len(isi_py) > 0 else 0

# Calculate Frequency (Hz equivalent in simulation steps)
freq_hw = 1.0 / avg_isi_hw if avg_isi_hw > 0 else 0
freq_py = 1.0 / avg_isi_py if avg_isi_py > 0 else 0

# --- 3. REPORT CARD ---
print("\n" + "="*40)
print("     RIGOROUS SPIKE BEHAVIOR REPORT     ")
print("="*40)

print(f"Total Cycles: {num_steps}")
print("-" * 30)
print(f"Total Spikes (Hardware): {len(peaks_hw)}")
print(f"Total Spikes (Python):   {len(peaks_py)}")
print("-" * 30)
print(f"Avg Interval (Hardware): {avg_isi_hw:.2f} cycles")
print(f"Avg Interval (Python):   {avg_isi_py:.2f} cycles")
print("-" * 30)
print(f"Difference in Interval:  {avg_isi_hw - avg_isi_py:.4f} cycles")
if avg_isi_py > 0:
    error_percent = abs(avg_isi_hw - avg_isi_py) / avg_isi_py * 100
    print(f"Timing Error:            {error_percent:.4f}%")
else:
    print("No spikes detected.")

print("="*40)

if abs(error_percent) < 1.0:
    print("RESULT: PASS. Behavior is consistent.")
else:
    print("RESULT: WARNING. Significant timing deviation.")

# --- 4. VISUAL PROOF ---
# Plot just the first 3 spikes to see shape match
plt.figure(figsize=(10, 5))
limit = min(5000, num_steps)
plt.plot(t_hw[:limit], v_py[:limit], 'r--', label='Python')
plt.plot(t_hw[:limit], v_hw[:limit], 'b-', alpha=0.7, label='Hardware')
plt.title("Spike Shape Comparison (First 5000 cycles)")
plt.legend()
plt.grid(True)
plt.savefig("spike_shape.png")
plt.show()