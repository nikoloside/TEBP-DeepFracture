#!/usr/bin/env python3
"""
Test MPS compatibility fixes
"""

import torch
from Utils.utils_device import get_device, to_device

def test_mps_compatibility():
    """Test MPS compatibility fixes"""
    print("Testing MPS compatibility fixes...")
    
    # Test device selection
    print("\n1. Testing device selection:")
    device = get_device(use_cuda=False)
    print(f"   Selected device: {device}")
    
    # Test basic tensor operations
    print("\n2. Testing basic tensor operations:")
    test_tensor = torch.randn(2, 2)
    moved_tensor = to_device(test_tensor, device)
    print(f"   Tensor device: {moved_tensor.device}")
    
    # Test 3D convolution transpose operations (key operations in the network)
    print("\n3. Testing 3D convolution transpose operations:")
    try:
        conv3d = torch.nn.ConvTranspose3d(1, 1, 4, 2, 1)
        conv3d = to_device(conv3d, device)
        
        test_input = torch.randn(1, 1, 8, 8, 8)
        test_input = to_device(test_input, device)
        
        output = conv3d(test_input)
        print(f"   ✅ 3D convolution transpose successful, output shape: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ 3D convolution transpose failed: {e}")
        return False
    
    # Test BatchNorm3d operations
    print("\n4. Testing BatchNorm3d operations:")
    try:
        bn3d = torch.nn.BatchNorm3d(1)
        bn3d = to_device(bn3d, device)
        
        test_input = torch.randn(1, 1, 8, 8, 8)
        test_input = to_device(test_input, device)
        
        output = bn3d(test_input)
        print(f"   ✅ BatchNorm3d successful, output shape: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ BatchNorm3d failed: {e}")
        return False
    
    # Test LeakyReLU operations
    print("\n5. Testing LeakyReLU operations:")
    try:
        relu = torch.nn.LeakyReLU(0.2, inplace=True)
        relu = to_device(relu, device)
        
        test_input = torch.randn(2, 2)
        test_input = to_device(test_input, device)
        
        output = relu(test_input)
        print(f"   ✅ LeakyReLU successful, output shape: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ LeakyReLU failed: {e}")
        return False
    
    print("\n✅ MPS compatibility test passed")
    return True

if __name__ == "__main__":
    test_mps_compatibility() 