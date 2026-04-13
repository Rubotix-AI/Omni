#!/usr/bin/env python3
"""Localization (AMCL on a pre-built map) + Nav2 autonomous navigation.

Reuses nav2_bringup's bringup_launch.py in localization mode (slam:=False)
so the robot loads the apriori map, localizes with AMCL, and accepts
navigation goals. Assumes the simulation (or hardware) is already publishing
/scan, /odom and TF.

Usage:  ros2 launch omni_navigation navigation.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('omni_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    default_map = os.path.join(pkg_nav, 'maps', 'test_map.yaml')
    default_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    default_rviz = os.path.join(pkg_nav, 'config', 'nav.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_rviz = LaunchConfiguration('use_rviz')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'slam': 'False',
            'autostart': 'True',
        }.items(),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', default_rviz],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=None,
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        nav2,
        rviz,
    ])
