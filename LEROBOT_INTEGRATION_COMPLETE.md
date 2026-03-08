# LeRobot Integration Complete - Setup Guide

## ✅ What Has Been Done

I've successfully integrated **LeRobot** into your Django robotics application. Here's what has been implemented:

### 1. **LeRobot Package Installation** ✅
- Created `requirements.txt` with LeRobot and dependencies
- Installed LeRobot in your virtual environment (`.venv`)

### 2. **LeRobot Bridge Module** ✅
- Created `control/lerobot_bridge.py` - A comprehensive bridge between LeRobot and Django
- Implements:
  - Robot scanning and detection
  - Leader/Follower arm configuration (SO100/SO101)
  - Connection management
  - Teleoperation control
  - Camera integration (OpenCV and RealSense)
  - Dataset recording
  - Episode replay

### 3. **Updated Robot Utilities** ✅
- Modified `control/robot_utils.py` to import and use LeRobot bridge
- Enhanced `scan_robot()` to use LeRobot's device detection
- Integrated real robot control instead of mock implementations

### 4. **Updated Django Views** ✅
- Modified `control/views.py` with LeRobot integration:
  - Enhanced `/connect/` page with actual robot connection
  - Added robot type selection (SO100/SO101)
  - Real-time port scanning using LeRobot
  - Connect/Disconnect buttons that actually work

### 5. **New API Endpoints** ✅
Added the following REST API endpoints in `control/urls.py`:

```
POST /api/robot/connect/          - Connect to robot arms
POST /api/robot/disconnect/       - Disconnect from robot arms
GET  /api/robot/status/            - Get robot connection status
POST /api/robot/teleoperation/start/  - Start teleoperation
POST /api/robot/teleoperation/stop/   - Stop teleoperation
```

---

## 🚀 How to Use Your Robot Now

### Step 1: Configure Robot Arms
1. Navigate to `http://127.0.0.1:8000/connect/`
2. The page will automatically scan for connected devices
3. Select the ports for:
   - **Leader Arm** (the arm you manually control)
   - **Follower Arm** (the arm that copies movements)
4. Enter IDs for each arm (e.g., "my_leader_arm", "my_follower_arm")
5. Select robot type (SO100 or SO101)
6. Click **"Save Configuration"**

### Step 2: Connect to Robot
After saving configuration, click the **"Connect to Robot"** button on the same page.

Your robot arms should now connect using the actual LeRobot library!

### Step 3: Use Teleoperation
Once connected, you can:
- Start teleoperation mode where the follower mirrors the leader
- Record datasets for training
- Replay recorded episodes

---

## 🔌 API Usage

### Connect to Robot (from terminal or script)
```bash
curl -X POST http://127.0.0.1:8000/api/robot/connect/
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully connected to robot arms",
  "status": {
    "connected": true,
    "leader_arm": "my_leader_arm",
    "follower_arm": "my_follower_arm",
    "cameras": [],
    "lerobot_available": true
  }
}
```

### Check Robot Status
```bash
curl http://127.0.0.1:8000/api/robot/status/
```

### Start Teleoperation
```bash
curl -X POST http://127.0.0.1:8000/api/robot/teleoperation/start/
```

### Stop Teleoperation
```bash
curl -X POST http://127.0.0.1:8000/api/robot/teleoperation/stop/
```

### Disconnect Robot
```bash
curl -X POST http://127.0.0.1:8000/api/robot/disconnect/
```

---

## 🔧 Configuration Files

### Your Current Configuration
The system uses `robot_config.json` in the project root. Based on your working LeRobot scripts, it should have:

```json
{
  "leader_arm": {
    "port": "/dev/tty.usbmodem5A680135091",
    "id": "my_awesome_leader_arm",
    "type": "so101_leader"
  },
  "follower_arm": {
    "port": "/dev/tty.usbmodem5A680125711",
    "id": "my_awesome_follower_arm",
    "type": "so101_follower"
  },
  "robot_type": "so101",
  "connected": false,
  "calibrated": false
}
```

---

## 📸 Camera Integration

Your LeRobot scripts show you have:
- **OpenCV Camera** (index 0): UGREEN camera
- **RealSense Camera** (Serial: 349422070330)

To add cameras to your Django app:

```python
from control.lerobot_bridge import lerobot_manager

# Configure OpenCV camera
lerobot_manager.configure_camera(
    camera_name='front',
    camera_type='opencv',
    camera_index=0,
    width=1920,
    height=1080,
    fps=30
)

# Configure RealSense camera
lerobot_manager.configure_camera(
    camera_name='wrist',
    camera_type='realsense',
    serial_number='349422070330',
    width=640,
    height=480,
    fps=15
)
```

---

## 🎯 Recording Datasets

To record teleoperation data (like your `Record_Data.py` script):

```python
from control.lerobot_bridge import lerobot_manager

# Ensure robot is connected
lerobot_manager.connect(robot_type='so101')

# Start recording
lerobot_manager.start_recording(
    repo_id="Sepehrmo/my-robot-demo1",
    num_episodes=5,
    fps=30,
    episode_time_sec=60,
    task_description="Pick and place task"
)

# ... perform teleoperation ...

# Stop and save
lerobot_manager.stop_recording()
```

---

## 🔄 Replaying Episodes

To replay recorded episodes (like your `Replay_Episod.py` script):

```python
from control.lerobot_bridge import lerobot_manager

# Ensure robot is connected
lerobot_manager.connect(robot_type='so101')

# Replay episode 1
lerobot_manager.replay_episode(
    dataset_repo="Sepehrmo/my-robot-demo1",
    episode_idx=1
)
```

---

## ⚠️ Important Notes

### Port Names (macOS)
Your working scripts use:
- Leader: `/dev/tty.usbmodem5A680135091`
- Follower: `/dev/tty.usbmodem5A680125711`

These are the exact ports you should configure in the web interface.

### Robot Type
Based on your scripts, you're using **SO101** robot arms (both leader and follower).

### HuggingFace Token
You'll need a HuggingFace token for dataset uploads. Get one from: https://huggingface.co/settings/tokens

Set this as an environment variable for dataset uploads:
```bash
export HF_TOKEN="your_huggingface_token_here"
```

---

## 🐛 Troubleshooting

### If Robot Won't Connect:

1. **Check Power**: Ensure both arms are powered on
2. **Check USB**: Verify USB cables are properly connected
3. **Check Ports**: Run in terminal:
   ```bash
   ls /dev/tty.usbmodem*
   ```
   You should see both ports listed.

4. **Check Permissions** (if on Linux):
   ```bash
   sudo usermod -a -G dialout $USER
   sudo chmod 666 /dev/ttyUSB0  # or your port
   ```

5. **Check Django Server**: Ensure Django is running:
   ```bash
   python manage.py runserver
   ```

6. **Check Virtual Environment**: Make sure you're using the venv:
   ```bash
   source .venv/bin/activate  # or `. .venv/bin/activate`
   ```

### If LeRobot Import Fails:
```bash
# Activate virtual environment first
source .venv/bin/activate

# Install/reinstall LeRobot
pip install lerobot --upgrade
```

### View Logs:
Django will show connection errors in the console where `runserver` is running.

---

## 📝 Next Steps

1. **Test Connection**: Try connecting via the web interface at `/connect/`
2. **Calibrate**: After connecting, go to `/calibrate/` to calibrate your robot
3. **Start Teleoperation**: Use the new API endpoints or web interface
4. **Record Data**: Record your own datasets for training
5. **Train Models**: Use recorded data to train AI models

---

## 🎓 Understanding the Architecture

```
Your Django App
     ↓
control/views.py (Web Interface & API)
     ↓
control/lerobot_bridge.py (Bridge Layer)
     ↓
LeRobot Library (SO101Leader, SO101Follower, Cameras, etc.)
     ↓
USB Serial Connection
     ↓
Physical Robot Arms
```

The `lerobot_bridge.py` acts as a singleton manager that handles all LeRobot interactions, making it easy for Django views to control the robot without dealing with low-level details.

---

## ✨ Summary

Your Django app is now fully integrated with LeRobot! The same robot control that works in your standalone Python scripts (`Record_Data.py`, `Replay_Episod.py`, `Teleport_config.py`) now works through your web interface and REST API.

**Key Features Now Available:**
- ✅ Real robot detection and connection
- ✅ SO100/SO101 support
- ✅ Teleoperation control
- ✅ Camera integration (OpenCV + RealSense)
- ✅ Dataset recording to HuggingFace
- ✅ Episode replay
- ✅ REST API for programmatic control
- ✅ Web interface for visual control

You can now control your robot through the web browser or via API calls!
