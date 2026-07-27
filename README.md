# AixScan
AixScan: Edge AI E-Waste Classifier AixScan is an embedded machine learning system designed for STM32 microcontrollers to classify electronic waste using multi-modal sensor fusion (computer vision + weight data).

```bash
hardware_check/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── hx711.h                 # Load cell sensor header
│   │   └── camera_driver.h         # Camera module header
│   └── Src/
│       ├── main.c                  # Sensor capture & logging logic
│       ├── hx711.c                 # Load cell driver implementation
│       └── camera_driver.c         # Camera driver implementation
├── Drivers/                        # Generated STM32 HAL Drivers
├── .gitignore                      # Ignores build output (Debug/, Release/, *.elf, *.o)
├── hardware_check.ioc              # STM32CubeMX Project File
└── README.md                       # Pinout & test instructions
```