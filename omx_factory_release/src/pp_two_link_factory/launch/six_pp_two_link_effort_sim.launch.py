#!/usr/bin/env python3
import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def robot_description(xacro_file, prefix, namespace, controller_config):
    doc = xacro.process_file(
        xacro_file,
        mappings={
            'prefix': prefix,
            'namespace': namespace,
            'controller_config': controller_config,
        },
    )
    return doc.toxml()


def generate_launch_description():
    pp_share = get_package_share_directory('pp_two_link_factory')
    world_share = get_package_share_directory('pp_factory_world')

    world_file = os.path.join(world_share, 'worlds', 'omx_factory_v6_harmonic.sdf')
    effort_xacro = os.path.join(pp_share, 'urdf', 'pp_two_link_gripper_effort.urdf.xacro')

    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[pp_share, ':', world_share, ':', os.environ.get('GZ_SIM_RESOURCE_PATH', '')],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-v 2 -r {world_file}'}.items(),
    )

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge', output='screen',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    )

    configs = [
        ('arm1_', 'arm1', -2.20,  1.06, 0.800, -1.57079632679),
        ('arm2_', 'arm2',  0.00,  1.06, 0.800, -1.57079632679),
        ('arm3_', 'arm3',  2.20,  1.06, 0.800, -1.57079632679),
        ('arm4_', 'arm4', -2.20, -1.06, 0.800,  1.57079632679),
        ('arm5_', 'arm5',  0.00, -1.06, 0.800,  1.57079632679),
        ('arm6_', 'arm6',  2.20, -1.06, 0.800,  1.57079632679),
    ]

    actions = [resource_path, gazebo, bridge]
    combined_spawners = []

    for prefix, name, x, y, z, yaw in configs:
        yaml_file = os.path.join(pp_share, 'config', f'{name}_effort_controller.yaml')
        desc = robot_description(effort_xacro, prefix, name, yaml_file)

        actions.append(Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            namespace=name, name='robot_state_publisher', output='screen',
            parameters=[{'robot_description': desc, 'use_sim_time': True}],
        ))
        actions.append(Node(
            package='ros_gz_sim', executable='create', name=f'spawn_{name}', output='screen',
            arguments=['-string', desc, '-name', name,
                       '-x', str(x), '-y', str(y), '-z', str(z),
                       '-R', '0.0', '-P', '0.0', '-Y', str(yaw),
                       '-allow_renaming', 'false'],
        ))

        # Spawn both controllers in a single manager transaction. The final
        # recovery guard checks for inactive controllers after startup.
        combined_spawners.append(Node(
            package='controller_manager', executable='spawner', output='screen',
            arguments=['joint_state_broadcaster', 'effort_controller',
                       '--controller-manager', f'/{name}/controller_manager',
                       '--controller-manager-timeout', '120',
                       '--switch-timeout', '20', '--activate-as-group'],
        ))

    # Stagger only six controller-manager startup operations (not twelve).
    for idx, combined in enumerate(combined_spawners):
        actions.append(TimerAction(period=5.0 + 1.2 * idx, actions=[combined]))

    # Verify/recover both controllers on all six arms after spawn.
    actions.append(TimerAction(period=13.0, actions=[Node(
        package='pp_two_link_factory', executable='controller_state_guard',
        name='controller_state_guard', output='screen',
    )]))

    return LaunchDescription(actions)
