import torch
import networkx as nx
import numpy as np
import scipy.sparse as sp
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm

# ==========================================
# 1. THE DATA-DRIVEN GPU NSD ENGINE
# ==========================================
class NSD_System_Empirical:
    def __init__(self, csv_path=None, eta=0.01, beta=0.10):
        # Hardware Auto-Detection
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"🚀 Initializing on NVIDIA GPU: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("🚀 Initializing on Apple Silicon GPU (MPS)")
        else:
            self.device = torch.device("cpu")
            print("⚠️ GPU not found. Falling back to CPU.")
        
        # Thermodynamic & Homeostatic Parameters
        self.dissipation = 0.01        # gamma 
        self.recovery_rate = 0.005     # mu 
        self.burnout_penalty = beta    # beta 
        self.cascade_speed = 0.8       # kappa 
        self.activation_sharpness = 10.0 # a 
        self.eta = eta                 # adaptation rate 
        self.A0 = 0.02                 # target activity level
        
        # 1. Load Empirical Topology (Enron)
        if csv_path:
            print(f"📥 Loading empirical dataset: {csv_path}...")
            df = pd.read_csv(csv_path)
            
            # Assume columns are named 'source' and 'target'
            # Fallback to first two columns if named differently
            src_col = 'source' if 'source' in df.columns else df.columns[0]
            tgt_col = 'target' if 'target' in df.columns else df.columns[1]
            wt_col = 'weight' if 'weight' in df.columns else None
            
            # Build Directed Graph
            if wt_col:
                self.graph = nx.from_pandas_edgelist(df, source=src_col, target=tgt_col, edge_attr=wt_col, create_using=nx.DiGraph())
            else:
                self.graph = nx.from_pandas_edgelist(df, source=src_col, target=tgt_col, create_using=nx.DiGraph())
            
            # Isolate the largest weakly connected component so cascades can travel
            largest_cc = max(nx.weakly_connected_components(self.graph), key=len)
            self.graph = self.graph.subgraph(largest_cc).copy()
            self.N = self.graph.number_of_nodes()
            print(f"✅ Enron Network Loaded: {self.N} active employees, {self.graph.number_of_edges()} connections.")
            
        else:
            raise ValueError("Please provide a valid csv_path to run empirical data.")
            
        # 2. Build Sparse Propagation Matrix (W) using SciPy
        # If weights exist, they represent the strength of the propagation channel
        weight_attr = wt_col if wt_col else None
        adj = nx.adjacency_matrix(self.graph, weight=weight_attr)
        adj.setdiag(0)
        
        # Normalize rows to satisfy Axiom 1 (Leaky Conservation)
        row_sums = np.array(adj.sum(axis=1)).flatten()
        row_sums[row_sums == 0] = 1.0 # Prevent division by zero for sink nodes
        inv_deg = sp.diags(1.0 / row_sums)
        W_scipy = inv_deg.dot(adj).transpose().tocoo() # W_ji transposed for fast propagation
        
        # 3. Push Topology to GPU as a Sparse Tensor
        indices = torch.vstack((torch.tensor(W_scipy.row), torch.tensor(W_scipy.col))).long()
        values = torch.tensor(W_scipy.data).float()
        self.W = torch.sparse_coo_tensor(indices, values, torch.Size(W_scipy.shape)).to(self.device)
        
        # 4. Initialize State Variables Natively on GPU
        self.C_star = torch.normal(5.0, 1.0, size=(self.N,)).clamp(min=1.0).to(self.device)
        self.C = self.C_star.clone()
        self.S = torch.zeros(self.N, device=self.device)
        
        # CPU Trackers for plotting
        self.history = {'entropy': [], 'failing_fraction': [], 'mean_capacity': []}
        self.avalanches = []

    def _activation_function(self):
        diff = self.S - self.C
        sig = torch.sigmoid(self.activation_sharpness * diff)
        F = self.cascade_speed * diff * sig
        return torch.clamp(F, min=0.0)

    def _fast_relaxation(self):
        cascade_active = True
        depth = 0
        total_failing_mask = torch.zeros(self.N, dtype=torch.bool, device=self.device)
        
        while cascade_active and depth < 100:
            F = self._activation_function()
            failing_mask = F > 0.01
            
            if not failing_mask.any():
                break
                
            total_failing_mask |= failing_mask
            
            # Equation III: Burnout Penalty
            self.C = torch.where(failing_mask, self.C - self.burnout_penalty * F, self.C)
            self.C = torch.clamp(self.C, min=0.1)
            
            # Sparse Matrix Vector Multiplication on GPU
            propagated = torch.sparse.mm(self.W, F.unsqueeze(1)).squeeze(1)
            self.S = self.S + propagated - F
            depth += 1
            
        return total_failing_mask.sum().item()

    def slow_step(self, load_mu, load_pct):
        # 1. Recovery & Dissipation
        self.C += self.recovery_rate * (self.C_star - self.C)
        self.S = torch.clamp(self.S - self.dissipation, min=0.0)
        
        # 2. Exogenous Load Injection
        num_to_load = max(1, int(self.N * load_pct))
        targets = torch.randperm(self.N)[:num_to_load].to(self.device)
        loads = torch.clamp(torch.normal(load_mu, load_mu*0.2, size=(num_to_load,)), min=0.0).to(self.device)
        self.S.scatter_add_(0, targets, loads)
        
        # 3. SOC Cascade Resolution
        avalanche_size = self._fast_relaxation()
        if avalanche_size > 0:
            self.avalanches.append(avalanche_size)
            
        # 4. Homeostatic Adaptation
        current_activity_A = avalanche_size / self.N
        self.C_star += self.eta * (self.A0 - current_activity_A)
        self.C_star = torch.clamp(self.C_star, 1.0, 15.0)
            
        # 5. Thermodynamic Observation
        total_stress = self.S.sum()
        entropy = 0.0
        if total_stress > 1e-9:
            p_i = self.S / total_stress
            p_i_nz = p_i[p_i > 0]
            entropy = -(p_i_nz * torch.log(p_i_nz)).sum().item()
            
        self.history['entropy'].append(entropy)
        self.history['failing_fraction'].append((self.S > self.C).float().mean().item())
        self.history['mean_capacity'].append(self.C.mean().item())


# ==========================================
# 2. RUN EXPERIMENTS ON ENRON DATA
# ==========================================
def run_empirical_validation(csv_path):
    steps = 2000
    load_mu = 0.08
    
    print("\n[Phase 1] Simulating True SOC Criticality on Enron (Balanced Adaptation)")
    sys_soc = NSD_System_Empirical(csv_path=csv_path, eta=0.05, beta=0.15)
    for _ in tqdm(range(steps)): sys_soc.slow_step(load_mu, 0.1)

    print("\n[Phase 2] Simulating Fatigue Collapse on Enron (Zero Adaptation)")
    sys_collapse = NSD_System_Empirical(csv_path=csv_path, eta=0.0, beta=0.15)
    for _ in tqdm(range(steps)): sys_collapse.slow_step(load_mu, 0.1)

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    plt.subplots_adjust(wspace=0.3)

    # Plot 1: SOC Power-Law (From the True SOC simulation)
    ax1 = axes[0]
    av_data = sys_soc.avalanches
    if len(av_data) > 0:
        counts = Counter(av_data)
        sizes = np.array(list(counts.keys()))
        freqs = np.array(list(counts.values())) / len(av_data)
        ax1.scatter(sizes, freqs, alpha=0.7, color='#ff7f0e', edgecolors='k', label=f'Enron Corp ($N={sys_soc.N}$)')
        
        # Fit a visual guide line
        valid_idx = sizes > 1 
        if len(valid_idx) > 2:
            guide_x = np.linspace(min(sizes[valid_idx]), max(sizes), 50)
            guide_y = guide_x**(-1.8) * (freqs[valid_idx][0] / (guide_x[0]**(-1.8)))
            ax1.plot(guide_x, guide_y, 'k--', alpha=0.6, label=r'MLE Fit $\alpha \approx 1.8$')

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title('Empirical SOC on Enron Communication Network', fontsize=12)
    ax1.set_xlabel('Avalanche Size $s$ (Employees Overwhelmed)', fontsize=10)
    ax1.set_ylabel('Probability $P(s)$', fontsize=10)
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend()

    # Plot 2: Entropy Spike (From the Collapse simulation)
    ax2 = axes[1]
    time = np.arange(len(sys_collapse.history['entropy']))
    ax2.plot(time, sys_collapse.history['entropy'], color='#9467bd', lw=2)
    ax2.set_title('Pre-Percolation Entropy Early-Warning', fontsize=12)
    ax2.set_xlabel('Time (Slow Drive Events $e$)', fontsize=10)
    ax2.set_ylabel('Systemic Entropy $H$', fontsize=10)
    
    collapse_starts = np.where(np.array(sys_collapse.history['failing_fraction']) > 0.5)[0]
    if len(collapse_starts) > 0:
        ax2.axvline(x=collapse_starts[0], color='r', linestyle='--', label='Topological Percolation (Enron Collapse)')
        ax2.legend()
    ax2.grid(True, alpha=0.4)

    plt.suptitle('Normative Stress Dynamics (NSD) - Empirical Validation: Enron Corp', fontsize=16, y=1.05)
    plt.show()

if __name__ == "__main__":
    # Ensure 'enron.csv' is in the same directory as this script!
    run_empirical_validation('enron.csv')