# Robotics Control Web App

This project implements a web‑based interface for controlling and
calibrating a robot, recording datasets, managing cameras, training
action models and running the robot under AI control. It draws
inspiration from the phosphobot project but is designed to be easily
extended and customised. The application is built with Django and
includes a simple front‑end for interacting with the robot.

## Features

1. **Robot connection** – Detects connected robots by scanning common serial
   device prefixes (`/dev/ttyUSB*`, `/dev/ttyACM*`) and lists them to
   the user.
2. **Calibration** – Provides a one‑click calibration routine via the
   `CalibrationManager`. Replace the dummy calibration logic with the
   procedure specific to your hardware.
3. **Dataset recording** – Records timestamped entries to a newline‑
   delimited JSON (`.jsonl`) file in the `dataset/` directory. The
   `DataRecorder` class manages a background thread to write entries
   until recording is stopped.
4. **Camera access** – Lists available video devices (e.g. `/dev/video0`).
   Extend `robot_utils.list_cameras()` to integrate with OpenCV for
   streaming or previewing frames.
5. **Model training** – Selects a recorded dataset and trains a simple
   model. The sample `train_model()` function writes a dummy model file
   to the `training/` directory. Replace it with your own training
   pipeline (e.g. using a behaviour cloning or offline reinforcement
   learning library).
6. **AI control** – Runs the robot using a trained model. The
   `run_ai_control()` function should load the model and implement
   inference logic; it currently returns `True` for demonstration.
7. **Clean user interface** – Templates provide a minimal dashboard
   with clear navigation and forms. Styles are defined in
   `static/control/css/style.css` and can be customised.
8. **Debugging** – The utilities print messages and save files as
   actions are performed. Use Django’s debugging tools or Python’s
   logging to trace issues.

## Quick Start

### Prerequisites

* Python 3.9 or later
* Django 4.2 or newer (install via `pip install django`)
* Optional libraries for your hardware (e.g. `pyserial`, `opencv-python`)

### Installation

1. Clone or download this repository.
2. Install dependencies:

   ```bash
   pip install django pyserial opencv-python
   ```

3. Run migrations to create the SQLite database:

   ```bash
   cd robotics_app
   python manage.py migrate
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

5. Open your browser and navigate to `http://localhost:8000/` to use the
   dashboard.

## Usage

### Connect Robot

The *Connect Robot* page scans for connected serial devices and lists
the paths of any detected robots. If your robot uses a network
connection or a different interface, update `robot_utils.scan_robot()`
to match your environment.

### Calibration

On the *Calibration* page, click **Start Calibration** to run the
calibration routine. The default implementation simply records the
current time; you should replace the logic in
`CalibrationManager.calibrate()` with the commands required to calibrate
your robot (e.g. moving to known poses and measuring offsets).

### Record Dataset

Navigate to *Record Dataset* to start recording. A file will be
created in the `dataset/` directory with a timestamped name. While
recording, each line of the file contains a JSON object with a
timestamp. Extend the `_record_loop()` method in `DataRecorder` to
include sensor readings and commands. Stop recording to close the file.

### Camera Access

The *Camera Access* page lists available camera devices under `/dev`.
To display live previews, integrate with OpenCV or another camera
library in `robot_utils.list_cameras()` and create appropriate views
and templates.

### Train Model

On the *Train Model* page, select a recorded dataset and click
**Train**. The sample implementation writes a `.bin` file in the
`training/` directory containing the path of the dataset. Replace the
body of `robot_utils.train_model()` with your training pipeline,
loading the dataset, training an action model, and saving the trained
weights. Common frameworks for robotics include PyTorch, TensorFlow
and JAX.

### AI Control

The *AI Control* page lists available model files in the `training/`
directory. Select one and start AI control. Implement your control
loop in `robot_utils.run_ai_control()` to load the model, observe the
robot’s state and send actions at each timestep.

## Extending the Application

* Add user authentication and permissions for multi‑user environments.
* Use Django REST Framework to provide an API for remote control and
  data access.
* Integrate real robot drivers (e.g. [LeRobot](https://github.com/
  phospho-app/lerobot)) and camera streams.
* Implement data visualisation of recorded episodes using charts or
  3D plots.
* Deploy with a production WSGI server and configure static/media
  serving for remote access.

## Class Diagram

See `class_diagram.md` for a high‑level class diagram showing how the
core classes interact.

## License

This project is released under the MIT License. See the `LICENSE`
file for details.
