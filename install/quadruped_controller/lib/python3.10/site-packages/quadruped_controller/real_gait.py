#!/usr/bin/env python3
"""
真实四足步态控制器 - Trot 步态
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
import time


class RealGaitController(Node):
    def __init__(self):
        super().__init__('real_gait_controller')
        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 所有关节
        self.joint_names = [
            'FL_hip', 'FL_knee', 'FR_hip', 'FR_knee',
            'RL_hip', 'RL_knee', 'RR_hip', 'RR_knee'
        ]
        
        # 步态参数
        self.gait_cycle = 1.0  # 完整步态周期（秒）
        self.step_height = 0.5  # 抬腿幅度
        self.step_length = 0.5  # 摆腿幅度
        
        self.timer = self.create_timer(0.02, self.update)  # 50Hz
        self.start_time = time.time()
        
        print('🐕 真实步态控制器启动 - Trot 步态')
        print('对角线腿同时运动: (左前+右后) 和 (右前+左后)')
    
    def update(self):
        t = time.time() - self.start_time
        phase = (t % self.gait_cycle) / self.gait_cycle  # 相位 [0, 1)
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        
        positions = []
        
        # 定义四条腿的相位
        legs = {
            'FL': {'hip_phase': 0.0, 'knee_phase': 0.0},      # 前左: 相位0
            'FR': {'hip_phase': 0.5, 'knee_phase': 0.5},      # 前右: 相位0.5
            'RL': {'hip_phase': 0.5, 'knee_phase': 0.5},      # 后左: 相位0.5
            'RR': {'hip_phase': 0.0, 'knee_phase': 0.0}       # 后右: 相位0
        }
        
        for leg_name in ['FL', 'FR', 'RL', 'RR']:
            # 计算该腿的相位
            leg_phase = (phase + legs[leg_name]['hip_phase']) % 1.0
            
            # 髋关节角度（前后摆动）
            if leg_phase < 0.5:
                # 支撑相：腿向后推
                t_phase = leg_phase / 0.5
                hip_angle = -self.step_length * (1 - np.cos(np.pi * t_phase)) / 2
            else:
                # 摆动相：腿向前迈
                t_phase = (leg_phase - 0.5) / 0.5
                hip_angle = self.step_length * (1 - np.cos(np.pi * t_phase)) / 2
            
            # 膝关节角度（抬腿）
            if leg_phase < 0.5:
                # 支撑相：腿伸直
                knee_angle = -0.2
            else:
                # 摆动相：抬腿
                t_phase = (leg_phase - 0.5) / 0.5
                knee_angle = -0.6 + self.step_height * np.sin(np.pi * t_phase)
            
            # 右侧腿相位相反（保持平衡）
            if leg_name in ['FR', 'RR']:
                hip_angle = -hip_angle
            
            positions.append(hip_angle)   # FL_hip
            positions.append(knee_angle)  # FL_knee
        
        msg.position = positions
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = RealGaitController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n👋 停止步态')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
