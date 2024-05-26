import networkx as nx

# Sample preference data (replace with your actual data)
data = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")]


# Function to create the NetworkX DiGraph with decay factor (optional)
def create_preference_graph(data, decay=1.0):
    """
    Creates a NetworkX DiGraph from preference data with optional decay factor.

    Args:
        data: List of tuples representing preferences (image A preferred to image B).
        decay: Optional decay factor (0 to 1) to down-weight older preferences.

    Returns:
        A NetworkX DiGraph representing the image preference relationships.
    """
    G = nx.DiGraph()
    for pref in data:
        source, target = pref
        weight = decay  # Initial weight with decay applied
        if source in G and target in G:  # Check if source node already exists
            # Adjust weight based on existing edge and decay
            if G.get_edge_data(source, target) is not None:
                weight = max(weight, G.get_edge_data(source, target).get('weight', 0) * decay)
        G.add_edge(source, target, weight=weight)
    return G


# Create the preference graph (optional decay factor of 0.9)
G = create_preference_graph(data, decay=0.9)

# Choose a ranking algorithm
# Option 1: Topological Sort (works for acyclic graphs - no cycles)
# ranking = nx.topological_sort(G)

# Option 2: PageRank (works for cyclic graphs)
#ranking = nx.pagerank_centrality(G)
ranking = nx.pagerank(G)

# Interpret ranking (assuming node name corresponds to image ID)
print("Ranked image order:", ranking)
