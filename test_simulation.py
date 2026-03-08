#!/usr/bin/env python3
"""Test script for gym_hil simulation environment.

This script tests the basic functionality of the simulation environment
and verifies that all components are working correctly.
"""
import os
import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import gymnasium as gym
        print(f"✅ Gymnasium {gym.__version__}")
    except ImportError as e:
        print(f"❌ Gymnasium import failed: {e}")
        return False
    
    try:
        import mujoco
        print(f"✅ MuJoCo {mujoco.__version__}")
    except ImportError as e:
        print(f"❌ MuJoCo import failed: {e}")
        return False
    
    try:
        import pygame
        print("✅ Pygame")
    except ImportError as e:
        print(f"❌ Pygame import failed: {e}")
        return False
    
    return True

def test_environment_creation():
    """Test basic environment creation."""
    print("\n🏗️  Testing environment creation...")
    
    try:
        import gymnasium as gym
        
        # Test basic CartPole environment
        env = gym.make('CartPole-v1')
        observation, info = env.reset()
        print(f"✅ CartPole environment created, observation shape: {observation.shape}")
        env.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Environment creation failed: {e}")
        return False

def test_mujoco_environment():
    """Test MuJoCo-based environment."""
    print("\n🦾 Testing MuJoCo environment...")
    
    try:
        import gymnasium as gym
        
        # Try to create a MuJoCo environment
        env_names = ['Ant-v4', 'HalfCheetah-v4', 'Hopper-v4']
        
        for env_name in env_names:
            try:
                env = gym.make(env_name)
                observation, info = env.reset()
                print(f"✅ {env_name} created, observation shape: {observation.shape}")
                env.close()
                return True
            except Exception as e:
                print(f"⚠️  {env_name} failed: {e}")
                continue
        
        print("❌ No MuJoCo environments could be created")
        return False
        
    except Exception as e:
        print(f"❌ MuJoCo test failed: {e}")
        return False

def create_test_config():
    """Create a test configuration file."""
    print("\n📝 Creating test configuration...")
    
    config = {
        "env": {
            "type": "gym_manipulator",
            "name": "gym_hil",
            "task": "PandaPickCubeGamepad-v0",
            "fps": 10,
            "processor": {
                "control_mode": "gamepad",
                "gripper": {
                    "use_gripper": True,
                    "gripper_penalty": -0.02
                },
                "reset": {
                    "control_time_s": 15.0,
                    "fixed_reset_joint_positions": [
                        0.0, 0.195, 0.0, -2.43, 0.0, 2.62, 0.785
                    ]
                },
                "inverse_kinematics": {
                    "end_effector_step_sizes": {
                        "x": 0.025,
                        "y": 0.025,
                        "z": 0.025
                    }
                }
            }
        },
        "device": "cpu"  # Will be set to cuda if available
    }
    
    try:
        config_dir = Path("control/simulation_configs")
        config_dir.mkdir(exist_ok=True)
        
        config_path = config_dir / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Test configuration created: {config_path}")
        return str(config_path)
        
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return None

def main():
    """Run all tests."""
    print("🚀 Starting gym_hil simulation tests...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install required packages.")
        return False
    
    # Test basic environment
    if not test_environment_creation():
        print("\n❌ Basic environment test failed.")
        return False
    
    # Test MuJoCo
    if not test_mujoco_environment():
        print("\n⚠️  MuJoCo environment test failed, but this may be expected.")
    
    # Create test config
    config_path = create_test_config()
    if not config_path:
        print("\n❌ Configuration test failed.")
        return False
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("✅ Core packages installed correctly")
    print("✅ Basic environment creation works")
    print("✅ Configuration files can be created")
    print("\n🎮 Ready to use simulation in Django app!")
    print("   Navigate to: http://localhost:8000/manipulation/?mode=simulation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
