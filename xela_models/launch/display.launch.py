import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('xela_models')
    
    # Arguments to select the model (default is your uSP44 / 4x4)
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='4x4',
        description='Model name (e.g., 4x4, 1x6, aftc)'
    )
    
    # Generate the robot_description "on the fly" by converting the xacro file
    robot_description_content = Command([
        'xacro ', 
        pkg_share, 
        '/urdf/', 
        LaunchConfiguration('model'), 
        '.xacro' 
    ])
    
    # Node Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )
    
    # Node Joint State Publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
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
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])