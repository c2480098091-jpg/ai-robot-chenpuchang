import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/chenpuuuu/ai-robot-chenpuchang/install/quadruped_controller'
