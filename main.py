from multiprocessing import Process, Queue
import numpy as np
import os
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TensorFlow logging except for errors

num_nodes = 5

### CPU ###
def node_operation_cpu(node_id, data):
    # Placeholder for the operation performed by each node
    # For demonstration, let's just print the node ID and its data sum
    data_sum = np.sum(data)
    print(f"Node {node_id} processing data sum: {data_sum}")

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

### GPU ###
def node_operation_gpu(node_id, data, result_queue):
    # Simplify GPU assignment by allowing TensorFlow to manage GPU allocation
    tf.config.experimental.set_memory_growth(tf.config.experimental.list_physical_devices('GPU')[0], True)
    
    # TensorFlow operations
    with tf.device(f'/device:GPU:0'):  # Assume using the first GPU for all operations
        tensor_data = tf.convert_to_tensor(data, dtype=tf.float32)
        data_sum = tf.reduce_sum(tensor_data)
        result = data_sum.numpy()
    
    result_queue.put((node_id, result))

def initialize_tensorflow_gpu():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Attempt to set TensorFlow to use only the GPUs you plan to use and limit memory usage
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

def simulate_decentralized_nodes_gpu():
    initialize_tensorflow_gpu() # Initialize TensorFlow and GPU settings in the main process
    
    processes = []
    result_queue = Queue()
    mock_data = {node_id: np.random.rand(100).astype(np.float32) for node_id in range(num_nodes)}
    
    for node_id, data in mock_data.items():
        process = Process(target=node_operation_gpu, args=(node_id, data, result_queue))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    while not result_queue.empty():
        node_id, result = result_queue.get()
        print(f"Node {node_id} processed data sum on GPU: {result}")

if __name__ == "__main__":
    simulate_decentralized_nodes_gpu()