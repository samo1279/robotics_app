#!/bin/bash

# Installation script for gym_hil simulation environment
# Based on LeRobot HIL-SERL documentation

echo "🤖 Installing gym_hil Simulation Environment..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one."
fi

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install --upgrade pip

# Install PyTorch with CUDA support (adjust for your CUDA version)
echo "🔥 Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Gymnasium and MuJoCo
echo "🏃 Installing Gymnasium and MuJoCo..."
pip install gymnasium[mujoco]
pip install mujoco>=2.3.0

# Install additional simulation dependencies
echo "🎮 Installing simulation dependencies..."
pip install pygame
pip install imageio
pip install opencv-python
pip install matplotlib
pip install wandb  # For experiment tracking

# Install LeRobot (if not already installed)
echo "🦾 Installing LeRobot..."
pip install lerobot

# Alternatively, install from source for latest features:
# git clone https://github.com/huggingface/lerobot.git
# cd lerobot
# pip install -e ".[hilserl]"

# Verify installations
echo "✅ Verifying installations..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import gymnasium; print(f'Gymnasium version: {gymnasium.__version__}')"
python -c "import mujoco; print(f'MuJoCo version: {mujoco.__version__}')"

# Test simple environment creation
echo "🧪 Testing environment creation..."
python -c "
import gymnasium as gym
try:
    # Test basic gym environment
    env = gym.make('CartPole-v1')
    print('✅ Basic Gymnasium environment works')
    env.close()
except Exception as e:
    print(f'❌ Gymnasium test failed: {e}')

try:
    import mujoco
    print('✅ MuJoCo import successful')
except Exception as e:
    print(f'❌ MuJoCo test failed: {e}')
"

echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure you have a gamepad connected (optional)"
echo "2. Check NVIDIA GPU drivers for CUDA support" 
echo "3. Start the Django server and navigate to Manipulation"
echo "4. Switch to Simulation Mode to test the environment"
echo ""
echo "🔧 Configuration files will be created automatically in:"
echo "   robotics_app/control/simulation_configs/"
echo ""
echo "🎮 Available simulation tasks:"
echo "   - PandaPickCubeGamepad-v0 (with gamepad control)"
echo "   - PandaPickCubeKeyboard-v0 (with keyboard control)"
echo "   - PandaPickCubeBase-v0 (basic environment)"
