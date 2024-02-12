import json
import sys

######################
# Network Topology Representation
# Key-Value Pairs: In the dictionary neighbors, each key-value pair represents a node 
# and its directly connected neighbors within the network. 
# The key is the unique identifier (ID) of a node, and the value is a list of IDs 
# representing the neighbors of that node.
#
# Significance in Decentralized Systems
# 1. Data Exchange: This topology dictates how data (such as model updates, gradients, or any other information) 
#    is exchanged in the decentralized system. For instance, when performing decentralized SGD updates, Node 0 
#    would share its updates with Nodes 1 and 2, and similarly, Nodes 1 and 2 would share their updates 
#    with their respective neighbors.
# 2. Decentralized Decision Making: The network topology influences the process of aggregating information from 
#    various nodes to make decisions or update models in a decentralized manner. Each node only communicates with 
#    its neighbors, ensuring that the system operates without a central authority.
# 3. Scalability and Fault Tolerance: By defining which nodes are connected to which others, the system can be made 
#    more scalable and fault-tolerant. If a node goes offline, the rest of the network can continue to function, 
#    albeit with potentially reduced capacity or efficiency depending on the node's role in the network topology.
######################

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