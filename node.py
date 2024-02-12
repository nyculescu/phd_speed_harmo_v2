import time
import tensorflow as tf
import logging

# Node class representing each participant in the decentralized system
class Node:
    def __init__(self, node_id, blockchain, data, run_period):
        self.node_id = node_id
        self.blockchain = blockchain
        self.run_period = run_period

        # Ensure data is converted to a TensorFlow tensor at the node level
        self.data = tf.convert_to_tensor(data, dtype=tf.float32)
        self.model = tf.Variable(tf.random.normal([data.shape[1], 1]))  # Example model parameters

        self.logger = logging.getLogger(f"Node {node_id}")
        self.logger.addHandler(logging.StreamHandler())  # Add console output
        self.logger.addHandler(logging.FileHandler(f"logs/node_{node_id}.log"))  # Add file logging
    
    def decentralized_sgd_update(self, use_gpu):
        result = None

        if use_gpu:
            try:
                with tf.GradientTape() as tape:
                    predicted = tf.matmul(self.data, self.model)
                    loss = tf.reduce_mean((predicted - 0.5)**2)  # Simplified loss calculation

                gradients = tape.gradient(loss, [self.model])
                self.model.assign_sub(0.01 * gradients[0])  # Update model with gradient
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
    
    def run(self, use_gpu):
        while True:
            if (None != self.decentralized_sgd_update(use_gpu)):
                # Process or utilize the result 
                pass

            time.sleep(self.run_period)