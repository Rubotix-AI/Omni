# Omni-Bot

An omni-wheeled mobile robot for autonomous navigation.

## What it does

- **Simulates** the bot in a 6×6 m walled test arena in Gazebo.
- **Loads a pre-built map _apriori_** (`omni_navigation/maps/test_map.*`) and
  **localizes** on it with **AMCL**.
- **Autonomous navigation** source→destination via **Nav2**.
- **Manual terminal control** via holonomic `teleop_twist_keyboard` (strafe + rotate).

## Packages

| Package | Purpose |
|---|---|
| `omni_description` | URDF/Xacro model: mecanum base, IMU, Pi camera, sim lidar, Gazebo plugins |
| `omni_gazebo` | Test world + simulation launch (Gazebo + spawn + robot_state_publisher) |
| `omni_navigation` | Pre-built map, Nav2 params, AMCL localization + navigation launch, RViz |
| `omni_hardware` | Stub driver nodes for the real Pi 4B / Arduino UNO / GY-9250 / Pi Camera 3 |
| `omni_bringup` | Top-level launch: full sim+nav demo, and teleop |

> **Note on the lidar:** the physical robot has no lidar, but Nav2 + AMCL need a
> `/scan`. A 2D lidar is added **in simulation only** (`sensors.xacro`). On
> real hardware, add a lidar driver in `hardware.launch.py`, or convert the Pi
> Camera depth image to a `LaserScan` with `depthimage_to_laserscan`.

## Prerequisites

ROS 2 **Humble** on Ubuntu 22.04, plus:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-xacro \
  ros-humble-joint-state-publisher-gui \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard \
  xterm
```

## Build

```bash
cd omni_ws
rosdep install --from-paths src --ignore-src -r -y   # optional, resolves deps
colcon build --symlink-install
source install/setup.bash
```

## Run

### 1. Full demo — simulation + map + AMCL + Nav2

```bash
ros2 launch omni_bringup sim_navigation.launch.py
```

Gazebo and RViz open. In **RViz**:

1. The map and the robot appear; AMCL starts pre-seeded at the spawn pose
   `(-2, -2)`. If needed, use **2D Pose Estimate** to correct it.
2. Click **Nav2 Goal** and pick a destination — the bot plans and drives there
   autonomously, avoiding the two interior obstacles.

### 2. Teleop Control

In a seperate terminal;

```bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use `u i o / j k l / m , .` to translate and rotate. Press `b` to toggle
**holonomic mode**, then hold **Shift** with a key to strafe sideways (mecanum). This publishes `/cmd_vel`, which drives the sim (and the
Arduino bridge on real hardware). You can teleop and use Nav2 in the same session.

### 3. Just view the model

```bash
ros2 launch omni_description rsp.launch.py
```

### 4. Hardware stubs

On the Pi 4B (replaces Gazebo as the source of odom/scan/sensors):

```bash
ros2 launch omni_hardware hardware.launch.py     # then run navigation.launch.py
```

Fill in the `TODO(hardware)` blocks in `omni_hardware/omni_hardware/*.py`
(serial to Arduino, MPU-9250 I2C, picamera2) and add a real lidar/scan source.

## Make your own map

Drive around with teleop while running `slam_toolbox`, then
`ros2 run nav2_map_server map_saver_cli -f my_map`, and point
`omni_navigation` at the new `my_map.yaml`.

## Topics used

| Topic | Type | Direction |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | in (teleop / Nav2 → base) |
| `/odom` | `nav_msgs/Odometry` | out (planar_move / Arduino) |
| `/scan` | `sensor_msgs/LaserScan` | out (sim lidar) |
| `/imu/data` | `sensor_msgs/Imu` | out |
| `/pi_camera/image_raw` | `sensor_msgs/Image` | out |
| `/map` | `nav_msgs/OccupancyGrid` | out (map_server) |
| `/goal_pose` | `geometry_msgs/PoseStamped` | in (RViz Nav2 Goal) |

---