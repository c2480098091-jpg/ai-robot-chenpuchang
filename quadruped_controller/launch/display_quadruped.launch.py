#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    # 获取URDF文件路径
    urdf_file = os.path.join(
        os.path.dirname(__file__),
        '../urdf/quadruped.urdf'
    )
    
    # 读取URDF内容
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    return LaunchDescription([
        # 机器人状态发布器
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),
        
        # 关节状态发布器
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),
        
        # Rviz2可视化
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(os.path.dirname(__file__), '../config/quadruped.rviz')]
        ),
        
        # 控制器节点
        Node(
            package='quadruped_controller',
            executable='controller',
            name='quadruped_controller',
            output='screen'
        )
    ])
