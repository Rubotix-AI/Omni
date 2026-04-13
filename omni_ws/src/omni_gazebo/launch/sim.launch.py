#!/usr/bin/env python3
"""Bring up Gazebo Classic with the test world and spawn the omni_bot.

Starts: gazebo server+client, robot_state_publisher, spawn_entity.
Usage:  ros2 launch omni_gazebo sim.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_desc = get_package_share_directory('omni_description')
    pkg_gz = get_package_share_directory('omni_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    xacro_file = os.path.join(pkg_desc, 'urdf', 'omni_bot.urdf.xacro')
    world_file = os.path.join(pkg_gz, 'worlds', 'test_world.world')

    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')

    robot_description = {
        'robot_description': Command(['xacro ', xacro_file]),
        'use_sim_time': use_sim_time,
    }

    # Gazebo server + client
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world, 'verbose': 'true'}.items(),
    )
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'omni_bot',
            '-x', '-2.0', '-y', '-2.0', '-z', '0.06', '-Y', '0.0',
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value=world_file),
        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_entity,
    ])
