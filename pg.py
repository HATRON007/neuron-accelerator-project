import numpy as np
import matplotlib.pyplot as plt

DURATION_NS = 30000
DT_FACTOR = 2**-7
TAU = 2.0
A = 0.7
B = 0.5
THRESHOLD_VAL = 175.0 / 4096.0
V_INIT = -1.1
W_INIT = -0.625

def get_stimulus(t_step):
    if t_step < 5000:
        return 0.5
    elif t_step < 15000:
        return 0.0
    elif t_step < 25000:
        return 1.0
    else:
        return 0.5

def get_pow2_approx(x):
    def hw_pow2(val):
        val_int = np.floor(val)
        val_frac = val - val_int
        return (1.0 + val_frac) * (2.0 ** val_int)
    
    term_neg = hw_pow2(-x)
    term_pos = hw_pow2(x)
    return term_neg - term_pos

num_steps = int(DURATION_NS)
t_axis = np.arange(num_steps)
v_trace = np.zeros(num_steps)
w_trace = np.zeros(num_steps)
i_trace = np.zeros(num_steps)

v = V_INIT
w = W_INIT

for k in range(num_steps):
    I = get_stimulus(k)
    i_trace[k] = I
    
    g_v = 3.0 * get_pow2_approx(v)
    linear_v = 5.0 * v
    
    force = linear_v + g_v - w + I
    
    if -THRESHOLD_VAL < force < THRESHOLD_VAL:
        force = 0.0

    dv = DT_FACTOR * force
    dw = (DT_FACTOR / TAU) * (v + A - B * w)
    
    v = v + dv
    w = w + dw
    
    v_trace[k] = v
    w_trace[k] = w

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

ax1.plot(t_axis, v_trace, 'b-', linewidth=1.5, label='Membrane Potential (V)')
ax1.set_ylabel("Voltage (V)")
ax1.set_title(f"FitzHugh-Nagumo Simulation")
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend()

ax2.plot(t_axis, i_trace, 'g-', linewidth=1.5, label='Input Stimulus (I)')
ax2.set_ylabel("Current (I)")
ax2.set_xlabel("Time Steps")
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend()

plt.tight_layout()
plt.show()