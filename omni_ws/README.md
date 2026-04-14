# Omni-Bot — ROS 2 Humble MVP (RoboStack / pixi)

An omni-wheeled (mecanum) mobile robot for autonomous navigation. This
workspace is the **MVP**: a fully simulatable stack in **Gazebo Sim (Fortress)** plus
**hardware bringup stubs** for the real robot. It is set up to build and run
under **RoboStack ROS 2 Humble managed by pixi** — no system/apt ROS install
needed.

**Real robot target:** Raspberry Pi 4B (brain) · Arduino UNO (motor MCU) ·
Pi Camera 3 · GY-9250 9DOF IMU · mecanum wheels · 6400 mAh LiPo.

## What it does

- **Simulates** the bot in a 6×6 m walled test arena in Gazebo.
- **Loads a pre-built map _apriori_** (`omni_navigation/maps/test_map.*`) and
  **localizes** on it with **AMCL** (omni motion model).
- **Autonomous navigation** source→destination via **Nav2** (send a goal in RViz).
- **Manual terminal control** via holonomic `teleop_twist_keyboard` (strafe + rotate).
- **Hardware stubs** (`omni_hardware`) for the Pi/Arduino/IMU/camera to fill in later.

## Packages

| Package | Purpose |
|---|---|
| `omni_description` | URDF/Xacro model: mecanum base, IMU, Pi camera, sim lidar, Gazebo plugins |
| `omni_gazebo` | Test world + simulation launch (Gazebo + spawn + robot_state_publisher) |
| `omni_navigation` | Pre-built map, Nav2 params, AMCL localization + navigation launch, RViz |
| `omni_hardware` | Stub driver nodes for the real Pi 4B / Arduino UNO / GY-9250 / Pi Camera 3 |
| `omni_bringup` | Top-level launch: full sim+nav demo, and teleop |

> **Note on the lidar:** the physical robot has no lidar, but Nav2 + AMCL need a
> `/scan`. A 2D lidar is added **in simulation only** (see `sensors.xacro`). On
> real hardware, add a lidar driver in `hardware.launch.py`, or convert the Pi
> Camera depth image to a `LaserScan` with `depthimage_to_laserscan`.

---

## Run with RoboStack + pixi

### 0. Install pixi (once)

```bash
curl -fsSL https://pixi.sh/install.sh | bash
# then restart the shell, or:  source ~/.bashrc   (or ~/.zshrc)
pixi --version
```

### 1. Create the ROS 2 Humble environment

From the workspace root (the folder containing `pixi.toml`):

```bash
cd omni_ws
pixi install
```

This reads `pixi.toml` and downloads ROS 2 Humble, Gazebo Sim (Fortress) + ros_gz, Nav2, and the
build toolchain from the `robostack-staging` + `conda-forge` channels into a
local `.pixi/` env. First run takes a few minutes.

### 2. Build the workspace

```bash
pixi run build
```

(equivalently: `pixi shell` then `colcon build`)

> Uses plain `colcon build` — the RoboStack setuptools is too new for
> `--symlink-install`'s editable-install of Python packages. After editing a
> config/launch/xacro, just re-run `pixi run build` (incremental, fast). To get
> `--symlink-install` back, pin `setuptools = "<80"` in `pixi.toml`.

### 3. Run — full demo (sim + map + AMCL + Nav2 + RViz)

```bash
pixi run sim
```

Gazebo and RViz open. In **RViz**:

1. The map and robot appear; AMCL is pre-seeded at the spawn pose `(-2, -2)`.
   If the robot looks misplaced, click **2D Pose Estimate** and click/drag on
   the map to set its true pose.
2. Click **Nav2 Goal** and pick a destination — the bot plans and drives there
   autonomously, avoiding the two interior obstacles.

### 4. Manual keyboard control (teleop)

teleop needs a real terminal for key capture, so run it directly in a **second
terminal** (not through the launch file):

```bash
cd omni_ws
pixi run teleop
```

Keys: `u i o / j k l / m , .` to translate and rotate. Press `b` to toggle
**holonomic mode**, then hold **Shift** + a key to strafe sideways (mecanum).
This publishes `/cmd_vel`; you can teleop and use Nav2 in the same session.

### 5. Other entry points

```bash
pixi run gazebo   # just the Gazebo simulation, no navigation
pixi run view     # RViz view of the robot model only
```

### Working inside the environment directly

If you prefer a normal ROS workflow, drop into the env and run commands by hand:

```bash
cd omni_ws
pixi shell                       # activates the ROS 2 Humble env
colcon build
source install/setup.bash        # source the overlay (do this in each new shell)
ros2 launch omni_bringup sim_navigation.launch.py
```

> **macOS / Apple Silicon note:** the sim uses **Gazebo Sim (Fortress)** via
> `ros_gz`. The lidar and camera need GPU rendering (`ogre2` → Metal on Apple
> Silicon). If Gazebo starts but `/scan` never publishes (RViz shows no laser and
> Nav2 logs *"waiting for transform ... odom"*), rendering is the culprit. Try:
>
> - run the GUI + server explicitly with the OGRE2/Metal backend already set (default), and
> - if sensors still don't render, launch Gazebo **headless-rendering** is not
>   enough for lidar — in that case run the stack on Linux (native/VM), where
>   Fortress rendering is rock-solid.
>
> Physics, motion (teleop) and odometry do **not** need rendering and will work
> regardless.

---

## Real hardware bringup (stubs)

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

## Topics (quick reference)

| Topic | Type | Direction |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | in (teleop / Nav2 → base) |
| `/odom` | `nav_msgs/Odometry` | out (planar_move / Arduino) |
| `/scan` | `sensor_msgs/LaserScan` | out (sim lidar) |
| `/imu/data` | `sensor_msgs/Imu` | out |
| `/pi_camera/image` | `sensor_msgs/Image` | out (sim) |
| `/map` | `nav_msgs/OccupancyGrid` | out (map_server) |
| `/goal_pose` | `geometry_msgs/PoseStamped` | in (RViz Nav2 Goal) |
