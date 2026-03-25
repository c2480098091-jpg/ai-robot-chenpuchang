#!/usr/bin/env python3
"""
运动学计算模块
"""

import numpy as np


class LegKinematics:
    """单腿运动学类"""
    
    def __init__(self):
        # 腿参数（单位：米）
        self.leg_params = {
            'FL': {'hip_offset': 0.15, 'thigh_length': 0.25, 'calf_length': 0.25},
            'FR': {'hip_offset': 0.15, 'thigh_length': 0.25, 'calf_length': 0.25},
            'RL': {'hip_offset': 0.15, 'thigh_length': 0.25, 'calf_length': 0.25},
            'RR': {'hip_offset': 0.15, 'thigh_length': 0.25, 'calf_length': 0.25}
        }
        
    def inverse_kinematics(self, leg_name, x, y, z):
        """
        逆运动学计算
        Args:
            leg_name: 腿名称 (FL, FR, RL, RR)
            x, y, z: 足端相对髋关节的位置
        Returns:
            [hip_angle, thigh_angle, calf_angle]: 关节角度（弧度）
        """
        params = self.leg_params[leg_name]
        L_hip = params["hip_offset"]
        L_thigh = params["thigh_length"]
        L_calf = params["calf_length"]
        
        # 髋关节角度（侧向）
        hip_angle = np.arctan2(y, L_hip)
        
        # 腿部平面内的目标点
        x_leg = x - L_hip
        z_leg = z
        
        # 计算从髋关节到足端的距离
        r = np.sqrt(x_leg**2 + z_leg**2)
        
        # 膝关节角度（余弦定理）
        cos_calf = (L_thigh**2 + L_calf**2 - r**2) / (2 * L_thigh * L_calf)
        cos_calf = np.clip(cos_calf, -1.0, 1.0)
        calf_angle = np.pi - np.arccos(cos_calf)
        
        # 大腿关节角度（腿部平面内）
        alpha = np.arctan2(z_leg, x_leg)
        beta = np.arccos((L_thigh**2 + r**2 - L_calf**2) / (2 * L_thigh * r))
        thigh_angle = alpha + beta
        
        # 限制角度范围
        hip_angle = np.clip(hip_angle, -0.8, 0.8)
        thigh_angle = np.clip(thigh_angle, -1.5, 1.5)
        calf_angle = np.clip(calf_angle, -2.0, 2.0)
        
        return [hip_angle, thigh_angle, calf_angle]
