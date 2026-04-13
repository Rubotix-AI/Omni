#!/usr/bin/env python3
"""Arduino UNO motor bridge — STUB for real-hardware bringup.

Role on the physical robot (Raspberry Pi 4B <-> Arduino UNO over USB serial):
  * Subscribe to /cmd_vel (geometry_msgs/Twist).
  * Convert the body twist (vx, vy, wz) into four mecanum wheel angular
    velocities using the inverse kinematics below.
  * Send the wheel targets to the Arduino (which closes the loop on the
    motor drivers / encoders).
  * Read wheel encoder ticks back from the Arduino, compute wheel odometry,
    publish nav_msgs/Odometry on /odom and broadcast the odom->base_footprint TF.

Mecanum inverse kinematics (wheel angular velocity, rad/s):
    w_fl = (1/R) * (vx - vy - (lx+ly)*wz)
    w_fr = (1/R) * (vx + vy + (lx+ly)*wz)
    w_rl = (1/R) * (vx + vy - (lx+ly)*wz)
    w_rr = (1/R) * (vx - vy + (lx+ly)*wz)
  where R = wheel radius, lx = half wheel-base (x), ly = half track (y).

This is a STUB: serial I/O and encoder odometry are marked TODO. In simulation
the gazebo_ros_planar_move plugin already provides /odom, so this node is only
needed on the real robot.
"""
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# import serial   # TODO: pyserial — uncomment on hardware


class ArduinoBridge(Node):
    def __init__(self):
        super().__init__('arduino_bridge')

        # --- robot geometry (metres) — keep in sync with the URDF ---
        self.declare_parameter('wheel_radius', 0.048)
        self.declare_parameter('half_wheelbase_x', 0.11)   # lx
        self.declare_parameter('half_track_y', 0.145)      # ly
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud', 115200)

        self.R = self.get_parameter('wheel_radius').value
        self.lx = self.get_parameter('half_wheelbase_x').value
        self.ly = self.get_parameter('half_track_y').value
        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('baud').value

        # TODO(hardware): open the serial link to the Arduino
        # self.ser = serial.Serial(port, baud, timeout=0.05)
        self.ser = None
        self.get_logger().warn(
            f'STUB arduino_bridge running (would open {port} @ {baud}). '
            'Serial + encoder odometry not implemented — fill in TODOs.')

        self.sub = self.create_subscription(Twist, 'cmd_vel', self.on_cmd_vel, 10)
        # TODO(hardware): create the /odom publisher + TF broadcaster and a
        # timer that reads encoder ticks and integrates wheel odometry.

    def on_cmd_vel(self, msg: Twist):
        vx, vy, wz = msg.linear.x, msg.linear.y, msg.angular.z
        k = (self.lx + self.ly)
        w_fl = (vx - vy - k * wz) / self.R
        w_fr = (vx + vy + k * wz) / self.R
        w_rl = (vx + vy - k * wz) / self.R
        w_rr = (vx - vy + k * wz) / self.R

        # TODO(hardware): frame + send, e.g. b"M %.3f %.3f %.3f %.3f\n"
        # self.ser.write(f'M {w_fl:.3f} {w_fr:.3f} {w_rl:.3f} {w_rr:.3f}\n'.encode())
        self.get_logger().debug(
            f'wheels[rad/s] fl={w_fl:.2f} fr={w_fr:.2f} rl={w_rl:.2f} rr={w_rr:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
