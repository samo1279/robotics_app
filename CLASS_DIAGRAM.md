# Robotics Application - Class Diagram

This document provides a comprehensive class diagram showing all models, utility classes, and their relationships in the Django robotics application.

---

## 📊 Class Diagram Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ROBOTICS APPLICATION ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      User            │
│ (Django Auth)        │
├──────────────────────┤
│ +username: String    │
│ +email: String       │
│ +password: String    │
│ +is_active: Boolean  │
│ +is_staff: Boolean   │
│ +date_joined: DateTime│
└──────────┬───────────┘
           │ owns
           │ creates
           │
           ▼
┌──────────────────────┐         1:1          ┌──────────────────────┐
│      Robot           │◄─────────────────────┤   Calibration        │
├──────────────────────┤                      ├──────────────────────┤
│ +id: Integer (PK)    │                      │ +id: Integer (PK)    │
│ +name: String        │                      │ +robot: ForeignKey   │
│ +type: String        │                      │ +leader_arm_serial:  │
│ +port: String        │                      │   String             │
│ +ip_address: IPAddr  │                      │ +follower_arm_serial:│
│ +is_connected: Bool  │                      │   String             │
│ +last_seen: DateTime │                      │ +calibration_data:   │
└──────────┬───────────┘                      │   JSONField          │
           │                                  │ +calibrated_at:      │
           │ 1:N                              │   DateTime           │
           │                                  └──────────────────────┘
           │
           │ has many
           │
           ▼
┌──────────────────────┐         N:1          ┌──────────────────────┐
│   MotionPattern      │─────────────────────►│     Dataset          │
├──────────────────────┤   source_pattern     ├──────────────────────┤
│ +id: Integer (PK)    │                      │ +id: Integer (PK)    │
│ +name: String        │                      │ +name: String        │
│ +description: Text   │                      │ +description: Text   │
│ +robot: ForeignKey   │                      │ +source_pattern:     │
│ +sequence_data:      │                      │   ForeignKey         │
│   JSONField          │                      │ +created_at: DateTime│
│ +created_at: DateTime│                      │ +path: String        │
└──────────────────────┘                      └──────────┬───────────┘
                                                         │
                                                         │ 1:N
                                                         │
                                                         ▼
                                              ┌──────────────────────┐
                                              │   TrainingRun        │
                                              ├──────────────────────┤
                                              │ +id: Integer (PK)    │
                                              │ +dataset: ForeignKey │
                                              │ +status: String      │
                                              │   (PENDING/RUNNING/  │
                                              │    COMPLETED/FAILED) │
                                              │ +hyperparameters:    │
                                              │   JSONField          │
                                              │ +start_time: DateTime│
                                              │ +end_time: DateTime  │
                                              │ +model_path: String  │
                                              │ +training_log: Text  │
                                              └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│                              UTILITY CLASSES                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐                      ┌──────────────────────┐
│ CalibrationManager   │                      │   DataRecorder       │
├──────────────────────┤                      ├──────────────────────┤
│ +calibrated: Boolean │                      │ +dataset_dir: String │
│ +calibration_data:   │                      │ +recording: Boolean  │
│   Dict               │                      │ +thread: Thread      │
│ +config_file: String │                      │ +current_file: String│
│                      │                      │ +sample_rate: Float  │
│ +calibrate(): Dict   │                      │ +episode_count: Int  │
│ +save_config(): Bool │                      │                      │
│ +load_config(): Dict │                      │ +start_recording():  │
└──────────────────────┘                      │   String             │
                                              │ +stop_recording():   │
                                              │   Int                │
                                              │ +_record_loop(): None│
                                              └──────────────────────┘

┌──────────────────────┐                      ┌──────────────────────┐
│   ArmController      │                      │  TeleopController    │
├──────────────────────┤                      ├──────────────────────┤
│ +leader_arm: Robot   │                      │ +leader: Robot       │
│ +follower_arm: Robot │                      │ +follower: Robot     │
│ +connected: Boolean  │                      │ +running: Boolean    │
│ +control_thread:     │                      │ +control_thread:     │
│   Thread             │                      │   Thread             │
│ +leader_positions:   │                      │ +control_frequency:  │
│   List[Float]        │                      │   Float              │
│ +follower_positions: │                      │                      │
│   List[Float]        │                      │ +start_teleop(): Bool│
│                      │                      │ +stop_teleop(): None │
│ +connect(): Boolean  │                      │ +_control_loop(): None│
│ +disconnect(): None  │                      └──────────────────────┘
│ +read_leader(): List │
│ +write_follower():   │
│   None               │
│ +_control_loop(): None│
└──────────────────────┘

┌──────────────────────┐                      ┌──────────────────────┐
│   MotionRecorder     │                      │  MotionReplayer      │
├──────────────────────┤                      ├──────────────────────┤
│ +robot: Robot        │                      │ +robot: Robot        │
│ +recording: Boolean  │                      │ +motion_data: List   │
│ +recorded_motions:   │                      │ +playing: Boolean    │
│   List               │                      │ +playback_thread:    │
│ +sample_rate: Float  │                      │   Thread             │
│                      │                      │                      │
│ +start_recording():  │                      │ +load_motion(): Bool │
│   Bool               │                      │ +play_motion(): Bool │
│ +stop_recording():   │                      │ +stop_playback(): None│
│   Dict               │                      │ +_playback_loop(): None│
│ +save_motion(): String│                     └──────────────────────┘
└──────────────────────┘

┌──────────────────────┐                      ┌──────────────────────┐
│  DatasetRecorder     │                      │  SimulationManager   │
├──────────────────────┤                      ├──────────────────────┤
│ +controller:         │                      │ +env: Gymnasium      │
│   ArmController      │                      │ +env_name: String    │
│ +recorder:           │                      │ +headless: Boolean   │
│   DataRecorder       │                      │ +sim_running: Boolean│
│ +recording: Boolean  │                      │ +observation_space:  │
│ +dataset_name: String│                      │   Space              │
│                      │                      │ +action_space: Space │
│ +start_dataset():    │                      │                      │
│   String             │                      │ +load_env(): Boolean │
│ +stop_dataset(): Int │                      │ +reset(): Array      │
│ +add_episode(): None │                      │ +step(): Tuple       │
└──────────────────────┘                      │ +close(): None       │
                                              │ +render(): None      │
                                              └──────────────────────┘

┌──────────────────────┐
│  IsaacSimManager     │
├──────────────────────┤
│ +isaac_sim_path: Str │
│ +config_path: String │
│ +sim_process: Process│
│ +is_running: Boolean │
│ +env_config: Dict    │
│                      │
│ +check_isaac_sim():  │
│   Boolean            │
│ +start_simulation(): │
│   Boolean            │
│ +stop_simulation():  │
│   None               │
│ +get_status(): Dict  │
└──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FORMS & VIEWS                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│    DatasetForm       │
│  (Django Form)       │
├──────────────────────┤
│ +name: CharField     │
│ +description:        │
│   CharField          │
│ +num_episodes:       │
│   IntegerField       │
│                      │
│ +clean(): Dict       │
│ +save(): Dataset     │
└──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RELATIONSHIPS SUMMARY                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

1. User → Robot (1:N)
   - One user can own/create multiple robots
   
2. Robot → Calibration (1:1)
   - Each robot has one calibration record
   - Calibration is deleted when robot is deleted (CASCADE)
   
3. Robot → MotionPattern (1:N)
   - One robot can have multiple recorded motion patterns
   - Motion patterns are deleted when robot is deleted (CASCADE)
   
4. MotionPattern → Dataset (N:1, optional)
   - Multiple datasets can reference the same motion pattern
   - Dataset can exist without a source pattern (SET_NULL)
   
5. Dataset → TrainingRun (1:N)
   - One dataset can have multiple training runs
   - Training runs are deleted when dataset is deleted (CASCADE)

6. Utility Classes:
   - CalibrationManager: Manages robot calibration process
   - DataRecorder: Records robot data to JSONL files
   - ArmController: Controls leader-follower arm pairs
   - TeleopController: Provides teleoperation functionality
   - MotionRecorder: Records robot motion sequences
   - MotionReplayer: Replays recorded motions
   - DatasetRecorder: Combines controller + recorder for dataset creation
   - SimulationManager: Manages Gymnasium simulation environments
   - IsaacSimManager: Manages NVIDIA Isaac Sim integration


┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                           │
└─────────────────────────────────────────────────────────────────────────────────┘

1. CALIBRATION FLOW:
   User → Robot → CalibrationManager → Calibration (DB)

2. MOTION RECORDING FLOW:
   User → Robot → MotionRecorder → MotionPattern (DB)

3. TELEOPERATION FLOW:
   User → TeleopController → ArmController → Leader/Follower Robots

4. DATASET CREATION FLOW:
   User → DatasetRecorder → DataRecorder + ArmController → Dataset (DB) + JSONL files

5. TRAINING FLOW:
   User → Dataset → TrainingRun (DB) → AI Model (filesystem)

6. SIMULATION FLOW:
   User → SimulationManager/IsaacSimManager → Gymnasium Env → Observations/Actions


┌─────────────────────────────────────────────────────────────────────────────────┐
│                          FILE STORAGE STRUCTURE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

/robotics_app/
├── db.sqlite3                          # Django database (models data)
├── robot_config.json                   # Robot calibration config
├── dataset/                            # Training datasets
│   ├── dataset_20250930_155213.jsonl
│   ├── test_20250930_160301.jsonl
│   └── ...
├── training/                           # Trained AI models
│   ├── test_20250930_160345_model.bin
│   ├── test_comprehensive_model.bin
│   └── ...
└── simulation_configs/                 # Simulation configurations
    ├── sim_config_PandaPickCube.json
    └── ...


┌─────────────────────────────────────────────────────────────────────────────────┐
│                         KEY DESIGN PATTERNS                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

1. **MVC Pattern**: Django's MTV (Model-Template-View) architecture
   - Models: Database entities (Robot, Calibration, etc.)
   - Views: Business logic and request handling
   - Templates: HTML presentation layer

2. **Manager Pattern**: Utility classes act as service managers
   - CalibrationManager, DataRecorder, ArmController, etc.
   - Encapsulate complex operations
   - Separate concerns from models

3. **Observer Pattern**: Threading for real-time control
   - TeleopController runs control loop in separate thread
   - DataRecorder runs recording loop in separate thread
   - Non-blocking operations

4. **Strategy Pattern**: Multiple simulation backends
   - SimulationManager (Gymnasium)
   - IsaacSimManager (NVIDIA Isaac Sim)
   - Interchangeable simulation strategies

5. **Repository Pattern**: Models + QuerySets
   - Django ORM provides repository functionality
   - Clean data access layer

6. **Factory Pattern**: Dataset/Model creation
   - DatasetRecorder creates datasets with proper structure
   - TrainingRun creates and manages model files
```

---

## 📋 Complete Attribute List

### Database Models (Django ORM)

#### 1. **Robot**
- `id`: Integer (Primary Key, Auto)
- `name`: String (max 100 chars, unique)
- `type`: String (max 50 chars, default="Generic Arm")
- `port`: String (max 100 chars, blank allowed)
- `ip_address`: IP Address (nullable)
- `is_connected`: Boolean (default=False)
- `last_seen`: DateTime (auto-updated)

**Relationships:**
- `calibration`: One-to-One → Calibration
- `motion_patterns`: One-to-Many → MotionPattern

---

#### 2. **Calibration**
- `id`: Integer (Primary Key, Auto)
- `robot`: ForeignKey → Robot (CASCADE)
- `leader_arm_serial`: String (max 100 chars, blank)
- `follower_arm_serial`: String (max 100 chars, blank)
- `calibration_data`: JSONField (detailed parameters)
- `calibrated_at`: DateTime (auto on create)

**Relationships:**
- `robot`: One-to-One ← Robot

---

#### 3. **MotionPattern**
- `id`: Integer (Primary Key, Auto)
- `name`: String (max 255 chars)
- `description`: Text (blank allowed)
- `robot`: ForeignKey → Robot (CASCADE)
- `sequence_data`: JSONField (joint states + timestamps)
- `created_at`: DateTime (auto on create)

**Relationships:**
- `robot`: Many-to-One → Robot
- `datasets`: One-to-Many → Dataset (reverse)

---

#### 4. **Dataset**
- `id`: Integer (Primary Key, Auto)
- `name`: String (max 255 chars)
- `description`: Text (blank allowed)
- `source_pattern`: ForeignKey → MotionPattern (SET_NULL, nullable)
- `created_at`: DateTime (auto on create)
- `path`: String (max 1024 chars, filesystem path)

**Relationships:**
- `source_pattern`: Many-to-One → MotionPattern (optional)
- `training_runs`: One-to-Many → TrainingRun

---

#### 5. **TrainingRun**
- `id`: Integer (Primary Key, Auto)
- `dataset`: ForeignKey → Dataset (CASCADE)
- `status`: String (choices: PENDING/RUNNING/COMPLETED/FAILED)
- `hyperparameters`: JSONField (nullable)
- `start_time`: DateTime (nullable)
- `end_time`: DateTime (nullable)
- `model_path`: String (max 1024 chars, blank)
- `training_log`: Text (blank)

**Relationships:**
- `dataset`: Many-to-One → Dataset

---

### Utility Classes

#### 6. **CalibrationManager**
- `calibrated`: Boolean (default=False)
- `calibration_data`: Dict (default empty)
- `config_file`: String (default="robot_config.json")

**Methods:**
- `calibrate()`: Dict - Perform calibration, return data
- `save_config()`: Boolean - Save to JSON file
- `load_config()`: Dict - Load from JSON file

---

#### 7. **DataRecorder**
- `dataset_dir`: String - Target directory
- `recording`: Boolean - Recording state
- `thread`: Thread (optional) - Background thread
- `current_file`: String (optional) - Active file path
- `sample_rate`: Float (default=10.0 Hz)
- `episode_count`: Integer - Episodes recorded

**Methods:**
- `start_recording(name)`: String - Begin recording, return filepath
- `stop_recording()`: Integer - Stop recording, return episode count
- `_record_loop()`: None - Internal recording loop

---

#### 8. **ArmController**
- `leader_arm`: Object - Leader robot
- `follower_arm`: Object - Follower robot
- `connected`: Boolean - Connection state
- `control_thread`: Thread (optional) - Control loop thread
- `leader_positions`: List[Float] - Current leader positions
- `follower_positions`: List[Float] - Current follower positions

**Methods:**
- `connect()`: Boolean - Connect to both arms
- `disconnect()`: None - Disconnect both arms
- `read_leader()`: List[Float] - Read leader positions
- `write_follower(positions)`: None - Write to follower
- `_control_loop()`: None - Internal control loop

---

#### 9. **TeleopController**
- `leader`: Object - Leader robot
- `follower`: Object - Follower robot
- `running`: Boolean - Teleop active
- `control_thread`: Thread (optional) - Control thread
- `control_frequency`: Float (default=30 Hz)

**Methods:**
- `start_teleop()`: Boolean - Start teleoperation
- `stop_teleop()`: None - Stop teleoperation
- `_control_loop()`: None - Internal control loop

---

#### 10. **MotionRecorder**
- `robot`: Object - Target robot
- `recording`: Boolean - Recording state
- `recorded_motions`: List - Motion buffer
- `sample_rate`: Float - Sampling frequency

**Methods:**
- `start_recording()`: Boolean - Begin recording
- `stop_recording()`: Dict - Stop and return data
- `save_motion(filename)`: String - Save to file

---

#### 11. **MotionReplayer**
- `robot`: Object - Target robot
- `motion_data`: List - Loaded motion sequence
- `playing`: Boolean - Playback state
- `playback_thread`: Thread (optional) - Playback thread

**Methods:**
- `load_motion(filepath)`: Boolean - Load motion file
- `play_motion()`: Boolean - Start playback
- `stop_playback()`: None - Stop playback
- `_playback_loop()`: None - Internal playback loop

---

#### 12. **DatasetRecorder**
- `controller`: ArmController - Arm controller instance
- `recorder`: DataRecorder - Data recorder instance
- `recording`: Boolean - Recording state
- `dataset_name`: String - Dataset identifier

**Methods:**
- `start_dataset(name)`: String - Start dataset recording
- `stop_dataset()`: Integer - Stop and return episode count
- `add_episode()`: None - Mark episode boundary

---

#### 13. **SimulationManager**
- `env`: Gymnasium.Env (optional) - Gym environment
- `env_name`: String - Environment identifier
- `headless`: Boolean - Headless mode flag
- `sim_running`: Boolean - Simulation state
- `observation_space`: Space - Observation space definition
- `action_space`: Space - Action space definition

**Methods:**
- `load_env(env_name)`: Boolean - Load environment
- `reset()`: Array - Reset environment, return observation
- `step(action)`: Tuple - Execute action, return (obs, reward, done, info)
- `close()`: None - Close environment
- `render()`: None - Render visualization

---

#### 14. **IsaacSimManager**
- `isaac_sim_path`: String - Isaac Sim installation path
- `config_path`: String - Configuration file path
- `sim_process`: Process (optional) - Simulation process
- `is_running`: Boolean - Running state
- `env_config`: Dict - Environment configuration

**Methods:**
- `check_isaac_sim()`: Boolean - Verify installation
- `start_simulation(config)`: Boolean - Launch Isaac Sim
- `stop_simulation()`: None - Stop Isaac Sim
- `get_status()`: Dict - Get current status

---

#### 15. **DatasetForm** (Django Form)
- `name`: CharField - Dataset name field
- `description`: CharField - Description field
- `num_episodes`: IntegerField - Episode count field

**Methods:**
- `clean()`: Dict - Validate form data
- `save()`: Dataset - Create dataset instance

---

## 🔗 Integration Points

### 1. **Django ORM ↔ Utility Classes**
- Views instantiate utility classes
- Utility classes read/write to models via Django ORM
- Example: `CalibrationManager` saves to `Calibration` model

### 2. **Frontend ↔ Backend**
- HTML templates display model data
- Forms submit to views
- AJAX requests for real-time updates
- WebSocket for live robot control

### 3. **Filesystem ↔ Database**
- Database stores metadata (paths, timestamps, status)
- Filesystem stores actual data (JSONL datasets, model binaries)
- Models reference filesystem paths

### 4. **Simulation ↔ Real Hardware**
- Same interface for both (duck typing)
- Swap `SimulationManager` ↔ `ArmController`
- Unified teleoperation and recording

---

## 📊 Database Schema (ERD)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Robot     │1─────1│ Calibration  │       │ MotionPattern│
│             │       │              │       │             │
│ id (PK)     │       │ id (PK)      │   ┌──→│ id (PK)     │
│ name        │       │ robot_id (FK)│   │   │ name        │
│ type        │       │ leader_serial│   │   │ robot_id(FK)│
│ port        │       │ follower...  │   │   │ sequence... │
│ ip_address  │       │ calib_data   │   │   └─────────────┘
│ is_connected│       │ calibrated_at│   │          │
│ last_seen   │       └──────────────┘   │          │ source
└─────────────┘                          │          │
       │                                 │          ▼
       │ has many                        │   ┌─────────────┐
       │                                 │   │   Dataset   │
       └─────────────────────────────────┘   │             │
                                             │ id (PK)     │
                                             │ name        │
                                             │ source(FK)  │
                                             │ created_at  │
                                             │ path        │
                                             └─────────────┘
                                                    │
                                                    │ has many
                                                    ▼
                                             ┌─────────────┐
                                             │ TrainingRun │
                                             │             │
                                             │ id (PK)     │
                                             │ dataset(FK) │
                                             │ status      │
                                             │ start_time  │
                                             │ end_time    │
                                             │ model_path  │
                                             └─────────────┘
```

---

## 🎯 Conclusion

This robotics application follows a **layered architecture**:

1. **Presentation Layer**: Django templates, forms, JavaScript
2. **Business Logic Layer**: Views, utility classes (managers, controllers, recorders)
3. **Data Access Layer**: Django ORM models
4. **Storage Layer**: SQLite database + filesystem (JSONL, models)
5. **Hardware/Simulation Layer**: Real robot APIs + Gymnasium/Isaac Sim

The design emphasizes **separation of concerns**, **modularity**, and **testability** while maintaining clean interfaces between components.
