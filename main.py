def check_for_TF():
    import tensorflow as tf
    # Check TensorFlow GPU availability
    if tf.config.list_physical_devices('GPU'):
        print("GPU is available for TensorFlow")
    else:
        print("GPU not available for TensorFlow")
    
    print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

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
    # check_for_PT()
    check_for_TF()
    # simulate_decentralized_nodes()
