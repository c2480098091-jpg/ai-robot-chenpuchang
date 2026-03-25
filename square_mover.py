#!/usr/bin/env python3
"""
让小乌龟走正方形的控制脚本
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class SquareMover(Node):
    def __init__(self):
        super().__init__('square_mover')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # 速度参数
        self.SPEED = 1.0
        self.TURN_SPEED = 1.5
        self.SIDE_LENGTH = 2.0
        self.MOVE_TIME = self.SIDE_LENGTH / self.SPEED
        self.TURN_TIME = 1.57 / self.TURN_SPEED
        
        self.get_logger().info('🐢 正方形移动节点已启动')
        self.get_logger().info(f'移动时间: {self.MOVE_TIME:.2f}秒')
        self.get_logger().info(f'旋转时间: {self.TURN_TIME:.2f}秒')
    
    def move_straight(self, duration):
        msg = Twist()
        msg.linear.x = self.SPEED
        msg.angular.z = 0.0
        
        self.get_logger().info(f'⬆️ 直行 {duration:.2f} 秒')
        self.publisher.publish(msg)
        
        start_time = self.get_clock().now()
        while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
            rclpy.spin_once(self, timeout_sec=0.01)
        
        self.stop()
    
    def turn(self, duration):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = self.TURN_SPEED
        
        self.get_logger().info(f'🔄 旋转 {duration:.2f} 秒')
        self.publisher.publish(msg)
        
        start_time = self.get_clock().now()
        while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
            rclpy.spin_once(self, timeout_sec=0.01)
        
        self.stop()
    
    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher.publish(msg)
        self.get_logger().info('⏸️ 停止')
    
    def run_square(self):
        self.get_logger().info('🎯 开始走正方形...')
        
        for i in range(4):
            self.get_logger().info(f'📐 第 {i+1} 条边')
            self.move_straight(self.MOVE_TIME)
            if i < 3:
                self.turn(self.TURN_TIME)
        
        self.get_logger().info('🎉 正方形走完！回到起点！')


def main(args=None):
    rclpy.init(args=args)
    node = SquareMover()
    
    try:
        node.run_square()
    except KeyboardInterrupt:
        node.get_logger().info('👋 用户中断')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
