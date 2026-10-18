import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'api_gateway'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Flask reads these from the install space, not the source tree
        (os.path.join('share', package_name, 'templates'), glob('templates/*.html')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='srirambadri',
    maintainer_email='sriram.badri-ext@ayiram-r3.com',
    description='ROS 2 gateway for the RVM scanner.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'scan_listener = api_gateway.scan_listener:main',
            'web_form = api_gateway.app:main',
        ],
    },
)
