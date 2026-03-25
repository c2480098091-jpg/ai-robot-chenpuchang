#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class Square(Node):
    def __init__(self):
        super().__init__('square')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
    def move_straight(self, speed, duration):
        msg = Twist()
        msg.linear.x = speed
        self.publisher.publish(msg)
        time.sleep(duration)
        self.stop()
        
    def rotate(self, speed, duration):
        msg = Twist()
        msg.angular.z = speed
        self.publisher.publish(msg)
        time.sleep(duration)
        self.stop()
        
    def stop(self):
        msg = Twist()
        self.publisher.publish(msg)
        time.sleep(0.5)
        
    def draw_square(self):
        for _ in range(4):
            print("Moving straight...")
            self.move_straight(2.0, 1.0)  # 前进
            print("Rotating...")
            self.rotate(1.57, 1.0)        # 旋转90度
        print("Square completed!")

def main():
    print("Starting square drawing...")
    rclpy.init()
    square = Square()
    square.draw_square()
    square.destroy_node()
    rclpy.shutdown()
    print("Done!")

if __name__ == '__main__':
    main()
    