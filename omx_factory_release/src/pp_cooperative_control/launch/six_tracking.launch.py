#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    diagnostic_dir = os.path.expanduser(
        '~/pp_data/PPV18/tracking')

    nodes = [
        Node(
            package='pp_cooperative_control',
            executable='pp_final_path_relay',
            name='pp_final_path_relay_tracking',
            output='screen',
            parameters=[{'mode': 'tracking', 'period_sec': 1.0}],
        ),
        Node(
            package='pp_cooperative_control',
            executable='pp_start_sync',
            name='pp_tracking_sync',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'sync_mode': 'tracking',
                'lead_time': 0.5,
                'required_start_subscribers': 6,
                'observer_path_duration': 30.0,
                # PPV18 clock-fix: start sync is independent of /clock; after all retained Paths and fresh state streams are ready,
                # keep the system quiet before publishing the common start.
                'tracking_quiet_period': 2.0,
                'joint_state_ready_timeout': 0.25,
                'joint_state_queue_depth': 512,
                'exit_after_publish': True,
            }],
        )
    ]

    for i in range(1, 7):
        nodes.append(Node(
            package='pp_cooperative_control',
            executable=f'pp_tracking{i}',
            ros_arguments=['--log-level', 'warn'],
            remappings=[
                (f'/pp_tracking{i}/joint{j}_path',
                 f'/pp_tracking_raw{i}/joint{j}_path') for j in (1, 2)
            ],
            name=f'pp_tracking{i}',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'joint_state_topic': f'/arm{i}/joint_states',
                'joint_state_queue_depth': 512,
                'max_valid_state_dt': 0.0075,
                # Fixed algorithm clock in C++: dt=0.005 s, N=6000.
                'path_publish_period': 0.5,
                'Talpha_t': 5.0,
                'sigma_t': 0.1,
                'kit1': 2.0,
                'kit2': 4.0,
                'kia1': 1.2,
                'kic1': 2.2,
                'kia2': 1.2,
                'kic2': 2.2,
                'kfi': 1.2,
                'nu1': 0.10,
                'nu2': 0.10,
                'nuf': 0.10,
                # PPV18 keeps the previous-version-proven
                # faster self-trigger refresh on all six manipulators.
                # kit3=0.7 gives an approximately 10-ms post-PP trigger interval
                # and reduces stale held torque without changing the controller law.
                'kit3': 0.7,
                'kit4': 1.2,
                # PPV18 dynamic soft reference safety.  The physical state
                # barrier remains b_v(t)=2.0+0.1*cos(t).  Below 35% velocity
                # utilization v_ref is unchanged.  From 50% to 75% utilization
                # same-direction v_ref is smoothly softened; at >=75% the
                # attenuation reaches 60%.  The dynamic magnitude reserve tops
                # out at 0.20 rad/s but NEVER enters the state barrier.
                'velocity_safety_activation_ratio': 0.50,
                'velocity_safety_full_ratio': 0.75,
                'velocity_safety_attenuation_max': 0.60,
                'velocity_reference_margin_max': 0.20,
                'varsigma': 0.5,
                'dbar': 1000.0,
                'torque_max': [6.0, 6.0],
                'log_dir': diagnostic_dir,
                'diagnostic_enabled': True,
                # 100 fixed steps = 0.5 s algorithmic time.
                'diagnostic_console_period_steps': 100,
            }],
        ))

    return LaunchDescription(nodes)
