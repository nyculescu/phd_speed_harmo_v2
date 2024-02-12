import time
import tensorflow as tf
import logging
import numpy as np

# Node class representing each participant in the decentralized system
class Node:
    def __init__(self, node_id, run_period, blockchain, \
                 neighbors, data_size=100, features=10):
        self.node_id = node_id # Unique identifier for the node
        self.blockchain = blockchain # Reference to the shared blockchain object
        self.run_period = run_period
        self.neighbors = neighbors  # Neighbors of this node

        # Generate mock data
        X, y = self.generate_mock_data(data_size, features)
        self.X = tf.convert_to_tensor(X, dtype=tf.float32)
        self.y = tf.convert_to_tensor(y, dtype=tf.float32)

        self.model = tf.Variable(tf.random.normal([features, 1])) # Initialize model parameters

        # Set up logging for each node
        self.logger = logging.getLogger(f"Node {node_id}") 
        self.logger.setLevel(logging.INFO)  # Set logging level
        self.logger.addHandler(logging.StreamHandler())  # Log output to console
        self.logger.addHandler(logging.FileHandler(f"logs/node_{node_id}.log")) # Log output to file
    
    def decentralized_sgd_update(self, learning_rate=0.01):
        # Perform local SGD update
        with tf.GradientTape() as tape:
            predicted = tf.matmul(self.X, self.model)
            loss = tf.reduce_mean((predicted - self.y)**2)

        gradients = tape.gradient(loss, self.model)
        
        # Check if the node has neighbors
        if self.neighbors is not None and len(self.neighbors) > 0:
            # Mocking the gradient aggregation from neighbors
            aggregated_gradients = gradients
            for neighbor_id in self.neighbors:
                # Realistically, fetch or compute the neighbor's specific gradients using neighbor_id.
                # This could involve accessing a shared database, blockchain ledger, or direct network communication.
                neighbor_gradients = gradients  # Placeholder for neighbor's gradients
                aggregated_gradients += neighbor_gradients
            
            # Averaging the gradients (simulating decentralized aggregation)
            averaged_gradients = aggregated_gradients / (len(self.neighbors) + 1)
        else:
            # If no neighbors, use only the node's own gradients
            averaged_gradients = gradients

        # Update model parameters
        self.model.assign_sub(learning_rate * averaged_gradients)
        
        return loss.numpy()


    # Function to perform a single SGD update
    def decentralized_sgd_update_gpu_switch(self, use_gpu):
        result = None
        if use_gpu:
            try:
                loss = self.decentralized_sgd_update()
                # Placeholder for additional processing or decision-making based on the update

                # Log the completion of SGD update
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - On GPU {self.node_id}, SGD update complete with loss: {loss}")
                result = 0
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during GPU {self.node_id} computation", exc_info=e)
                result = 1  # Handle errors gracefully
        else:
            try:
                loss = self.decentralized_sgd_update()
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - On CPU {self.node_id}, SGD update complete with loss: {loss}")
                result = 0
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during CPU {self.node_id} computation", exc_info=e)
                result = 1  # Handle errors gracefully
        return result
    
    def generate_mock_data(self, data_size, features):
        # Generate synthetic features and labels
        X = np.random.randn(data_size, features)
        y = np.dot(X, np.random.randn(features, 1)) + np.random.randn(data_size, 1) * 0.1
        return X, y
    
    # Main loop for the node to continuously perform SGD updates
    def run(self, use_gpu):
        while True:
            # Perform SGD update and process the result
            if (None != self.decentralized_sgd_update_gpu_switch(use_gpu)):
                # Placeholder for additional processing
                pass
            
            # Wait for a specified interval before the next update
            time.sleep(self.run_period)