import pandas as pd

def extract_graph_features(df_firs: pd.DataFrame, df_accused: pd.DataFrame):
    """
    Extracts Node List and Edge List for Criminal Network Analysis.
    Returns (nodes_df, edges_df).
    - Nodes: Accused individuals (NodeID, Name, RiskScore (placeholder))
    - Edges: Shared CaseMasterID between two accused individuals.
    """
    # Nodes
    nodes_df = df_accused[['AccusedMasterID', 'AccusedName', 'PersonID', 'AgeYear']].copy()
    nodes_df = nodes_df.rename(columns={'AccusedMasterID': 'node_id', 'AccusedName': 'name'})
    nodes_df = nodes_df.drop_duplicates(subset=['node_id'])
    
    # Edges - find all pairs of accused in the same case
    # This requires a self-join on CaseMasterID
    acc_case = df_accused[['AccusedMasterID', 'CaseMasterID']].dropna()
    
    # Merge on CaseMasterID to find co-accused
    edges = pd.merge(acc_case, acc_case, on='CaseMasterID', suffixes=('_1', '_2'))
    
    # Remove self-loops (where AccusedMasterID_1 == AccusedMasterID_2)
    edges = edges[edges['AccusedMasterID_1'] < edges['AccusedMasterID_2']]
    
    # Group by pairs to get edge weights (number of shared cases)
    edges_df = edges.groupby(['AccusedMasterID_1', 'AccusedMasterID_2']).size().reset_index(name='weight')
    
    edges_df = edges_df.rename(columns={
        'AccusedMasterID_1': 'source',
        'AccusedMasterID_2': 'target'
    })
    
    print(f"[PREPARE_GRAPH] Extracted {len(nodes_df)} nodes and {len(edges_df)} edges.")
    return nodes_df, edges_df
