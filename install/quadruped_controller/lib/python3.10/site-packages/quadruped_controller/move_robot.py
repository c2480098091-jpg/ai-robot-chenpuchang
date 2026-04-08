#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
import time

class RobotMover(Node):
    def __init__(self):
        super().__init__('robot_mover')
        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 关节名称（与 URDF 中的 joint 名称一致）
        self.joint_names = ['FL_hip', 'FR_hip', 'RL_hip', 'RR_hip']
        
        self.timer = self.create_timer(0.05, self.update)
        self.start_time = time.time()
        print('🤖 机器狗开始运动！')
    
    def update(self):
        t = time.time() - self.start_time
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        
        # 每条腿做正弦运动
        positions = []
        for i, name in enumerate(self.joint_names):
            # 前后腿有相位差
            phase = t * 2
            if 'FR' in name or 'RR' in name:
                phase = phase + np.pi  # 对侧腿相反相位
            pos = 0.5 * np.sin(phase)
            positions.append(pos)
        
        msg.position = positions
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = RobotMover()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
