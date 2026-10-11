# OMX Factory — PPV18 Binary-only ROS 2 Demonstration (V2)

This public-facing workspace distributes the paper **PPV18** implementation as 13 precompiled ELF executables. **No observer/controller C++ implementation source is included.** No comparison or baseline algorithm programs are shipped.

**Platform:** Ubuntu 24.04 x86-64, ROS 2 Jazzy, Gazebo Harmonic, ROS 2 Control.

## Installation

```bash
cd ~/omx_factory_release
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build
source install/setup.bash
```

If rebuilding a previously installed workspace, delete `build install log` first. Do **not** source a different old `omx_factory_ws/install/setup.bash` at runtime.

## Run (three terminals)

All terminals first:

```bash
source /opt/ros/jazzy/setup.bash
source ~/omx_factory_release/install/setup.bash
```

Terminal 1, Gazebo and automatic controller activation:

```bash
ros2 launch pp_two_link_factory six_pp_two_link_effort_sim.launch.py
```

Wait for `[controller guard] ALL SIX ARMS READY.`; check with `ros2 control list_controllers -c /arm1/controller_manager`. Both `joint_state_broadcaster` and `effort_controller` must be `active` on every arm.

Terminal 2, six distributed observers:

```bash
ros2 launch pp_cooperative_control six_observers.launch.py
```

Wait for `ALL SIX OBSERVER PATH SETS READY`; leave it running. The full 30-second, 6001-sample Path is then published repeatedly at 1 Hz on the **original** `/pp_observer1/joint1_path` ... `/pp_observer6/joint2_path` topics.

Terminal 3, six tracking controllers:

```bash
ros2 launch pp_cooperative_control six_tracking.launch.py
```

Wait for `ALL SIX TRACKING PATH SETS READY`. The same original `/pp_tracking*/joint*_path` topics are published repeatedly at 1 Hz after the run.

Check `ros2 topic hz /pp_observer1/joint1_path` and `ros2 topic hz /pp_tracking1/joint1_path` **after finishing**. Numerical result CSVs are still generated under `~/pp_data/PPV18/observer` and `~/pp_data/PPV18/tracking`.

## How binary-only V2 works

The 13 core ELF binaries are the **unchanged V1 core machine code**, not freshly compiled from modified C++ sources. A small open infrastructure node (`pp_final_path_relay.py`) and explicit launch remaps adapt the existing binaries: during a run, their raw `Path` topics are private; only complete 6001-sample trajectories are passed to the original public topics and continuously republished at 1 Hz. The relay also prints the completion summary. The source of this relay does **not** contain the research algorithm.

The original binaries still exchange the same real-time observer synchronization messages and publish the same torque commands/diagnostics. Their routine INFO output is suppressed by per-node ROS log level; WARN/ERROR remain visible. The final summary printed by the compatibility layer includes trajectory completion statistics; the relay also reads newly generated diagnostic summary text files and prints key observer/control metrics once; the complete metrics remain in the original CSV/summary files.

Do not use `ros2 topic hz` on very large Paths during numerical iteration; final Paths are published only when complete. Do not run this public release alongside old `omx_factory_ws` processes with matching ROS nodes/topics.

## Platform/build evidence and scope

Static checks of Python launch/scripts and ZIP consistency are performed on the release package; full ROS 2 + Gazebo execution must be validated on the target platform. ELF binaries require compatible ROS 2 Jazzy dynamic libraries. Source changes in the separately delivered private V2 developer workspace must be compiled on a compatible ROS machine before those *new* C++ behaviors can be included in any later public binary distribution.

Note: binary stripping hides original implementation files but does not prevent binary reverse engineering. The root `LICENSE.Apache-2.0` and package license metadata are inherited from V1 and should be reviewed by the authors before public licensing.
