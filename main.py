from multiprocessing import Process
import numpy as np
import os
import tensorflow as tf

num_nodes = 5

def node_operation_cpu(node_id, data):
    # Placeholder for the operation performed by each node
    # For demonstration, let's just print the node ID and its data sum
    data_sum = np.sum(data)
    print(f"Node {node_id} processing data sum: {data_sum}")

def node_operation_gpu(node_id, data, gpus):
    # TensorFlow device scopes can direct operations to run on a specific GPU
    with tf.device(f'/GPU:{node_id % len(gpus)}'):  # Simple modulo for GPU assignment
        # Convert data to TensorFlow tensors
        tensor_data = tf.convert_to_tensor(data, dtype=tf.float32)
        # Example operation: summing data using TensorFlow, leveraging GPU acceleration
        data_sum = tf.reduce_sum(tensor_data)
        # Execute the TensorFlow operations to ensure they run on the GPU
        print(f"Node {node_id} processed data sum on GPU: {data_sum.numpy()}")

def simulate_decentralized_nodes_cpu():
    processes = []
    # Generate mock data for each node
    mock_data = {node_id: np.random.rand(100) for node_id in range(num_nodes)}
    
    for node_id, data in mock_data.items():
        # Create a process for each node
        process = Process(target=node_operation_cpu, args=(node_id, data))
        processes.append(process)
        process.start()
    
    # Wait for all processes to complete
    for process in processes:
        process.join()

def simulate_decentralized_nodes_gpu():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    try:
        # Restrict TensorFlow to only allocate 1 GB of memory on the first GPU for each node
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit = 1024 * num_nodes)])
        processes = []

        # Generate mock data for each node
        mock_data = {node_id: np.random.rand(100).astype(np.float32) for node_id in range(num_nodes)}
        
        for node_id, data in mock_data.items():
            # Create a separate process for each node's operation
            process = Process(target=node_operation_gpu, args=(node_id, data, gpus))
            processes.append(process)
            process.start()
        
        # Wait for all processes to complete
        for process in processes:
            process.join()
    except RuntimeError as e:
        # Virtual devices must be set before GPUs have been initialized
        print(e)

if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TensorFlow logging except for errors
            
    simulate_decentralized_nodes_gpu()
