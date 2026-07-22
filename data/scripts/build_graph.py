import os
import json
import pandas as pd
import networkx as nx

# Load preprocessed graph features from Feature Store
FEATURE_STORE_BASE = os.path.join(os.path.dirname(__file__), '..', 'feature_store')
with open(os.path.join(FEATURE_STORE_BASE, 'latest.txt'), 'r') as f:
    latest_version = f.read().strip()
store_dir = os.path.join(FEATURE_STORE_BASE, latest_version)

NODES_PARQUET = os.path.join(store_dir, 'graph_nodes.parquet')
EDGES_PARQUET = os.path.join(store_dir, 'graph_edges.parquet')

def load_graph_data():
    nodes_df = pd.read_parquet(NODES_PARQUET)
    edges_df = pd.read_parquet(EDGES_PARQUET)
    return nodes_df, edges_df

def build_network():
    nodes_df, edges_df = load_graph_data()
    
    print(f"Building Criminal Network from Feature Store (v: {latest_version})")
    
    # Initialize graph
    G = nx.Graph()
    
    # Add nodes
    for _, row in nodes_df.iterrows():
        node_id = int(row['node_id']) if pd.notnull(row['node_id']) else 0
        age = int(row['AgeYear']) if pd.notnull(row['AgeYear']) else 0
        G.add_node(node_id, name=str(row['name']), age=age, risk=0.5)
        
    # Add edges
    for _, row in edges_df.iterrows():
        source = int(row['source'])
        target = int(row['target'])
        weight = int(row['weight'])
        G.add_edge(source, target, weight=weight)
        
    print(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # Convert to JSON for D3.js or similar
    data = nx.node_link_data(G)
    
    out_file = os.path.join(os.path.dirname(__file__), "graph_index.json")
    with open(out_file, 'w') as f:
        json.dump(data, f)
        
    print(f"Saved graph index to {out_file}")

if __name__ == "__main__":
    build_network()
