## Differential Drive Robot

A differential drive robot with a lidar and a camera, simulated in Gazebo Sim (Jazzy) and controlled through ros2_control.

### Run the simulation

```bash
ros2 launch my_bot launch_sim.launch.py
```

### Drive the robot

In a second terminal, run the teleop with its output remapped to the stamper input:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel_remap
```

Command chain: `teleop → /cmd_vel_remap → twist_stamper → /cmd_vel → diff_cont`.

`twist_stamper` converts `Twist` to `TwistStamped` because the controller only accepts stamped commands.

### Files

| File | Purpose | Recent changes |
|---|---|---|
| `description/robot_core.xacro` | Base links, chassis, wheels, materials | Added `red` material and chassis/wheel links |
| `description/robot.urdf.xacro` | Top-level robot file that includes the others | Includes ros2_control, lidar and camera |
| `description/inertial_macros.xacro` | Inertia macros for box, cylinder, sphere | Split from robot_core |
| `description/ros2_control.xacro` | `gz_ros2_control` hardware interface for wheel joints | New, declares velocity command limits |
| `description/lidar.xacro` | Lidar link and gpu_lidar sensor publishing `/scan` | New |
| `description/camera.xacro` | Camera link and sensor publishing `/camera/image_raw` | New |
| `description/depth_camera.xacro` | Depth camera, not included yet | New, unused |
| `description/gazebo_control.xacro` | Legacy Gazebo DiffDrive and JointState plugins | Not included, kept for reference |
| `config/gz_bridge.yaml` | ROS-Gazebo bridge for clock, scan and camera | Removed cmd_vel, odom, tf, joint_states |
| `config/my_controllers.yaml` | Controller manager, diff_cont and joint_broad parameters | New |
| `launch/launch_sim.launch.py` | Starts Gazebo, spawn, robot_state_publisher, bridge and controllers | New |
| `worlds/testworld.sdf` | Test world with cones, barrels, rocks | New |
| `src/test.cpp` | Publishes a constant Twist to drive in a circle | New |
| `package.xml` | Runtime dependencies | Added ros2_control, controllers, ros_gz, twist_stamper |
| `CMakeLists.txt` | Builds test_program, installs config, description, launch, worlds | Added test_program target |

### Template origin

This package started from a GitHub template. Each directory originally held a placeholder file so git would track it. Rename `my_bot` in all files if you change the project name.
