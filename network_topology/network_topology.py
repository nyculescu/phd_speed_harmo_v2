import json
import sys

# Function to load network topology from a JSON file
def load_network_topology(file_path):
    with open(file_path, 'r') as f:
        topology = json.load(f)
    # Convert string keys to integers, as JSON keys are always strings
    topology = {int(node): neighbors for node, neighbors in topology.items()}
    return topology

def check_topology_consistency(neighbors):
    """
    Checks if the network topology is consistent.
    For every pair of nodes (A, B), if A considers B a neighbor,
    then B should also consider A a neighbor.
    
    Parameters:
    - neighbors: A dictionary where keys are node IDs and values are lists of neighbor node IDs.
    
    Returns:
    - consistency: True if the topology is consistent, False otherwise.
    """
    consistency = True
    inconsistencies = []  # List to hold inconsistency messages

    for node, node_neighbors in neighbors.items():
        for neighbor in node_neighbors:
            # First, check if the neighbor is defined in the neighbors dictionary
            if neighbor not in neighbors:
                message = f"Node {neighbor}, listed as a neighbor of Node {node}, is not defined in the network."
                inconsistencies.append(message)
                consistency = False
                continue  # Skip further checks for this undefined neighbor
            
            # Then, check if the current node is listed in its neighbor's list of neighbors
            if node not in neighbors[neighbor]:
                message = f"Inconsistency found: Node {neighbor} does not list Node {node} as a neighbor."
                inconsistencies.append(message)
                consistency = False

    return consistency, inconsistencies

def load_and_check_network_topology():
    # Define the path to the JSON file
    file_path = 'network_topology/network_topology.json'

    # Load the network topology
    network_topology = load_network_topology(file_path)
    print(f"Loaded Network Topology: {network_topology}")

    # Check the consistency of the network topology
    is_consistent, inconsistencies = check_topology_consistency(network_topology)
    print(f"Topology is consistent: {is_consistent}")
    if not is_consistent:
        print("Inconsistencies found:")
        for inconsistency in inconsistencies:
            print(inconsistency)
        sys.exit()
    else:
        return network_topology