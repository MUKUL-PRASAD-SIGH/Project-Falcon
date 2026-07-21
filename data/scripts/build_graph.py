import json
import networkx as nx
import os
import argparse

def build_graph(is_real=False):
    if is_real:
        print("Building graph from REAL DataStore / CSV data...")
        # Placeholder for querying real data
        firs = []
        accused = []
    else:
        print("Building graph from DEMO synthetic data...")
        firs_path = os.path.join(os.path.dirname(__file__), 'firs_synthetic.json')
        accused_path = os.path.join(os.path.dirname(__file__), 'accused_synthetic.json')
        
        if not os.path.exists(firs_path) or not os.path.exists(accused_path):
            print("Demo data files not found. Run generate_synthetic.py first.")
            return
            
        with open(firs_path, 'r') as f:
            firs = json.load(f)
            
        with open(accused_path, 'r') as f:
            accused = json.load(f)
            
    G = nx.Graph()
    
    # Add FIR nodes
    for fir in firs:
        G.add_node(f"FIR_{fir['CaseMasterID']}", type="FIR", label=fir.get('CrimeNo', str(fir['CaseMasterID'])))
        
    # Add Accused nodes and edges to FIRs
    for acc in accused:
        acc_node = f"ACC_{acc['AccusedName']}"
        G.add_node(acc_node, type="Accused", label=acc['AccusedName'])
        fir_node = f"FIR_{acc['CaseMasterID']}"
        if G.has_node(fir_node):
            G.add_edge(acc_node, fir_node)
            
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # Export for frontend Cytoscape
    cytoscape_elements = []
    for node, data in G.nodes(data=True):
        cytoscape_elements.append({"data": {"id": node, "label": data.get("label", node), "type": data.get("type", "Unknown")}})
        
    for source, target in G.edges():
        cytoscape_elements.append({"data": {"source": source, "target": target}})
        
    output_path = os.path.join(os.path.dirname(__file__), 'graph_index.json')
    with open(output_path, 'w') as f:
        json.dump(cytoscape_elements, f, indent=2)
        
    print(f"Exported graph index to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Graph Index")
    parser.add_argument('--real', action='store_true', help="Use real DataStore data")
    args = parser.parse_args()
    build_graph(args.real)
