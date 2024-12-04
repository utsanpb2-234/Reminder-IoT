import tensorflow as tf

def check_gpu_utilization():
    # List available physical devices
    devices = tf.config.list_physical_devices()
    
    print("Available physical devices:")
    for device in devices:
        print(device)
    
    # Check if GPU is available
    gpu_available = tf.config.list_physical_devices('GPU')
    if gpu_available:
        print("\nTensorFlow is utilizing the GPU (Apple M1 GPU detected).")
    else:
        print("\nNo GPU detected. TensorFlow is using the CPU.")

if __name__ == "__main__":
    check_gpu_utilization()