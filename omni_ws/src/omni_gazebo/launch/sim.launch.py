#!/usr/bin/env python3
"""Bring up Gazebo Sim (Fortress) with the test world and spawn omni_bot.

Starts: gz sim (server+GUI), robot_state_publisher, ros_gz spawn (create),
and ros_gz_bridge nodes (core topics + per-sensor frame-corrected bridges).

Usage:  ros2 launch omni_gazebo sim.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_desc = get_package_share_directory('omni_description')
    pkg_gz = get_package_share_directory('omni_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg_desc, 'urdf', 'omni_bot.urdf.xacro')
    world_file = os.path.join(pkg_gz, 'worlds', 'test_world.sdf')
    bridge_config = os.path.join(pkg_gz, 'config', 'bridge.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = {
        'robot_description': ParameterValue(
            Command([FindExecutable(name='xacro'), ' ', xacro_file]), value_type=str),
        'use_sim_time': use_sim_time,
    }

    # Launch Gazebo Sim (-r = run immediately, -v 3 = info logging).
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r -v 3 ' + world_file}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    # Spawn the robot from the /robot_description topic.
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'omni_bot',
            '-x', '-2.0', '-y', '-2.0', '-z', '0.06', '-Y', '0.0',
        ],
        output='screen',
    )

    # Core bridge: clock, cmd_vel, odom, tf.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config, 'use_sim_time': use_sim_time}],
        output='screen',
    )

    # Per-sensor bridges with override_frame_id so frame_ids match the URDF
    # links (lidar_link / imu_link / camera_optical_link) and Nav2/TF work.
    scan_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        name='scan_bridge', output='screen',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        parameters=[{'override_frame_id': 'lidar_link', 'use_sim_time': use_sim_time}],
    )
    imu_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        name='imu_bridge', output='screen',
        arguments=['/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU'],
        parameters=[{'override_frame_id': 'imu_link', 'use_sim_time': use_sim_time}],
    )
    cam_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        name='camera_bridge', output='screen',
        arguments=[
            '/pi_camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/pi_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        parameters=[{'override_frame_id': 'camera_optical_link',
                     'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gz_sim,
        robot_state_publisher,
        spawn,
        bridge,
        scan_bridge,
        imu_bridge,
        cam_bridge,
    ])
