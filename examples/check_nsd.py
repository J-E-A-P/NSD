import torch
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

print(f"Torch version: {torch.__version__}")
print(f"NetworkX version: {nx.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

# Quick test of a Barabási-Albert graph
G = nx.barabasi_albert_graph(100, 3)
print(f"Test Graph Nodes: {len(G.nodes())}, Edges: {len(G.edges())}")