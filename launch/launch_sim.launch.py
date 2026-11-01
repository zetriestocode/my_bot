import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
import xacro


def generate_launch_description():

    # Match the name of the xacro file with the name of the robot in the xacro file
    robot_name = 'differential_drive_robot'

    # Name of package in workspace
    package_name = 'my_bot'

    world = LaunchConfiguration('world')
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value="empty.sdf",
        description='World to load'
    )

    # Robot state publisher, from rsp.launch.py (builds the URDF from xacro)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Gazebo Sim with the chosen world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v4 ', world], 'on_exit_shutdown': 'true'}.items()
    )

    # Spawn the robot from the robot_description topic
    spawn_entity = TimerAction(
        period=5.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', robot_name,
                       '-topic', 'robot_description',
                       '-z', '0.1'],
            output='screen'
        )]
    )

    # ROS <-> Gazebo bridge (clock, scan, camera)
    bridge_params = os.path.join(
        get_package_share_directory(package_name), 'config', 'gz_bridge.yaml')

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_params}],
        output='screen'
    )

    ros_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw']
    )

    # Controllers, started after the controller manager exists
    joint_broad_spawner = TimerAction(
        period=10.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_broad'],
        )]
    )

    diff_drive_spawner = TimerAction(
        period=10.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['diff_cont',
                       '--controller-ros-args',
                       '-r /diff_cont/cmd_vel:=/cmd_vel'],
        )]
    )

    # Teleop publishes Twist to /cmd_vel_remap. This node converts it to
    # TwistStamped on /cmd_vel, which diff_cont subscribes to.
    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        parameters=[{'frame_id': 'base_link'}],
        remappings=[
            ('cmd_vel_in', '/cmd_vel_remap'),
            ('cmd_vel_out', '/cmd_vel'),
        ],
        output='screen'
    )

    return LaunchDescription([
        world_arg,
        rsp,
        gazebo,
        spawn_entity,
        ros_gz_bridge,
        ros_gz_image_bridge,
        joint_broad_spawner,
        diff_drive_spawner,
        twist_stamper,
    ])

