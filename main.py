import os

def check_for_TF():
    import tensorflow as tf
    # Check TensorFlow GPU availability
    if tf.config.list_physical_devices('GPU'):
        print("GPU is available for TensorFlow")
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
        return True
    else:
        print("GPU not available for TensorFlow")
        return False

def check_for_PT():
    import torch
    # Check PyTorch GPU availability
    if torch.cuda.is_available():
        print("GPU is available for PyTorch")
        # device = torch.device("cuda")
        # Example: Move a tensor to GPU
        # tensor = torch.zeros(1)
        # tensor = tensor.to(device)
    else:
        print("GPU not available for PyTorch")
        # device = torch.device("cpu")

if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TensorFlow logging except for errors
    
    if check_for_TF(): # check_for_PT()
        print("System started running")
    else:
        print("System is not running")
    
    # simulate_decentralized_nodes()
