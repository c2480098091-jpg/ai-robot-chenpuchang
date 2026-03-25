#!/usr/bin/env python3
"""
四足机器狗主控制器
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np

from quadruped_controller.kinematics import LegKinematics
from quadruped_controller.gait_generator import GaitGenerator
from quadruped_controller.balance_controller import BalanceController


class QuadrupedController(Node):
    """四足机器狗主控制器"""
    
    def __init__(self):
        super().__init__('quadruped_controller')
        
        self.get_logger().info('🤖 四足机器狗控制器启动中...')
        
        # 初始化组件
        self.kinematics = LegKinematics()
        self.gait_generator = GaitGenerator()
        self.balance_controller = BalanceController()
        
        # 关节名称（根据实际机器人调整）
        self.joint_names = [
            'FL_hip', 'FL_thigh', 'FL_calf',
            'FR_hip', 'FR_thigh', 'FR_calf',
            'RL_hip', 'RL_thigh', 'RL_calf',
            'RR_hip', 'RR_thigh', 'RR_calf'
        ]
        
        # 腿的顺序
        self.leg_order = ['FL', 'FR', 'RL', 'RR']
        
        # 创建发布器
        self.joint_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 控制参数
        self.control_rate = 50.0  # 50 Hz
        self.dt = 1.0 / self.control_rate
        self.current_time = 0.0
        
        # 创建定时器
        self.timer = self.create_timer(self.dt, self.control_loop)
        
        self.get_logger().info('✅ 控制器初始化完成')
    
    def control_loop(self):
        """主控制循环"""
        try:
            self.current_time += self.dt
            
            # 1. 生成步态轨迹
            foot_trajectories = self.gait_generator.update(self.current_time, self.dt)
            
            # 2. 计算平衡补偿
            balance_offsets = self.balance_controller.update(
                self.current_time, 
                foot_trajectories,
                imu_data=None
            )
            
            # 3. 逆运动学计算关节角度
            joint_angles = []
            for leg_name in self.leg_order:
                # 获取足端目标位置
                foot_pos = foot_trajectories[leg_name]
                
                # 添加平衡补偿
                if leg_name in balance_offsets:
                    foot_pos = foot_pos + balance_offsets[leg_name]
                
                # 逆运动学计算
                angles = self.kinematics.inverse_kinematics(
                    leg_name, 
                    foot_pos[0], 
                    foot_pos[1], 
                    foot_pos[2]
                )
                joint_angles.extend(angles)
            
            # 4. 发送关节命令
            self.send_joint_commands(joint_angles)
            
            # 可选：发布调试信息
            if int(self.current_time * 10) % 50 == 0:
                self.get_logger().info(f'时间: {self.current_time:.1f}s')
                
        except Exception as e:
            self.get_logger().error(f'控制循环错误: {e}')
    
    def send_joint_commands(self, positions):
        """发送关节轨迹命令"""
        traj_msg = JointTrajectory()
        traj_msg.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * len(positions)
        point.accelerations = [0.0] * len(positions)
        point.time_from_start = rclpy.duration.Duration(seconds=0.1).to_msg()
        
        traj_msg.points.append(point)
        self.joint_pub.publish(traj_msg)
    
    def stop(self):
        """停止所有运动"""
        self.get_logger().info('🛑 停止运动')
        zero_positions = [0.0] * len(self.joint_names)
        self.send_joint_commands(zero_positions)


def main(args=None):
    """主函数"""
    rclpy.init(args=args)
    controller = QuadrupedController()
    
    try:
        controller.get_logger().info('🚀 开始运行控制器')
        rclpy.spin(controller)
    except KeyboardInterrupt:
        print('\n👋 用户中断程序')
        controller.stop()
    except Exception as e:
        print(f'❌ 程序错误: {e}')
    finally:
        controller.destroy_node()
        rclpy.shutdown()
        print('✅ 程序结束')


if __name__ == '__main__':
    main()