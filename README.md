# AixScan
AixScan: Edge AI E-Waste Classifier AixScan is an embedded machine learning system designed for STM32 microcontrollers to classify electronic waste using multi-modal sensor fusion (computer vision + weight data).

```bash
AixScan/
├── .github/
│   └── workflows/
│       └── ci.yml                      # GitHub Actions CI workflow
├── dataset/
│   ├── images/                         # Place your dataset images here
│   └── metadata.csv                    # CSV mapping images to weight (g) and labels
├── model_training/
│   ├── test_pipeline.py                # Multi-modal training + TFLite export
│   ├── predict.py                      # Single-item inference CLI script
│   └── continuous_eval.py              # Continuous loop testing script
├── firmware/                           # (For STM32 C/C++ project code)
├── .gitignore                          # Ignores large models & temp files
└── README.md                           # Project description
```

Example AixScan workflow:
```bash
  ┌───────────────────────┐          ┌───────────────────────┐
  │  Camera Module        │          │  HX711 Load Cell      │
  │  Captures Photo       │          │  Measures Weight (g)  │
  └───────────┬───────────┘          └───────────┬───────────┘
              │                                  │
              │ 224x224 RGB                      │ Float (e.g., 185.0g)
              ▼                                  ▼
 ┌────────────────────────────────────────────────────────────┐
 │              aixscan_classifier.c (NUCLEO MCU)             │
 │                                                            │
 │  • Passes image into Model Input 0                         │
 │  • Passes weight into Model Input 1                        │
 │  • Runs X-CUBE-AI inference engine                         │
 └────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ Output Result:                      │
           │ "Smartphone (98.4% Confidence)"     │
           └─────────────────────────────────────┘
```

(NUCLEO) STM Board firmware install/update process:
```bash
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ 1. Import TFLite Model │ ───> │ 2. Convert to C Code   │ ───> │ 3. Write Hardware Drivers│
│    in STM32CubeMX      │      │    via X-CUBE-AI       │      │    (Camera + Load Cell) │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
                                                                            │
                                                                            ▼
┌────────────────────────┐                                      ┌────────────────────────┐
│ 5. Monitor Output      │ <─────────────────────────────────── │ 4. Flash Firmware via  │
│    over Serial (UART)  │                                      │    STM32CubeIDE        │
└────────────────────────┘                                      └────────────────────────┘
```
