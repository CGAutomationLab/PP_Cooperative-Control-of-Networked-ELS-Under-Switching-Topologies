Prescribed-Performance Cooperative Control of Networked Euler–Lagrange Systems Under Switching Topologies
Notice 1: This repository provides the ROS 2 / Gazebo experimental implementation associated with the study of prescribed-performance cooperative control of networked Euler–Lagrange systems under switching communication topologies.
Notice 2: The current repository is provided for experimental reproducibility and peer review. It contains executable binary implementations of the distributed observer and cooperative tracking controller, together with the required ROS 2 launch files, controller configurations, robot descriptions, and Gazebo simulation resources. The core C++ source code of the proposed observer and controller is not included in this review release and is intended to be made available after formal publication.
Notice 3: The experiments in this repository are ROS 2 / Gazebo simulations involving six two-degree-of-freedom (two-DOF) robotic manipulators. They should not be interpreted as experiments on physical industrial manipulators.
Notice 4: This release focuses on the proposed method. Source code and launch configurations for comparison algorithms and auxiliary comparison experiments are not included.
---
1. Overview
This repository provides the experimental implementation corresponding to the research project:
> **Prescribed-Performance Cooperative Control of Networked Euler–Lagrange Systems Under Switching Topologies**
The experimental platform consists of:
a Gazebo Harmonic industrial workcell containing six two-DOF robotic manipulators with fixed grippers;
six independent ROS 2 `controller_manager` instances and joint-effort control interfaces;
six distributed observer nodes for cooperative reference-state estimation;
six cooperative tracking controller nodes implementing the proposed control method;
synchronized experiment initiation, prescribed-performance control, and ROS 2 communication interfaces;
ROS 2 trajectory topics and diagnostic data files for evaluating observer and tracking results.
The released `pp_cooperative_control` package contains 13 precompiled Linux x86-64 executables: six observers, six tracking controllers, and one synchronization program. Public Python helper nodes handle controller-state recovery and publication of completed trajectories; they are not the protected observer or controller algorithms.
The core C++ algorithms are therefore not rebuilt from source. A standard `colcon build` is nevertheless required to install the supplied binaries, launch files, and simulation packages into the local ROS 2 workspace.
---
2. ROS 2 and Robotic Manipulator Experimental Platform
2.1 ROS 2
The experimental system is implemented using ROS 2 Jazzy Jalisco. ROS 2 provides DDS-based distributed communication, modular node execution, robot namespaces, topic-based information exchange, and integration with `ros2_control` and Gazebo. These facilities are used to execute the distributed observers and cooperative controllers in a networked multi-manipulator simulation.
2.2 Six Two-DOF Euler–Lagrange Manipulators
The simulated plant comprises six robotic manipulators, each with two independently actuated revolute joints. The models are representative robotic Euler–Lagrange systems rather than UR5e or other commercial six-axis robot models.
The six manipulators are arranged around a central conveyor in a digital industrial workcell. The environment includes worktables, drive cabinets, industrial fixtures, and simulated workpieces. Each manipulator is operated through a dedicated ROS 2 joint-effort controller and publishes joint-state feedback.
The platform uses:
`pp_factory_world` for the Gazebo workcell;
`pp_two_link_factory` for the robot descriptions, controller settings, and simulation launch files;
`pp_cooperative_control` for the binary observer and tracking implementation.
All experiments are performed in Gazebo Harmonic. No physical robot, external robot controller, or robot IP address is needed.
---
3. System Requirements
The precompiled release targets the following environment:
Operating system: Ubuntu 24.04 LTS (Noble Numbat)
ROS distribution: ROS 2 Jazzy Jalisco
Recommended ROS installation: ROS 2 Jazzy Desktop
Simulation: Gazebo Harmonic / Gazebo Sim 8
CPU architecture: amd64 / x86_64
Control framework: `ros2_control` and `gz_ros2_control`
Robot platform: six simulated two-DOF manipulators
Install ROS 2 Jazzy in accordance with the official Ubuntu installation guide. If ROS 2 packages have already been configured, the desktop installation can be installed using:
```bash
sudo apt update
sudo apt install ros-jazzy-desktop
```
Initialize ROS 2 in each new terminal:
```bash
source /opt/ros/jazzy/setup.bash
```
Compatibility note: The included algorithm executables are precompiled for the specified ROS 2 / Linux environment. Other ROS distributions, operating systems, or CPU architectures are not covered by this binary release.
---
4. Install Additional Dependencies
After ROS 2 Jazzy is installed, install the Gazebo integration, controller packages, robot description tools, and workspace build utilities:
```bash
sudo apt update

sudo apt install -y \
  git \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-controller-manager \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-effort-controllers \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher
```
The official `ros2_control` and Gazebo integration documentation is available at:
https://control.ros.org/jazzy/doc/getting_started/getting_started.html
https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html
No Universal Robots UR5e packages are required. All required two-link robot descriptions and the factory world are included in this repository.
---
5. Clone and Build the Repository
Clone the public repository into a local workspace named `omx_factory_release`:
```bash
git clone \
  https://github.com/CGAutomationLab/PP_Cooperative-Control-of-Networked-ELS-Under-Switching-Topologies.git \
  ~/omx_factory_release

cd ~/omx_factory_release
```
The repository root should contain a `src/` folder with the three ROS 2 packages:
```text
omx_factory_release/
└── src/
    ├── pp_cooperative_control/
    │   ├── bin/              # Precompiled observer/controller binaries
    │   ├── launch/
    │   └── scripts/          # Public ROS 2 support utilities
    ├── pp_two_link_factory/
    │   ├── config/
    │   ├── launch/
    │   └── urdf/
    └── pp_factory_world/
        └── worlds/
```
Install dependencies and build the ROS 2 workspace:
```bash
source /opt/ros/jazzy/setup.bash
cd ~/omx_factory_release

rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build
source install/setup.bash
```
If `rosdep` has not been initialized on the computer, run `sudo rosdep init` once followed by `rosdep update`, then retry the dependency command.
The `colcon build` step installs the supplied binaries and packages the public ROS 2 resources; it does not compile the protected research algorithms from C++ source.
You can verify installation using:
```bash
ros2 pkg executables pp_cooperative_control
```
The output should include the six `pp_observer` executables, six `pp_tracking` executables, `pp_start_sync`, and the public trajectory-relay helper.
---
6. Run the Experiment
The experimental startup uses three terminals:
```text
Terminal 1: Start Gazebo and six manipulator controllers
Terminal 2: Start the six distributed observers
Terminal 3: Start the six cooperative tracking controllers
```
In every new terminal, source both ROS 2 Jazzy and the installed workspace:
```bash
source /opt/ros/jazzy/setup.bash
source ~/omx_factory_release/install/setup.bash
```
6.1 Terminal 1 — Start the Industrial Simulation Platform
```bash
ros2 launch pp_two_link_factory \
  six_pp_two_link_effort_sim.launch.py
```
This launch file loads the factory world, starts Gazebo, spawns the six manipulators, and starts the corresponding ROS 2 joint-state broadcasters and joint-effort controllers. It also includes a controller-state recovery helper to activate controllers that remain inactive during startup.
Wait for the following terminal message before beginning the tracking stage:
```text
[controller guard] ALL SIX ARMS READY.
```
To check an individual manipulator's controller state:
```bash
ros2 control list_controllers -c /arm1/controller_manager
```
Both `joint_state_broadcaster` and `effort_controller` should be `active`. Joint-state publication can be checked with:
```bash
ros2 topic hz /arm1/joint_states
```
6.2 Terminal 2 — Start the Distributed Observers
```bash
ros2 launch pp_cooperative_control \
  six_observers.launch.py
```
This starts six distributed observer executables and the observer synchronization process. The observers compute their 30-second state-estimation records. Intermediate information-level diagnostic messages are suppressed, while completion messages and available diagnostic summaries are printed after computation.
Wait until:
```text
ALL SIX OBSERVER PATH SETS READY
```
Upon completion, each observer's full `nav_msgs/msg/Path` trajectory remains available under the original public topic names and is republished at approximately 1 Hz. Leave this terminal running for the tracking stage.
6.3 Terminal 3 — Start the Cooperative Tracking Controllers
After the Gazebo controllers are active and all six observer results are ready, run:
```bash
ros2 launch pp_cooperative_control \
  six_tracking.launch.py
```
This starts the tracking synchronization process and six cooperative tracking controllers. Each manipulator executes a 30-second cooperative tracking experiment through its joint-effort interface.
As with the observer stage, repeated information-level diagnostic messages are suppressed. Upon completion, the public relay displays completion and diagnostic summaries and continuously republishes the completed trajectories at approximately 1 Hz.
A completed run reports:
```text
ALL SIX TRACKING PATH SETS READY
```
Keep the running terminals open while inspecting the results. Use `Ctrl+C` to terminate the experiment.
---
7. Experimental Outputs and Verification
7.1 ROS 2 Trajectory Topics
After the observer computation, check an observer trajectory topic:
```bash
ros2 topic hz /pp_observer1/joint1_path
```
After the tracking computation, check a tracking trajectory topic:
```bash
ros2 topic hz /pp_tracking1/joint1_path
```
The naming pattern is:
```text
/pp_observer{1..6}/joint{1..2}_path
/pp_tracking{1..6}/joint{1..2}_path
```
Completed observer and tracking paths contain the 30-second experiment trajectory and are republished at approximately 1 Hz. The topic names remain unchanged from the experimental ROS 2 interface.
7.2 Diagnostic Data
The default diagnostic output directories are:
```text
~/pp_data/PPV18/observer/
~/pp_data/PPV18/tracking/
```
Check the generated files with:
```bash
ls -lh ~/pp_data/PPV18/observer/
ls -lh ~/pp_data/PPV18/tracking/
```
These records support post-processing of observer performance, tracking errors, controller updates, and related experimental diagnostics. The release is focused on the proposed method and does not contain the separate comparison-algorithm implementations.
---
8. Reproducibility and Source-Code Availability
The present repository is intended to support evaluation and reproduction of the manuscript's proposed ROS 2 / Gazebo experiment while withholding the core research C++ implementation during review.
It provides precompiled observer and controller programs, supporting ROS 2 launch/configuration files, simulation robot models, Gazebo resources, and public runtime utilities. The core observer and cooperative tracking controller source code is not part of this binary release and is intended to be released after the paper is formally published.
The supplied binaries are platform-specific and may require the stated Ubuntu 24.04 / ROS 2 Jazzy environment. No physical-robot results are claimed. Comparison algorithm implementations are outside the scope of this repository.
