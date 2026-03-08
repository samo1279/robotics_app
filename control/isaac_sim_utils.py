"""Isaac Sim integration module for robotics visualization and simulation.

This module provides Django integration with NVIDIA Isaac Sim for advanced
robot visualization, physics simulation, and Real2Sim deployment based on
the SO-ARM tutorial series from LycheeAI Hub.
"""
from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import omni.isaac.sim as isaac_sim
    ISAAC_SIM_AVAILABLE = True
except ImportError:
    ISAAC_SIM_AVAILABLE = False


class IsaacSimManager:
    """Manages Isaac Sim integration for advanced robot visualization."""
    
    def __init__(self):
        self.isaac_sim_running = False
        self.isaac_process: Optional[subprocess.Popen] = None
        self.urdf_path = None
        self.robot_loaded = False
        self.config_dir = Path("control/isaac_configs")
        self.config_dir.mkdir(exist_ok=True)
        
    def check_isaac_sim_available(self) -> bool:
        """Check if Isaac Sim is installed and available."""
        try:
            # Check if Isaac Sim executable exists
            isaac_paths = [
                "/home/.local/share/ov/pkg/isaac_sim-2023.1.1/isaac-sim.sh",
                "/opt/nvidia/isaac_sim/isaac-sim.sh",
                "~/.local/share/ov/pkg/isaac-sim-2023.1.1/isaac-sim.sh"
            ]
            
            for path in isaac_paths:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    return True
            
            return ISAAC_SIM_AVAILABLE
            
        except Exception:
            return False
    
    def create_isaac_sim_config(self, robot_type: str = "SO-ARM101") -> str:
        """Create Isaac Sim configuration for robot visualization."""
        config = {
            "isaac_sim": {
                "version": "2023.1.1",
                "headless": False,
                "physics_dt": 1.0/60.0,
                "rendering_dt": 1.0/60.0,
                "stage_units_per_meter": 1.0
            },
            "robot": {
                "type": robot_type,
                "urdf_path": f"assets/urdf/{robot_type.lower()}.urdf",
                "position": [0.0, 0.0, 0.0],
                "orientation": [0.0, 0.0, 0.0, 1.0],
                "scale": [1.0, 1.0, 1.0]
            },
            "environment": {
                "lighting": "dome_light",
                "ground_plane": True,
                "background": "nvidia_logo"
            },
            "camera": {
                "position": [2.0, 2.0, 1.5],
                "look_at": [0.0, 0.0, 0.5],
                "fov": 60.0
            },
            "physics": {
                "gravity": [0.0, 0.0, -9.81],
                "enable_gpu": True,
                "solver_type": "TGS",
                "bounce_threshold_velocity": 0.2,
                "friction_offset_threshold": 0.04,
                "friction_correlation_distance": 0.025
            },
            "ros2": {
                "enable": True,
                "bridge_name": "isaac_ros_bridge",
                "topics": {
                    "joint_states": "/joint_states",
                    "joint_commands": "/joint_group_position_controller/commands",
                    "tf": "/tf",
                    "tf_static": "/tf_static"
                }
            }
        }
        
        config_path = self.config_dir / f"isaac_config_{robot_type.lower()}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(config_path)
    
    def create_urdf_import_script(self, urdf_path: str, robot_name: str = "SO-ARM101") -> str:
        """Create Python script to import URDF into Isaac Sim."""
        script_content = f'''#!/usr/bin/env python3
"""
Isaac Sim URDF Import Script for {robot_name}
Based on SO-ARM tutorial series from LycheeAI Hub
"""

import omni.isaac.sim as isaac_sim
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.urdf import _urdf
import carb

def main():
    """Import and setup robot in Isaac Sim."""
    
    # Start Isaac Sim
    isaac_sim.SimulationApp({{
        "headless": False,
        "width": 1920,
        "height": 1080
    }})
    
    # Create world
    world = World(stage_units_in_meters=1.0)
    
    # Import URDF
    try:
        urdf_interface = _urdf.acquire_urdf_interface()
        
        # Import configuration
        import_config = _urdf.ImportConfig()
        import_config.merge_fixed_joints = False
        import_config.convex_decomp = False
        import_config.import_inertia_tensor = True
        import_config.fix_base = True
        import_config.make_default_prim = True
        import_config.create_physics_scene = True
        
        # Import the URDF
        success = urdf_interface.parse_urdf(
            urdf_path="{urdf_path}",
            import_config=import_config,
            dest_path="/World/{robot_name}"
        )
        
        if success:
            print(f"✅ Successfully imported {{robot_name}} URDF into Isaac Sim")
            
            # Add ground plane
            world.scene.add_default_ground_plane()
            
            # Setup lighting
            import omni.isaac.core.utils.stage as stage_utils
            stage_utils.add_reference_to_stage(
                usd_path="/Isaac/Environments/Simple_Room/simple_room.usd",
                prim_path="/World/simple_room"
            )
            
            # Start simulation
            world.reset()
            
            print("🎮 Isaac Sim is ready! Robot loaded successfully.")
            print("📱 You can now control the robot from Django interface.")
            
        else:
            print(f"❌ Failed to import {{robot_name}} URDF")
            
    except Exception as e:
        print(f"Error importing URDF: {{e}}")
        
    # Keep simulation running
    while isaac_sim.is_running():
        world.step(render=True)

if __name__ == "__main__":
    main()
'''
        
        script_path = self.config_dir / f"import_{robot_name.lower()}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        return str(script_path)
    
    def create_ros2_bridge_config(self) -> str:
        """Create ROS2 bridge configuration for Isaac Sim integration."""
        config = {
            "bridge": {
                "publishers": [
                    {
                        "topic": "/joint_states",
                        "type": "sensor_msgs/JointState",
                        "frequency": 30
                    },
                    {
                        "topic": "/tf",
                        "type": "tf2_msgs/TFMessage", 
                        "frequency": 30
                    },
                    {
                        "topic": "/camera/image_raw",
                        "type": "sensor_msgs/Image",
                        "frequency": 15
                    }
                ],
                "subscribers": [
                    {
                        "topic": "/joint_group_position_controller/commands",
                        "type": "std_msgs/Float64MultiArray"
                    },
                    {
                        "topic": "/gripper_controller/commands",
                        "type": "std_msgs/Float64MultiArray"
                    }
                ]
            },
            "isaac_sim": {
                "physics_frequency": 60,
                "render_frequency": 30,
                "ros_frequency": 30
            }
        }
        
        config_path = self.config_dir / "ros2_bridge_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(config_path)
    
    def start_isaac_sim(self, robot_type: str = "SO-ARM101", 
                       urdf_path: Optional[str] = None) -> bool:
        """Start Isaac Sim with robot visualization."""
        try:
            if self.isaac_sim_running:
                return False
            
            # Create configuration
            config_path = self.create_isaac_sim_config(robot_type)
            
            # Create URDF import script if URDF provided
            if urdf_path and os.path.exists(urdf_path):
                script_path = self.create_urdf_import_script(urdf_path, robot_type)
                
                # Start Isaac Sim with URDF
                cmd = [
                    "python",
                    script_path
                ]
            else:
                # Start Isaac Sim standalone
                isaac_sim_path = self._find_isaac_sim_executable()
                if not isaac_sim_path:
                    return False
                
                cmd = [
                    isaac_sim_path,
                    "--/app/window/dpiScaleOverride=1.0",
                    "--/app/window/scaleToMonitor=false"
                ]
            
            # Start Isaac Sim process
            self.isaac_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.isaac_sim_running = True
            return True
            
        except Exception as e:
            print(f"Error starting Isaac Sim: {e}")
            return False
    
    def stop_isaac_sim(self) -> bool:
        """Stop Isaac Sim simulation."""
        try:
            if self.isaac_process:
                self.isaac_process.terminate()
                self.isaac_process.wait(timeout=10)
                self.isaac_process = None
            
            self.isaac_sim_running = False
            self.robot_loaded = False
            return True
            
        except Exception as e:
            print(f"Error stopping Isaac Sim: {e}")
            return False
    
    def _find_isaac_sim_executable(self) -> Optional[str]:
        """Find Isaac Sim executable path."""
        possible_paths = [
            "/home/.local/share/ov/pkg/isaac_sim-2023.1.1/isaac-sim.sh",
            "/opt/nvidia/isaac_sim/isaac-sim.sh",
            "~/.local/share/ov/pkg/isaac-sim-2023.1.1/isaac-sim.sh",
            "/isaac-sim/isaac-sim.sh"
        ]
        
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
        
        return None
    
    def create_robot_urdf(self, robot_type: str = "SO-ARM101") -> str:
        """Create basic URDF for robot if not available."""
        urdf_content = f'''<?xml version="1.0"?>
<robot name="{robot_type.lower()}">
  
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.2 0.2 0.1"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.2 0.2 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>
  
  <!-- Leader Arm Base -->
  <link name="leader_base">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
  </link>
  
  <!-- Follower Arm Base -->
  <link name="follower_base">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
  </link>
  
  <!-- Joints -->
  <joint name="leader_joint" type="fixed">
    <parent link="base_link"/>
    <child link="leader_base"/>
    <origin xyz="-0.15 0 0.1" rpy="0 0 0"/>
  </joint>
  
  <joint name="follower_joint" type="fixed">
    <parent link="base_link"/>
    <child link="follower_base"/>
    <origin xyz="0.15 0 0.1" rpy="0 0 0"/>
  </joint>
  
</robot>'''
        
        # Create assets directory
        assets_dir = Path("assets/urdf")
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        urdf_path = assets_dir / f"{robot_type.lower()}.urdf"
        with open(urdf_path, 'w') as f:
            f.write(urdf_content)
        
        return str(urdf_path)
    
    def get_isaac_sim_status(self) -> Dict[str, Any]:
        """Get current Isaac Sim status."""
        return {
            "isaac_sim_available": self.check_isaac_sim_available(),
            "isaac_sim_running": self.isaac_sim_running,
            "robot_loaded": self.robot_loaded,
            "process_active": self.isaac_process is not None,
            "config_dir": str(self.config_dir),
            "urdf_path": self.urdf_path
        }
    
    def install_isaac_sim_dependencies(self) -> bool:
        """Install Isaac Sim Python dependencies."""
        try:
            # Install core dependencies
            cmd = [
                "pip", "install",
                "omni-isaac-core",
                "omni-isaac-sim", 
                "omni-isaac-urdf",
                "pxr-usd",
                "warp-lang"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error installing Isaac Sim dependencies: {e}")
            return False


# Global Isaac Sim manager instance
isaac_sim_manager = IsaacSimManager()
