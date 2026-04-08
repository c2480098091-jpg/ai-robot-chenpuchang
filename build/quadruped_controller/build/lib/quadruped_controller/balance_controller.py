#!/usr/bin/env python3
"""
平衡控制器模块
"""

import numpy as np


class BalanceController:
    """姿态平衡控制器"""
    
    def __init__(self):
        # PID控制器参数
        self.kp_roll = 2.0   # 滚转比例系数
        self.kp_pitch = 2.0  # 俯仰比例系数
        self.kd_roll = 0.5   # 滚转微分系数
        self.kd_pitch = 0.5  # 俯仰微分系数
        
        # 状态变量
        self.prev_roll_error = 0.0
        self.prev_pitch_error = 0.0
        self.prev_time = 0.0
        
    def update(self, current_time, foot_positions, imu_data=None):
        """
        更新平衡补偿
        Args:
            current_time: 当前时间
            foot_positions: 当前足端位置
            imu_data: IMU数据（可选）
        Returns:
            dict: 每条腿的位置补偿
        """
        compensation = {}
        
        if imu_data is None:
            # 如果没有IMU数据，返回零补偿
            for leg_name in foot_positions.keys():
                compensation[leg_name] = np.array([0.0, 0.0, 0.0])
            return compensation
        
        # 计算姿态误差（假设目标姿态为水平）
        roll_error = 0.0 - imu_data.get('roll', 0.0)
        pitch_error = 0.0 - imu_data.get('pitch', 0.0)
        
        # 计算时间差
        dt = current_time - self.prev_time if self.prev_time > 0 else 0.01
        self.prev_time = current_time
        
        # PID计算
        roll_comp = self.kp_roll * roll_error + self.kd_roll * (roll_error - self.prev_roll_error) / dt
        pitch_comp = self.kp_pitch * pitch_error + self.kd_pitch * (pitch_error - self.prev_pitch_error) / dt
        
        # 更新误差
        self.prev_roll_error = roll_error
        self.prev_pitch_error = pitch_error
        
        # 根据姿态误差调整各腿高度
        compensation['FL'] = np.array([0.0, 0.0, -roll_comp + pitch_comp])
        compensation['FR'] = np.array([0.0, 0.0, roll_comp + pitch_comp])
        compensation['RL'] = np.array([0.0, 0.0, -roll_comp - pitch_comp])
        compensation['RR'] = np.array([0.0, 0.0, roll_comp - pitch_comp])
        
        return compensation