# Switching_Topology_PP_Tracking_Control_For_MAS
**Notice 1:** *ROS Implementation for the Second Subsection of the Simulation Study on Prescribed-Performance Cooperative Control of Networked Euler--Lagrange Systems Under Switching Topologies*

**Notice 2:** *This repository provides a runnable ROS/Gazebo simulation package for reproducing the submitted manuscript results. The full controller source code will be released after publication. This package contains precompiled ROS nodes and the required launch, configuration, model, and visualization files for review.*

## 1. Preliminary Preparation

Before running the code in this subsection, the runtime environment should be configured in advance.

### System Requirements

- Operating System: Ubuntu 20.04
- Robot Operating System: ROS Noetic
- ROS Installation Type: Full Desktop Version

The detailed installation tutorial for ROS Noetic can be found at:

https://wiki.ros.org/noetic/Installation/Ubuntu

After the installation is completed, please check whether Gazebo and RViz can be opened properly.

## 2. Running the Tracking Control

Execute the following commands to run the tracking control code:

```bash
source /opt/ros/noetic/setup.bash
source ~/paper_demo_ws/devel/setup.bash
roslaunch your_package_name your_launch_file.launch


