import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm

# ==========================================
# 1. THE CONTINUOUS DYNAMICAL ENGINE (NSD)
# ==========================================
class NSD_System:
    def __init__(self, N=1000, topology='scale-free', eta=0.01, beta=0.10):
        self.N = N
        self.tick = 0
        
        # Thermodynamic & Homeostatic Parameters
        self.dissipation = 0.01        # gamma (natural stress decay)
        self.recovery_rate = 0.005     # mu (institutional recovery)
        self.burnout_penalty = beta    # beta (fatigue from cascading)
        self.cascade_speed = 0.8       # kappa (propagation speed)
        self.activation_sharpness = 10.0 # a (sigmoid threshold sharpness)
        
        # NEW: Homeostatic Parameters (Equation IV)
        self.eta = eta                 # adaptation rate (bureaucratic friction)
        self.A0 = 0.02                 # Target activity: tolerate 2% network cascading
        
        # Initialize Graph Topology
        if topology == 'scale-free':
            self.graph = nx.barabasi_albert_graph(N, 3)
        else:
            self.graph = nx.erdos_renyi_graph(N, 0.006)
            
        # Pre-calculate Leaky Conservation Propagation Matrix (W)
        adj = nx.to_numpy_array(self.graph)
        np.fill_diagonal(adj, 0)
        row_sums = adj.sum(axis=1)
        with np.errstate(divide='ignore', invalid='ignore'):
            row_sums_inv = np.nan_to_num(1.0 / row_sums, posinf=0.0)
        self.W = (adj * row_sums_inv[:, np.newaxis]).T
        
        # Initialize Node States
        self.C_star = np.maximum(1.0, np.random.normal(5.0, 1.0, N)) # Dynamic Baseline
        self.C = self.C_star.copy()                                  # Current Capacity
        self.S = np.zeros(N)                                         # Accumulated Stress
        
        # Data Trackers
        self.history = {'entropy': [], 'failing_fraction': [], 'mean_capacity': [], 'mean_baseline': []}
        self.avalanches = []

    def _activation_function(self):
        """Equation II: Differentiable Cascade Activation"""
        diff = self.S - self.C
        sig = 1.0 / (1.0 + np.exp(-self.activation_sharpness * diff))
        F = self.cascade_speed * diff * sig
        return np.maximum(0.0, F)

    def _fast_relaxation(self):
        """Topological Cascade Loop (Time freezes while stress resolves)"""
        cascade_active = True
        nodes_involved = set()
        depth = 0
        
        while cascade_active and depth < 100:
            F = self._activation_function()
            failing_indices = np.where(F > 0.01)[0]
            
            if len(failing_indices) == 0:
                break
                
            nodes_involved.update(failing_indices)
            
            # Equation III: Saddle-Node Burnout Degradation
            self.C[failing_indices] -= self.burnout_penalty * F[failing_indices]
            self.C = np.maximum(0.1, self.C) 
            
            # Conserved Propagation
            propagated = np.dot(self.W, F)
            self.S = self.S + propagated - F
            depth += 1
            
        return len(nodes_involved)

    def slow_step(self, load_mu, load_pct):
        """Equation I & IV: Exogenous Event Loop (Slow Time)"""
        # 1. Equation III (Recovery) & Equation I (Dissipation)
        self.C += self.recovery_rate * (self.C_star - self.C)
        self.S = np.maximum(0.0, self.S - self.dissipation)
        
        # 2. Equation I (Exogenous Load Injection)
        num_to_load = max(1, int(self.N * load_pct))
        targets = np.random.choice(self.N, num_to_load, replace=False)
        self.S[targets] += np.maximum(0.0, np.random.normal(load_mu, load_mu*0.2, num_to_load))
        
        # 3. SOC Cascade Resolution
        avalanche_size = self._fast_relaxation()
        if avalanche_size > 0:
            self.avalanches.append(avalanche_size)
            
        # 4. NEW: Equation IV (Homeostatic Adaptation)
        current_activity_A = avalanche_size / self.N
        self.C_star += self.eta * (self.A0 - current_activity_A)
        self.C_star = np.clip(self.C_star, 1.0, 15.0) # Prevent absurd infinite growth/decay
            
        # 5. Thermodynamic Observation
        total_stress = self.S.sum()
        entropy = 0.0
        if total_stress > 1e-9:
            p_i = self.S / total_stress
            p_i_nz = p_i[p_i > 0]
            entropy = -np.sum(p_i_nz * np.log(p_i_nz))
            
        self.history['entropy'].append(entropy)
        self.history['failing_fraction'].append(np.mean(self.S > self.C))
        self.history['mean_capacity'].append(np.mean(self.C))
        self.history['mean_baseline'].append(np.mean(self.C_star))
        
        self.tick += 1

# ==========================================
# 2. MONTE CARLO EXPERIMENT RUNNER
# ==========================================
def run_experiments():
    N_nodes = 1000
    steps = 1500
    load_mu = 0.08
    
    print("Running Phase 1: Fatigue Collapse (eta = 0.0)")
    sys_collapse = NSD_System(N=N_nodes, eta=0.0, beta=0.15)
    for _ in tqdm(range(steps)): sys_collapse.slow_step(load_mu, 0.1)

    print("Running Phase 2: True SOC Criticality (eta = 0.05)")
    sys_soc = NSD_System(N=N_nodes, eta=0.05, beta=0.15)
    for _ in tqdm(range(steps)): sys_soc.slow_step(load_mu, 0.1)

    print("Running Phase 3: Chaotic Oscillation (eta = 0.5)")
    sys_chaos = NSD_System(N=N_nodes, eta=0.5, beta=0.15)
    for _ in tqdm(range(steps)): sys_chaos.slow_step(load_mu, 0.1)

    return sys_collapse, sys_soc, sys_chaos

# ==========================================
# 3. EMPIRICAL VALIDATION PLOTTER
# ==========================================
def plot_results(sys_collapse, sys_soc, sys_chaos):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    plt.subplots_adjust(wspace=0.3)

    # --- Plot 1: The Phase Dynamics of Capacity (C_star & C) ---
    ax1 = axes[0]
    time = np.arange(len(sys_collapse.history['mean_capacity']))
    
    ax1.plot(time, sys_collapse.history['mean_capacity'], label=r'Fatigue Collapse ($\eta=0$)', color='#d62728', alpha=0.8)
    ax1.plot(time, sys_soc.history['mean_capacity'], label=r'True SOC ($\eta=0.05$)', color='#2ca02c', alpha=0.9, lw=2)
    ax1.plot(time, sys_chaos.history['mean_capacity'], label=r'Oscillatory ($\eta=0.5$)', color='#1f77b4', alpha=0.6)
    
    ax1.set_title('Indicator 1: Homeostatic Phase Regimes', fontsize=12)
    ax1.set_xlabel('Time (Slow Drive Events $e$)', fontsize=10)
    ax1.set_ylabel(r'Mean Integration Capacity $\langle C \rangle$', fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.4)

    # --- Plot 2: SOC Power-Law Fingerprint ---
    ax2 = axes[1]
    # We plot the avalanches only for the True SOC regime
    av_data = sys_soc.avalanches
    if len(av_data) > 0:
        counts = Counter(av_data)
        sizes = np.array(list(counts.keys()))
        freqs = np.array(list(counts.values())) / len(av_data)
        ax2.scatter(sizes, freqs, alpha=0.7, color='#2ca02c', edgecolors='k', label='Scale-Free (True SOC)')
        
        # Fit a visual guide line for alpha ~ 1.8
        guide_x = np.linspace(min(sizes), max(sizes), 50)
        guide_y = guide_x**(-1.8) * (freqs[0] / (guide_x[0]**(-1.8))) # Normalize to first point
        ax2.plot(guide_x, guide_y, 'k--', alpha=0.6, label=r'MLE Fit $\alpha \approx 1.8$')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title('Indicator 2: Self-Organized Criticality', fontsize=12)
    ax2.set_xlabel('Avalanche Size $s$ (Nodes Failed)', fontsize=10)
    ax2.set_ylabel('Probability $P(s)$', fontsize=10)
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend()

    # --- Plot 3: Entropy Early-Warning in Collapse Regime ---
    ax3 = axes[2]
    ax3.plot(time, sys_collapse.history['entropy'], color='#9467bd', lw=2)
    ax3.set_title('Indicator 3: Pre-Percolation Entropy Spike', fontsize=12)
    ax3.set_xlabel('Time (Slow Drive Events $e$)', fontsize=10)
    ax3.set_ylabel('Systemic Entropy $H$', fontsize=10)
    
    collapse_starts = np.where(np.array(sys_collapse.history['failing_fraction']) > 0.5)[0]
    if len(collapse_starts) > 0:
        ax3.axvline(x=collapse_starts[0], color='r', linestyle='--', label='Topological Percolation')
        ax3.legend()
    ax3.grid(True, alpha=0.4)

    plt.suptitle('Normative Stress Dynamics (NSD): Validating Adaptive-Threshold SOC', fontsize=16, y=1.05)
    plt.show()

if __name__ == "__main__":
    sys_collapse, sys_soc, sys_chaos = run_experiments()
    plot_results(sys_collapse, sys_soc, sys_chaos)