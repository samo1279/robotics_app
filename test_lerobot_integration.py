#!/usr/bin/env python
"""
Test script to verify LeRobot integration with Django app.

This script checks:
1. LeRobot installation
2. Robot configuration file
3. Serial port detection
4. LeRobot bridge functionality
"""

import sys
import os
import json

# Add the project to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotics_app.settings')

import django
django.setup()

print("=" * 60)
print("  LeRobot Integration Test")
print("=" * 60)
print()

# Test 1: Check LeRobot installation
print("1. Testing LeRobot Installation...")
try:
    import lerobot
    print(f"   ✅ LeRobot installed: version {lerobot.__version__}")
except ImportError as e:
    print(f"   ❌ LeRobot not installed: {e}")
    print("   → Install with: pip install lerobot")
    sys.exit(1)

# Test 2: Check robot configuration
print("\n2. Checking Robot Configuration...")
config_path = 'robot_config.json'
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"   ✅ Configuration file found")
    print(f"   → Leader:   {config.get('leader_arm', {}).get('id', 'Not set')} on {config.get('leader_arm', {}).get('port', 'Not set')}")
    print(f"   → Follower: {config.get('follower_arm', {}).get('id', 'Not set')} on {config.get('follower_arm', {}).get('port', 'Not set')}")
    print(f"   → Type:     {config.get('robot_type', 'Not set')}")
else:
    print(f"   ⚠️  No configuration file found at {config_path}")
    print("   → Configure via web interface at /connect/")

# Test 3: Scan for serial ports
print("\n3. Scanning for Serial Devices...")
try:
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if ports:
        print(f"   ✅ Found {len(ports)} serial device(s):")
        for port in ports:
            robot_type = ""
            if port.pid == 21971:
                robot_type = " [SO-100/Koch]"
            elif port.pid == 24596:
                robot_type = " [WX-250s]"
            elif port.pid == 29987:
                robot_type = " [Feetech]"
            
            print(f"   → {port.device}{robot_type}")
            if port.manufacturer:
                print(f"     Manufacturer: {port.manufacturer}")
            if port.serial_number:
                print(f"     Serial: {port.serial_number}")
    else:
        print("   ⚠️  No serial devices found")
        print("   → Make sure robot arms are powered and connected via USB")
except Exception as e:
    print(f"   ❌ Error scanning ports: {e}")

# Test 4: Test LeRobot bridge import
print("\n4. Testing LeRobot Bridge...")
try:
    from control.lerobot_bridge import lerobot_manager, LEROBOT_AVAILABLE
    print(f"   ✅ LeRobot bridge imported successfully")
    print(f"   → LeRobot Available: {LEROBOT_AVAILABLE}")
    
    # Get status
    status = lerobot_manager.get_status()
    print(f"   → Connected: {status['connected']}")
    print(f"   → Recording: {status['recording']}")
    if status.get('leader_arm'):
        print(f"   → Leader: {status['leader_arm']}")
    if status.get('follower_arm'):
        print(f"   → Follower: {status['follower_arm']}")
    
except Exception as e:
    print(f"   ❌ Error with LeRobot bridge: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test robot scanning with LeRobot
print("\n5. Testing LeRobot Robot Scanner...")
try:
    from control.lerobot_bridge import lerobot_manager
    devices = lerobot_manager.scan_for_robots()
    if devices:
        print(f"   ✅ LeRobot found {len(devices)} device(s):")
        for device in devices:
            print(f"   → {device['device']}")
            if device.get('robot_type'):
                print(f"     Type: {device['robot_type']}")
    else:
        print("   ⚠️  No devices detected by LeRobot scanner")
except Exception as e:
    print(f"   ⚠️  LeRobot scanner error: {e}")

# Test 6: Django views import
print("\n6. Testing Django Views...")
try:
    from control import views
    print("   ✅ Views imported successfully")
    
    # Check if API endpoints exist
    endpoints = [
        'api_robot_connect',
        'api_robot_disconnect', 
        'api_robot_status',
        'api_start_teleoperation',
        'api_stop_teleoperation'
    ]
    
    missing = []
    for endpoint in endpoints:
        if not hasattr(views, endpoint):
            missing.append(endpoint)
    
    if not missing:
        print(f"   ✅ All {len(endpoints)} API endpoints present")
    else:
        print(f"   ⚠️  Missing endpoints: {', '.join(missing)}")
        
except Exception as e:
    print(f"   ❌ Error importing views: {e}")

# Summary
print("\n" + "=" * 60)
print("  Test Complete")
print("=" * 60)
print()
print("Next Steps:")
print("1. Start Django server: python manage.py runserver")
print("   or use: ./start_server.sh")
print()
print("2. Open browser to: http://127.0.0.1:8000/connect/")
print()
print("3. Configure your robot arms using the web interface")
print()
print("4. Test API:")
print("   curl -X POST http://127.0.0.1:8000/api/robot/connect/")
print()
print("For detailed documentation, see: LEROBOT_INTEGRATION_COMPLETE.md")
print("=" * 60)
