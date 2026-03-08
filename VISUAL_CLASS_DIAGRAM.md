# Robotics Application - Visual Class Diagram (Mermaid)

## UML Class Diagram

This diagram can be viewed in GitHub, VS Code (with Mermaid extension), or any Mermaid-compatible viewer.

```mermaid
classDiagram
    %% Django Models
    class User {
        +String username
        +String email
        +String password
        +Boolean is_active
        +Boolean is_staff
        +DateTime date_joined
    }

    class Robot {
        +Integer id
        +String name
        +String type
        +String port
        +IPAddress ip_address
        +Boolean is_connected
        +DateTime last_seen
        +__str__() String
    }

    class Calibration {
        +Integer id
        +ForeignKey robot
        +String leader_arm_serial
        +String follower_arm_serial
        +JSONField calibration_data
        +DateTime calibrated_at
        +__str__() String
    }

    class MotionPattern {
        +Integer id
        +String name
        +Text description
        +ForeignKey robot
        +JSONField sequence_data
        +DateTime created_at
        +__str__() String
    }

    class Dataset {
        +Integer id
        +String name
        +Text description
        +ForeignKey source_pattern
        +DateTime created_at
        +String path
        +__str__() String
    }

    class TrainingRun {
        +Integer id
        +ForeignKey dataset
        +String status
        +JSONField hyperparameters
        +DateTime start_time
        +DateTime end_time
        +String model_path
        +Text training_log
        +__str__() String
    }

    %% Utility Classes
    class CalibrationManager {
        +Boolean calibrated
        +Dict calibration_data
        +String config_file
        +calibrate() Dict
        +save_config() Boolean
        +load_config() Dict
    }

    class DataRecorder {
        +String dataset_dir
        +Boolean recording
        +Thread thread
        +String current_file
        +Float sample_rate
        +Integer episode_count
        +start_recording(name) String
        +stop_recording() Integer
        -_record_loop() None
    }

    class ArmController {
        +Object leader_arm
        +Object follower_arm
        +Boolean connected
        +Thread control_thread
        +List~Float~ leader_positions
        +List~Float~ follower_positions
        +connect() Boolean
        +disconnect() None
        +read_leader() List~Float~
        +write_follower(positions) None
        -_control_loop() None
    }

    class TeleopController {
        +Object leader
        +Object follower
        +Boolean running
        +Thread control_thread
        +Float control_frequency
        +start_teleop() Boolean
        +stop_teleop() None
        -_control_loop() None
    }

    class MotionRecorder {
        +Object robot
        +Boolean recording
        +List recorded_motions
        +Float sample_rate
        +start_recording() Boolean
        +stop_recording() Dict
        +save_motion(filename) String
    }

    class MotionReplayer {
        +Object robot
        +List motion_data
        +Boolean playing
        +Thread playback_thread
        +load_motion(filepath) Boolean
        +play_motion() Boolean
        +stop_playback() None
        -_playback_loop() None
    }

    class DatasetRecorder {
        +ArmController controller
        +DataRecorder recorder
        +Boolean recording
        +String dataset_name
        +start_dataset(name) String
        +stop_dataset() Integer
        +add_episode() None
    }

    class SimulationManager {
        +Gymnasium.Env env
        +String env_name
        +Boolean headless
        +Boolean sim_running
        +Space observation_space
        +Space action_space
        +load_env(env_name) Boolean
        +reset() Array
        +step(action) Tuple
        +close() None
        +render() None
    }

    class IsaacSimManager {
        +String isaac_sim_path
        +String config_path
        +Process sim_process
        +Boolean is_running
        +Dict env_config
        +check_isaac_sim() Boolean
        +start_simulation(config) Boolean
        +stop_simulation() None
        +get_status() Dict
    }

    class DatasetForm {
        +CharField name
        +CharField description
        +IntegerField num_episodes
        +clean() Dict
        +save() Dataset
    }

    %% Relationships - Models
    User "1" --> "*" Robot : owns/creates
    Robot "1" --> "1" Calibration : has
    Robot "1" --> "*" MotionPattern : has
    MotionPattern "1" <-- "*" Dataset : source_pattern
    Dataset "1" --> "*" TrainingRun : has

    %% Relationships - Utility Classes
    CalibrationManager ..> Calibration : creates
    CalibrationManager ..> Robot : calibrates
    
    DataRecorder ..> Dataset : writes to
    
    ArmController ..> Robot : controls
    
    TeleopController ..> Robot : operates
    TeleopController ..> ArmController : uses
    
    MotionRecorder ..> Robot : records
    MotionRecorder ..> MotionPattern : creates
    
    MotionReplayer ..> Robot : controls
    MotionReplayer ..> MotionPattern : replays
    
    DatasetRecorder ..> ArmController : uses
    DatasetRecorder ..> DataRecorder : uses
    DatasetRecorder ..> Dataset : creates
    
    DatasetForm ..> Dataset : creates
    
    SimulationManager ..> Robot : simulates
    IsaacSimManager ..> Robot : simulates

```

---

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o{ ROBOT : "owns/creates"
    ROBOT ||--|| CALIBRATION : "has calibration"
    ROBOT ||--o{ MOTION_PATTERN : "has motion patterns"
    MOTION_PATTERN ||--o{ DATASET : "source for dataset"
    DATASET ||--o{ TRAINING_RUN : "has training runs"

    USER {
        int id PK
        string username UK
        string email
        string password
        boolean is_active
        boolean is_staff
        datetime date_joined
    }

    ROBOT {
        int id PK
        string name UK
        string type
        string port
        ipaddress ip_address
        boolean is_connected
        datetime last_seen
    }

    CALIBRATION {
        int id PK
        int robot_id FK
        string leader_arm_serial
        string follower_arm_serial
        json calibration_data
        datetime calibrated_at
    }

    MOTION_PATTERN {
        int id PK
        string name
        text description
        int robot_id FK
        json sequence_data
        datetime created_at
    }

    DATASET {
        int id PK
        string name
        text description
        int source_pattern_id FK
        datetime created_at
        string path
    }

    TRAINING_RUN {
        int id PK
        int dataset_id FK
        string status
        json hyperparameters
        datetime start_time
        datetime end_time
        string model_path
        text training_log
    }
```

---

## System Architecture Flow

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[Django Templates]
        B[Forms]
        C[JavaScript/AJAX]
    end

    subgraph "Business Logic Layer"
        D[Views]
        E[CalibrationManager]
        F[ArmController]
        G[DataRecorder]
        H[TeleopController]
        I[MotionRecorder/Replayer]
        J[DatasetRecorder]
    end

    subgraph "Data Access Layer"
        K[Django ORM]
        L[Models: Robot, Calibration, etc.]
    end

    subgraph "Storage Layer"
        M[(SQLite Database)]
        N[(/dataset/*.jsonl)]
        O[(/training/*.bin)]
        P[(robot_config.json)]
    end

    subgraph "Hardware/Simulation Layer"
        Q[Real Robot Hardware]
        R[Gymnasium Simulation]
        S[Isaac Sim]
    end

    A --> D
    B --> D
    C --> D
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L
    L --> M
    
    G --> N
    J --> N
    L --> O
    E --> P
    
    F --> Q
    H --> Q
    I --> Q
    
    F -.-> R
    H -.-> R
    
    F -.-> S
    H -.-> S

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#fff4e1
    style G fill:#fff4e1
    style H fill:#fff4e1
    style I fill:#fff4e1
    style J fill:#fff4e1
    
    style K fill:#e8f5e9
    style L fill:#e8f5e9
    
    style M fill:#f3e5f5
    style N fill:#f3e5f5
    style O fill:#f3e5f5
    style P fill:#f3e5f5
    
    style Q fill:#ffe0b2
    style R fill:#ffe0b2
    style S fill:#ffe0b2
```

---

## Data Flow Diagrams

### 1. Calibration Flow
```mermaid
sequenceDiagram
    participant User
    participant View
    participant CalibrationManager
    participant Robot
    participant Calibration_DB

    User->>View: Request calibration
    View->>Robot: Get robot instance
    View->>CalibrationManager: calibrate()
    CalibrationManager->>Robot: Read joint positions
    Robot-->>CalibrationManager: Joint data
    CalibrationManager->>CalibrationManager: Calculate parameters
    CalibrationManager->>Calibration_DB: Save calibration
    Calibration_DB-->>View: Calibration record
    View-->>User: Success message
```

### 2. Dataset Recording Flow
```mermaid
sequenceDiagram
    participant User
    participant View
    participant DatasetRecorder
    participant ArmController
    participant DataRecorder
    participant Dataset_DB
    participant File_System

    User->>View: Start dataset recording
    View->>DatasetRecorder: start_dataset(name)
    DatasetRecorder->>ArmController: Start control
    DatasetRecorder->>DataRecorder: Start recording
    
    loop Every sample period
        ArmController->>Robot: Read positions
        DataRecorder->>File_System: Write JSONL line
    end
    
    User->>View: Stop recording
    View->>DatasetRecorder: stop_dataset()
    DatasetRecorder->>ArmController: Stop control
    DatasetRecorder->>DataRecorder: Stop recording
    DataRecorder-->>DatasetRecorder: Episode count
    DatasetRecorder->>Dataset_DB: Create dataset record
    DatasetRecorder-->>View: Dataset info
    View-->>User: Recording saved
```

### 3. Training Flow
```mermaid
sequenceDiagram
    participant User
    participant View
    participant TrainingRun_DB
    participant AI_Framework
    participant File_System

    User->>View: Start training
    View->>TrainingRun_DB: Create training run (PENDING)
    View->>AI_Framework: Load dataset
    AI_Framework->>File_System: Read JSONL files
    View->>TrainingRun_DB: Update status (RUNNING)
    
    loop Training epochs
        AI_Framework->>AI_Framework: Train model
        AI_Framework->>View: Progress update
        View->>TrainingRun_DB: Update training_log
    end
    
    AI_Framework->>File_System: Save model (.bin/.pt)
    AI_Framework-->>View: Training complete
    View->>TrainingRun_DB: Update status (COMPLETED)
    View->>TrainingRun_DB: Set model_path
    View-->>User: Training finished
```

---

## Component Interaction Map

```mermaid
graph LR
    subgraph "Frontend"
        UI[User Interface]
    end

    subgraph "Controllers"
        ARM[ArmController]
        TEL[TeleopController]
        MOT[MotionRecorder]
        REP[MotionReplayer]
    end

    subgraph "Managers"
        CAL[CalibrationManager]
        DAT[DatasetRecorder]
        REC[DataRecorder]
        SIM[SimulationManager]
        ISA[IsaacSimManager]
    end

    subgraph "Data Layer"
        DB[(Database)]
        FS[File System]
    end

    subgraph "Hardware"
        ROB[Robot Hardware]
        GYM[Gymnasium]
        ISM[Isaac Sim]
    end

    UI --> ARM
    UI --> TEL
    UI --> MOT
    UI --> REP
    UI --> CAL
    UI --> DAT
    UI --> SIM
    UI --> ISA

    ARM --> ROB
    TEL --> ARM
    MOT --> ROB
    REP --> ROB
    CAL --> ROB
    DAT --> ARM
    DAT --> REC

    ARM --> DB
    TEL --> DB
    MOT --> DB
    REP --> DB
    CAL --> DB
    REC --> DB

    REC --> FS
    MOT --> FS
    CAL --> FS

    SIM --> GYM
    ISA --> ISM

    style UI fill:#6366f1,color:#fff
    style ARM fill:#4ecdc4
    style TEL fill:#4ecdc4
    style MOT fill:#4ecdc4
    style REP fill:#4ecdc4
    style CAL fill:#45b7d1
    style DAT fill:#45b7d1
    style REC fill:#45b7d1
    style SIM fill:#45b7d1
    style ISA fill:#45b7d1
    style DB fill:#5f27cd,color:#fff
    style FS fill:#5f27cd,color:#fff
    style ROB fill:#f7b731
    style GYM fill:#f7b731
    style ISM fill:#f7b731
```

---

## State Machine: Training Run Status

```mermaid
stateDiagram-v2
    [*] --> PENDING: Create training run
    PENDING --> RUNNING: Start training
    RUNNING --> COMPLETED: Training succeeds
    RUNNING --> FAILED: Training fails
    COMPLETED --> [*]
    FAILED --> [*]
    
    note right of PENDING
        Initial state
        No training started
    end note
    
    note right of RUNNING
        Training in progress
        Model updating
        Logs being written
    end note
    
    note right of COMPLETED
        Training finished
        Model saved
        Metrics recorded
    end note
    
    note right of FAILED
        Error occurred
        Logs contain error
        Model not saved
    end note
```

---

## File Structure Tree

```mermaid
graph TD
    ROOT[robotics_app/]
    
    ROOT --> DB[(db.sqlite3)]
    ROOT --> CFG[robot_config.json]
    ROOT --> CTRL[control/]
    ROOT --> DSET[dataset/]
    ROOT --> TRAIN[training/]
    ROOT --> SIMCFG[simulation_configs/]
    
    CTRL --> MODELS[models.py]
    CTRL --> VIEWS[views.py]
    CTRL --> UTILS[robot_utils.py]
    CTRL --> FORMS[forms.py]
    CTRL --> SIMU[simulation_utils.py]
    CTRL --> ISAAC[isaac_sim_utils.py]
    
    DSET --> DS1[dataset_20250930.jsonl]
    DSET --> DS2[test_20250930.jsonl]
    
    TRAIN --> M1[model_20250930.bin]
    TRAIN --> M2[comprehensive_model.pt]
    
    SIMCFG --> SC1[sim_config_Panda.json]
    SIMCFG --> SC2[sim_config_UR5.json]
    
    style ROOT fill:#6366f1,color:#fff
    style DB fill:#5f27cd,color:#fff
    style DSET fill:#4ecdc4
    style TRAIN fill:#45b7d1
    style DS1 fill:#f7b731
    style DS2 fill:#f7b731
    style M1 fill:#ff6b6b
    style M2 fill:#ff6b6b
```

---

## Usage Examples

### Rendering in VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file in VS Code
3. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to preview

### Rendering in GitHub
- GitHub automatically renders Mermaid diagrams in markdown files
- Just push this file to your repository

### Exporting as Image
- Use [Mermaid Live Editor](https://mermaid.live/)
- Copy-paste the diagram code
- Export as PNG/SVG

---

## Summary

This comprehensive class diagram shows:

✅ **5 Django Models** (Robot, Calibration, MotionPattern, Dataset, TrainingRun)  
✅ **9 Utility Classes** (Managers, Controllers, Recorders)  
✅ **1 Form Class** (DatasetForm)  
✅ **All Relationships** (1:1, 1:N, N:1)  
✅ **Data Flow** (Calibration, Recording, Training)  
✅ **System Architecture** (Layered design)  
✅ **Component Interactions** (How classes work together)  
✅ **File Structure** (Storage organization)

The diagrams provide multiple perspectives on the same system, making it easy to understand how your robotics application works! 🤖✨
