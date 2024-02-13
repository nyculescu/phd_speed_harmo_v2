import time
import tensorflow as tf
import logging
import numpy as np

class Node:
    def __init__(self, node_id, run_period, tangle, neighbors, data_size=100, features=10):
        """
        Initializes a new Node instance.

        Parameters:
        - node_id: A unique identifier for the node.
        - run_period: Time period between consecutive SGD updates.
        - tangle: Reference to the shared tangle object, facilitating decentralized communication.
        - neighbors: A list of neighbors' IDs for decentralized gradient aggregation.
        - data_size: The number of data samples to generate for training.
        - features: The number of features for each data sample.
        """
        self.node_id = node_id
        self.tangle = tangle
        self.run_period = run_period
        self.neighbors = neighbors

        # Generating synthetic training data
        x, y = self.generate_mock_data(data_size, features)
        self.x = tf.convert_to_tensor(x, dtype=tf.float32)
        self.y = tf.convert_to_tensor(y, dtype=tf.float32)

        # Model initialization with random weights
        self.model = tf.Variable(tf.random.normal([features, 1]))

        # Setting up node-specific logging
        self.setup_logging()

    def setup_logging(self):
        """Configures logging for the node, including console and file handlers."""
        self.logger = logging.getLogger(f"Node {self.node_id}")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        file_handler = logging.FileHandler(f"logs/node_{self.node_id}.log")
        self.logger.addHandler(file_handler)

    def decentralized_sgd_update(self, learning_rate=0.01):
        """
        Performs a decentralized SGD update using local and neighbors' gradients.

        Parameters:
        - learning_rate: The learning rate for the SGD update.

        Returns:
        - The current loss after the update.
        """
        with tf.GradientTape() as tape:
            predicted = tf.matmul(self.x, self.model)
            loss = tf.reduce_mean((predicted - self.y) ** 2)

        gradients = tape.gradient(loss, self.model)

        averaged_gradients = self.aggregate_gradients(gradients)

        # Update the model parameters
        self.model.assign_sub(learning_rate * averaged_gradients)
        
        current_loss = loss.numpy()
        self.record_loss_to_tangle(current_loss)

        return current_loss

    def aggregate_gradients(self, gradients):
        """
        Aggregates gradients from the node and its neighbors.

        Parameters:
        - gradients: The gradients computed from the node's own data.

        Returns:
        - The averaged gradients after aggregation.
        """
        if self.neighbors and len(self.neighbors) > 0:
            aggregated_gradients = gradients
            for neighbor_id in self.neighbors:
                # Simulate fetching gradients from the neighbor
                neighbor_gradients = gradients  # Placeholder for actual neighbor's gradients
                aggregated_gradients += neighbor_gradients

            averaged_gradients = aggregated_gradients / (len(self.neighbors) + 1)
        else:
            averaged_gradients = gradients

        return averaged_gradients

    def record_loss_to_tangle(self, current_loss):
        """
        Records the current loss to the tangle and selects transactions for approval.

        Parameters:
        - current_loss: The loss value to be recorded.
        """
        approving_transactions = self.tangle.get_transactions_for_approval(self.node_id, self.neighbors)
        message = {"loss": float(current_loss), "message": "Normal Loss", "added_by": self.node_id}
        self.tangle.add_transaction(message, approving_transactions)

    def decentralized_sgd_update_gpu_switch(self, use_gpu):
        """
        Wrapper for performing SGD update with optional GPU acceleration.

        Parameters:
        - use_gpu: A boolean flag indicating whether to use GPU for computation.

        Returns:
        - Result code: 0 for success, 1 for failure.
        """
        device = "GPU" if use_gpu else "CPU"
        try:
            loss = self.decentralized_sgd_update()
            self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - On {device} {self.node_id}, SGD update complete with loss: {loss}")
            return 0
        except Exception as e:
            self.logger.error(f"Error during {device} {self.node_id} computation", exc_info=e)
            return 1

    def generate_mock_data(self, data_size, features):
        """
        Generates synthetic data for training.

        Parameters:
        - data_size: The number of samples to generate.
        - features: The number of features per sample.

        Returns:
        - A tuple of features (x) and labels (y).
        """
        x = np.random.randn(data_size, features)
        y = np.dot(x, np.random.randn(features, 1)) + np.random.randn(data_size, 1) * 0.1
        return x, y

    def run(self, use_gpu):
        """
        Main loop to perform SGD updates at a specified interval.

        Parameters:
        - use_gpu: Flag to enable GPU computation.
        """
        while True:
            result = self.decentralized_sgd_update_gpu_switch(use_gpu)
            if result is not None:
                # Placeholder for additional processing based on update result
                pass
            time.sleep(self.run_period)
