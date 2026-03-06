# experiment_runner.py
from nsd_engine import NSD_System
from tqdm import tqdm
import pickle

def run_hysteresis_experiment(N=1000):
    print("Initializing Scale-Free NSD System...")
    sys = NSD_System(N=N, topology='scale-free')
    
    # We will ramp load_mu up, then down to prove hysteresis
    # Crank up peak load_mu to 0.8 to ensure we cross rho = 1
    load_profile = list(np.linspace(0.01, 0.80, 800)) + list(np.linspace(0.80, 0.01, 800))
    load_pct = 0.10
    
    print("Running slow-drive events...")
    for load_mu in tqdm(load_profile):
        sys.slow_step(load_mu, load_pct)
        
    return sys

def run_soc_comparison(N=1000, steps=2000):
    print("Running Scale-Free vs Random SOC Avalanches...")
    sys_sf = NSD_System(N=N, topology='scale-free')
    sys_er = NSD_System(N=N, topology='random')
    
    # Drive systems deep into the critical regime
    for _ in tqdm(range(steps), desc="Scale-Free"):
        sys_sf.slow_step(load_mu=0.55, load_pct=0.1)
    for _ in tqdm(range(steps), desc="Random (ER)"):
        sys_er.slow_step(load_mu=0.55, load_pct=0.1)
        
    return sys_sf.avalanches, sys_er.avalanches

if __name__ == "__main__":
    import numpy as np # Ensure numpy is available for linspace
    
    # 1. Run Hysteresis & Entropy Track
    main_sys = run_hysteresis_experiment(N=2500)
    
    # 2. Run SOC cascades
    avalanches_sf, avalanches_er = run_soc_comparison(N=2500, steps=3000)
    
    # Save data for the plotter
    data = {
        'history': main_sys.history,
        'avalanches_sf': avalanches_sf,
        'avalanches_er': avalanches_er
    }
    with open('nsd_data.pkl', 'wb') as f:
        pickle.dump(data, f)
    print("Experiments complete. Run plotter.py to view results.")