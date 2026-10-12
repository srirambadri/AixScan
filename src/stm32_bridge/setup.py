from setuptools import find_packages, setup

package_name = 'stm32_bridge'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='srirambadri',
    maintainer_email='sriram.badri-ext@ayiram-r3.com',
    description='ROS 2 bridge between an STM32 microcontroller and ROS 2 topics.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'log_receiver = stm32_bridge.log_receiver:main',
        ],
    },
)
