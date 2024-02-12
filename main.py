import threading
import time
import numpy as np
import tensorflow as tf
import logging
import os

# Suppress TensorFlow logging except for errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

num_nodes = 5

class Node:
    def __init__(self, node_id, blockchain):
        self.node_id = node_id
        self.blockchain = blockchain
        self.logger = logging.getLogger(f"Node {node_id}")
        self.logger.addHandler(logging.StreamHandler())  # Add console output
        self.logger.addHandler(logging.FileHandler(f"node_{node_id}.log"))  # Add file logging

    def compute(self, use_gpu):
        """
        Performs computations based on GPU availability.

        Args:
            use_gpu (bool): Flag indicating whether to use GPU.

        Returns:
            float: The result of the computation.
        """

        if use_gpu:
            try:
                data = tf.random.normal((1000, 1000))  # Example data
                result = tf.reduce_mean(data).numpy()
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - GPU {self.node_id} result: {result}")
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during GPU {self.node_id} computation", exc_info=e)
                result = None  # Handle errors gracefully
        else:
            try:
                data = np.random.randn(1000, 1000)
                result = data.mean()
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - CPU {self.node_id} result: {result}")
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during CPU {self.node_id} computation", exc_info=e)
                result = None  # Handle errors gracefully

        return result

    def run(self, use_gpu):
        while True:
            result = self.compute(use_gpu)
            if result is not None:
                # Process or utilize the result (replace with your application logic)
                pass

            time.sleep(5)

class Blockchain:
    def __init__(self):
        # Replace with an appropriate data structure and access control mechanisms
        self.chain = []

    def add_block(self, data):
        # Implement secure and synchronized block addition logic
        pass


def create_and_start_threads(blockchain):
    threads = []

    # Configure GPU usage based on availability
    use_gpu = tf.config.list_physical_devices('GPU')

    # Create and start threads
    for node_id in range(num_nodes):
        node = Node(node_id, blockchain)
        thread = threading.Thread(target=node.run, args=(use_gpu,))
        threads.append(thread)
        thread.start()

    # Optionally wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # Use a more meaningful format for the log file name
    logging.basicConfig(filename=f"node_activity_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.INFO)
    blockchain = Blockchain()
    create_and_start_threads(blockchain)
