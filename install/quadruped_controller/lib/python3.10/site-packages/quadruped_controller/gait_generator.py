#!/usr/bin/env python3
"""
步态生成器模块
"""

import numpy as np


class GaitGenerator:
    """步态生成器"""
    
    def __init__(self):
        # 步态参数
        self.gait_cycle = 0.6  # 步态周期（秒）
        self.step_height = 0.05  # 抬腿高度（米）
        self.step_length = 0.1   # 步长（米）
        
        # 相位偏移（trot步态）
        self.phases = {
            'FL': 0.0,   # 前左
            'FR': 0.5,   # 前右
            'RL': 0.5,   # 后左
            'RR': 0.0    # 后右
        }
        
        # 站立高度
        self.stand_height = -0.25
        
    def update(self, current_time, dt):
        """
        更新步态轨迹
        Returns:
            dict: 每条腿的足端轨迹 {leg_name: [x, y, z]}
        """
        foot_positions = {}
        
        for leg_name, phase_offset in self.phases.items():
            # 计算相位
            phase = (current_time / self.gait_cycle + phase_offset) % 1.0
            
            # 计算足端位置
            foot_pos = self._compute_foot_position(phase)
            foot_positions[leg_name] = foot_pos
            
        return foot_positions
    
    def _compute_foot_position(self, phase):
        """
        计算单条腿的足端轨迹
        Args:
            phase: 步态相位 [0, 1)
        Returns:
            [x, y, z]: 足端位置
        """
        if phase < 0.5:  # 摆动相
            t = phase / 0.5
            x = self.step_length * (t - 0.5)
            z = self.stand_height + self.step_height * np.sin(np.pi * t)
            y = 0.0
        else:  # 支撑相
            t = (phase - 0.5) / 0.5
            x = self.step_length * (0.5 - t)
            z = self.stand_height
            y = 0.0
            
        return np.array([x, 0.2, z])  # 0.2是腿的横向偏移
    
    def set_gait_type(self, gait_type):
        """设置步态类型"""
        if gait_type == 'trot':
            self.phases = {
                'FL': 0.0,
                'FR': 0.5,
                'RL': 0.5,
                'RR': 0.0
            }
        elif gait_type == 'walk':
            self.phases = {
                'FL': 0.0,
                'FR': 0.25,
                'RL': 0.5,
                'RR': 0.75
            }
        elif gait_type == 'gallop':
            self.phases = {
                'FL': 0.0,
                'FR': 0.0,
                'RL': 0.0,
                'RR': 0.0
            }