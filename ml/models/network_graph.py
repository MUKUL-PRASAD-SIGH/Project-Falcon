import os
import json
import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
RAW_FIRS = DATA_SCRIPTS_DIR / "firs_synthetic.json"
RAW_ACCUSED = DATA_SCRIPTS_DIR / "accused_synthetic.json"
PROCESSED_CSV = BASE_DIR / "data" / "processed" / "accused_features.csv"

OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
SCRIPTS_OUT = BASE_DIR / "ml" / "scripts"

class CriminalNetworkGraph:
    def __init__(self):
        self.G = nx.Graph()
        self.communities = []
        self.pagerank_scores = {}
        self.nodes_data = {}

    def build_graph(self):
        print("Loading data for NetworkX Criminal Graph...")
        with open(RAW_ACCUSED, 'r') as f:
            accused_data = json.load(f)
            
        accused_df = pd.DataFrame(accused_data)
        
        # Load risk features if available
        features_df = None
        if PROCESSED_CSV.exists():
            features_df = pd.read_csv(PROCESSED_CSV)
            
        # Add Nodes
        for _, row in accused_df.iterrows():
            aid = int(row['AccusedMasterID'])
            name = str(row['AccusedName'])
            
            # Lookup risk score
            risk_score = 50.0
            if features_df is not None and not features_df[features_df['AccusedMasterID'] == aid].empty:
                risk_score = float(features_df[features_df['AccusedMasterID'] == aid]['risk_score'].iloc[0])
                
            self.G.add_node(aid, name=name, risk_score=risk_score, person_id=str(row.get('PersonID', '')))
            self.nodes_data[aid] = {
                "id": aid,
                "name": name,
                "risk_score": risk_score
            }
            
        # Add Edges (Shared CaseMasterID)
        acc_case = accused_df[['AccusedMasterID', 'CaseMasterID']].dropna()
        merged_edges = pd.merge(acc_case, acc_case, on='CaseMasterID', suffixes=('_1', '_2'))
        filtered_edges = merged_edges[merged_edges['AccusedMasterID_1'] < merged_edges['AccusedMasterID_2']]
        
        edge_counts = filtered_edges.groupby(['AccusedMasterID_1', 'AccusedMasterID_2']).size().reset_index(name='weight')
        
        for _, row in edge_counts.iterrows():
            u = int(row['AccusedMasterID_1'])
            v = int(row['AccusedMasterID_2'])
            w = int(row['weight'])
            self.G.add_edge(u, v, weight=w)
            
        print(f"Graph built with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges.")
        
        # Community Detection (Louvain or fallback)
        self._detect_communities()
        # PageRank calculation
        self._calculate_pagerank()
        
        self.export_graph_data()
        return self

    def _detect_communities(self):
        print("Running Louvain Community Detection...")
        try:
            communities = list(nx.community.louvain_communities(self.G, weight='weight', seed=42))
        except Exception:
            # Fallback for disconnected components / networkx versions
            communities = list(nx.community.greedy_modularity_communities(self.G, weight='weight'))
            
        self.communities = communities
        print(f"Detected {len(communities)} criminal communities/gangs.")
        
        for comm_id, node_set in enumerate(communities):
            for node in node_set:
                self.G.nodes[node]['community'] = comm_id
                if node in self.nodes_data:
                    self.nodes_data[node]['community'] = comm_id

    def _calculate_pagerank(self):
        print("Computing PageRank key actor rankings...")
        if self.G.number_of_nodes() > 0:
            self.pagerank_scores = nx.pagerank(self.G, weight='weight')
            for node, rank in self.pagerank_scores.items():
                self.G.nodes[node]['pagerank'] = round(float(rank), 5)
                if node in self.nodes_data:
                    self.nodes_data[node]['pagerank'] = round(float(rank), 5)

    def get_subgraph(self, accused_id: int, depth: int = 2):
        if not self.G.has_node(accused_id):
            # Fallback to first node if given accused_id is not in graph
            nodes = list(self.G.nodes())
            if not nodes:
                return {"nodes": [], "edges": []}
            accused_id = nodes[0]
            
        # Ego graph radius = depth
        ego_G = nx.ego_graph(self.G, accused_id, radius=depth)
        
        nodes_res = []
        for n in ego_G.nodes():
            node_attr = self.G.nodes[n]
            # Determine if key actor / leader (top PageRank in ego network)
            is_leader = (n == accused_id) or (node_attr.get('pagerank', 0) > 0.005)
            nodes_res.append({
                "id": str(n),
                "accused_id": n,
                "name": node_attr.get('name', f"Accused #{n}"),
                "risk_score": node_attr.get('risk_score', 50.0),
                "community": node_attr.get('community', 0),
                "pagerank": node_attr.get('pagerank', 0.001),
                "is_leader": is_leader
            })
            
        edges_res = []
        for u, v, data in ego_G.edges(data=True):
            edges_res.append({
                "source": str(u),
                "target": str(v),
                "weight": data.get('weight', 1)
            })
            
        return {
            "center_accused_id": accused_id,
            "community_id": self.G.nodes[accused_id].get('community', 0),
            "total_nodes": len(nodes_res),
            "total_edges": len(edges_res),
            "nodes": nodes_res,
            "edges": edges_res
        }

    def export_graph_data(self):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
        
        # Pick node with maximum degree or connections for sample subgraph export
        degrees = dict(self.G.degree())
        top_node = max(degrees, key=degrees.get) if degrees else 1
        
        sample_subgraph = self.get_subgraph(top_node, depth=2)
        
        # Export sample subgraph
        with open(OUTPUTS_DIR / "sample_subgraph.json", 'w') as f:
            json.dump(sample_subgraph, f, indent=2)
        with open(SCRIPTS_OUT / "sample_subgraph.json", 'w') as f:
            json.dump(sample_subgraph, f, indent=2)
            
        # Export gang communities overview
        gang_summary = []
        for comm_id, node_set in enumerate(self.communities):
            members = [self.nodes_data[n] for n in node_set if n in self.nodes_data]
            members_sorted = sorted(members, key=lambda x: x.get('pagerank', 0), reverse=True)
            leader = members_sorted[0]['name'] if members_sorted else "Unknown"
            
            gang_summary.append({
                "community_id": comm_id,
                "member_count": len(node_set),
                "key_leader": leader,
                "avg_risk_score": round(np.mean([m['risk_score'] for m in members]), 1) if members else 50.0,
                "top_members": members_sorted
            })
            
        with open(OUTPUTS_DIR / "gang_network.json", 'w') as f:
            json.dump(gang_summary, f, indent=2)
        with open(SCRIPTS_OUT / "gang_network.json", 'w') as f:
            json.dump(gang_summary, f, indent=2)
            
        print(f"Exported sample_subgraph.json and gang_network.json successfully.")

def build_network_model():
    model = CriminalNetworkGraph()
    model.build_graph()
    print("\n[NETWORK GRAPH MODEL DONE]")
    return model

if __name__ == "__main__":
    build_network_model()
