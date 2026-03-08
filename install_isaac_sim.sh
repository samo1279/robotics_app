#!/bin/bash

# Isaac Sim Installation Script for Django Robotics App
# Based on SO-ARM tutorial series and LycheeAI Hub documentation

echo "🌟 Installing Isaac Sim for Advanced Robot Visualization..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
print_status "Checking system requirements..."

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    print_success "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
else
    print_warning "NVIDIA GPU not detected. Isaac Sim will run in CPU mode (limited functionality)."
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
    print_success "Python $PYTHON_VERSION detected (compatible)"
else
    print_error "Python 3.8+ required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check available disk space (Isaac Sim requires ~8GB)
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [[ $AVAILABLE_SPACE -gt 10 ]]; then
    print_success "Sufficient disk space available: ${AVAILABLE_SPACE}GB"
else
    print_warning "Low disk space: ${AVAILABLE_SPACE}GB. Isaac Sim requires ~8GB."
fi

# Method 1: Try installing Isaac Sim via pip (if available)
print_status "Attempting Isaac Sim pip installation..."
pip install --upgrade pip

# Install Isaac Sim Python packages
print_status "Installing Isaac Sim Python dependencies..."
pip install isaacsim-python || print_warning "isaacsim-python not available via pip"
pip install omni-isaac-sim || print_warning "omni-isaac-sim not available via pip"
pip install omni-isaac-core || print_warning "omni-isaac-core not available via pip"

# Install supporting packages
print_status "Installing supporting packages..."
pip install pxr-usd
pip install warp-lang
pip install omegaconf
pip install hydra-core
pip install pyglet

# Method 2: Download Isaac Sim (if pip installation failed)
print_status "Checking if Isaac Sim installation was successful..."

python3 -c "
try:
    import omni.isaac.sim
    print('✅ Isaac Sim Python packages installed successfully')
    exit(0)
except ImportError:
    print('❌ Isaac Sim not available via pip installation')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    print_warning "Isaac Sim not available via pip. Manual installation required."
    print_status "Please follow these steps for manual installation:"
    echo ""
    echo "1. 📥 Download Isaac Sim from NVIDIA:"
    echo "   https://developer.nvidia.com/isaac-sim"
    echo ""
    echo "2. 🔑 Create NVIDIA Developer account (free)"
    echo ""
    echo "3. 💾 Download Isaac Sim 2023.1.1 or later"
    echo ""
    echo "4. 📦 Install Isaac Sim:"
    echo "   - Linux: Extract and run isaac-sim.sh"
    echo "   - Windows: Run installer executable"
    echo ""
    echo "5. 🐍 Setup Python environment:"
    echo "   source ~/.local/share/ov/pkg/isaac-sim-*/setup_python_env.sh"
    echo ""
    echo "6. 🔄 Restart Django server after installation"
    echo ""
fi

# Create Isaac Sim assets directory
print_status "Creating Isaac Sim asset directories..."
mkdir -p assets/urdf
mkdir -p assets/meshes
mkdir -p control/isaac_configs

# Create example URDF files
print_status "Creating example URDF files..."
cat > assets/urdf/so-arm101.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="so-arm101">
  <!-- Based on SO-ARM101 dual-arm robot -->
  
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
      <material name="base_material">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.02"/>
    </inertial>
  </link>
  
  <!-- Leader Arm -->
  <link name="leader_base">
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.12"/>
      </geometry>
      <material name="leader_material">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.06" length="0.12"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.008" ixy="0" ixz="0" iyy="0.008" iyz="0" izz="0.008"/>
    </inertial>
  </link>
  
  <!-- Follower Arm -->
  <link name="follower_base">
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.12"/>
      </geometry>
      <material name="follower_material">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.06" length="0.12"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.008" ixy="0" ixz="0" iyy="0.008" iyz="0" izz="0.008"/>
    </inertial>
  </link>
  
  <!-- Joints -->
  <joint name="leader_joint" type="revolute">
    <parent link="base_link"/>
    <child link="leader_base"/>
    <origin xyz="-0.12 0 0.12" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="1"/>
  </joint>
  
  <joint name="follower_joint" type="revolute">
    <parent link="base_link"/>
    <child link="follower_base"/>
    <origin xyz="0.12 0 0.12" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="1"/>
  </joint>
  
</robot>
EOF

print_success "SO-ARM101 URDF created"

# Install ROS2 dependencies (optional)
print_status "Installing ROS2 integration dependencies..."
pip install rclpy
pip install geometry_msgs
pip install sensor_msgs
pip install tf2_ros

# Create test script
print_status "Creating Isaac Sim test script..."
cat > test_isaac_sim.py << 'EOF'
#!/usr/bin/env python3
"""Test Isaac Sim installation and basic functionality."""

import sys
import os
from pathlib import Path

def test_isaac_sim_imports():
    """Test if Isaac Sim packages can be imported."""
    print("🧪 Testing Isaac Sim imports...")
    
    try:
        import omni.isaac.sim
        print("✅ omni.isaac.sim imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import omni.isaac.sim: {e}")
        return False

def test_urdf_files():
    """Test if URDF files are available."""
    print("📁 Testing URDF files...")
    
    urdf_path = Path("assets/urdf/so-arm101.urdf")
    if urdf_path.exists():
        print(f"✅ URDF file found: {urdf_path}")
        return True
    else:
        print(f"❌ URDF file not found: {urdf_path}")
        return False

def main():
    """Run all tests."""
    print("🌟 Isaac Sim Installation Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 2
    
    if test_isaac_sim_imports():
        tests_passed += 1
    
    if test_urdf_files():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Isaac Sim installation test completed successfully!")
        print("\n📱 You can now use Isaac Sim in Django:")
        print("   http://localhost:8000/manipulation/?mode=isaac")
        return True
    else:
        print("⚠️  Some tests failed. Check installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

chmod +x test_isaac_sim.py
print_success "Isaac Sim test script created"

# Final instructions
print_success "Isaac Sim setup completed!"
echo ""
print_status "🎯 Next Steps:"
echo "1. Run test: python3 test_isaac_sim.py"
echo "2. Start Django server: python manage.py runserver"
echo "3. Navigate to: http://localhost:8000/manipulation/"
echo "4. Click 'Isaac Sim' mode for advanced 3D visualization"
echo ""
print_status "📚 Additional Resources:"
echo "• SO-ARM Tutorial: https://lycheeai-hub.com/project-so-arm101-x-isaac-sim-x-isaac-lab-tutorial-series"
echo "• Isaac Sim Docs: https://docs.omniverse.nvidia.com/isaacsim/"
echo "• NVIDIA Developer: https://developer.nvidia.com/isaac-sim"
echo ""
print_status "🎮 Features Available:"
echo "• Photorealistic 3D robot visualization"
echo "• Physics-based simulation"
echo "• ROS2 integration"
echo "• Real2Sim teleoperation"
echo "• URDF import and visualization"
