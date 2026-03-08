"""LeRobot Bridge Module

This module bridges the LeRobot library with the Django application,
providing a clean interface for robot control, teleoperation, recording,
and replay functionality.

Based on the working scripts in Lerobot folder:
- Record_Data.py: Recording teleoperation data
- Replay_Episod.py: Replaying recorded episodes
- Teleport_config.py: Teleoperating the robot
- Teleport_Camera.py: Camera integration
"""

import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import serial.tools.list_ports

# LeRobot imports
try:
    from lerobot.robots.so100_follower import SO100Follower, SO100FollowerConfig
    from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
    from lerobot.teleoperators.so100_leader.so100_leader import SO100Leader
    from lerobot.teleoperators.so100_leader.config_so100_leader import SO100LeaderConfig
    from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
    from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
    from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig
    from lerobot.cameras.realsense.camera_realsense import RealSenseCamera
    from lerobot.cameras.configs import ColorMode, Cv2Rotation
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    from lerobot.datasets.utils import hw_to_dataset_features
    from lerobot.record import record_loop
    from lerobot.utils.control_utils import init_keyboard_listener
    from lerobot.utils.utils import log_say
    from lerobot.utils.robot_utils import busy_wait
    LEROBOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LeRobot not available: {e}")
    LEROBOT_AVAILABLE = False


@dataclass
class RobotArmConfig:
    """Configuration for a robot arm (leader or follower)"""
    port: str
    robot_id: str
    robot_type: str  # 'so100' or 'so101'
    arm_type: str  # 'leader' or 'follower'


class LeRobotManager:
    """
    Manages LeRobot robot connections, teleoperation, and data recording.
    
    This class provides a singleton interface to:
    - Detect and connect to SO100/SO101 robot arms
    - Manage leader (teleop) and follower (robot) arms
    - Record teleoperation data
    - Replay recorded episodes
    - Integrate cameras (OpenCV and RealSense)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.leader_arm = None
        self.follower_arm = None
        self.leader_config = None
        self.follower_config = None
        self.cameras = {}
        self.connected = False
        self.recording = False
        self.dataset = None
        self.recording_thread = None
        self.teleop_thread = None
        self._stop_teleop = False
        
    def scan_for_robots(self) -> List[Dict[str, Any]]:
        """
        Scan for connected robot devices.
        
        Returns:
            List of dictionaries containing device information
        """
        devices = []
        
        try:
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                device_info = {
                    'device': port.device,
                    'description': port.description or 'Unknown',
                    'manufacturer': port.manufacturer or 'Unknown',
                    'pid': port.pid,
                    'serial_number': port.serial_number,
                    'robot_type': None
                }
                
                # Identify robot types based on PID
                if port.pid == 21971:  # Koch v1.1 / SO-100
                    device_info['robot_type'] = 'SO-100'
                    device_info['description'] = 'SO-100/Koch Robot Arm'
                elif port.pid == 24596:  # WX-250s
                    device_info['robot_type'] = 'WX-250s'
                    device_info['description'] = 'WX-250s Robot Arm'
                elif port.pid == 29987:  # Feetech
                    device_info['robot_type'] = 'Feetech'
                    device_info['description'] = 'Feetech Robot Arm'
                    
                devices.append(device_info)
                
        except Exception as e:
            print(f"Error scanning for robots: {e}")
            
        return devices
    
    def configure_arms(self, leader_port: str, leader_id: str, 
                      follower_port: str, follower_id: str,
                      robot_type: str = 'so101') -> bool:
        """
        Configure leader and follower arms.
        
        Args:
            leader_port: Serial port for leader arm (e.g., '/dev/tty.usbmodem...')
            leader_id: Identifier for leader arm
            follower_port: Serial port for follower arm
            follower_id: Identifier for follower arm
            robot_type: 'so100' or 'so101'
            
        Returns:
            True if configuration successful
        """
        if not LEROBOT_AVAILABLE:
            print("Error: LeRobot not installed")
            return False
            
        try:
            # Create configurations based on robot type
            if robot_type == 'so100':
                self.leader_config = SO100LeaderConfig(
                    port=leader_port,
                    id=leader_id
                )
                self.follower_config = SO100FollowerConfig(
                    port=follower_port,
                    id=follower_id
                )
            else:  # so101
                self.leader_config = SO101LeaderConfig(
                    port=leader_port,
                    id=leader_id
                )
                self.follower_config = SO101FollowerConfig(
                    port=follower_port,
                    id=follower_id
                )
                
            print(f"Configured {robot_type} arms: Leader={leader_id}, Follower={follower_id}")
            return True
            
        except Exception as e:
            print(f"Error configuring arms: {e}")
            return False
    
    def connect(self, robot_type: str = 'so101') -> bool:
        """
        Connect to both leader and follower arms.
        
        Args:
            robot_type: 'so100' or 'so101'
            
        Returns:
            True if connection successful
        """
        if not LEROBOT_AVAILABLE:
            print("Error: LeRobot not installed")
            return False
            
        if not self.leader_config or not self.follower_config:
            print("Error: Arms not configured. Call configure_arms() first")
            return False
            
        try:
            # Initialize robot instances based on type
            if robot_type == 'so100':
                self.leader_arm = SO100Leader(self.leader_config)
                self.follower_arm = SO100Follower(self.follower_config)
            else:  # so101
                self.leader_arm = SO101Leader(self.leader_config)
                self.follower_arm = SO101Follower(self.follower_config)
            
            # Connect to both arms
            print(f"Connecting to leader arm on {self.leader_config.port}...")
            self.leader_arm.connect()
            
            print(f"Connecting to follower arm on {self.follower_config.port}...")
            self.follower_arm.connect()
            
            self.connected = True
            print("✅ Successfully connected to both arms!")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to arms: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """Disconnect from robot arms and cameras."""
        try:
            if self.leader_arm:
                self.leader_arm.disconnect()
                self.leader_arm = None
                
            if self.follower_arm:
                self.follower_arm.disconnect()
                self.follower_arm = None
                
            for camera in self.cameras.values():
                try:
                    camera.disconnect()
                except:
                    pass
                    
            self.cameras = {}
            self.connected = False
            print("Disconnected from robot arms and cameras")
            
        except Exception as e:
            print(f"Error during disconnect: {e}")
    
    def start_teleoperation(self):
        """
        Start teleoperation mode where leader controls follower.
        Runs in a background thread.
        """
        if not self.connected:
            print("Error: Not connected to robot arms")
            return False
            
        if self.teleop_thread and self.teleop_thread.is_alive():
            print("Teleoperation already running")
            return False
            
        self._stop_teleop = False
        self.teleop_thread = threading.Thread(target=self._teleoperation_loop, daemon=True)
        self.teleop_thread.start()
        print("Started teleoperation mode")
        return True
    
    def _teleoperation_loop(self):
        """Internal teleoperation loop."""
        try:
            while not self._stop_teleop and self.connected:
                # Get action from leader arm
                action = self.leader_arm.get_action()
                
                # Send action to follower arm
                self.follower_arm.send_action(action)
                
                # Small delay to prevent overwhelming the robot
                time.sleep(0.01)  # 100Hz control loop
                
        except Exception as e:
            print(f"Error in teleoperation loop: {e}")
            self._stop_teleop = True
    
    def stop_teleoperation(self):
        """Stop teleoperation mode."""
        self._stop_teleop = True
        if self.teleop_thread:
            self.teleop_thread.join(timeout=2.0)
        print("Stopped teleoperation mode")
    
    def configure_camera(self, camera_name: str, camera_type: str = 'opencv', 
                        camera_index: int = 0, width: int = 640, height: int = 480,
                        fps: int = 30, serial_number: Optional[str] = None) -> bool:
        """
        Configure a camera for recording.
        
        Args:
            camera_name: Name identifier for the camera (e.g., 'front', 'wrist')
            camera_type: 'opencv' or 'realsense'
            camera_index: Index for OpenCV camera (0, 1, 2...)
            width: Camera resolution width
            height: Camera resolution height
            fps: Frames per second
            serial_number: Serial number for RealSense camera
            
        Returns:
            True if configuration successful
        """
        if not LEROBOT_AVAILABLE:
            return False
            
        try:
            if camera_type == 'opencv':
                config = OpenCVCameraConfig(
                    index_or_path=camera_index,
                    width=width,
                    height=height,
                    fps=fps
                )
                self.cameras[camera_name] = {'type': 'opencv', 'config': config}
                
            elif camera_type == 'realsense':
                if not serial_number:
                    print("Error: serial_number required for RealSense camera")
                    return False
                    
                config = RealSenseCameraConfig(
                    serial_number_or_name=serial_number,
                    fps=fps,
                    width=width,
                    height=height,
                    color_mode=ColorMode.RGB,
                    use_depth=True,
                    rotation=Cv2Rotation.NO_ROTATION
                )
                self.cameras[camera_name] = {'type': 'realsense', 'config': config}
                
            print(f"Configured {camera_type} camera: {camera_name}")
            return True
            
        except Exception as e:
            print(f"Error configuring camera: {e}")
            return False
    
    def start_recording(self, repo_id: str, num_episodes: int = 5, 
                       fps: int = 30, episode_time_sec: int = 60,
                       task_description: str = "Robot task") -> bool:
        """
        Start recording teleoperation data to a LeRobot dataset.
        
        Args:
            repo_id: HuggingFace repo ID (e.g., 'username/dataset-name')
            num_episodes: Number of episodes to record
            fps: Recording frame rate
            episode_time_sec: Maximum time per episode
            task_description: Description of the task being performed
            
        Returns:
            True if recording started successfully
        """
        if not LEROBOT_AVAILABLE:
            print("Error: LeRobot not available")
            return False
            
        if not self.connected:
            print("Error: Not connected to robot arms")
            return False
            
        if self.recording:
            print("Already recording")
            return False
            
        try:
            # Prepare camera configs for follower arm
            camera_configs = {}
            for name, cam_info in self.cameras.items():
                camera_configs[name] = cam_info['config']
            
            # Update follower config with cameras
            self.follower_config.cameras = camera_configs
            
            # Reinitialize follower with camera config
            robot_type = 'so101'  # Default, could be made configurable
            if robot_type == 'so100':
                self.follower_arm = SO100Follower(self.follower_config)
            else:
                self.follower_arm = SO101Follower(self.follower_config)
            self.follower_arm.connect()
            
            # Configure dataset features
            action_features = hw_to_dataset_features(
                self.follower_arm.action_features, "action"
            )
            obs_features = hw_to_dataset_features(
                self.follower_arm.observation_features, "observation"
            )
            dataset_features = {**action_features, **obs_features}
            
            # Create dataset
            self.dataset = LeRobotDataset.create(
                repo_id=repo_id,
                fps=fps,
                features=dataset_features,
                robot_type=self.follower_arm.name,
                use_videos=True,
                image_writer_threads=4,
            )
            
            self.recording = True
            print(f"✅ Started recording to {repo_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_recording(self) -> bool:
        """Stop recording and save the dataset."""
        if not self.recording:
            print("Not currently recording")
            return False
            
        try:
            if self.dataset:
                self.dataset.save_episode()
                # Optionally push to hub
                # self.dataset.push_to_hub()
                
            self.recording = False
            print("✅ Stopped recording and saved dataset")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping recording: {e}")
            return False
    
    def replay_episode(self, dataset_repo: str, episode_idx: int = 0) -> bool:
        """
        Replay a recorded episode.
        
        Args:
            dataset_repo: HuggingFace repo ID of the dataset
            episode_idx: Index of episode to replay
            
        Returns:
            True if replay successful
        """
        if not LEROBOT_AVAILABLE:
            print("Error: LeRobot not available")
            return False
            
        if not self.connected or not self.follower_arm:
            print("Error: Follower arm not connected")
            return False
            
        try:
            # Load dataset
            dataset = LeRobotDataset(dataset_repo, episodes=[episode_idx])
            actions = dataset.hf_dataset.select_columns("action")
            
            log_say(f"Replaying episode {episode_idx}")
            
            # Replay loop
            for idx in range(dataset.num_frames):
                t0 = time.perf_counter()
                
                # Get action
                action = {
                    name: float(actions[idx]["action"][i]) 
                    for i, name in enumerate(dataset.features["action"]["names"])
                }
                
                # Send to robot
                self.follower_arm.send_action(action)
                
                # Maintain framerate
                busy_wait(1.0 / dataset.fps - (time.perf_counter() - t0))
            
            print(f"✅ Completed replay of episode {episode_idx}")
            return True
            
        except Exception as e:
            print(f"❌ Error replaying episode: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the robot system."""
        return {
            'connected': self.connected,
            'recording': self.recording,
            'leader_arm': self.leader_config.id if self.leader_config else None,
            'follower_arm': self.follower_config.id if self.follower_config else None,
            'cameras': list(self.cameras.keys()),
            'lerobot_available': LEROBOT_AVAILABLE
        }


# Global singleton instance
lerobot_manager = LeRobotManager()
