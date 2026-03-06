# enron_runner.py
import pandas as pd
import email
import networkx as nx
import numpy as np
import torch
from collections import Counter
from tqdm import tqdm
import pickle
from nsd_engine import NSD_System

def parse_enron_network(csv_file='emails.csv', max_rows=100000, top_n=1000):
    print(f"Parsing top {max_rows} rows of {csv_file}...")
    
    # Load a chunk of the massive CSV
    df = pd.read_csv(csv_file, nrows=max_rows)
    
    edges = []
    
    for raw_message in tqdm(df['message'], desc="Extracting From/To headers"):
        msg = email.message_from_string(raw_message)
        
        sender = msg['From']
        recipients = msg['To']
        
        if sender and recipients:
            sender = sender.strip().lower()
            # Only track internal Enron communication
            if '@enron.com' not in sender:
                continue
                
            # Split multiple recipients
            for rec in recipients.split(','):
                rec = rec.strip().lower()
                if '@enron.com' in rec:
                    edges.append((sender, rec))
                    
    print(f"Extracted {len(edges)} internal email connections.")
    
    # Keep only the top N most active communicators to match our N=1000 simulation
    print(f"Filtering down to the top {top_n} core Enron employees...")
    node_counts = Counter([node for edge in edges for node in edge])
    top_nodes = set([node for node, count in node_counts.most_common(top_n)])
    
    filtered_edges = [(u, v) for u, v in edges if u in top_nodes and v in top_nodes]
    
    # Build a directed, weighted graph
    G = nx.DiGraph()
    for u, v in filtered_edges:
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1.0
        else:
            G.add_edge(u, v, weight=1.0)
            
    print(f"Enron Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return G

def run_enron_collapse(G):
    print("Initializing NSD Engine with Enron Topology...")
    
    # Get the raw adjacency matrix from the NetworkX graph
    adj = nx.to_numpy_array(G, nodelist=list(G.nodes()), weight='weight')
    N = adj.shape[0]
    
    # Initialize the system (we use 'custom' to skip the random graph generation)
    sys = NSD_System(N=N, topology='custom')
    
    # Normalize the Enron adjacency matrix to create the W propagation matrix
    np.fill_diagonal(adj, 0)
    row_sums = adj.sum(axis=1)
    with np.errstate(divide='ignore', invalid='ignore'):
        row_sums_inv = np.nan_to_num(1.0 / row_sums, posinf=0.0)
    W_np = (adj * row_sums_inv[:, np.newaxis]).T
    
    # Push the Enron topology to the GPU/CPU Engine
    W_tensor = torch.tensor(W_np, dtype=torch.float32)
    sys.W = W_tensor.to_sparse().to(sys.device)
    
    # Run the Hysteresis / Collapse experiment
    load_profile = list(np.linspace(0.01, 0.80, 800)) + list(np.linspace(0.80, 0.01, 800))
    load_pct = 0.10
    
    print("Injecting thermodynamic stress into Enron Corporation...")
    for load_mu in tqdm(load_profile):
        sys.slow_step(load_mu, load_pct)
        
    return sys

if __name__ == "__main__":
    # 1. Parse Enron emails
    enron_graph = parse_enron_network(csv_file='emails.csv', max_rows=100000, top_n=1000)
    
    # 2. Run the collapse simulation
    enron_sys = run_enron_collapse(enron_graph)
    
    # 3. Save for the plotter
    data = {
        'history': enron_sys.history,
        'avalanches_sf': enron_sys.avalanches,  # We hijack this variable for Enron's avalanches
        'avalanches_er': []                     # Empty because we aren't comparing to random
    }
    with open('nsd_data.pkl', 'wb') as f:
        pickle.dump(data, f)
        
    print("Enron collapse simulation complete! Run `python plotter.py` to view.")