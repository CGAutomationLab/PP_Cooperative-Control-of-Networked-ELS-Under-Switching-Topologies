# PP Two-Link Factory V2

This package spawns six compact two-DOF PP manipulators in the unchanged factory world provided by `pp_factory_world`.

V2 geometry:
- link 1: 0.45 m;
- link 2: 0.38 m;
- base radius: 0.12 m;
- shoulder support: 0.22 m;
- compact fixed two-finger gripper at the end of link 2;
- exactly two controlled joints per manipulator.

The six bases sit on the table tops at z=0.800 m. Their centers are y=+/-1.06 m so the 0.12 m base radius touches the inner table edge y=+/-0.94 m while remaining fully on the table.

## Build

```bash
cd ~/omx_factory_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select pp_factory_world pp_two_link_factory
source install/setup.bash
```

## Visual check

```bash
ros2 launch pp_two_link_factory six_pp_two_link_visual.launch.py
```

## Effort simulation

```bash
ros2 launch pp_two_link_factory six_pp_two_link_effort_sim.launch.py
```

Expected state topics are `/arm1/joint_states` ... `/arm6/joint_states`, and each effort command contains exactly `[tau1, tau2]`.

## PPV18 plant inertia test

Relative to the compact PPV8 plant, only the inertial parameters of the moving chain are scaled by 3.1. This deliberately backs away from PPV11's rejected 3.3x test while staying slightly above the PPV9 3.0x baseline:

- `upper_arm`: mass 2.0 -> 6.2 kg; inertia tensor 3.1x;
- `forearm`: mass 1.2 -> 3.72 kg; inertia tensor 3.1x;
- fixed `ee_link`: mass 0.05 -> 0.155 kg; inertia tensor 3.1x.

Geometry, two controlled DOFs, joint damping (0.02), joint limits and gravity-disabled
configuration are unchanged.  The controller does not use these model parameters.
