#!/usr/bin/env python3
"""FULL DEMO: Gazebo sim + pre-built map + AMCL + Nav2 + RViz.

This is the one command that satisfies the project goals:
  * simulates the bot in Gazebo with the test arena,
  * loads the apriori map and localizes on it (AMCL),
  * lets the bot autonomously drive source -> destination (Nav2 goals).

For manual terminal control instead of / alongside autonomy, run the teleop
launch in a second terminal:  ros2 launch omni_bringup teleop.launch.py

Usage:  ros2 launch omni_bringup sim_navigation.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_gz = get_package_share_directory('omni_gazebo')
    pkg_nav = get_package_share_directory('omni_navigation')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gz, 'launch', 'sim.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # Give Gazebo a few seconds to start publishing /clock, /scan and /odom
    # before Nav2 + AMCL come up.
    navigation = TimerAction(
        period=8.0,
        actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav, 'launch', 'navigation.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items(),
        )],
    )

    return LaunchDescription([sim, navigation])
