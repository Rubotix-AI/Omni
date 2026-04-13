#!/usr/bin/env python3
"""GY-9250 (MPU-9250) 9DOF IMU driver — STUB for real-hardware bringup.

Role on the physical robot: read the accelerometer, gyroscope and
magnetometer over I2C from the Raspberry Pi 4B and publish
sensor_msgs/Imu on /imu/data (plus optionally sensor_msgs/MagneticField).

This stub publishes a zero-motion Imu message at a fixed rate so the rest of
the stack (e.g. an EKF via robot_localization) has a topic to subscribe to.
Replace the TODO block with real I2C reads (e.g. smbus2) and calibration.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

# import smbus2   # TODO: I2C on hardware


class ImuDriver(Node):
    def __init__(self):
        super().__init__('imu_driver')
        self.declare_parameter('frame_id', 'imu_link')
        self.declare_parameter('rate_hz', 100.0)
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('i2c_addr', 0x68)

        self.frame_id = self.get_parameter('frame_id').value
        rate = self.get_parameter('rate_hz').value

        self.pub = self.create_publisher(Imu, 'imu/data', 10)
        self.timer = self.create_timer(1.0 / rate, self.tick)
        self.get_logger().warn(
            'STUB imu_driver running — publishing zero-motion Imu. '
            'Replace the TODO with real MPU-9250 I2C reads.')

    def tick(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        # TODO(hardware): read accel (m/s^2), gyro (rad/s), fuse orientation.
        msg.orientation.w = 1.0
        msg.linear_acceleration.z = 9.81
        # Covariances: -1 in [0] means "unknown" until calibrated.
        msg.orientation_covariance[0] = -1.0
        msg.angular_velocity_covariance[0] = 0.0004
        msg.linear_acceleration_covariance[0] = 0.03
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
