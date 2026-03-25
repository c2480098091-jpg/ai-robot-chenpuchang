from setuptools import setup
import os
from glob import glob

package_name = 'quadruped_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 添加urdf文件
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        # 添加launch文件
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # 添加config文件
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='chenpuuuu',
    maintainer_email='chenpuuuu@todo.todo',
    description='四足机器狗控制器',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controller = quadruped_controller.controller:main',
        ],
    },
)
