import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('xela_models')
    
    # Argument to select the model
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='4x4',
        description='Model name (e.g., 4x4, 1x6, aftc)'
    )
        # Argument to enable/disable the joint sliders GUI
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Show the joint_state_publisher GUI (true/false)'
    )
    
    # Generate the robot_description by looking for a .urdf file (instead of .xacro)
    robot_description_content = Command([
        'xacro ', 
        pkg_share, 
        '/urdf/', 
        LaunchConfiguration('model'), 
        '.urdf' 
    ])
    
    # Node Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )
    
    # Node Joint State Publisher with Gui
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui'))
    )
    
    # Node Joint State Publisher without GUI
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )
    
    # Node RViz2
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )
    
    return LaunchDescription([
        model_arg,
        gui_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        joint_state_publisher_node,
        rviz_node
    ])