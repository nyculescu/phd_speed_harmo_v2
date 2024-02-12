import time
import tensorflow as tf
import logging

# Node class representing each participant in the decentralized system
class Node:
    def __init__(self, node_id, blockchain, data, run_period):
        self.node_id = node_id # Unique identifier for the node
        self.blockchain = blockchain # Reference to the shared blockchain object
        self.run_period = run_period

        # Ensure data is converted to a TensorFlow tensor at the node level
        self.data = tf.convert_to_tensor(data, dtype=tf.float32) # Convert data to TensorFlow tensor
        self.model = tf.Variable(tf.random.normal([data.shape[1], 1])) # Initialize model parameters

        # Set up logging for each node
        self.logger = logging.getLogger(f"Node {node_id}") 
        self.logger.setLevel(logging.INFO)  # Set logging level
        self.logger.addHandler(logging.StreamHandler())  # Log output to console
        self.logger.addHandler(logging.FileHandler(f"logs/node_{node_id}.log")) # Log output to file
    
    # Function to perform a single SGD update
    def decentralized_sgd_update(self, use_gpu):
        result = None

        if use_gpu:
            try:
                with tf.GradientTape() as tape:
                    predicted = tf.matmul(self.data, self.model) # Predict output with current model
                    loss = tf.reduce_mean((predicted - 0.5)**2)  # Simplified loss function for demonstration

                gradients = tape.gradient(loss, [self.model]) # Compute gradients
                self.model.assign_sub(0.01 * gradients[0])  # Apply gradient descent update
                # Log the completion of SGD update
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - On GPU {self.node_id}, SGD update complete with loss: {loss.numpy()}")
                result = 0
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during GPU {self.node_id} computation", exc_info=e)
                result = 1  # Handle errors gracefully
        else:
            try:
                self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - On CPU {self.node_id}, SGD update complete with loss: {loss.numpy()}")
                result = 0
            except Exception as e:
                self.logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - Error during CPU {self.node_id} computation", exc_info=e)
                result = 1  # Handle errors gracefully

        return result
    
    # Main loop for the node to continuously perform SGD updates
    def run(self, use_gpu):
        while True:
            # Perform SGD update and process the result
            if (None != self.decentralized_sgd_update(use_gpu)):
                # Placeholder for additional processing
                pass
            
            # Wait for a specified interval before the next update
            time.sleep(self.run_period)