import pybullet as p
import pybullet_data as pd
import time
import math
import numpy as np

# 连接PyBullet
p.connect(p.GUI)
p.setAdditionalSearchPath(pd.getDataPath())
p.setGravity(0, 0, -9.8)

# 设置更好的相机视角
p.resetDebugVisualizerCamera(cameraDistance=1.6, cameraYaw=45, cameraPitch=-35, cameraTargetPosition=[0.6, 0, 0.75])

# 加载地面和桌子
p.loadURDF("plane.urdf")
table_pos = [0.5, 0, 0]
p.loadURDF("table/table.urdf", table_pos, useFixedBase=True)

# 加载Franka机械臂
panda_pos = [0.5, 0, 0.65]
pandaId = p.loadURDF("franka_panda/panda.urdf", panda_pos, useFixedBase=True)

print("="*60)
print("机器人画圆和直线程序")
print("="*60)

# ========== 定义圆的参数 ==========
circle_center = [0.6, 0.0, 0.85]  # 圆心位置
circle_radius = 0.12              # 半径
circle_points_count = 80          # 圆的点数

# 生成圆的路径点
circle_path = []
for i in range(circle_points_count):
    angle = 2 * math.pi * i / circle_points_count
    x = circle_center[0] + circle_radius * math.cos(angle)
    y = circle_center[1] + circle_radius * math.sin(angle)
    z = circle_center[2]
    circle_path.append([x, y, z])

# ========== 定义直线的参数 ==========
# 直线的起点和终点（在圆上的两点）
line_start_point = [circle_center[0] + circle_radius, circle_center[1], circle_center[2]]  # 圆最右边点
line_end_point = [circle_center[0] - circle_radius, circle_center[1], circle_center[2]]    # 圆最左边点
line_points_count = 50  # 直线的点数

# 生成直线的路径点
line_path = []
for i in range(line_points_count):
    t = i / (line_points_count - 1)  # 0到1的插值
    x = line_start_point[0] + (line_end_point[0] - line_start_point[0]) * t
    y = line_start_point[1] + (line_end_point[1] - line_start_point[1]) * t
    z = line_start_point[2] + (line_end_point[2] - line_start_point[2]) * t
    line_path.append([x, y, z])

print(f"圆心位置: ({circle_center[0]}, {circle_center[1]}, {circle_center[2]})")
print(f"圆半径: {circle_radius}米")
print(f"圆的点数: {len(circle_path)}")
print(f"直线起点: ({line_start_point[0]}, {line_start_point[1]}, {line_start_point[2]})")
print(f"直线终点: ({line_end_point[0]}, {line_end_point[1]}, {line_end_point[2]})")
print(f"直线的点数: {len(line_path)}")

# ========== 绘制目标路径（虚线）==========
print("\n绘制目标路径...")

# 绘制绿色的圆（目标路径）
for i in range(len(circle_path) - 1):
    p.addUserDebugLine(circle_path[i], circle_path[i+1], [0, 1, 0], 2)
p.addUserDebugLine(circle_path[-1], circle_path[0], [0, 1, 0], 2)

# 绘制橙色的直线（目标路径）
for i in range(len(line_path) - 1):
    p.addUserDebugLine(line_path[i], line_path[i+1], [1, 0.5, 0], 2)

# 添加标记点
# 圆心标记（红色小球）
center_sphere = p.createVisualShape(p.GEOM_SPHERE, radius=0.008, rgbaColor=[1, 0, 0, 1])
center_marker = p.createMultiBody(baseVisualShapeIndex=center_sphere, basePosition=circle_center)

# 直线起点标记（蓝色小球）
start_sphere = p.createVisualShape(p.GEOM_SPHERE, radius=0.006, rgbaColor=[0, 0, 1, 1])
start_marker = p.createMultiBody(baseVisualShapeIndex=start_sphere, basePosition=line_start_point)

# 直线终点标记（黄色小球）
end_sphere = p.createVisualShape(p.GEOM_SPHERE, radius=0.006, rgbaColor=[1, 1, 0, 1])
end_marker = p.createMultiBody(baseVisualShapeIndex=end_sphere, basePosition=line_end_point)

print("路径绘制完成！")
print("- 绿色圆圈: 目标圆路径")
print("- 橙色直线: 目标直线路径")
print("- 红色球体: 圆心")
print("- 蓝色球体: 直线起点")
print("- 黄色球体: 直线终点")

# ========== 初始化机械臂位置 ==========
print("\n移动机械臂到圆的起点...")
circle_start_point = circle_path[0]

# 计算起始点的关节角度
start_joint_angles = p.calculateInverseKinematics(
    pandaId, 11, circle_start_point,
    p.getQuaternionFromEuler([math.pi, 0, 0])
)

# 移动到起点
for i in range(7):
    p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL, start_joint_angles[i], force=500)

# 等待到达起点
for step in range(300):
    p.stepSimulation()
    time.sleep(1./240.)

current_pos = p.getLinkState(pandaId, 11)[0]
print(f"机械臂已到达起点: ({current_pos[0]:.3f}, {current_pos[1]:.3f}, {current_pos[2]:.3f})")

# ========== 存储实际轨迹 ==========
actual_circle_trajectory = []
actual_line_trajectory = []

# 全局文本ID
info_text_id = None

# ========== 画圆函数 ==========
def draw_circle():
    global info_text_id
    
    print("\n开始画圆...")
    
    # 移除旧文本
    if info_text_id is not None:
        p.removeUserDebugItem(info_text_id)
    
    text_id = p.addUserDebugText("正在画圆 (IK模式)...", [0.4, -0.7, 1.0], [0, 0, 1], 1.2)
    
    for idx, target_point in enumerate(circle_path):
        # IK计算关节角度
        joint_angles = p.calculateInverseKinematics(
            pandaId, 11, target_point,
            p.getQuaternionFromEuler([math.pi, 0, 0])
        )
        
        # 应用关节控制
        for i in range(7):
            p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL, joint_angles[i], force=500)
        
        # 记录实际位置
        actual_pos = p.getLinkState(pandaId, 11)[0]
        actual_circle_trajectory.append([actual_pos[0], actual_pos[1], actual_pos[2]])
        
        # 实时绘制轨迹（蓝色实线）
        if len(actual_circle_trajectory) > 1:
            p.addUserDebugLine(
                actual_circle_trajectory[-2], 
                actual_circle_trajectory[-1], 
                [0, 0.5, 1],  # 蓝色
                3
            )
        
        # 更新进度显示
        progress = (idx + 1) / len(circle_path) * 100
        p.removeUserDebugItem(text_id)
        info_text = f"画圆进度: {progress:.1f}%\n"
        info_text += f"当前点: {idx + 1}/{len(circle_path)}\n"
        info_text += f"当前位置: ({actual_pos[0]:.3f}, {actual_pos[1]:.3f}, {actual_pos[2]:.3f})"
        text_id = p.addUserDebugText(info_text, [0.4, -0.7, 1.0], [0, 0, 0], 1.0)
        
        # 控制速度
        time.sleep(0.02)
        p.stepSimulation()
    
    print(f"圆绘制完成！实际轨迹点数: {len(actual_circle_trajectory)}")
    
    # 保存文本ID供后续使用
    info_text_id = text_id
    return text_id

# ========== 画直线函数 ==========
def draw_line():
    global info_text_id
    
    print("\n开始画直线...")
    
    # 移除旧文本
    if info_text_id is not None:
        p.removeUserDebugItem(info_text_id)
    
    text_id = p.addUserDebugText("正在画直线 (关节空间)...", [0.4, -0.7, 1.0], [0, 1, 0], 1.2)
    
    # 获取当前关节角度作为直线运动的起点
    current_joint_angles = [p.getJointState(pandaId, i)[0] for i in range(7)]
    
    # 计算直线终点的关节角度
    end_joint_angles = p.calculateInverseKinematics(
        pandaId, 11, line_end_point,
        p.getQuaternionFromEuler([math.pi, 0, 0])
    )
    
    # 使用关节空间插值画直线
    for step in range(line_points_count):
        t = step / (line_points_count - 1)  # 0到1的插值
        
        # 关节角度线性插值
        for i in range(7):
            angle = current_joint_angles[i] + (end_joint_angles[i] - current_joint_angles[i]) * t
            p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL, angle, force=500)
        
        # 记录实际位置
        actual_pos = p.getLinkState(pandaId, 11)[0]
        actual_line_trajectory.append([actual_pos[0], actual_pos[1], actual_pos[2]])
        
        # 实时绘制轨迹（红色实线）
        if len(actual_line_trajectory) > 1:
            p.addUserDebugLine(
                actual_line_trajectory[-2], 
                actual_line_trajectory[-1], 
                [1, 0, 0],  # 红色
                3
            )
        
        # 更新进度显示
        progress = (step + 1) / line_points_count * 100
        p.removeUserDebugItem(text_id)
        info_text = f"画直线进度: {progress:.1f}%\n"
        info_text += f"当前步数: {step + 1}/{line_points_count}\n"
        info_text += f"当前位置: ({actual_pos[0]:.3f}, {actual_pos[1]:.3f}, {actual_pos[2]:.3f})"
        text_id = p.addUserDebugText(info_text, [0.4, -0.7, 1.0], [0, 0, 0], 1.0)
        
        # 控制速度
        time.sleep(0.02)
        p.stepSimulation()
    
    print(f"直线绘制完成！实际轨迹点数: {len(actual_line_trajectory)}")
    
    # 保存文本ID供后续使用
    info_text_id = text_id
    return text_id

# ========== 执行运动 ==========
try:
    # 画圆
    text_id = draw_circle()
    
    # 短暂停顿，让用户看到圆完成
    time.sleep(1)
    
    # 画直线
    text_id = draw_line()
    
    # 完成
    print("\n所有任务完成！")
    if info_text_id is not None:
        p.removeUserDebugItem(info_text_id)
    
    final_text = f"任务完成！\n圆轨迹点数: {len(actual_circle_trajectory)}\n直线轨迹点数: {len(actual_line_trajectory)}"
    p.addUserDebugText(final_text, [0.4, -0.7, 1.0], [0, 1, 0], 1.2)
    
    print("\n程序继续运行，按Ctrl+C退出...")
    
    # 保持窗口打开
    while True:
        p.stepSimulation()
        time.sleep(1./240.)
        
except KeyboardInterrupt:
    print("\n程序被用户中断")
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    p.disconnect()
    print("仿真已断开")
