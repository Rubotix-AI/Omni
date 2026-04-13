#!/usr/bin/env python3
"""Real-hardware bringup (STUBS) for the physical omni robot.

Starts: robot_state_publisher (real time), the Arduino motor bridge, the
GY-9250 IMU driver, and the Pi Camera 3 node. On the real robot this replaces
the Gazebo simulation as the source of /odom, /scan (add a lidar driver here),
TF and sensor data. Nav2 + AMCL then run unchanged on top.

Usage (on the Pi 4B):  ros2 launch omni_hardware hardware.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_desc = get_package_share_directory('omni_description')
    xacro_file = os.path.join(pkg_desc, 'urdf', 'omni_bot.urdf.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file]),
            'use_sim_time': use_sim_time,
        }],
    )

    arduino_bridge = Node(
        package='omni_hardware', executable='arduino_bridge',
        name='arduino_bridge', output='screen',
        parameters=[{'serial_port': '/dev/ttyACM0', 'baud': 115200}],
    )

    imu_driver = Node(
        package='omni_hardware', executable='imu_driver',
        name='imu_driver', output='screen',
    )

    camera_node = Node(
        package='omni_hardware', executable='camera_node',
        name='camera_node', output='screen',
    )

    # TODO(hardware): add your 2D lidar driver node here so Nav2/AMCL get /scan,
    # OR run depthimage_to_laserscan on the Pi Camera depth stream.

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        robot_state_publisher,
        arduino_bridge,
        imu_driver,
        camera_node,
    ])
