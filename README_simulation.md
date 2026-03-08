# 🎮 Gym HIL Simulation Setup for Robotics App

This guide helps you set up the **gym_hil** simulation environment with your Django robotics application, based on the LeRobot Human-In-the-Loop (HIL) reinforcement learning framework.

## 🚀 Quick Start

### 1. Install Dependencies

Run the installation script:

```bash
./install_simulation.sh
```

Or install manually:

```bash
# Install core simulation packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install gymnasium[mujoco]
pip install mujoco>=3.3.0
pip install pygame imageio opencv-python matplotlib
```

### 2. Test Installation

```bash
# Fix OpenMP issue (macOS)
export KMP_DUPLICATE_LIB_OK=TRUE

# Run tests
python test_simulation.py
```

### 3. Start Django Server

```bash
# Start with OpenMP fix
KMP_DUPLICATE_LIB_OK=TRUE python manage.py runserver
```

### 4. Access Simulation

Navigate to: **http://127.0.0.1:8000/manipulation/?mode=simulation**

## 🎯 Available Features

### Simulation Tasks
- **PandaPickCubeGamepad-v0** - Control with gamepad
- **PandaPickCubeKeyboard-v0** - Control with keyboard  
- **PandaPickCubeBase-v0** - Basic environment

### Control Modes
- **Gamepad Control** - Use connected gamepad/controller
- **Keyboard Control** - WASD + QE keys for movement

### Training Features
- **Dataset Recording** - Collect demonstration data
- **Policy Training** - Human-in-the-loop RL training
- **Real-time Interaction** - Direct manipulation during learning

## 🎮 Controls

### Keyboard Controls (Simulation Mode)
- **W/A/S/D** - Forward/Left/Back/Right movement
- **Q/E** - Up/Down movement  
- **I/J/K/L** - Pitch/Yaw rotation
- **Space** - Toggle gripper
- **Enter** - Activate gripper

### Gamepad Controls
- Connect any standard gamepad/controller
- Left stick: X/Y movement
- Right stick: Rotation
- Triggers: Z movement and gripper

## 🔧 Configuration

Configuration files are automatically created in:
```
robotics_app/control/simulation_configs/
```

### Example Configuration:
```json
{
  "env": {
    "type": "gym_manipulator",
    "name": "gym_hil",
    "task": "PandaPickCubeGamepad-v0",
    "fps": 10,
    "processor": {
      "control_mode": "gamepad",
      "gripper": {
        "use_gripper": true,
        "gripper_penalty": -0.02
      },
      "reset": {
        "control_time_s": 15.0,
        "fixed_reset_joint_positions": [0.0, 0.195, 0.0, -2.43, 0.0, 2.62, 0.785]
      }
    }
  },
  "device": "cuda"
}
```

## 🎓 Training Workflow

### 1. Start Simulation
1. Go to manipulation page
2. Switch to "Simulation Mode"
3. Select task (e.g., PandaPickCubeGamepad-v0)
4. Click "Start Simulation"

### 2. Record Dataset
1. Set number of episodes (e.g., 10)
2. Click "Record Dataset"
3. Control the robot to demonstrate tasks
4. Dataset saved automatically

### 3. Train Policy
1. Click "Train Policy" 
2. Actor and learner servers start
3. Human interventions during training
4. Real-time policy updates

## 🛠️ Troubleshooting

### OpenMP Error (macOS)
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
```

### CUDA Not Available
- Simulation runs on CPU (slower but works)
- For GPU: Install CUDA toolkit and PyTorch with CUDA

### MuJoCo Issues
```bash
pip install mujoco>=3.3.0
pip uninstall mujoco-py  # Remove old version
```

### Gamepad Not Detected
- Check USB connection
- Install gamepad drivers
- Test with other applications first

## 🔗 Integration with Real Robots

The simulation integrates seamlessly with your real robot setup:

1. **Test in Simulation** - Develop and test policies safely
2. **Transfer to Real** - Switch back to "Real Robot Mode"
3. **Use Same Interface** - Consistent controls and workflows
4. **Combined Training** - Mix simulation and real robot data

## 📊 File Structure

```
robotics_app/
├── control/
│   ├── simulation_utils.py      # Simulation management
│   ├── simulation_configs/      # Auto-generated configs
│   └── templates/control/
│       └── manipulation.html    # Dual mode interface
├── test_simulation.py           # Test simulation setup
├── install_simulation.sh        # Installation script  
└── README_simulation.md         # This file
```

## 🎉 Success!

If everything is working, you should see:
- ✅ Django server running without errors
- ✅ Simulation mode accessible at `/manipulation/?mode=simulation`
- ✅ MuJoCo environments loading successfully
- ✅ Configuration files generated automatically
- ✅ Smooth switching between real robot and simulation modes

## 📚 Learn More

- [LeRobot Documentation](https://huggingface.co/docs/lerobot/index)
- [HIL-SERL Paper](https://arxiv.org/abs/2410.21845)
- [MuJoCo Documentation](https://mujoco.readthedocs.io/)
- [Gymnasium Documentation](https://gymnasium.farama.org/)

Happy simulating! 🤖🎮
