"""
Database models for the control app, providing a comprehensive structure for
managing robots, calibration, motion patterns, datasets, and AI model training.
"""
from django.db import models


class Robot(models.Model):
    """Represents a physical or simulated robot."""

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50, default="Generic Arm")
    port = models.CharField(
        max_length=100, blank=True, help_text="USB or serial port identifier"
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_connected = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Calibration(models.Model):
    """Stores calibration data for a robot."""

    robot = models.OneToOneField(
        Robot, on_delete=models.CASCADE, related_name="calibration"
    )
    leader_arm_serial = models.CharField(max_length=100, blank=True)
    follower_arm_serial = models.CharField(max_length=100, blank=True)
    calibration_data = models.JSONField(
        help_text="Stores detailed calibration parameters"
    )
    calibrated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calibration for {self.robot.name}"


class MotionPattern(models.Model):
    """Stores a recorded sequence of robot movements."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    robot = models.ForeignKey(
        Robot, on_delete=models.CASCADE, related_name="motion_patterns"
    )
    sequence_data = models.JSONField(
        help_text="Array of joint states and timestamps"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    """
    Metadata for a recorded robotics dataset, used for AI training.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_pattern = models.ForeignKey(
        MotionPattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(
        max_length=1024,
        help_text="Filesystem path to the dataset file or directory",
    )

    def __str__(self):
        return self.name


class TrainingRun(models.Model):
    """Tracks an AI model training process."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="training_runs"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="PENDING"
    )
    hyperparameters = models.JSONField(blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    model_path = models.CharField(
        max_length=1024, blank=True, help_text="Path to the final trained model file"
    )
    training_log = models.TextField(blank=True)

    def __str__(self):
        return f"Training Run for {self.dataset.name} ({self.status})"
