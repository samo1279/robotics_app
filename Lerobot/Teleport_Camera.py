from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower
#intel realsense
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig
from lerobot.cameras.realsense.camera_realsense import RealSenseCamera
from lerobot.cameras.configs import ColorMode, Cv2Rotation

camera_config = {
    "front": OpenCVCameraConfig(index_or_path=0, width=1920, height=1080, fps=30)
}

# Create a `RealSenseCameraConfig` specifying your camera’s serial number and enabling depth.
config = RealSenseCameraConfig(
    serial_number_or_name="349422070330",
    fps=15,
    width=640,
    height=480,
    color_mode=ColorMode.RGB,
    use_depth=True,
    rotation=Cv2Rotation.NO_ROTATION
)
camera = RealSenseCamera(config)
camera.connect()

try:
    color_frame = camera.read()
    depth_map = camera.read_depth()
    print("Color frame shape:", color_frame.shape)
    print("Depth map shape:", depth_map.shape)
finally:
    camera.disconnect()

##
robot_config = SO101FollowerConfig(
    port="/dev/tty.usbmodem5A680125711",
    id="my_awesome_follower_arm",
)

teleop_config = SO101LeaderConfig(
    port="/dev/tty.usbmodem5A680135091",
    id="my_blue_leader_arm",
)

robot = SO101Follower(robot_config)
teleop_device = SO101Leader(teleop_config)
robot.connect()
teleop_device.connect()

while True:
    observation = robot.get_observation()
    action = teleop_device.get_action()
    robot.send_action(action)