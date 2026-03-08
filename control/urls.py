"""URL configuration for the control app.

Defines routes for the various control pages. Each path is mapped
to a view function in ``views.py``. See the docstrings of those
functions for more details about their behaviour.
"""
from django.urls import path
from . import views

app_name = 'control'

urlpatterns = [
    path('', views.home, name='home'),
    path('connect/', views.connect, name='connect'),
    path('calibrate/', views.calibrate, name='calibrate'),
    path('calibrate/visual/', views.visual_calibration, name='visual_calibration'),
    path('record/', views.record, name='record'),
    path('cameras/', views.cameras, name='cameras'),
    path('train/', views.train_model_view, name='train'),
    path('ai_control/', views.ai_control, name='ai_control'),
    path('manipulation/', views.manipulation, name='manipulation'),
    path('robot_connection/', views.robot_connection, name='robot_connection'),
    
    # API endpoints for manipulation
    path('api/get_robots/', views.get_robots_api, name='get_robots_api'),
    path('api/test_arm_connection/', views.test_arm_connection_api, name='test_arm_connection_api'),
    path('api/start_manipulation/', views.start_manipulation_api, name='start_manipulation_api'),
    path('api/stop_manipulation/', views.stop_manipulation_api, name='stop_manipulation_api'),
    path('api/emergency_stop/', views.emergency_stop_api, name='emergency_stop_api'),
    path('api/send_joint_command/', views.send_joint_command_api, name='send_joint_command_api'),
    path('api/get_arm_position/', views.get_arm_position_api, name='get_arm_position_api'),
    path('api/keyboard_input/', views.keyboard_input_api, name='keyboard_input_api'),
    path('api/record_motion/<str:action>/', views.record_motion_api, name='record_motion_api'),
    path('api/replay_motion/<int:motion_id>/', views.replay_motion_api, name='replay_motion_api'),
    path('dataset/', views.dataset, name='dataset'),
    path('api/dataset/<str:action>/', views.dataset_api, name='dataset_api'),
    
    # LeRobot API endpoints
    path('api/robot/connect/', views.api_robot_connect, name='api_robot_connect'),
    path('api/robot/disconnect/', views.api_robot_disconnect, name='api_robot_disconnect'),
    path('api/robot/status/', views.api_robot_status, name='api_robot_status'),
    path('api/robot/teleoperation/start/', views.api_start_teleoperation, name='api_start_teleoperation'),
    path('api/robot/teleoperation/stop/', views.api_stop_teleoperation, name='api_stop_teleoperation'),
]


