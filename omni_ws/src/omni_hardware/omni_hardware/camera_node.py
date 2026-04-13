#!/usr/bin/env python3
"""Raspberry Pi Camera Module 3 node — STUB for real-hardware bringup.

Role on the physical robot: capture frames from the Pi Camera 3 (via
picamera2/libcamera on the Pi 4B) and publish sensor_msgs/Image on
/pi_camera/image_raw, plus a matching sensor_msgs/CameraInfo.

This stub publishes an empty (black) frame at a low rate so downstream
consumers have a topic. Replace the TODO with picamera2 capture + cv_bridge.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

# from picamera2 import Picamera2   # TODO: hardware capture
# from cv_bridge import CvBridge


class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.declare_parameter('frame_id', 'camera_optical_link')
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self.declare_parameter('rate_hz', 15.0)

        self.frame_id = self.get_parameter('frame_id').value
        self.w = self.get_parameter('width').value
        self.h = self.get_parameter('height').value
        rate = self.get_parameter('rate_hz').value

        self.pub = self.create_publisher(Image, 'pi_camera/image_raw', 10)
        self.timer = self.create_timer(1.0 / rate, self.tick)
        self.get_logger().warn(
            'STUB camera_node running — publishing empty frames. '
            'Replace the TODO with picamera2 + cv_bridge capture.')

    def tick(self):
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.height = self.h
        msg.width = self.w
        msg.encoding = 'rgb8'
        msg.is_bigendian = 0
        msg.step = self.w * 3
        msg.data = bytes(self.w * self.h * 3)  # TODO: real pixels
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
