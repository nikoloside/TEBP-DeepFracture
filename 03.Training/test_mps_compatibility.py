#!/usr/bin/env python3
"""
测试 MPS 兼容性修复
"""

import torch
from Utils.utils_device import get_device, to_device

def test_mps_compatibility():
    """测试 MPS 兼容性修复"""
    print("测试 MPS 兼容性修复...")
    
    # 测试设备选择
    print("\n1. 测试设备选择:")
    device = get_device(use_cuda=False)
    print(f"   选择的设备: {device}")
    
    # 测试基本张量操作
    print("\n2. 测试基本张量操作:")
    test_tensor = torch.randn(2, 2)
    moved_tensor = to_device(test_tensor, device)
    print(f"   张量设备: {moved_tensor.device}")
    
    # 测试 3D 卷积转置操作（网络中的关键操作）
    print("\n3. 测试 3D 卷积转置操作:")
    try:
        conv3d = torch.nn.ConvTranspose3d(1, 1, 4, 2, 1)
        conv3d = to_device(conv3d, device)
        
        test_input = torch.randn(1, 1, 8, 8, 8)
        test_input = to_device(test_input, device)
        
        output = conv3d(test_input)
        print(f"   ✅ 3D 卷积转置成功，输出形状: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ 3D 卷积转置失败: {e}")
        return False
    
    # 测试 BatchNorm3d 操作
    print("\n4. 测试 BatchNorm3d 操作:")
    try:
        bn3d = torch.nn.BatchNorm3d(1)
        bn3d = to_device(bn3d, device)
        
        test_input = torch.randn(1, 1, 8, 8, 8)
        test_input = to_device(test_input, device)
        
        output = bn3d(test_input)
        print(f"   ✅ BatchNorm3d 成功，输出形状: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ BatchNorm3d 失败: {e}")
        return False
    
    # 测试 LeakyReLU 操作
    print("\n5. 测试 LeakyReLU 操作:")
    try:
        relu = torch.nn.LeakyReLU(0.2, inplace=True)
        relu = to_device(relu, device)
        
        test_input = torch.randn(2, 2)
        test_input = to_device(test_input, device)
        
        output = relu(test_input)
        print(f"   ✅ LeakyReLU 成功，输出形状: {output.shape}")
        
    except Exception as e:
        print(f"   ❌ LeakyReLU 失败: {e}")
        return False
    
    print("\n✅ MPS 兼容性测试通过")
    return True

if __name__ == "__main__":
    test_mps_compatibility() 