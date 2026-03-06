# plotter.py
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# Load Data
with open('nsd_data.pkl', 'rb') as f:
    data = pickle.load(f)

history = data['history']
avalanches_sf = data['avalanches_sf']
avalanches_er = data['avalanches_er']

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
plt.subplots_adjust(wspace=0.3)

# ---------------------------------------------------------
# Plot 1: The SOC Power-Law (Log-Log)
# ---------------------------------------------------------
ax1 = axes[0]
for av_data, label, color in zip([avalanches_sf, avalanches_er], ['Scale-Free (BA)', 'Random (ER)'], ['#d62728', '#1f77b4']):
    if len(av_data) > 0:
        counts = Counter(av_data)
        sizes = np.array(list(counts.keys()))
        freqs = np.array(list(counts.values())) / len(av_data)
        ax1.scatter(sizes, freqs, alpha=0.7, label=label, color=color, edgecolors='k')

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_title('Indicator 1: SOC Avalanche Size Distribution', fontsize=12)
ax1.set_xlabel('Avalanche Size $s$ (Nodes Failed)', fontsize=10)
ax1.set_ylabel('Probability $P(s)$', fontsize=10)
ax1.grid(True, which="both", ls="--", alpha=0.4)
ax1.legend()

# ---------------------------------------------------------
# Plot 2: Systemic Entropy (Early Warning)
# ---------------------------------------------------------
ax2 = axes[1]
time_steps = np.arange(len(history['entropy']))
ax2.plot(time_steps, history['entropy'], color='#9467bd', lw=2)
ax2.set_title('Indicator 2: Pre-Percolation Entropy Spike', fontsize=12)
ax2.set_xlabel('Time (Slow Drive Events $e$)', fontsize=10)
ax2.set_ylabel('Systemic Entropy $H$', fontsize=10)

# Mark the collapse region
collapse_starts = np.where(np.array(history['failing_fraction']) > 0.5)[0]
if len(collapse_starts) > 0:
    ax2.axvline(x=collapse_starts[0], color='k', linestyle='--', label='Macro Collapse Triggered')
    ax2.legend()
ax2.grid(True, alpha=0.4)

# ---------------------------------------------------------
# Plot 3: Topological Hysteresis
# ---------------------------------------------------------
ax3 = axes[2]
rho = np.array(history['rho'])
capacity = np.array(history['mean_capacity'])

# Split into loading (ramping up) and unloading (ramping down)
midpoint = len(rho) // 2
ax3.plot(rho[:midpoint], capacity[:midpoint], color='#ff7f0e', lw=2, label='Loading (Increasing Stress)')
ax3.plot(rho[midpoint:], capacity[midpoint:], color='#2ca02c', lw=2, linestyle='--', label='Unloading (Recovery Attempt)')

ax3.set_title('Indicator 3: Hub-Induced Hysteresis', fontsize=12)
ax3.set_xlabel(r'Systemic Control Parameter $\rho$ (Load/Capacity)', fontsize=10)
ax3.set_ylabel(r'Mean Integration Capacity $\langle C \rangle$', fontsize=10)
ax3.axvline(x=1.0, color='r', linestyle=':', label=r'Critical Threshold $\rho \approx 1$')
ax3.grid(True, alpha=0.4)
ax3.legend()

plt.suptitle('Normative Stress Dynamics (NSD): Validating Empirical Predictions', fontsize=16, y=1.05)
plt.savefig('nsd_results.png', dpi=300, bbox_inches='tight')
print("Plots saved as 'nsd_results.png'. Opening window...")
plt.show()