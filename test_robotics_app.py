#!/usr/bin/env python3
"""
Comprehensive test script for the robotics Django application.
Tests all functionality including robot detection, calibration, recording, training, and AI control.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotics_app.settings')
import django
django.setup()

from control.robot_utils import (
    scan_robot, 
    list_cameras, 
    CalibrationManager, 
    DataRecorder, 
    train_model, 
    run_ai_control,
    get_robot_status
)

def test_robot_detection():
    """Test robot detection functionality."""
    print("🤖 Testing Robot Detection...")
    robots = scan_robot()
    print(f"✅ Found {len(robots)} potential robot devices:")
    for robot in robots:
        print(f"   - {robot}")
    return len(robots) > 0

def test_camera_detection():
    """Test camera detection functionality."""
    print("\n📹 Testing Camera Detection...")
    cameras = list_cameras()
    print(f"✅ Found {len(cameras)} camera devices:")
    for camera in cameras:
        print(f"   - {camera}")
    return len(cameras) > 0

def test_calibration():
    """Test robot calibration functionality."""
    print("\n⚙️ Testing Robot Calibration...")
    
    # Test calibration
    cal_manager = CalibrationManager()
    result = cal_manager.calibrate()
    
    # Verify calibration data
    required_keys = ['timestamp', 'robot_type', 'joint_limits', 'home_position']
    missing_keys = [key for key in required_keys if key not in result]
    
    if missing_keys:
        print(f"❌ Missing calibration keys: {missing_keys}")
        return False
    
    print("✅ Calibration completed successfully")
    print(f"   - Robot type: {result['robot_type']}")
    print(f"   - Joints configured: {len(result['joint_limits'])}")
    print(f"   - Status: {result['status']}")
    
    # Test loading calibration
    cal_manager2 = CalibrationManager()
    loaded = cal_manager2.load_calibration()
    print(f"✅ Calibration file loading: {'Success' if loaded else 'Failed'}")
    
    return True

def test_data_recording():
    """Test data recording functionality."""
    print("\n📊 Testing Data Recording...")
    
    # Create recorder
    recorder = DataRecorder('dataset')
    
    # Start recording
    file_path = recorder.start_recording('test_comprehensive')
    if not file_path:
        print("❌ Failed to start recording")
        return False
    
    print(f"✅ Recording started: {os.path.basename(file_path)}")
    
    # Record for 2 seconds
    time.sleep(2)
    
    # Stop recording
    result_path = recorder.stop_recording()
    if not result_path:
        print("❌ Failed to stop recording")
        return False
    
    print(f"✅ Recording stopped: {os.path.basename(result_path)}")
    
    # Verify file exists and has content
    if not os.path.exists(result_path):
        print("❌ Recording file not found")
        return False
    
    file_size = os.path.getsize(result_path)
    print(f"✅ Recording file size: {file_size} bytes")
    
    # Verify JSON format
    try:
        with open(result_path, 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                json.loads(lines[0])  # Test first line is valid JSON
                print(f"✅ Recorded {len(lines)} data points")
            else:
                print("❌ No data recorded")
                return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in recording")
        return False
    
    return result_path

def test_model_training(dataset_path):
    """Test model training functionality."""
    print("\n🧠 Testing Model Training...")
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found: {dataset_path}")
        return False
    
    try:
        model_path = train_model(dataset_path, 'training')
        
        if not os.path.exists(model_path):
            print(f"❌ Model file not created: {model_path}")
            return False
        
        print(f"✅ Model trained successfully: {os.path.basename(model_path)}")
        
        # Verify model file content
        with open(model_path, 'r') as f:
            content = f.read()
            if 'behavior_cloning' in content and 'training_samples' in content:
                print("✅ Model file contains expected metadata")
            else:
                print("⚠️ Model file missing some metadata")
        
        return model_path
        
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        return False

def test_ai_control(model_path):
    """Test AI control functionality."""
    print("\n🤖 Testing AI Control...")
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    try:
        success = run_ai_control(model_path)
        
        if success:
            print("✅ AI control started successfully")
        else:
            print("❌ AI control failed to start")
        
        return success
        
    except Exception as e:
        print(f"❌ AI control error: {e}")
        return False

def test_web_interface():
    """Test 7: Web interface access test."""
    print("\\n=== Test 7: Web Interface Access ===")
    
    try:
        import requests
        
        base_url = "http://127.0.0.1:8000"
        
        # Test pages
        pages = [
            "/",
            "/connect/",
            "/calibrate/",
            "/record/",
            "/cameras/",
            "/train/",
            "/ai_control/",
            "/manipulation/"
        ]
        
        working_pages = 0
        
        for page in pages:
            try:
                response = requests.get(base_url + page, timeout=5)
                if response.status_code == 200:
                    working_pages += 1
                    print(f"  ✓ {page} - OK")
                else:
                    print(f"  ✗ {page} - Error {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"  ✗ {page} - Connection failed")
        
        print(f"Working pages: {working_pages}/{len(pages)}")
        return working_pages == len(pages)
        
    except ImportError:
        print("  ⚠ requests library not available - skipping web test")
        return True  # Don't fail test if requests not available

def test_robot_status():
    """Test robot status functionality."""
    print("\n📋 Testing Robot Status...")
    
    try:
        status = get_robot_status()
        required_keys = ['connected_robots', 'robot_list', 'calibrated', 'system', 'timestamp']
        missing_keys = [key for key in required_keys if key not in status]
        
        if missing_keys:
            print(f"❌ Missing status keys: {missing_keys}")
            return False
        
        print(f"✅ Robot status retrieved successfully")
        print(f"   - Connected robots: {status['connected_robots']}")
        print(f"   - System: {status['system']}")
        print(f"   - Calibrated: {status['calibrated']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Robot status error: {e}")
        return False


def test_manipulation_system():
    """Test manipulation system functionality."""
    print("\n🦾 Testing Manipulation System...")
    
    try:
        from control.robot_utils import teleop_controller, ArmController
        
        # Test teleop controller initialization
        assert teleop_controller is not None
        print("✅ Teleoperation controller initialized")
        
        # Test arm controller creation
        test_arm = ArmController("test_arm", "/dev/test", "SO-100")
        assert test_arm.robot_id == "test_arm"
        assert test_arm.arm_type == "SO-100"
        print("✅ Arm controller creation works")
        
        # Test connection simulation
        connected = test_arm.connect()
        assert connected == True
        assert test_arm.connected == True
        print("✅ Arm connection simulation works")
        
        # Test calibration
        calibrated = test_arm.calibrate()
        assert calibrated == True  
        assert test_arm.calibrated == True
        print("✅ Arm calibration simulation works")
        
        # Test action generation
        action = test_arm.get_action()
        assert isinstance(action, dict)
        assert len(action) > 0
        print("✅ Action generation works")
        
        # Test joint command
        success = test_arm.send_joint_command("shoulder_pan", 45.0)
        assert success == True
        print("✅ Joint command works")
        
        # Test position update
        assert isinstance(test_arm.position, dict)
        assert 'x' in test_arm.position
        print("✅ Position tracking works")
        
        # Clean up
        test_arm.disconnect()
        print("✅ Manipulation system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Manipulation system test failed: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("🚀 Starting Comprehensive Robotics App Test\n")
    
    results = []
    
    # Run tests
    results.append(("Robot Detection", test_robot_detection()))
    results.append(("Camera Detection", test_camera_detection()))
    results.append(("Robot Status", test_robot_status()))
    results.append(("Calibration", test_calibration()))
    results.append(("Manipulation System", test_manipulation_system()))
    
    # Recording test (returns dataset path if successful)
    dataset_path = test_data_recording()
    results.append(("Data Recording", bool(dataset_path)))
    
    # Training test (returns model path if successful)
    model_path = None
    if dataset_path:
        model_path = test_model_training(dataset_path)
        results.append(("Model Training", bool(model_path)))
    else:
        results.append(("Model Training", False))
        print("⚠️ Skipping model training due to recording failure")
    
    # AI control test
    if model_path:
        results.append(("AI Control", test_ai_control(model_path)))
    else:
        results.append(("AI Control", False))
        print("⚠️ Skipping AI control due to training failure")
    
    # Web interface test
    results.append(("Web Interface", test_web_interface()))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print("="*50)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your robotics app is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
