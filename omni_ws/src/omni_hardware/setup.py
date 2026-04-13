import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'omni_hardware'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Machiraju',
    maintainer_email='machirajus7@gmail.com',
    description='Hardware bringup stubs for the omni robot.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'arduino_bridge = omni_hardware.arduino_bridge:main',
            'imu_driver = omni_hardware.imu_driver:main',
            'camera_node = omni_hardware.camera_node:main',
        ],
    },
)
