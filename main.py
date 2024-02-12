import time
import logging
import os
from blockchain import Blockchain
from node import Node
import threading
import tensorflow as tf
import numpy as np

# Suppress TensorFlow logging except for errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Number of nodes in the decentralized system
num_nodes = 5

# All processes will run cyclically
run_period = 5 # seconds

# Function to generate mock data for each node
def generate_mock_data(num_nodes, data_size=100, features=10):
    # Returns a dictionary with node_id as keys and randomly generated data as values
    return {node_id: np.random.randn(data_size, features) for node_id in range(num_nodes)}

def create_and_start_threads(blockchain, num_nodes):
    threads = []
    data = generate_mock_data(num_nodes)

    # Check for GPU availability and configure TensorFlow to use GPU
    use_gpu = tf.config.list_physical_devices('GPU')
    
    # Configure TensorFlow to use only specified GPU and limit memory
    if use_gpu:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                use_gpu[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024*num_nodes)])
        except RuntimeError as e:
            print(e)

    # Create and start a thread for each node
    for node_id in range(num_nodes):
        node = Node(node_id, blockchain, data[node_id], run_period) # Create a Node object
        thread = threading.Thread(target=node.run, args=(use_gpu,)) # Initialize thread for the node
        threads.append(thread) # Add thread to the list
        thread.start() # Start the thread

    # Wait for all threads to complete (optional)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Configure logging for the application. Use a more meaningful format for the log file name
    logging.basicConfig(filename=f"logs/node_activity_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.INFO)
    
    # Initialize the blockchain object
    blockchain = Blockchain()

    # Create and start threads for each node
    create_and_start_threads(blockchain, num_nodes)