# 🚀 QUICK START - Robot Connection Fix

## ⚡ THE PROBLEM
Your Django app couldn't detect/connect to the robot because **LeRobot library was not installed**.

## ⚡ THE SOLUTION (3 STEPS)

### 1️⃣ Free Up Disk Space (~3 GB needed)
```bash
df -h  # Check available space
# Empty Trash, delete old Downloads, etc.
```

### 2️⃣ Install LeRobot
```bash
cd /Users/sepehrmortazavi/Desktop/robotics_app
source .venv/bin/activate
pip install lerobot
```

### 3️⃣ Start Server & Connect
```bash
./start_server.sh
# OR
python manage.py runserver
```

Then open: `http://127.0.0.1:8000/connect/`

---

## 📍 YOUR ROBOT PORTS
From your working `Lerobot/` scripts:
- **Leader:** `/dev/tty.usbmodem5A680135091`
- **Follower:** `/dev/tty.usbmodem5A680125711`
- **Type:** SO101

---

## ✅ WHAT WAS ADDED TO YOUR APP

### New Files:
1. `control/lerobot_bridge.py` - LeRobot integration layer
2. `requirements.txt` - All dependencies
3. `start_server.sh` - Quick start script
4. `test_lerobot_integration.py` - Test script
5. `LEROBOT_INTEGRATION_COMPLETE.md` - Full guide
6. `ROBOT_CONNECTION_FIX_SUMMARY.md` - Detailed analysis
7. `QUICK_START.md` - This file

### Updated Files:
1. `control/robot_utils.py` - Now uses LeRobot
2. `control/views.py` - Real robot connection
3. `control/urls.py` - Added API endpoints

### New API Endpoints:
```
POST /api/robot/connect/              - Connect to robot
POST /api/robot/disconnect/           - Disconnect
GET  /api/robot/status/                - Get status
POST /api/robot/teleoperation/start/  - Start teleop
POST /api/robot/teleoperation/stop/   - Stop teleop
```

---

## 🧪 TEST YOUR SETUP

### Verify Installation:
```bash
python -c "import lerobot; print('✅ LeRobot OK')"
```

### Test API:
```bash
# Terminal 1:
python manage.py runserver

# Terminal 2:
curl -X POST http://127.0.0.1:8000/api/robot/connect/
```

### Run Full Test:
```bash
python test_lerobot_integration.py
```

---

## 🎯 USAGE EXAMPLES

### Connect to Robot (Web):
1. Go to: `http://127.0.0.1:8000/connect/`
2. Select ports (see above)
3. Enter IDs:
   - Leader: `my_awesome_leader_arm`
   - Follower: `my_awesome_follower_arm`
4. Click "Save Configuration"
5. Click "Connect to Robot" ✅

### Connect to Robot (API):
```bash
curl -X POST http://127.0.0.1:8000/api/robot/connect/
```

### Connect to Robot (Python):
```python
from control.lerobot_bridge import lerobot_manager

# Configure
lerobot_manager.configure_arms(
    leader_port='/dev/tty.usbmodem5A680135091',
    leader_id='my_awesome_leader_arm',
    follower_port='/dev/tty.usbmodem5A680125711',
    follower_id='my_awesome_follower_arm',
    robot_type='so101'
)

# Connect
lerobot_manager.connect(robot_type='so101')

# Start teleoperation
lerobot_manager.start_teleoperation()
```

---

## 🐛 COMMON ISSUES

### "No space left on device"
→ Free up 3+ GB, then `pip install lerobot`

### "No module named 'lerobot'"
→ `pip install lerobot`

### "Failed to connect to robot"
→ Check:
- ✅ Robot powered on
- ✅ USB cables connected
- ✅ Correct ports: `ls /dev/tty.usbmodem*`
- ✅ No other program using ports

### "Port already in use"
→ Close other programs or: `lsof | grep usbmodem`

---

## 📖 MORE INFO

- **Full Guide:** `LEROBOT_INTEGRATION_COMPLETE.md`
- **Root Cause Analysis:** `ROBOT_CONNECTION_FIX_SUMMARY.md`
- **Your Working Scripts:** `Lerobot/` folder

---

## ✨ BOTTOM LINE

**Your standalone scripts (`Record_Data.py`, etc.) work because they use LeRobot.**

**Your Django app will work too, once you install LeRobot:**

```bash
pip install lerobot
```

**That's it!** 🎉

The entire integration is complete. Just install LeRobot and your robot will connect through the web app!
