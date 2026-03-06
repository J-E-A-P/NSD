# nsd_engine.py
import torch
import numpy as np
import networkx as nx

class NSD_System:
    def __init__(self, N=1000, topology='scale-free', m=3, p=0.006):
        self.N = N
        self.tick = 0
        
        # Hardware auto-detection: NVIDIA (CUDA), Apple Silicon (MPS), or CPU
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        
        print(f"Initializing NSD Engine on device: {self.device}")
        
        # Hyperparameters
        self.capacity_mu = 5.0
        self.dissipation = 0.01
        self.recovery_rate = 0.005
        self.burnout_penalty = 0.10
        self.cascade_speed = 0.8
        self.activation_sharpness = 10.0
        
        # Initialize Topology (CPU-bound generation)
        if topology == 'scale-free':
            self.graph = nx.barabasi_albert_graph(N, m)
            adj = nx.to_numpy_array(self.graph)
        elif topology == 'random':
            self.graph = nx.erdos_renyi_graph(N, p)
            adj = nx.to_numpy_array(self.graph)
        elif topology == 'custom':
            self.graph = None
            # Create a dummy matrix so __init__ can finish safely 
            # (enron_runner.py will overwrite this immediately)
            adj = np.zeros((N, N)) 
            
        # Adjacency and Propagation Matrix (W)
        np.fill_diagonal(adj, 0)
        row_sums = adj.sum(axis=1)
        with np.errstate(divide='ignore', invalid='ignore'):
            row_sums_inv = np.nan_to_num(1.0 / row_sums, posinf=0.0)
        W_np = (adj * row_sums_inv[:, np.newaxis]).T # W_ji
        
        # Convert W to a PyTorch SPARSE tensor and send to GPU/CPU
        W_tensor = torch.tensor(W_np, dtype=torch.float32)
        self.W = W_tensor.to_sparse().to(self.device)
        
        # State Variables (Sent to GPU)
        c_base_np = np.maximum(1.0, np.random.normal(self.capacity_mu, 1.0, N))
        self.C_baseline = torch.tensor(c_base_np, dtype=torch.float32, device=self.device)
        self.C = self.C_baseline.clone()
        self.S = torch.zeros(N, dtype=torch.float32, device=self.device)
        
        # Trackers (Kept on CPU memory)
        self.history = {'entropy': [], 'failing_fraction': [], 'mean_capacity': [], 'rho': []}
        self.avalanches = []

    def _activation_function(self):
        """Smooth SiLU/Softplus approximation of max(0, S-C) executing on GPU"""
        diff = self.S - self.C
        sig = 1.0 / (1.0 + torch.exp(-self.activation_sharpness * diff))
        F = self.cascade_speed * diff * sig
        return torch.clamp(F, min=0.0)

    def _fast_relaxation(self):
        """The SOC topological cascade loop (Fast Time) executing on GPU"""
        cascade_active = True
        nodes_involved_in_avalanche = set()
        max_depth = 100 
        depth = 0
        
        while cascade_active and depth < max_depth:
            F = self._activation_function()
            failing_mask = F > 0.01
            
            if not failing_mask.any():
                cascade_active = False
                break
                
            # Pull just the indices back to CPU briefly to track unique failing nodes
            failing_indices = failing_mask.nonzero(as_tuple=False).flatten().cpu().numpy()
            nodes_involved_in_avalanche.update(failing_indices)
            
            # Apply burnout penalty
            self.C = self.C - (self.burnout_penalty * F)
            self.C = torch.clamp(self.C, min=0.1) 
            
            # Propagate via sparse matrix multiplication
            # PyTorch sparse.mm requires a 2D tensor, so we reshape F to (N, 1) then back
            F_2d = F.unsqueeze(1)
            propagated = torch.sparse.mm(self.W, F_2d).squeeze(1)
            
            self.S = self.S + propagated - F
            depth += 1
            
        return len(nodes_involved_in_avalanche)

    def slow_step(self, load_mu, load_pct):
        """The exogenous event loop (Slow Time) executing on GPU"""
        # 1. Recovery & Dissipation
        self.C = self.C + self.recovery_rate * (self.C_baseline - self.C)
        self.S = torch.clamp(self.S - self.dissipation, min=0.0)
        
        # 2. Exogenous Load Injection
        num_to_load = max(1, int(self.N * load_pct))
        targets = torch.randperm(self.N, device=self.device)[:num_to_load]
        
        load = torch.empty(num_to_load, device=self.device).normal_(mean=load_mu, std=load_mu*0.2)
        load = torch.clamp(load, min=0.0)
        self.S[targets] += load
        
        # 3. SOC Cascade Resolution
        avalanche_size = self._fast_relaxation()
        if avalanche_size > 0:
            self.avalanches.append(avalanche_size)
            
        # 4. Record State (Pull scalar metrics back to CPU)
        total_stress = self.S.sum().item()
        entropy = 0.0
        if total_stress > 1e-9:
            p_i = self.S / total_stress
            p_i_nz = p_i[p_i > 0]
            entropy = -(p_i_nz * torch.log(p_i_nz)).sum().item()
            
        self.history['entropy'].append(entropy)
        self.history['failing_fraction'].append((self.S > self.C).float().mean().item())
        mean_cap = self.C.mean().item()
        self.history['mean_capacity'].append(mean_cap)
        
        # Calculate rho (Load / Capacity ratio)
        avg_load_injected = (load_mu * load_pct) / self.dissipation
        rho = avg_load_injected / mean_cap
        self.history['rho'].append(rho)
        
        self.tick += 1