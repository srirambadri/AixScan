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

```bash
cd ~/hardware_check
colcon build --packages-select stm32_bridge
source install/setup.bash
```

### Run
```bash
ros2 run stm32_bridge log_receiver```

Open new terminal and execute example command: 
```bash
ros2 topic pub --once /command std_msgs/msg/String "{data: 'hx711 read'}"```