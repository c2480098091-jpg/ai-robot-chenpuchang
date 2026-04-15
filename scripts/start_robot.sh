#!/bin/bash
echo "🚀 启动机器狗仿真..."

# 终端1: 启动 robot_state_publisher
gnome-terminal -- bash -c "cd ~/ai-robot-chenpuchang && source install/setup.bash && ros2 run robot_state_publisher robot_state_publisher quadruped_controller/urdf/quadruped.urdf; exec bash"

sleep 2

# 终端2: 启动 Rviz2
gnome-terminal -- bash -c "rviz2 -d ~/ai-robot-chenpuchang/quadruped_controller/config/quadruped.rviz; exec bash"

sleep 2

# 终端3: 启动动画控制器
gnome-terminal -- bash -c "cd ~/ai-robot-chenpuchang && source install/setup.bash && python3 quadruped_controller/quadruped_controller/animate.py; exec bash"

echo "✅ 所有程序已启动！"
