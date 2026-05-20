import pybullet as p
import pybullet_data
import time
import numpy as np
import math

class QuadrupedController:
    """简单的四足控制器"""

    def __init__(self, robot_id):
        self.robot_id = robot_id

        # 关节ID（需要根据实际模型调整）
        self.leg_joints = {
            'LF': [0, 1, 2],
            'RF': [3, 4, 5],
            'LH': [6, 7, 8],
            'RH': [9, 10, 11]
        }

        # 步态参数
        self.stance_height = 0.3  # 站立高度
        self.step_height = 0.05   # 抬腿高度
        self.step_length = 0.1    # 步长

    def trot_gait(self, t, leg_name, frequency=1.0):
        """
        Trot步态生成
        """
        # 相位（对角腿同相）
        if leg_name in ['LF', 'RH']:
            phase = 0
        else:  # RF, LH
            phase = np.pi

        # 步态周期位置
        cycle_phase = (2 * np.pi * frequency * t + phase) % (2 * np.pi)

        # 摆动相 vs 支撑相
        if cycle_phase < np.pi:  # 摆动相（腿抬起）
            progress = cycle_phase / np.pi
            x = self.step_length * (progress - 0.5)
            z = self.step_height * np.sin(np.pi * progress)
        else:  # 支撑相（腿着地）
            progress = (cycle_phase - np.pi) / np.pi
            x = self.step_length * (0.5 - progress)
            z = 0

        # 逆运动学（简化版）
        y = 0  # 横向位置
        hip = 0

        # 大腿和小腿角度（简化计算）
        l_thigh = 0.2  # 大腿长度
        l_calf = 0.2   # 小腿长度
        target_height = self.stance_height + z

        # 简化逆运动学
        thigh = np.arctan2(x, target_height)
        calf = -2 * thigh

        return [hip, thigh, calf]

    def step(self, t, frequency=1.0):
        """执行一步控制"""
        for leg_name, joint_ids in self.leg_joints.items():
            target_angles = self.trot_gait(t, leg_name, frequency)

            for joint_id, angle in zip(joint_ids, target_angles):
                p.setJointMotorControl2(
                    self.robot_id,
                    joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=100  # 增大力矩
                )

# 主程序
def main():
    # 初始化
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")

    # 加载机器人 - 修正姿态
    start_orientation = p.getQuaternionFromEuler([math.pi/2, 0, math.pi/2])
    robotId = p.loadURDF("laikago/laikago_toes.urdf", [0, 0, 0.5], start_orientation)

    # 打印关节信息
    print("关节信息：")
    for i in range(p.getNumJoints(robotId)):
        info = p.getJointInfo(robotId, i)
        print(f"关节 {i}: {info[1].decode()} 类型={info[2]}")

    # 创建控制器
    controller = QuadrupedController(robotId)

    # 仿真参数
    t = 0
    dt = 1./240.

    # 先让机器人稳定站立（自由落体）
    print("稳定站立中...")
    for _ in range(500):
        p.stepSimulation()
        time.sleep(dt)

    # 微抬每条腿（逐个抬起放下）
    print("微抬腿准备...")
    for leg_name, joint_ids in controller.leg_joints.items():
        print(f"抬起 {leg_name}...")
        # 抬腿：小腿收起
        for _ in range(100):
            for j_id in joint_ids:
                p.setJointMotorControl2(
                    robotId, j_id,
                    p.POSITION_CONTROL,
                    targetPosition=0, force=50
                )
            p.stepSimulation()
            time.sleep(dt)

        # 放下
        for _ in range(100):
            for j_id in joint_ids:
                p.setJointMotorControl2(
                    robotId, j_id,
                    p.POSITION_CONTROL,
                    targetPosition=0, force=50
                )
            p.stepSimulation()
            time.sleep(dt)

    print("开始行走，按Ctrl+C停止...")

    try:
        while True:
            controller.step(t, frequency=0.3)
            p.stepSimulation()
            time.sleep(dt)
            t += dt

    except KeyboardInterrupt:
        print("仿真结束")

    p.disconnect()

if __name__ == '__main__':
    main()