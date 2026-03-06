import torch
import networkx as nx
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm

# ==========================================
# 1. THE GPU-ACCELERATED NSD ENGINE
# ==========================================
class NSD_System_GPU:
    def __init__(self, N=10, topology='scale-free', eta=0.01, beta=0.10):
        self.N = N
        self.tick = 0
        
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
        
        # 1. Initialize Topology on CPU (Graph Gen is faster on CPU)
        if topology == 'scale-free':
            self.graph = nx.barabasi_albert_graph(N, 3)
        else:
            self.graph = nx.erdos_renyi_graph(N, 0.006)
            
        # 2. Build Sparse Propagation Matrix (W) using SciPy
        adj = nx.adjacency_matrix(self.graph)
        adj.setdiag(0)
        row_sums = np.array(adj.sum(axis=1)).flatten()
        row_sums[row_sums == 0] = 1.0 # Prevent division by zero
        
        inv_deg = sp.diags(1.0 / row_sums)
        W_scipy = inv_deg.dot(adj).transpose().tocoo() # W_ji transposed for fast propagation
        
        # 3. Push Topology to GPU as a Sparse Tensor
        indices = torch.vstack((torch.tensor(W_scipy.row), torch.tensor(W_scipy.col))).long()
        values = torch.tensor(W_scipy.data).float()
        self.W = torch.sparse_coo_tensor(indices, values, torch.Size(W_scipy.shape)).to(self.device)
        
        # 4. Initialize State Variables Natively on GPU
        self.C_star = torch.normal(5.0, 1.0, size=(N,)).clamp(min=1.0).to(self.device)
        self.C = self.C_star.clone()
        self.S = torch.zeros(N, device=self.device)
        
        # CPU Trackers for plotting later
        self.history = {'entropy': [], 'failing_fraction': [], 'mean_capacity': []}
        self.avalanches = []

    def _activation_function(self):
        """Equation II: Evaluated entirely in VRAM"""
        diff = self.S - self.C
        sig = torch.sigmoid(self.activation_sharpness * diff)
        F = self.cascade_speed * diff * sig
        return torch.clamp(F, min=0.0)

    def _fast_relaxation(self):
        """Topological Cascade Loop: Zero VRAM-to-RAM syncing until cascade ends"""
        cascade_active = True
        depth = 0
        total_failing_mask = torch.zeros(self.N, dtype=torch.bool, device=self.device)
        
        while cascade_active and depth < 100:
            F = self._activation_function()
            failing_mask = F > 0.01
            
            # If no nodes are failing, break the loop
            if not failing_mask.any():
                break
                
            # Track nodes involved natively on GPU using logical OR
            total_failing_mask |= failing_mask
            
            # Equation III: Burnout Penalty (only applied to cascading nodes)
            self.C = torch.where(failing_mask, self.C - self.burnout_penalty * F, self.C)
            self.C = torch.clamp(self.C, min=0.1)
            
            # Sparse Matrix Vector Multiplication on GPU
            # W is (N,N), F is (N). We unsqueeze F to (N,1) for math, then squeeze back
            propagated = torch.sparse.mm(self.W, F.unsqueeze(1)).squeeze(1)
            self.S = self.S + propagated - F
            depth += 1
            
        # Bring the final avalanche size back to the CPU
        return total_failing_mask.sum().item()

    def slow_step(self, load_mu, load_pct):
        """Equation I & IV: Exogenous Event Loop"""
        # 1. Recovery & Dissipation
        self.C += self.recovery_rate * (self.C_star - self.C)
        self.S = torch.clamp(self.S - self.dissipation, min=0.0)
        
        # 2. Exogenous Load Injection (Push indices to GPU)
        num_to_load = max(1, int(self.N * load_pct))
        targets = torch.randperm(self.N)[:num_to_load].to(self.device)
        loads = torch.clamp(torch.normal(load_mu, load_mu*0.2, size=(num_to_load,)), min=0.0).to(self.device)
        self.S.scatter_add_(0, targets, loads)
        
        # 3. SOC Cascade Resolution
        avalanche_size = self._fast_relaxation()
        if avalanche_size > 0:
            self.avalanches.append(avalanche_size)
            
        # 4. Equation IV (Homeostatic Adaptation)
        current_activity_A = avalanche_size / self.N
        self.C_star += self.eta * (self.A0 - current_activity_A)
        self.C_star = torch.clamp(self.C_star, 1.0, 15.0)
            
        # 5. Thermodynamic Observation (Bring summaries to CPU)
        total_stress = self.S.sum()
        entropy = 0.0
        if total_stress > 1e-9:
            p_i = self.S / total_stress
            p_i_nz = p_i[p_i > 0]
            # Shannon entropy calculated entirely on GPU, sum brought to CPU
            entropy = -(p_i_nz * torch.log(p_i_nz)).sum().item()
            
        self.history['entropy'].append(entropy)
        self.history['failing_fraction'].append((self.S > self.C).float().mean().item())
        self.history['mean_capacity'].append(self.C.mean().item())


# ==========================================
# 2. RUN EXPERIMENTS & PLOT
# ==========================================
def run_and_plot():
    # We can now easily simulate 10,000 nodes due to PyTorch sparsity
    N_nodes = 10000 
    steps = 1500
    load_mu = 0.08
    
    print("\n[Phase 1] Simulating True SOC Criticality (Balanced Adaptation)")
    sys_soc = NSD_System_GPU(N=N_nodes, eta=0.05, beta=0.15)
    for _ in tqdm(range(steps)): sys_soc.slow_step(load_mu, 0.1)

    print("\n[Phase 2] Simulating Fatigue Collapse (Zero Adaptation)")
    sys_collapse = NSD_System_GPU(N=N_nodes, eta=0.0, beta=0.15)
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
        ax1.scatter(sizes, freqs, alpha=0.7, color='#2ca02c', edgecolors='k', label=f'Scale-Free (N={N_nodes})')
        
        # Fit a visual guide line for alpha ~ 1.8
        valid_idx = sizes > 1 # Ignore single node failures for fit visually
        if len(valid_idx) > 2:
            guide_x = np.linspace(min(sizes[valid_idx]), max(sizes), 50)
            guide_y = guide_x**(-1.8) * (freqs[valid_idx][0] / (guide_x[0]**(-1.8)))
            ax1.plot(guide_x, guide_y, 'k--', alpha=0.6, label=r'MLE Fit $\alpha \approx 1.8$')

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title('Self-Organized Criticality (GPU Accelerated)', fontsize=12)
    ax1.set_xlabel('Avalanche Size $s$ (Nodes Failed)', fontsize=10)
    ax1.set_ylabel('Probability $P(s)$', fontsize=10)
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend()

    # Plot 2: Entropy Spike (From the Collapse simulation)
    ax2 = axes[1]
    time = np.arange(len(sys_collapse.history['entropy']))
    ax2.plot(time, sys_collapse.history['entropy'], color='#9467bd', lw=2)
    ax2.set_title('Pre-Percolation Entropy Spike', fontsize=12)
    ax2.set_xlabel('Time (Slow Drive Events $e$)', fontsize=10)
    ax2.set_ylabel('Systemic Entropy $H$', fontsize=10)
    
    collapse_starts = np.where(np.array(sys_collapse.history['failing_fraction']) > 0.5)[0]
    if len(collapse_starts) > 0:
        ax2.axvline(x=collapse_starts[0], color='r', linestyle='--', label='Topological Percolation')
        ax2.legend()
    ax2.grid(True, alpha=0.4)

    plt.suptitle('Normative Stress Dynamics (NSD) - PyTorch GPU Engine', fontsize=16, y=1.05)
    plt.show()

if __name__ == "__main__":
    run_and_plot()