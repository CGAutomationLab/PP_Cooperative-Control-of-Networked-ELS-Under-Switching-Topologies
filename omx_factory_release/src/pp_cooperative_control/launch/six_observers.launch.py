#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    initials = [
        [-0.55,  0.42],
        [ 0.50,  0.28],
        [ 0.18, -0.36],
        [-0.38, -0.23],
        [ 0.32, -0.08],
        [-0.28,  0.18],
    ]

    diagnostic_dir = os.path.expanduser(
        '~/pp_data/PPV18/observer')

    nodes = [
        Node(
            package='pp_cooperative_control',
            executable='pp_final_path_relay',
            name='pp_final_path_relay_observer',
            output='screen',
            parameters=[{'mode': 'observer', 'period_sec': 1.0}],
        ),
        Node(
            package='pp_cooperative_control',
            executable='pp_start_sync',
            name='pp_observer_sync',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'sync_mode': 'observer',
                'lead_time': 0.5,
                'required_start_subscribers': 6,
                'exit_after_publish': True,
            }],
        )
    ]

    for i in range(1, 7):
        nodes.append(Node(
            package='pp_cooperative_control',
            executable=f'pp_observer{i}',
            ros_arguments=['--log-level', 'warn'],
            remappings=[
                (f'/pp_observer{i}/joint{j}_path',
                 f'/pp_observer_raw{i}/joint{j}_path') for j in (1, 2)
            ],
            name=f'pp_observer{i}',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'Talpha_o': 5.0,
                'sigma_o': 0.1,
                'rho0': 30.0,
                'rho_d': 30.0,
                'k_rho': 0.2,
                'initial_qhat': initials[i - 1],
                'log_dir': diagnostic_dir,
                'diagnostic_enabled': True,
                # PPV18: exact synchronized 0.0005-s observer substeps are active.
                # Keep compact main-step diagnostics by default; set True only when a
                # full 60000-row per-observer substep trace is needed.
                'diagnostic_substep_log': False,
                # Original binary logs are filtered by ROS log-level; the
                # separate non-algorithm relay prints one final summary.
                'diagnostic_console_period_steps': 100,
                'diagnostic_eta_warn': 1000.0,
                'diagnostic_rho_warn': 100000.0,
                'diagnostic_consensus_warn': 1000.0,
            }],
        ))

    return LaunchDescription(nodes)
