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
┌────────────────────────┐      ┌────────────────────────┐      ┌───────────────────────────┐
│ 1. Import TFLite Model │ ───> │ 2. Convert to C Code   │ ───> │ 3. Write Hardware Drivers │
│    in STM32CubeMX      │      │    via X-CUBE-AI       │      │    (Camera + Load Cell)   │
└────────────────────────┘      └────────────────────────┘      └───────────────────────────┘
                                                                            │
                                                                            ▼
┌────────────────────────┐                                      ┌────────────────────────┐
│ 5. Monitor Output      │ <─────────────────────────────────── │ 4. Flash Firmware via  │
│    over Serial (UART)  │                                      │    STM32CubeIDE        │
└────────────────────────┘                                      └────────────────────────┘
```
Example dataset:
```bash
dataset/
├── metadata.csv          # Central multimodal mapping file (links images + weights -> classes)
└── images/               # Raw input images folder
    ├── cable/            # (Optional) Subfolders by class for easy manual sorting
    │   ├── cable_01.jpg
    │   └── cable_02.jpg
    ├── smartphone/
    │   ├── smartphone_01.jpg
    │   └── smartphone_02.jpg
    ├── feature_phone/
    │   ├── featurephone_01.jpg
    │   └── featurephone_02.jpg
    └── battery/
        ├── battery_01.jpg
        └── battery_02.jpg
```
metadata.csv 
```bash
filename,weight_g,label
images/cable/cable_01.jpg,42.5,cable
images/cable/cable_02.jpg,38.0,cable
images/smartphone/smartphone_01.jpg,185.0,smartphone
images/smartphone/smartphone_02.jpg,172.3,smartphone
images/feature_phone/featurephone_01.jpg,95.0,feature_phone
images/feature_phone/featurephone_02.jpg,102.1,feature_phone
images/battery/battery_01.jpg,280.0,battery
images/battery/battery_02.jpg,310.5,battery
```

## Download Dataset
```bash
# 1. Make the script executable
chmod +x download_dataset.sh
# 2. Run the script
./download_dataset.sh
```

## Run the Multi-Modal Training Pipeline
```bash
python model_training/test_pipeline.py
```

## Predict on a Single Test File
```bash
python model_training/predict.py --image dataset/images/Smartphone/photo1.jpg --weight 180.0
```

## Launch Interactive Evaluation Mode
```bash
python model_training/continuous_eval.py
```