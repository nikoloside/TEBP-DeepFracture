import torch

def get_device(use_cuda=True):
    """
    set device
    Args:
        use_cuda: if use cuda
    Returns:
        device: select device
    """
    if use_cuda and torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"use cuda: {torch.cuda.get_device_name()}")
    elif torch.backends.mps.is_available():
        # MPS not support 3D conv, use cpu
        device = torch.device("cpu")
        print("mps available but using cpu due to 3D conv limitations")
    else:
        device = torch.device("cpu")
        print("use cpu")
    
    return device

def to_device(tensor_or_model, device):
    """
    to device
    """
    return tensor_or_model.to(device) 