#!/usr/bin/env python3
import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def make_robot(prefix, model_name, x, y, z, yaw, visual_xacro):
    doc = xacro.process_file(visual_xacro, mappings={'prefix': prefix})
    robot_desc = doc.toxml()
    return Node(
        package='ros_gz_sim', executable='create', name=f'spawn_{model_name}', output='screen',
        arguments=['-string', robot_desc, '-name', model_name,
                   '-x', str(x), '-y', str(y), '-z', str(z),
                   '-R', '0.0', '-P', '0.0', '-Y', str(yaw),
                   '-allow_renaming', 'false'],
    )


def generate_launch_description():
    pp_share = get_package_share_directory('pp_two_link_factory')
    world_share = get_package_share_directory('pp_factory_world')

    world_file = os.path.join(world_share, 'worlds', 'omx_factory_v6_harmonic.sdf')
    visual_xacro = os.path.join(pp_share, 'urdf', 'pp_two_link_gripper_visual.urdf.xacro')

    # Keep the existing factory exactly as-is; only robot models are replaced.
    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[pp_share, ':', world_share, ':', os.environ.get('GZ_SIM_RESOURCE_PATH', '')],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-v 2 {world_file}'}.items(),
    )

    # Table top = z 0.800 m. Base radius = 0.12 m.
    # Table inner edges are y=+/-0.94 m, therefore base centres y=+/-1.06 m
    # place the whole circular base on the table while touching that edge.
    configs = [
        ('arm1_', 'arm1', -2.20,  1.06, 0.800, -1.57079632679),
        ('arm2_', 'arm2',  0.00,  1.06, 0.800, -1.57079632679),
        ('arm3_', 'arm3',  2.20,  1.06, 0.800, -1.57079632679),
        ('arm4_', 'arm4', -2.20, -1.06, 0.800,  1.57079632679),
        ('arm5_', 'arm5',  0.00, -1.06, 0.800,  1.57079632679),
        ('arm6_', 'arm6',  2.20, -1.06, 0.800,  1.57079632679),
    ]

    actions = [resource_path, gazebo]
    for cfg in configs:
        actions.append(make_robot(*cfg, visual_xacro))
    return LaunchDescription(actions)
