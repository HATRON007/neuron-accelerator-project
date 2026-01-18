import pandas as pd
import matplotlib.pyplot as plt

# 1. Load Data
# Assuming the CSV is in the same folder
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: data.csv not found. Run the Verilog simulation first!")
    exit()

# 2. Hardware Constants
FRC_BITS = 12
SCALE_FACTOR = 2**FRC_BITS  # 4096
dt = 2**-7                  # Time step per clock cycle (from paper Eq 4)

# 3. Process Data
# If your CSV has raw integers, convert them here. 
# (The testbench already logs a float column 'v_float', but let's re-calculate to be safe)
df['v_voltage'] = df['v_raw'] / SCALE_FACTOR

# Create the Model Time axis (in ms)
# Each row in the CSV represents one clock cycle = one dt step
df['model_time_ms'] = df.index * dt

# 4. Plotting
plt.figure(figsize=(10, 6))

# Plot V vs Time
plt.plot(df['model_time_ms'], df['v_voltage'], label='Membrane Potential (v)', color='#1f77b4', linewidth=1.5)

# Add Threshold line (Optional, visual guide)
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='0V Reference')

# Formatting to match Paper 
plt.title(f"FHN Neuron Response (Input Current I $\\approx$ 0.8)", fontsize=14)
plt.xlabel("Model Time (ms)", fontsize=12)
plt.ylabel("Membrane Potential (V)", fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()

# Save and Show
plt.savefig("fhn_response.png", dpi=300)
print("Plot saved as fhn_response.png")
plt.show()