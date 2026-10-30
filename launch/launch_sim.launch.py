import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
import xacro


def generate_launch_description():

    # Match the name of the xacro file with the name of the robot in the xacro file
    robotXacroName = 'differential_drive_robot'

    # Name of package in workspace
    namePackage = 'my_bot'

    # Relative path to model and world files
    modelFileRelativePath = 'description/robot.urdf.xacro'

    # Absolute paths to model and world files
    pathModelFile = os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)
    # pathWorldFile = os.path.join(get_package_share_directory(namePackage), worldFileRelativePath)

    # Robot description in xml format
    robotDescription = xacro.process_file(pathModelFile).toxml()

    # Launch file from gazebo_ros package
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'))

    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value="empty.sdf",
        description='World to load'
        )

    # Include the Gazebo launch file, provided by the ros_gz_sim package
    gazeboLaunch = IncludeLaunchDescription(gazebo_rosPackageLaunch, 
                                            launch_arguments={'gz_args': ['-r -v4 ', world], 'on_exit_shutdown': 'true'}.items()
    )
    
    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', robotXacroName, 
                   '-topic', 'robot_description',
                   '-z', '0.1'],
        output='screen'
    )

    # Robot state publisher node
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robotDescription,
                     'use_sim_time': True}]
    )

    # Important: to control robot from ROS2 
    bridge_params = os.path.join(get_package_share_directory(namePackage), 'config', 'gz_bridge.yaml')

    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        # arguments=[
        #     '--rosargs',
        #     '-p',
        #     f'config_file:={bridge_params}',
        # ],
        parameters=[{'config_file': bridge_params}],
        output='screen',
    )   

    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"]
    )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_cont",
            '--controller-ros-args',
            '-r /diff_cont/cmd_vel:=/cmd_vel'
        ],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    # Remapping cmd_vel. Teleop node will publish to /cmd_vel_remap, which will be  
    # stamped and published to /cmd_vel for the diff_drive_controller to use.
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

    # Empty launch description object
    LaunchDescriptionObject = LaunchDescription()

    LaunchDescriptionObject.add_action(world_arg)
    
    # Add gazeboLaunch
    LaunchDescriptionObject.add_action(gazeboLaunch)

    # Add spawn node and robot state publisher node
    LaunchDescriptionObject.add_action(spawnModelNodeGazebo)
    LaunchDescriptionObject.add_action(nodeRobotStatePublisher)
    LaunchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    LaunchDescriptionObject.add_action(ros_gz_image_bridge)
    LaunchDescriptionObject.add_action(diff_drive_spawner)
    LaunchDescriptionObject.add_action(joint_broad_spawner)
    LaunchDescriptionObject.add_action(twist_stamper)
    
    return LaunchDescriptionObject

