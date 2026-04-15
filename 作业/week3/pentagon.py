#!/usr/bin/env python3
"""
让小乌龟走五边形的控制脚本
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math


class PentagonMover(Node):
    """走五边形的控制节点"""

    def __init__(self):
        super().__init__('pentagon_mover')

        # 创建发布者
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # ============ 参数设置 ============
        self.SPEED = 1.0              # 线速度 m/s
        self.TURN_SPEED = 1.0          # 角速度 rad/s
        self.SIDE_LENGTH = 2.0         # 五边形边长 m
        self.MOVE_TIME = self.SIDE_LENGTH / self.SPEED  # 直行时间
        # 正五边形外角72度 = 2π/5 ≈ 1.256 rad
        self.TURN_ANGLE = 2 * math.pi / 5  # 72度
        self.TURN_TIME = self.TURN_ANGLE / self.TURN_SPEED  # 转弯时间

        self.get_logger().info('⬟ 五边形控制器初始化完成')
        self.get_logger().info(f'📐 边长: {self.SIDE_LENGTH}m, 直行时间: {self.MOVE_TIME:.2f}s')
        self.get_logger().info(f'🔄 转弯角度: 72°, 转弯时间: {self.TURN_TIME:.2f}s')

    def move_straight(self):
        """直行指定时间"""
        self.get_logger().info('➡️ 正在直行...')

        msg = Twist()
        msg.linear.x = self.SPEED
        msg.angular.z = 0.0

        start_time = time.time()
        while time.time() - start_time < self.MOVE_TIME:
            self.cmd_vel_pub.publish(msg)
            time.sleep(0.01)

        # 停止
        self.stop()
        self.get_logger().info('✅ 直行完成')

    def turn(self):
        """旋转指定角度"""
        self.get_logger().info('🔄 正在转弯(72°)...')

        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = self.TURN_SPEED  # 正值左转

        start_time = time.time()
        while time.time() - start_time < self.TURN_TIME:
            self.cmd_vel_pub.publish(msg)
            time.sleep(0.01)

        # 停止
        self.stop()
        self.get_logger().info('✅ 转弯完成')

    def stop(self):
        """停止运动"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_pub.publish(msg)
        time.sleep(0.1)

    def run(self):
        """执行走五边形"""
        self.get_logger().info('⬟ 开始走五边形！')
        self.get_logger().info('=' * 30)

        for i in range(5):
            self.get_logger().info(f'第 {i+1} 条边:')
            self.move_straight()  # 直行
            if i < 4:  # 最后一次不需要再转弯
                self.turn()  # 转弯

        self.get_logger().info('=' * 30)
        self.get_logger().info('🎉 五边形走完！回到起点！')


def main(args=None):
    rclpy.init(args=args)
    node = PentagonMover()

    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().info('⚠️ 用户中断')
    finally:
        node.destroy_node()
        rclpy.shutdown()
        print("程序结束")


if __name__ == '__main__':
    main()