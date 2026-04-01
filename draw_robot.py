import pybullet as p
import pybullet_data as pd
import time
import math

p.connect(p.GUI)
p.setAdditionalSearchPath(pd.getDataPath())
p.setGravity(0, 0, -9.8)
p.resetDebugVisualizerCamera(1.8, 45, -35, [0.5, 0, 0.7])

p.loadURDF("plane.urdf")
p.loadURDF("table/table.urdf", [0.5, 0, 0], useFixedBase=True)
pandaId = p.loadURDF("franka_panda/panda.urdf", [0.5, 0, 0.625], useFixedBase=True)

init_joints = [0, -0.5, 0, -2.0, 0, 1.5, 0.7]
for i in range(7):
    p.resetJointState(pandaId, i, init_joints[i])
for _ in range(200):
    p.stepSimulation()
    time.sleep(1./240.)
print("初始化完成")

DOWN = p.getQuaternionFromEuler([math.pi, 0, 0])

cx, cy, cz = 0.75, 0.25, 0.85
radius   = 0.08
N_circle = 120
N_line   = 80

print("预计算圆路径IK...")
circle_path, circle_ja = [], []
for i in range(N_circle + 1):
    angle = 2 * math.pi * i / N_circle
    pt = [cx + radius*math.cos(angle),
          cy + radius*math.sin(angle), cz]
    ja = p.calculateInverseKinematics(
        pandaId, 11, pt, DOWN,
        maxNumIterations=500, residualThreshold=1e-6)
    circle_path.append(pt)
    circle_ja.append(list(ja))

print("预计算直线路径IK...")
line_path, line_ja = [], []
for i in range(N_line):
    t  = i / (N_line - 1)
    pt = [cx + radius - 2*radius*t, cy, cz]
    ja = p.calculateInverseKinematics(
        pandaId, 11, pt, DOWN,
        maxNumIterations=500, residualThreshold=1e-6)
    line_path.append(pt)
    line_ja.append(list(ja))
print("预计算完成")

for i in range(N_circle):
    p.addUserDebugLine(circle_path[i], circle_path[i+1], [0,1,0], 2)
for i in range(N_line - 1):
    p.addUserDebugLine(line_path[i], line_path[i+1], [1,0.5,0], 2)
for pos, col in [([cx,cy,cz],[1,0,0]),
                 (line_path[0],[0,0,1]),
                 (line_path[-1],[1,1,0])]:
    vs = p.createVisualShape(p.GEOM_SPHERE, radius=0.006, rgbaColor=col+[1])
    p.createMultiBody(baseVisualShapeIndex=vs, basePosition=pos)

def move_to_start(ja, steps=400):
    for i in range(7):
        p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL,
                                ja[i], force=500, maxVelocity=0.4)
    for _ in range(steps):
        p.stepSimulation()
        time.sleep(1./240.)

def move_smooth(ja, steps=30):
    for i in range(7):
        p.setJointMotorControl2(pandaId, i, p.POSITION_CONTROL,
                                ja[i], force=500, maxVelocity=0.6)
    for _ in range(steps):
        p.stepSimulation()
        time.sleep(1./480.)

print("移动到圆起点...")
tid = p.addUserDebugText("移动到起点...", [0.5, 0.4, 1.1], [0,0,1], 1.2)
move_to_start(circle_ja[0])

print("开始画圆...")
actual = []
p.removeUserDebugItem(tid)
tid = p.addUserDebugText("画圆中...", [0.5, 0.4, 1.1], [0,0,1], 1.2)

for idx in range(N_circle + 1):
    move_smooth(circle_ja[idx], steps=30)
    pos = p.getLinkState(pandaId, 11)[0]
    actual.append(list(pos))
    if len(actual) > 1:
        p.addUserDebugLine(actual[-2], actual[-1], [0,0.5,1], 3)
    if idx % 15 == 0:
        p.removeUserDebugItem(tid)
        err = math.sqrt(sum((pos[k]-circle_path[idx][k])**2 for k in range(3)))*1000
        tid = p.addUserDebugText(
            f"画圆: {idx}/{N_circle}  误差:{err:.1f}mm",
            [0.5, 0.4, 1.1], [0,0,0], 1.1)

print("圆完成！")
time.sleep(1)

print("移动到直线起点...")
p.removeUserDebugItem(tid)
tid = p.addUserDebugText("移动到直线起点...", [0.5, 0.4, 1.1], [0,0.5,0], 1.2)
move_to_start(line_ja[0])

print("开始画直线...")
actual_line = []
p.removeUserDebugItem(tid)
tid = p.addUserDebugText("画直线中...", [0.5, 0.4, 1.1], [0,1,0], 1.2)

for idx in range(N_line):
    move_smooth(line_ja[idx], steps=30)
    pos = p.getLinkState(pandaId, 11)[0]
    actual_line.append(list(pos))
    if len(actual_line) > 1:
        p.addUserDebugLine(actual_line[-2], actual_line[-1], [1,0,0], 3)
    if idx % 10 == 0:
        p.removeUserDebugItem(tid)
        err = math.sqrt(sum((pos[k]-line_path[idx][k])**2 for k in range(3)))*1000
        tid = p.addUserDebugText(
            f"画直线: {idx+1}/{N_line}  误差:{err:.1f}mm",
            [0.5, 0.4, 1.1], [0,0,0], 1.1)

print("直线完成！")
p.removeUserDebugItem(tid)
p.addUserDebugText(
    "全部完成!\n绿=目标圆  蓝=实际圆\n橙=目标线  红=实际线",
    [0.5, 0.4, 1.1], [0,1,0], 1.1)

print("按 Ctrl+C 退出")
while True:
    p.stepSimulation()
    time.sleep(1./240.)
