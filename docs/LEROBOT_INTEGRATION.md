# LeRobot Integration Guide for SO-101 Robotic Arm

## Overview

This Django application integrates **LeRobot** standards and methodologies for controlling and training the **SO-101 robotic arm**. LeRobot is Hugging Face's comprehensive robotics framework that provides state-of-the-art tools for teleoperation, imitation learning, reinforcement learning, and policy deployment.

---

## Table of Contents

1. [SO-101 Hardware Specifications](#so-101-hardware-specifications)
2. [Installation & Setup](#installation--setup)
3. [Port Discovery & Configuration](#port-discovery--configuration)
4. [Calibration Workflow](#calibration-workflow)
5. [Teleoperation](#teleoperation)
6. [Data Collection](#data-collection)
7. [Training Policies](#training-policies)
   - [ACT (Action Chunking Transformers)](#act-action-chunking-transformers)
   - [Pi0 (3B VLM Foundation Model)](#pi0-3b-vlm-foundation-model)
   - [Pi0.5 (Open-World Generalization)](#pi05-open-world-generalization)
   - [SmolVLA (Lightweight 450M Model)](#smolvla-lightweight-450m-model)
8. [Reinforcement Learning with HIL-SERL](#reinforcement-learning-with-hil-serl)
9. [Asynchronous Inference](#asynchronous-inference)
10. [Simulation Environments](#simulation-environments)

---

## SO-101 Hardware Specifications

### Leader Arm (Teleoperation)
The **leader arm** features reduced gearing for easy manual manipulation during data collection and human interventions:

| Joint ID | Joint Name | Motor Type | Gearing Ratio |
|----------|------------|------------|---------------|
| 1 | Shoulder Pan | Feetech STS3215 | **1/191** |
| 2 | Shoulder Lift | Feetech STS3215 | **1/345** |
| 3 | Elbow Flex | Feetech STS3215 | **1/191** |
| 4 | Wrist Flex | Feetech STS3215 | **1/147** |
| 5 | Wrist Roll | Feetech STS3215 | **1/147** |
| 6 | Gripper | Feetech STS3215 | **1/147** |

**Purpose**: Manual teleoperation, demonstration collection, and human-in-the-loop interventions during RL training.

### Follower Arm (Policy Execution)
The **follower arm** has uniform gearing for precise policy control:

| Joint ID | Joint Name | Motor Type | Gearing Ratio |
|----------|------------|------------|---------------|
| 1-6 | All Joints | Feetech STS3215 | **1/345** |

**Purpose**: Autonomous policy execution with high precision and repeatability.

---

## Installation & Setup

### 1. Install LeRobot with Feetech Support

```bash
pip install lerobot[feetech]
```

### 2. Install Optional Dependencies

- **Simulation (MuJoCo)**: `pip install -e ".[hilserl]"`
- **SmolVLA Policy**: `pip install -e ".[smolvla]"`
- **Pi0/Pi0.5 Policies**: `pip install -e ".[pi]"`
- **Async Inference**: `pip install -e ".[async]"`

### 3. System Requirements

- **Python**: 3.10+
- **ffmpeg**: Required for video processing
- **CUDA GPU**: Recommended for training (can use MPS on macOS or CPU)
- **Gamepad**: Logitech F710 recommended for teleoperation

---

## Port Discovery & Configuration

### Step 1: Find Connected Arms

Use LeRobot's port discovery tool:

```bash
lerobot-find-port
```

**Expected Output**:
```
Found port /dev/ttyACM0 with motors [1, 2, 3, 4, 5, 6]
Found port /dev/ttyACM1 with motors [1, 2, 3, 4, 5, 6]
```

### Step 2: Identify Leader vs Follower

- **Leader Arm**: Lower resistance when manually moved (reduced gearing)
- **Follower Arm**: Higher resistance (uniform 1/345 gearing)

### Step 3: Configure in Django Application

1. Navigate to **Connect** page
2. Select ports for leader and follower arms
3. Assign unique IDs (e.g., `my_red_leader_arm`, `my_blue_follower_arm`)
4. Test connections
5. Save configuration to `robot_config.json`

---

## Calibration Workflow

### LeRobot Calibration Protocol

LeRobot requires calibration to establish zero positions and range of motion:

```bash
lerobot-calibrate --port /dev/ttyACM0 --arm-id follower_so101
```

### Calibration Steps

1. **Zero Position**: Move arm to neutral posture (all joints at mechanical zero)
2. **Full Range Motion**: Slowly move each joint through its complete range
3. **Verification**: LeRobot validates joint limits and creates calibration file
4. **Storage**: Calibration saved to `~/.cache/lerobot/calibration/{arm_id}.json`

### Visual Calibration Guide

The Django **Calibration** page provides:
- Interactive visual guide showing SO-101 joint configuration
- Motor specification tables (leader vs follower gearing)
- Step-by-step calibration instructions
- Real-time calibration status

---

## Teleoperation

### Three-Pipeline Architecture

LeRobot uses a three-stage processing pipeline:

1. **Teleop Action** → Human/gamepad commands in end-effector space
2. **Dataset Action** → Processed actions stored in dataset format
3. **Robot Command** → Low-level motor commands sent to hardware

### Teleoperation Modes

#### 1. Gamepad Control (Recommended)

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_follower \
  --teleop.type=gamepad \
  --dataset.repo_id=${HF_USER}/my_dataset
```

**Gamepad Controls**:
- **Left Stick**: X-Y movement
- **Right Stick**: Z movement + rotation
- **Triggers**: Gripper open/close
- **RB (Right Bumper)**: Enable human takeover (hold to control)
- **Start**: Mark episode as success
- **Back**: Mark episode as failure

#### 2. Leader Arm Control

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_follower \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=my_leader
```

#### 3. Keyboard Control (Fallback)

- **Arrow Keys**: X-Y plane movement
- **Shift/Shift_R**: Z-axis movement
- **Ctrl/Left Ctrl**: Gripper control
- **Spacebar**: Enable control
- **S**: Success
- **ESC**: Failure/Exit

---

## Data Collection

### Recording Demonstrations

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_blue_follower_arm \
  --robot.cameras="{ front: {type: opencv, index_or_path: 8, width: 640, height: 480, fps: 30}}" \
  --dataset.single_task="Pick up the cube and place it in the bin" \
  --dataset.repo_id=${HF_USER}/pick_place_dataset \
  --dataset.num_episodes=50
```

### Dataset Best Practices

- **Minimum Episodes**: 50 for simple tasks, 100+ for complex tasks
- **Variation**: Record multiple object positions/orientations
- **Quality**: Ensure consistent successful demonstrations
- **Task Description**: Clear natural language description of task goal

### Dataset Format (LeRobotDataset v3.0)

```python
{
  "observation.state": [q1, q2, q3, q4, q5, q6],  # Joint positions
  "observation.images.front": numpy.ndarray,      # Camera images
  "action": [q1_target, q2_target, ..., gripper], # Target joint positions
  "episode_index": int,
  "frame_index": int,
  "timestamp": float,
  "next.reward": float,  # 1.0 for success, 0.0 for failure
  "next.done": bool
}
```

---

## Training Policies

### ACT (Action Chunking Transformers)

**Best for**: Fast training, sample efficiency, simple manipulation tasks

#### Key Features
- **Parameters**: 80M
- **Training Time**: ~1 hour on A100 for 100k steps
- **Data Efficiency**: Works with 50-100 demos
- **Vision Backbone**: ResNet-18
- **Action Chunking**: Predicts 100 future actions per observation

#### Training Command

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/pick_place_dataset \
  --policy.type=act \
  --output_dir=outputs/train/act_so101 \
  --job_name=act_so101 \
  --policy.device=cuda \
  --batch_size=8 \
  --steps=100000 \
  --wandb.enable=true
```

#### Hyperparameters
- `chunk_size`: 100 (action chunk length)
- `n_action_steps`: 100
- `dim_model`: 512
- `n_heads`: 8
- `learning_rate`: 1e-4

---

### Pi0 (3B VLM Foundation Model)

**Best for**: Cross-embodiment transfer, vision-language understanding, generalization

#### Key Features
- **Parameters**: 3B (vision-language model)
- **Training**: Pre-trained on 8 robot platforms
- **Architecture**: Flow matching for action generation
- **Frequency**: 50 Hz control loop
- **License**: Apache 2.0

#### Training Command

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/my_dataset \
  --policy.type=pi0 \
  --policy.pretrained_path=lerobot/pi0_base \
  --output_dir=outputs/train/pi0_so101 \
  --job_name=pi0_so101 \
  --policy.device=cuda \
  --batch_size=16 \
  --steps=50000 \
  --wandb.enable=true
```

#### Flow Matching
Pi0 uses **flow matching** instead of traditional regression, enabling:
- Multimodal action distributions
- Better handling of ambiguous situations
- Smoother trajectory generation

---

### Pi0.5 (Open-World Generalization)

**Best for**: Novel environments, semantic understanding, household/office tasks

#### Key Features
- **Open-World Generalization**: Trained on heterogeneous data (web, verbal instructions, cross-embodiment)
- **Curriculum Learning**: Physical + semantic + environmental generalization
- **Mobile Manipulation**: ~400 hours of mobile robot data
- **Multi-Environment**: Static robots across diverse homes

#### Training Command

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/my_dataset \
  --policy.type=pi05 \
  --policy.pretrained_path=lerobot/pi05_base \
  --output_dir=outputs/train/pi05_so101 \
  --job_name=pi05_so101 \
  --policy.compile_model=true \
  --policy.gradient_checkpointing=true \
  --policy.dtype=bfloat16 \
  --batch_size=32 \
  --steps=3000 \
  --wandb.enable=true
```

#### Normalization Requirements

If dataset not pre-converted with quantiles:
```bash
python src/lerobot/datasets/v30/augment_dataset_quantile_stats.py \
  --repo-id=${HF_USER}/my_dataset
```

Or use mean-std normalization:
```bash
--policy.normalization_mapping='{"ACTION": "MEAN_STD", "STATE": "MEAN_STD", "VISUAL": "IDENTITY"}'
```

---

### SmolVLA (Lightweight 450M Model)

**Best for**: Resource-constrained environments, real-time deployment, fast inference

#### Key Features
- **Parameters**: 450M (10x smaller than Pi0)
- **Memory**: ~2GB at inference time
- **Training Time**: ~4 hours on A100 for 20k steps
- **Architecture**: Vision encoder + action expert
- **Input**: Multi-camera + state + language instruction

#### Training Command

```bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=${HF_USER}/my_dataset \
  --batch_size=64 \
  --steps=20000 \
  --output_dir=outputs/train/smolvla_so101 \
  --job_name=smolvla_so101 \
  --policy.device=cuda \
  --wandb.enable=true
```

#### Data Requirements
- **Minimum**: 50 episodes
- **Variation**: 10 episodes per object position/variation
- **Example Dataset**: [SVLA SO100 PickPlace](https://huggingface.co/lerobot/svla_so100_pickplace)

---

## Reinforcement Learning with HIL-SERL

**HIL-SERL** (Human-in-the-Loop Sample-Efficient Reinforcement Learning) combines:
1. Offline demonstrations
2. Vision-based reward classifier
3. Online RL with human interventions

### Workflow

#### 1. Collect Initial Demonstrations (15-30 episodes)

```bash
python -m lerobot.rl.gym_manipulator \
  --config_path=env_config.json
```

**Configuration** (`env_config.json`):
```json
{
  "env": {
    "type": "gym_manipulator",
    "name": "real_robot",
    "fps": 10,
    "robot": {
      "type": "so101_follower",
      "port": "/dev/ttyACM0",
      "id": "my_follower"
    },
    "teleop": {
      "type": "gamepad",
      "use_gripper": true
    },
    "processor": {
      "control_mode": "gamepad",
      "reset": {
        "reset_time_s": 5.0,
        "control_time_s": 20.0,
        "terminate_on_success": false  // For reward classifier training
      }
    }
  },
  "dataset": {
    "repo_id": "${HF_USER}/hilserl_demos",
    "num_episodes_to_record": 20
  },
  "mode": "record"
}
```

#### 2. Train Reward Classifier

```bash
lerobot-train \
  --config_path=reward_classifier_config.json
```

**Reward Classifier Config**:
```json
{
  "policy": {
    "type": "reward_classifier",
    "model_name": "helper2424/resnet10",
    "num_cameras": 2,
    "num_classes": 2,
    "hidden_dim": 256,
    "learning_rate": 1e-4
  }
}
```

#### 3. Determine Workspace Bounds

```bash
lerobot-find-joint-limits \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1
```

**Output**:
```
Max ee position [0.2417, 0.2012, 0.1027]
Min ee position [0.1663, -0.0823, 0.0336]
```

Add to config:
```json
{
  "env": {
    "processor": {
      "inverse_kinematics": {
        "end_effector_bounds": {
          "min": [0.16, -0.08, 0.03],
          "max": [0.24, 0.20, 0.10]
        }
      }
    }
  }
}
```

#### 4. Start Actor-Learner Training

**Terminal 1 - Learner**:
```bash
python -m lerobot.rl.learner \
  --config_path=train_config_hilserl.json
```

**Terminal 2 - Actor**:
```bash
python -m lerobot.rl.actor \
  --config_path=train_config_hilserl.json
```

**Training Config** (`train_config_hilserl.json`):
```json
{
  "policy": {
    "type": "sac",
    "device": "cuda",
    "temperature_init": 1e-2,
    "storage_device": "cuda",  // Keep weights on GPU
    "actor_learner_config": {
      "policy_parameters_push_frequency": 2  // Update actor every 2s
    }
  },
  "env": {
    "processor": {
      "reward_classifier": {
        "pretrained_path": "path/to/reward_classifier",
        "success_threshold": 0.7
      }
    }
  }
}
```

#### 5. Human Interventions

- **Gamepad**: Press **RB** to take over, release to return control to policy
- **Keyboard**: Press **Spacebar** to toggle control
- **Strategy**: 
  - Allow exploration in early episodes
  - Intervene briefly to correct mistakes
  - Reduce interventions as policy improves

#### Key Hyperparameters

- `temperature_init`: 1e-2 (higher = more exploration)
- `policy_parameters_push_frequency`: 2s (update frequency)
- `storage_device`: "cuda" (keep weights on GPU for speed)

---

## Asynchronous Inference

**Async inference** decouples action prediction from execution, eliminating idle frames.

### Architecture

- **Policy Server**: Runs on powerful GPU machine
- **Robot Client**: Runs on robot controller, sends observations, receives actions

### Setup

**Terminal 1 - Policy Server**:
```bash
python -m lerobot.async_inference.policy_server \
  --host=127.0.0.1 \
  --port=8080
```

**Terminal 2 - Robot Client**:
```bash
python -m lerobot.async_inference.robot_client \
  --server_address=127.0.0.1:8080 \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower_so101 \
  --robot.cameras="{ laptop: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
  --task="Pick up the cube" \
  --policy_type=smolvla \
  --pretrained_name_or_path=lerobot/smolvla_base \
  --policy_device=cuda \
  --actions_per_chunk=50 \
  --chunk_size_threshold=0.5 \
  --aggregate_fn_name=weighted_average \
  --debug_visualize_queue_size=True
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `actions_per_chunk` | 50 | Number of actions predicted at once |
| `chunk_size_threshold` | 0.5 | When queue ≤50% full, send new observation |
| `aggregate_fn_name` | weighted_average | How to blend overlapping action chunks |

### Tuning Guidelines

1. **Choose computational resources**: Pi0 (14GB VRAM), SmolVLA (2GB VRAM), ACT (<1GB VRAM)
2. **Adjust FPS**: Lower FPS if queue frequently empties
3. **Tune threshold**: 
   - `0.0` → Sequential (sync-like)
   - `0.5-0.6` → Balanced (recommended)
   - `1.0` → Maximum adaptability (high bandwidth)

---

## Simulation Environments

### Imitation Learning in Simulation

#### 1. Install Simulation Dependencies

```bash
pip install -e ".[hilserl]"
```

#### 2. Record Dataset in Simulation

```bash
python -m lerobot.rl.gym_manipulator \
  --config_path=sim_il_config.json
```

**Config** (`sim_il_config.json`):
```json
{
  "env": {
    "type": "gym_manipulator",
    "name": "gym_hil",
    "task": "PandaPickCubeGamepad-v0",
    "fps": 10
  },
  "dataset": {
    "repo_id": "${HF_USER}/il_gym",
    "num_episodes_to_record": 30
  },
  "mode": "record"
}
```

#### 3. Train Policy

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/il_gym \
  --policy.type=act \
  --output_dir=outputs/train/il_sim_test \
  --policy.device=cuda \
  --steps=100000
```

#### 4. Evaluate in Simulation

```bash
python -m lerobot.rl.eval_policy \
  --config_path=eval_config_gym_hil.json
```

---

## Django Application Integration

### Updated Features

1. **Connect Page** (`/connect/`):
   - Port discovery guide using `lerobot-find-port`
   - Leader/follower arm selection with custom port support
   - Motor specification tables (gearing differences)
   - Connection testing (AJAX endpoints)
   - Configuration save to `robot_config.json`

2. **Calibration Page** (`/calibrate/`):
   - SO-101 visual calibration guide
   - Motor configuration tables (leader vs follower)
   - 4-step calibration workflow
   - Real-time calibration status

3. **Backend Views** (`control/views.py`):
   - `test_arm_connection()`: Test leader/follower connectivity
   - `save_robot_config()`: Persist robot configuration

4. **URL Routes** (`control/urls.py`):
   - `/api/test_arm/`: Arm connection testing
   - `/api/save_config/`: Configuration persistence

### Styling

Modern iOS 16-inspired design with:
- Glassmorphism cards
- Smooth animations (fade-in, slide-up)
- Responsive grid layouts
- Color-coded motor specifications
- Interactive forms with validation

---

## Next Steps

1. **Implement Feetech SDK Integration**: Replace simulated motor detection with real Feetech SDK calls
2. **Calibration Backend**: Integrate `lerobot-calibrate` into Django backend
3. **Training Dashboard**: Add real-time WandB integration for monitoring
4. **Async Inference UI**: Web interface for policy server deployment
5. **Dataset Visualization**: Embed LeRobot dataset visualizer

---

## References

- [LeRobot Documentation](https://huggingface.co/docs/lerobot)
- [SO-101 Hardware Guide](https://huggingface.co/docs/lerobot/so101)
- [ACT Policy](https://huggingface.co/docs/lerobot/act)
- [Pi0 Policy](https://huggingface.co/docs/lerobot/pi0)
- [SmolVLA](https://huggingface.co/docs/lerobot/smolvla)
- [HIL-SERL](https://huggingface.co/docs/lerobot/hilserl)
- [Async Inference](https://huggingface.co/docs/lerobot/async)

---

**License**: Apache 2.0 (consistent with LeRobot framework)
