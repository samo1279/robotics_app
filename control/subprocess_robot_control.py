"""Subprocess Robot Controller - Uses your working Lerobot scripts"""
import subprocess, os, signal, time, logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SubprocessRobotController:
    def __init__(self):
        self.teleop_process = None
        self.lerobot_dir = Path(__file__).parent.parent / 'Lerobot'
    
    def connect_and_teleoperate(self) -> Dict[str, Any]:
        script_path = self.lerobot_dir / 'Teleport_config.py'
        if not script_path.exists():
            return {'success': False, 'error': f'Script not found: {script_path}'}
        if self.is_running():
            return {'success': False, 'error': 'Already running'}
        try:
            self.teleop_process = subprocess.Popen(['python', str(script_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(self.lerobot_dir), preexec_fn=os.setsid if hasattr(os, 'setsid') else None)
            time.sleep(0.5)
            if self.teleop_process.poll() is not None:
                _, stderr = self.teleop_process.communicate()
                return {'success': False, 'error': stderr.decode('utf-8') if stderr else 'Unknown error'}
            return {'success': True, 'message': 'Teleoperation started', 'pid': self.teleop_process.pid, 'follower_port': '/dev/tty.usbmodem5A680125711', 'leader_port': '/dev/tty.usbmodem5A680135091'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_teleoperation(self) -> Dict[str, Any]:
        if not self.teleop_process:
            return {'success': False, 'error': 'No process running'}
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(self.teleop_process.pid), signal.SIGTERM)
            else:
                self.teleop_process.terminate()
            self.teleop_process.wait(timeout=5)
            self.teleop_process = None
            return {'success': True, 'message': 'Stopped'}
        except Exception as e:
            self.teleop_process = None
            return {'success': False, 'error': str(e)}
    
    def is_running(self) -> bool:
        return self.teleop_process and self.teleop_process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        return {'is_running': self.is_running(), 'is_connected': self.is_running(), 'pid': self.teleop_process.pid if self.teleop_process else None, 'controller_type': 'subprocess'}

_controller = None
def get_controller():
    global _controller
    if not _controller:
        _controller = SubprocessRobotController()
    return _controller

def connect_robot(): return get_controller().connect_and_teleoperate()
def disconnect_robot(): return get_controller().stop_teleoperation()
def get_robot_status(): return get_controller().get_status()
def is_robot_connected(): return get_controller().is_running()
