"""View functions for the control app.

Each view corresponds to a page in the web interface and coordinates
between user requests, the robot utility functions and templates.

Now integrates with LeRobot for real robot control.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .robot_utils import (
    CalibrationManager,
    DataRecorder,
    scan_robot,
    list_cameras,
    train_model,
    run_ai_control,
    teleop_controller,
    get_available_ports,
    motion_recorder,
    motion_replayer,
    dataset_recorder,
)

# Import LeRobot bridge
try:
    from .lerobot_bridge import lerobot_manager, LEROBOT_AVAILABLE
except ImportError:
    lerobot_manager = None
    LEROBOT_AVAILABLE = False

from .simulation_utils import simulation_manager
from .isaac_sim_utils import isaac_sim_manager
from .models import Robot, Calibration, MotionPattern, Dataset, TrainingRun


# Global managers for calibration and data recording. In a more complex
# application these would be stored in a database or managed via
# dependency injection. They persist across requests and maintain
# state (e.g. whether recording is in progress).
calibration_manager = CalibrationManager()
data_recorder = DataRecorder(dataset_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset'))


def home(request: HttpRequest) -> HttpResponse:
    """Render the dashboard home page with REAL data only."""
    
    # Load robot configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
    robot_config = None
    robots_connected = 0
    robot_status = "Offline"
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                robot_config = json.load(f)
                
            # Check if both arms are configured
            if (robot_config.get('leader_arm', {}).get('port') and 
                robot_config.get('follower_arm', {}).get('port')):
                robots_connected = 2
                robot_status = "Online"
            elif robot_config.get('leader_arm', {}).get('port') or robot_config.get('follower_arm', {}).get('port'):
                robots_connected = 1
                robot_status = "Partial"
        except Exception:
            pass
    
    # Count REAL cameras
    try:
        cameras = list_cameras()
        camera_count = len(cameras) if cameras else 0
    except Exception:
        camera_count = 0
    
    # Count REAL AI models from training directory
    training_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'training')
    ai_model_count = 0
    if os.path.exists(training_dir):
        ai_model_count = len([f for f in os.listdir(training_dir) if f.endswith('.bin') or f.endswith('.pt')])
    
    # Count REAL dataset files
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset')
    dataset_count = 0
    total_data_points = 0
    if os.path.exists(dataset_dir):
        dataset_files = [f for f in os.listdir(dataset_dir) if f.endswith('.jsonl')]
        dataset_count = len(dataset_files)
        
        # Count actual data points in datasets
        for dataset_file in dataset_files:
            try:
                with open(os.path.join(dataset_dir, dataset_file), 'r') as f:
                    total_data_points += sum(1 for _ in f)
            except Exception:
                pass
    
    # Check if calibrated
    is_calibrated = False
    if robot_config:
        is_calibrated = robot_config.get('calibrated', False)
    
    context = {
        'robots_connected': robots_connected,
        'robot_status': robot_status,
        'camera_count': camera_count,
        'ai_model_count': ai_model_count,
        'dataset_count': dataset_count,
        'total_data_points': total_data_points,
        'is_calibrated': is_calibrated,
        'has_config': robot_config is not None,
    }
    
    return render(request, 'control/home.html', context)


def connect(request: HttpRequest) -> HttpResponse:
    """Detect available serial ports and configure leader/follower arms.
    Now integrates with LeRobot for real robot connection.
    """
    from django.contrib import messages
    import serial.tools.list_ports
    
    # Get current saved configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
    saved_config = {
        'leader_arm': {'port': '', 'id': ''},
        'follower_arm': {'port': '', 'id': ''}
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
        except Exception:
            pass
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            leader_port = request.POST.get('leader_port')
            leader_id = request.POST.get('leader_id')
            follower_port = request.POST.get('follower_port')
            follower_id = request.POST.get('follower_id')
            robot_type = request.POST.get('robot_type', 'so101')  # Default to SO101
            
            # Validation
            if not all([leader_port, leader_id, follower_port, follower_id]):
                messages.error(request, 'All fields are required. Please select ports and enter IDs for both arms.')
            elif leader_port == follower_port:
                messages.error(request, 'Leader and follower arms cannot use the same port. Please select different ports.')
            else:
                # Save configuration
                config = {
                    'leader_arm': {
                        'port': leader_port,
                        'id': leader_id,
                        'type': f'{robot_type}_leader',
                        'gearing': {
                            'joints_1_3': '1/191',
                            'joint_2': '1/345',
                            'joints_4_6': '1/147'
                        }
                    },
                    'follower_arm': {
                        'port': follower_port,
                        'id': follower_id,
                        'type': f'{robot_type}_follower',
                        'gearing': {
                            'all_joints': '1/345'
                        }
                    },
                    'motors': list(range(1, 7)),
                    'robot_type': robot_type,
                    'calibrated': False,
                    'connected': False
                }
                
                try:
                    with open(config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    # Try to configure LeRobot if available
                    if LEROBOT_AVAILABLE and lerobot_manager:
                        try:
                            success = lerobot_manager.configure_arms(
                                leader_port=leader_port,
                                leader_id=leader_id,
                                follower_port=follower_port,
                                follower_id=follower_id,
                                robot_type=robot_type
                            )
                            if success:
                                messages.success(request, f'✅ Robot arms configured with LeRobot! Leader: {leader_id} ({leader_port}), Follower: {follower_id} ({follower_port}). Click "Connect to Robot" to establish connection.')
                            else:
                                messages.warning(request, f'⚠️ Configuration saved but LeRobot configuration failed. Please check the ports and try connecting.')
                        except Exception as e:
                            messages.warning(request, f'⚠️ Configuration saved but LeRobot error: {str(e)}')
                    else:
                        messages.success(request, f'✅ Robot configuration saved successfully! Leader: {leader_id} ({leader_port}), Follower: {follower_id} ({follower_port}).')
                    
                    saved_config = config
                except Exception as e:
                    messages.error(request, f'Failed to save configuration: {str(e)}')
        
        elif action == 'connect':
            # Actually connect to the robot using LeRobot
            if not LEROBOT_AVAILABLE or not lerobot_manager:
                messages.error(request, '❌ LeRobot is not available. Please install LeRobot package.')
            else:
                try:
                    # Load config
                    if not os.path.exists(config_path):
                        messages.error(request, '❌ No robot configuration found. Please configure the robot first.')
                    else:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        
                        robot_type = config.get('robot_type', 'so101')
                        
                        # Try to connect
                        success = lerobot_manager.connect(robot_type=robot_type)
                        
                        if success:
                            config['connected'] = True
                            with open(config_path, 'w') as f:
                                json.dump(config, f, indent=2)
                            saved_config = config
                            messages.success(request, f'✅ Successfully connected to robot arms! Leader: {config["leader_arm"]["id"]}, Follower: {config["follower_arm"]["id"]}')
                        else:
                            messages.error(request, '❌ Failed to connect to robot arms. Please check:\n1. Both arms are powered on\n2. USB cables are properly connected\n3. Ports are correct\n4. No other program is using the serial ports')
                            
                except Exception as e:
                    messages.error(request, f'❌ Connection error: {str(e)}')
        
        elif action == 'disconnect':
            # Disconnect from robot
            if LEROBOT_AVAILABLE and lerobot_manager:
                try:
                    lerobot_manager.disconnect()
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        config['connected'] = False
                        with open(config_path, 'w') as f:
                            json.dump(config, f, indent=2)
                        saved_config = config
                    messages.success(request, '✅ Disconnected from robot arms')
                except Exception as e:
                    messages.error(request, f'Error disconnecting: {str(e)}')
    
    # Detect available ports using LeRobot scanner if available
    available_ports = []
    try:
        if LEROBOT_AVAILABLE and lerobot_manager:
            # Use LeRobot's enhanced scanner
            devices = lerobot_manager.scan_for_robots()
            for device in devices:
                port_info = {
                    'device': device['device'],
                    'description': device.get('description', 'Unknown'),
                    'manufacturer': device.get('manufacturer'),
                    'pid': device.get('pid'),
                    'serial_number': device.get('serial_number'),
                    'robot_type': device.get('robot_type')
                }
                available_ports.append(port_info)
        else:
            # Fallback to basic port detection
            ports = serial.tools.list_ports.comports()
            for port in ports:
                port_info = {
                    'device': port.device,
                    'description': port.description if port.description else None,
                    'manufacturer': port.manufacturer if port.manufacturer else None,
                    'pid': port.pid if port.pid else None,
                    'serial_number': port.serial_number if port.serial_number else None,
                    'robot_type': None
                }
                available_ports.append(port_info)
    except Exception as e:
        messages.error(request, f'Error scanning ports: {str(e)}')
    
    # Get LeRobot status
    lerobot_status = None
    if LEROBOT_AVAILABLE and lerobot_manager:
        try:
            lerobot_status = lerobot_manager.get_status()
        except:
            pass
    
    context = {
        'available_ports': available_ports,
        'saved_config': saved_config,
        'lerobot_available': LEROBOT_AVAILABLE,
        'lerobot_status': lerobot_status
    }
    
    return render(request, 'control/connect.html', context)


@require_http_methods(["GET", "POST"])
def calibrate(request: HttpRequest) -> HttpResponse:
    """
    Handle advanced robot calibration.
    - Checks if robot configuration exists (leader and follower arms configured)
    - On POST, performs calibration using the configured arms
    """
    from django.contrib import messages
    
    # Check if robot configuration exists
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
    
    if not os.path.exists(config_path):
        messages.error(request, '⚠️ No robot configuration found. Please connect and configure your leader and follower arms first.')
        return render(request, 'control/calibrate.html', {
            'config_missing': True,
            'config_path': config_path
        })
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        messages.error(request, f'Error loading robot configuration: {str(e)}')
        return render(request, 'control/calibrate.html', {
            'config_missing': True
        })
    
    # Check if both leader and follower are configured
    if not config.get('leader_arm', {}).get('port') or not config.get('follower_arm', {}).get('port'):
        messages.error(request, '⚠️ Incomplete robot configuration. Both leader and follower arms must be configured.')
        return render(request, 'control/calibrate.html', {
            'config_incomplete': True,
            'config': config
        })
    
    context: Dict[str, Any] = {
        'config': config,
        'leader_arm': config.get('leader_arm', {}),
        'follower_arm': config.get('follower_arm', {})
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calibrate':
            try:
                # Perform calibration logic
                calibration_data = calibration_manager.calibrate()
                
                # Update config with calibration status
                config['calibrated'] = True
                config['calibration_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messages.success(request, f"✅ Successfully calibrated {config['follower_arm']['id']} with leader {config['leader_arm']['id']}.")
                context['calibrated'] = True
                context['calibration_data'] = calibration_data
                
                
            except Exception as e:
                messages.error(request, f"❌ Calibration failed: {str(e)}")
    
    context['config'] = config
    return render(request, 'control/calibrate.html', context)


@require_http_methods(["GET", "POST"])
def record(request: HttpRequest) -> HttpResponse:
    """Start or stop dataset recording."""
    context: Dict[str, Any] = {'recording': data_recorder.recording}
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            file_path = data_recorder.start_recording()
            if file_path is None:
                context['message'] = 'Recording is already in progress.'
            else:
                context['message'] = f'Recording started: {os.path.basename(file_path)}'
        elif action == 'stop':
            file_path = data_recorder.stop_recording()
            if file_path is None:
                context['message'] = 'No recording was in progress.'
            else:
                context['message'] = f'Recording stopped: {os.path.basename(file_path)}'
        else:
            context['message'] = 'Invalid action.'
        context['recording'] = data_recorder.recording
    return render(request, 'control/record.html', context)


def cameras(request: HttpRequest) -> HttpResponse:
    """List available camera devices."""
    cams = list_cameras()
    return render(request, 'control/cameras.html', {'cameras': cams})


@require_http_methods(["GET", "POST"])
def train_model_view(request: HttpRequest) -> HttpResponse:
    """
    Handles the AI model training page.
    - On GET, it displays available datasets and past training runs.
    - On POST, it starts a new training run.
    """
    if request.method == 'POST':
        dataset_id = request.POST.get('dataset_id')
        model_type = request.POST.get('model_type')
        learning_rate = request.POST.get('learning_rate')

        try:
            dataset = Dataset.objects.get(id=dataset_id)
            
            # Create a new training run entry
            training_run = TrainingRun.objects.create(
                dataset=dataset,
                model_name=f"{dataset.name}_{model_type}",
                hyperparameters={'learning_rate': learning_rate, 'model_type': model_type}
            )
            
            # In a real application, you would trigger the training process in the background
            # For now, we'll just mark it as started.
            # e.g., start_background_training(training_run.id)
            
        except Dataset.DoesNotExist:
            # Handle error: dataset not found
            pass

    datasets = Dataset.objects.all()
    training_runs = TrainingRun.objects.all().order_by('-start_time')
    
    context = {
        'datasets': datasets,
        'training_runs': training_runs,
    }
    return render(request, 'control/train.html', context)


@require_http_methods(["GET", "POST"])
def ai_control(request: HttpRequest) -> HttpResponse:
    """Start AI‑based control using a trained model."""
    training_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'training')
    context: Dict[str, Any] = {}
    if request.method == 'POST':
        model_name = request.POST.get('model')
        if model_name:
            model_path = os.path.join(training_dir, model_name)
            success = run_ai_control(model_path)
            if success:
                context['message'] = f'AI control started with model: {model_name}'
            else:
                context['message'] = f'Failed to start AI control with model: {model_name}'
        else:
            context['message'] = 'Please select a model.'
    else:
        # List available model files
        try:
            models = [f for f in os.listdir(training_dir) if f.endswith('.bin')]
        except FileNotFoundError:
            models = []
        context['models'] = models
    return render(request, 'control/ai_control.html', context)


# Global variables for manipulation control
manipulation_active = False
current_control_mode = 'leader'


@require_http_methods(["GET"])
def manipulation(request: HttpRequest) -> HttpResponse:
    """Render the new robot manipulation control interface."""
    return render(request, 'control/manipulation.html', {})


@require_http_methods(["GET"])
def dataset(request: HttpRequest) -> HttpResponse:
    """Render the dataset management page."""
    datasets = Dataset.objects.all().order_by('-created_at')
    return render(request, 'control/dataset.html', {'datasets': datasets})


@require_http_methods(["GET"])
def get_robots_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to get available robots."""
    try:
        robots = scan_robot()
        return JsonResponse({'success': True, 'robots': robots})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def test_arm_connection_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to test arm connection."""
    try:
        data = json.loads(request.body)
        arm_id = data.get('arm_id')
        role = data.get('role')
        
        # In a real implementation, this would test actual connection to the arm
        # For now, we simulate based on available robots
        robots = scan_robot()
        connected = any(robot['id'] == arm_id for robot in robots)
        
        return JsonResponse({'success': True, 'connected': connected})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e), 'connected': False})


@require_http_methods(["POST"])
def start_manipulation_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to start teleoperation."""
    global manipulation_active, current_control_mode
    
    try:
        data = json.loads(request.body)
        leader_arm = data.get('leader_arm')
        follower_arm = data.get('follower_arm')
        control_mode = data.get('control_mode', 'leader')
        
        if manipulation_active:
            return JsonResponse({'success': False, 'error': 'Manipulation already active'})
        
        # Setup arms and start teleoperation
        if teleop_controller.setup_arms(leader_arm, follower_arm):
            if teleop_controller.start_teleoperation(control_mode):
                manipulation_active = True
                current_control_mode = control_mode
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to start teleoperation'})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to setup arms'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def stop_manipulation_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to stop teleoperation."""
    global manipulation_active
    
    try:
        teleop_controller.stop_teleoperation()
        manipulation_active = False
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def emergency_stop_api(request: HttpRequest) -> HttpResponse:
    """API endpoint for emergency stop."""
    global manipulation_active
    
    try:
        teleop_controller.emergency_stop()
        manipulation_active = False
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def send_joint_command_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to send joint commands in manual mode."""
    try:
        data = json.loads(request.body)
        joint = data.get('joint')
        value = data.get('value')
        
        if not manipulation_active or current_control_mode != 'manual':
            return JsonResponse({'success': False, 'error': 'Manual control not active'})
        
        success = teleop_controller.send_joint_command(joint, value)
        return JsonResponse({'success': success})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def get_arm_position_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to get current arm position."""
    try:
        position = teleop_controller.get_arm_position()
        return JsonResponse({'success': True, 'position': position})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def keyboard_input_api(request: HttpRequest) -> HttpResponse:
    """API endpoint to handle keyboard input."""
    try:
        data = json.loads(request.body)
        key = data.get('key')
        pressed = data.get('pressed', False)
        
        # In a real scenario, you'd check if keyboard control is active.
        # For now, we just process the input.
        teleop_controller.process_keyboard_input(key, pressed)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def robot_connection(request):
    """
    Handles robot connection and identification.
    - On GET, it lists available serial ports.
    - On POST, it attempts to connect to the selected robot.
    """
    if request.method == 'POST':
        port = request.POST.get('port')
        try:
            # Create or get the robot instance
            robot, created = Robot.objects.get_or_create(port=port, defaults={'name': f"Robot at {port}", 'type': 'Generic Arm'})
            
            # Simulate connection
            robot.is_connected = True
            robot.save()
            
            return JsonResponse({'status': 'success', 'message': f'Successfully connected to robot on {port}'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # GET request
    ports = get_available_ports()
    robots = Robot.objects.filter(port__in=ports)
    
    port_status = []
    for port in ports:
        robot = robots.filter(port=port).first()
        port_status.append({
            'port': port,
            'connected': robot.is_connected if robot else False,
            'robot_name': robot.name if robot else 'N/A'
        })
        
    return render(request, 'control/robot_connection.html', {'ports': port_status})


@require_http_methods(["POST"])
def record_motion_api(request: HttpRequest, action: str) -> HttpResponse:
    """API endpoint to start or stop motion recording."""
    if action == 'start':
        success, message = motion_recorder.start_recording()
        if success:
            return JsonResponse({'success': True, 'motion_pattern_id': message})
        else:
            return JsonResponse({'success': False, 'error': message})
    elif action == 'stop':
        success, message = motion_recorder.stop_recording()
        if success:
            return JsonResponse({'success': True, 'motion_pattern_id': message})
        else:
            return JsonResponse({'success': False, 'error': message})
    return JsonResponse({'success': False, 'error': 'Invalid action.'})


@require_http_methods(["POST"])
def replay_motion_api(request: HttpRequest, motion_id: int) -> HttpResponse:
    """API endpoint to replay a recorded motion."""
    success, message = motion_replayer.replay(motion_id)
    if success:
        return JsonResponse({'success': True, 'message': message})
    else:
        return JsonResponse({'success': False, 'error': message})


@require_http_methods(["POST"])
def dataset_api(request: HttpRequest, action: str) -> HttpResponse:
    """API endpoint for dataset creation."""
    if action == 'start_dataset_recording':
        name = request.POST.get('name')
        description = request.POST.get('description')
        sources = request.POST.getlist('sources')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Dataset name is required.'})
            
        success, message = dataset_recorder.start_recording(name, description, sources)
        if success:
            return JsonResponse({'success': True, 'dataset_id': message})
        else:
            return JsonResponse({'success': False, 'error': message})

    elif action == 'stop_dataset_recording':
        success, message = dataset_recorder.stop_recording()
        if success:
            return JsonResponse({'success': True, 'dataset_id': message})
        else:
            return JsonResponse({'success': False, 'error': message})

    return JsonResponse({'success': False, 'error': 'Invalid action.'})


def visual_calibration(request: HttpRequest) -> HttpResponse:
    """
    Visual 3D calibration guide with interactive STL model viewer.
    Shows step-by-step calibration instructions with 3D arm visualization.
    """
    from django.contrib import messages
    
    # Load robot configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
    config = None
    config_missing = True
    config_incomplete = False
    current_step = int(request.GET.get('step', 1))
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                config_missing = False
                
                # Check if configuration is complete
                if not config.get('leader_arm', {}).get('port') or not config.get('follower_arm', {}).get('port'):
                    config_incomplete = True
        except Exception as e:
            messages.error(request, f'Error loading configuration: {str(e)}')
    
    # Handle step completion
    if request.method == 'POST':
        action = request.POST.get('action')
        step = int(request.POST.get('step', 0))
        
        if action == 'complete_step':
            # Mark step as completed (could save to database/config)
            messages.success(request, f'✅ Step {step} completed! Moving to next step.')
            from django.shortcuts import redirect
            return redirect(f"{request.path}?step={step + 1}")
        
        elif action == 'start_calibration':
            # Start the actual calibration process
            try:
                calibration_data = calibration_manager.calibrate()
                config['calibrated'] = True
                config['calibration_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messages.success(request, '✅ Calibration completed successfully!')
                return redirect('control:calibrate')
                
            except Exception as e:
                messages.error(request, f'Calibration failed: {str(e)}')
    
    # Define calibration steps with 3D positions
    calibration_steps = [
        {
            'step': 1,
            'title': 'Power On & Connection Check',
            'description': 'Ensure both leader and follower arms are powered on and connected via USB. Check that all motors respond to commands.',
            'icon': 'fa-plug',
            'duration': '2 min',
            'joint_positions': [0, 0, 0, 0, 0, 0],  # All joints neutral
            'camera_position': {'x': 2, 'y': 2, 'z': 2},
            'instructions': [
                'Connect leader arm to USB port',
                'Connect follower arm to USB port',
                'Power on both arms',
                'Verify green LED indicators',
                'Check that joints move freely'
            ]
        },
        {
            'step': 2,
            'title': 'Move to Home Position',
            'description': 'Manually move both arms to the home/zero position where all joints are at mid-range.',
            'icon': 'fa-home',
            'duration': '3 min',
            'joint_positions': [0, 90, 90, 0, 0, 0],
            'camera_position': {'x': 3, 'y': 1.5, 'z': 3},
            'instructions': [
                'Gently move Joint 1 (base) to center (0°)',
                'Position Joint 2 (shoulder) at 90°',
                'Set Joint 3 (elbow) to 90°',
                'Center Joint 4 (wrist flex) at 0°',
                'Center Joint 5 (wrist roll) at 0°',
                'Set gripper to mid-position'
            ]
        },
        {
            'step': 3,
            'title': 'Record Zero Position',
            'description': 'Record the current position as the calibration zero point for both arms.',
            'icon': 'fa-bullseye',
            'duration': '1 min',
            'joint_positions': [0, 90, 90, 0, 0, 0],
            'camera_position': {'x': 2, 'y': 2, 'z': 2},
            'instructions': [
                'Ensure arms are stable and aligned',
                'Press the "Record Zero" button',
                'Wait for confirmation beep/LED',
                'Do not move arms during recording',
                'Verify zero position is saved'
            ]
        },
        {
            'step': 4,
            'title': 'Calibrate Joint 1 - Base Rotation',
            'description': 'Slowly rotate the base joint through its full range of motion (±180°).',
            'icon': 'fa-sync',
            'duration': '2 min',
            'joint_positions': [180, 90, 90, 0, 0, 0],
            'camera_position': {'x': 0, 'y': 3, 'z': 0},  # Top view
            'instructions': [
                'Rotate base fully counter-clockwise (-180°)',
                'Hold for 2 seconds',
                'Rotate base fully clockwise (+180°)',
                'Hold for 2 seconds',
                'Return to center position (0°)',
                'Press "Calibrate Joint 1" button'
            ]
        },
        {
            'step': 5,
            'title': 'Calibrate Joint 2 - Shoulder Lift',
            'description': 'Move the shoulder joint through its full range vertically.',
            'icon': 'fa-arrow-up',
            'duration': '2 min',
            'joint_positions': [0, 180, 90, 0, 0, 0],
            'camera_position': {'x': 3, 'y': 1, 'z': 0},  # Side view
            'instructions': [
                'Lift shoulder to maximum position (180°)',
                'Hold for 2 seconds',
                'Lower shoulder to minimum position (0°)',
                'Hold for 2 seconds',
                'Return to mid-position (90°)',
                'Press "Calibrate Joint 2" button'
            ]
        },
        {
            'step': 6,
            'title': 'Calibrate Joint 3 - Elbow Flex',
            'description': 'Flex the elbow joint through its full range of motion.',
            'icon': 'fa-angle-double-right',
            'duration': '2 min',
            'joint_positions': [0, 90, 180, 0, 0, 0],
            'camera_position': {'x': 3, 'y': 1, 'z': 0},
            'instructions': [
                'Extend elbow fully (0°)',
                'Hold for 2 seconds',
                'Flex elbow fully (180°)',
                'Hold for 2 seconds',
                'Return to mid-position (90°)',
                'Press "Calibrate Joint 3" button'
            ]
        },
        {
            'step': 7,
            'title': 'Calibrate Joint 4 - Wrist Flex',
            'description': 'Move the wrist flex joint through its range.',
            'icon': 'fa-hand-paper',
            'duration': '2 min',
            'joint_positions': [0, 90, 90, 90, 0, 0],
            'camera_position': {'x': 1.5, 'y': 1, 'z': 1.5},
            'instructions': [
                'Flex wrist down (-90°)',
                'Hold for 2 seconds',
                'Flex wrist up (+90°)',
                'Hold for 2 seconds',
                'Return to center (0°)',
                'Press "Calibrate Joint 4" button'
            ]
        },
        {
            'step': 8,
            'title': 'Calibrate Joint 5 - Wrist Roll',
            'description': 'Rotate the wrist roll joint through full rotation.',
            'icon': 'fa-redo',
            'duration': '2 min',
            'joint_positions': [0, 90, 90, 0, 180, 0],
            'camera_position': {'x': 1, 'y': 1.5, 'z': 1},
            'instructions': [
                'Roll wrist counter-clockwise (-180°)',
                'Hold for 2 seconds',
                'Roll wrist clockwise (+180°)',
                'Hold for 2 seconds',
                'Return to center (0°)',
                'Press "Calibrate Joint 5" button'
            ]
        },
        {
            'step': 9,
            'title': 'Calibrate Gripper',
            'description': 'Open and close the gripper to calibrate its range.',
            'icon': 'fa-hand-rock',
            'duration': '1 min',
            'joint_positions': [0, 90, 90, 0, 0, 180],
            'camera_position': {'x': 0.5, 'y': 1, 'z': 0.5},
            'instructions': [
                'Open gripper fully',
                'Hold for 2 seconds',
                'Close gripper fully (but gently)',
                'Hold for 2 seconds',
                'Return to mid-position',
                'Press "Calibrate Gripper" button'
            ]
        },
        {
            'step': 10,
            'title': 'Verification & Testing',
            'description': 'Verify calibration by moving both arms through synchronized motions.',
            'icon': 'fa-check-circle',
            'duration': '3 min',
            'joint_positions': [0, 90, 90, 0, 0, 0],
            'camera_position': {'x': 2, 'y': 2, 'z': 2},
            'instructions': [
                'Move leader arm slowly through all joints',
                'Verify follower arm mirrors movements accurately',
                'Check that position values match',
                'Test edge cases (max/min positions)',
                'Confirm smooth, synchronized motion',
                'Save calibration data'
            ]
        }
    ]
    
    context = {
        'config': config,
        'config_missing': config_missing,
        'config_incomplete': config_incomplete,
        'calibration_steps': calibration_steps,
        'current_step': current_step,
        'total_steps': len(calibration_steps),
        'current_step_data': calibration_steps[current_step - 1] if 1 <= current_step <= len(calibration_steps) else calibration_steps[0],
        'stl_url': 'https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/STL/SO101/Individual/SO101%20Assembly.stl',
        'progress_percent': int((current_step / len(calibration_steps)) * 100)
    }
    
    return render(request, 'control/visual_calibration.html', context)


# API Endpoints for LeRobot Integration

@require_http_methods(["POST"])
def api_robot_connect(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to connect to the robot using LeRobot.
    
    POST /api/robot/connect/
    
    Returns JSON with connection status.
    """
    if not LEROBOT_AVAILABLE or not lerobot_manager:
        return JsonResponse({
            'success': False,
            'error': 'LeRobot is not available. Please install: pip install lerobot'
        }, status=500)
    
    try:
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
        
        if not os.path.exists(config_path):
            return JsonResponse({
                'success': False,
                'error': 'No robot configuration found. Please configure the robot first via /connect/'
            }, status=400)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if already configured
        leader_arm = config.get('leader_arm', {})
        follower_arm = config.get('follower_arm', {})
        
        if not leader_arm.get('port') or not follower_arm.get('port'):
            return JsonResponse({
                'success': False,
                'error': 'Robot arms not configured. Please configure via /connect/'
            }, status=400)
        
        robot_type = config.get('robot_type', 'so101')
        
        # Configure arms if not already done
        if not lerobot_manager.leader_config or not lerobot_manager.follower_config:
            lerobot_manager.configure_arms(
                leader_port=leader_arm['port'],
                leader_id=leader_arm['id'],
                follower_port=follower_arm['port'],
                follower_id=follower_arm['id'],
                robot_type=robot_type
            )
        
        # Connect to robot
        success = lerobot_manager.connect(robot_type=robot_type)
        
        if success:
            # Update config
            config['connected'] = True
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully connected to robot arms',
                'status': lerobot_manager.get_status()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to robot arms. Check ports, power, and cables.'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Connection error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def api_robot_disconnect(request: HttpRequest) -> JsonResponse:
    """API endpoint to disconnect from the robot."""
    if not LEROBOT_AVAILABLE or not lerobot_manager:
        return JsonResponse({
            'success': False,
            'error': 'LeRobot is not available'
        }, status=500)
    
    try:
        lerobot_manager.disconnect()
        
        # Update config
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'robot_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            config['connected'] = False
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        return JsonResponse({
            'success': True,
            'message': 'Disconnected from robot arms'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Disconnect error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_robot_status(request: HttpRequest) -> JsonResponse:
    """API endpoint to get robot status."""
    if not LEROBOT_AVAILABLE or not lerobot_manager:
        return JsonResponse({
            'lerobot_available': False,
            'connected': False,
            'error': 'LeRobot not available'
        })
    
    try:
        status = lerobot_manager.get_status()
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Status error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def api_start_teleoperation(request: HttpRequest) -> JsonResponse:
    """API endpoint to start teleoperation mode."""
    if not LEROBOT_AVAILABLE or not lerobot_manager:
        return JsonResponse({
            'success': False,
            'error': 'LeRobot is not available'
        }, status=500)
    
    if not lerobot_manager.connected:
        return JsonResponse({
            'success': False,
            'error': 'Robot not connected. Please connect first.'
        }, status=400)
    
    try:
        success = lerobot_manager.start_teleoperation()
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Teleoperation started'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to start teleoperation'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Teleoperation error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def api_stop_teleoperation(request: HttpRequest) -> JsonResponse:
    """API endpoint to stop teleoperation mode."""
    if not LEROBOT_AVAILABLE or not lerobot_manager:
        return JsonResponse({
            'success': False,
            'error': 'LeRobot is not available'
        }, status=500)
    
    try:
        lerobot_manager.stop_teleoperation()
        return JsonResponse({
            'success': True,
            'message': 'Teleoperation stopped'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Stop teleoperation error: {str(e)}'
        }, status=500)


