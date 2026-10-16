# Hardware Check

## Communication SMT Microcontroller

This is a ROS 2 package for displaying SMT log

```bash
hardware_check/
└── src/
    └── stm32_bridge/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── stm32_bridge
        └── stm32_bridge/
            ├── __init__.py
            └── log_receiver.py            
```

### Installation

Install the dependencies (`rclpy`, `std_msgs`, `pyserial`):

```bash
cd ~/hardware_check
rosdep install --from-paths src --ignore-src -r -y
```

Then build and source the workspace:

```bash
colcon build --packages-select stm32_bridge
source install/setup.bash
```

### Run
```bash
ros2 run stm32_bridge log_receiver
```

The serial port and baud rate are ROS parameters, defaulting to `/dev/ttyACM0` and
`115200`. Pass them explicitly if you need to be sure:

```bash
ros2 run stm32_bridge log_receiver --ros-args -p serial_port:=/dev/ttyACM0 -p baud_rate:=115200
```

Open new terminal and execute example command: 
```bash
ros2 topic pub --once /command std_msgs/msg/String "{data: 'hx711 read'}"
```