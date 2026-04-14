#!/usr/bin/env python3
"""Manual terminal control of the omni robot.

Runs teleop_twist_keyboard, which publishes geometry_msgs/Twist on /cmd_vel —
consumed by the Gazebo VelocityControl plugin (sim) and the Arduino bridge (hardware).
teleop supports holonomic strafing (mecanum): press 'b' to toggle holonomic
mode, then hold Shift + a movement key to strafe sideways.

IMPORTANT — keyboard capture needs a real TTY:
  * RECOMMENDED (works everywhere, incl. RoboStack/macOS):
        ros2 run teleop_twist_keyboard teleop_twist_keyboard
  * This launch file only captures keys if you pass a terminal emulator, e.g.
    on Linux with xterm installed:
        ros2 launch omni_bringup teleop.launch.py terminal_emulator:='xterm -e'

Keys:  u i o / j k l / m , .  to move;  b = toggle holonomic;  Shift = strafe.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Empty by default so it also works when run in the foreground TTY.
    term = LaunchConfiguration('terminal_emulator')

    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix=term,
        remappings=[('cmd_vel', 'cmd_vel')],
    )
    return LaunchDescription([
        DeclareLaunchArgument('terminal_emulator', default_value=''),
        teleop,
    ])
