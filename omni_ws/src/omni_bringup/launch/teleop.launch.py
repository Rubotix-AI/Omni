#!/usr/bin/env python3
"""Manual terminal control of the omni robot.

Runs teleop_twist_keyboard in HOLONOMIC mode so you can strafe (vy) as well
as drive and rotate — matching the mecanum wheels. Publishes geometry_msgs/Twist
on /cmd_vel, which both the Gazebo planar_move plugin (sim) and the Arduino
bridge (hardware) consume.

Run this in its OWN terminal (it needs keyboard focus):
    ros2 launch omni_bringup teleop.launch.py

Keys (holonomic mode):  u i o / j k l / m , .  to move;  hold Shift for strafe.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',   # give the node its own terminal for key capture
        remappings=[('cmd_vel', 'cmd_vel')],
    )
    return LaunchDescription([teleop])
