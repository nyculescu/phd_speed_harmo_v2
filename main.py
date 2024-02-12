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

    # Configure GPU usage based on availability
    use_gpu = tf.config.list_physical_devices('GPU')
    
    # Configure TensorFlow to use only specified GPU and limit memory
    if use_gpu:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                use_gpu[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024*num_nodes)])
        except RuntimeError as e:
            print(e)

    # Create and start threads
    for node_id in range(num_nodes):
        node = Node(node_id, blockchain, data[node_id], run_period)
        thread = threading.Thread(target=node.run, args=(use_gpu,))
        threads.append(thread)
        thread.start()

    # Optionally wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Use a more meaningful format for the log file name
    logging.basicConfig(filename=f"logs/node_activity_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.INFO)
    blockchain = Blockchain()
    create_and_start_threads(blockchain, num_nodes)