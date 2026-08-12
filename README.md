# AixScan
AixScan: Edge AI E-Waste Classifier AixScan is an embedded machine learning system designed for STM32 microcontrollers to classify electronic waste using multi-modal sensor fusion (computer vision + weight data).

```bash
AixScan/
├── dataset/
│   ├── metadata.csv
│   └── images/
├── models/                     # Saved trained .keras & exported .tflite models
│   ├── autoencoder_smartphone.tflite
│   ├── autoencoder_cable.tflite
│   ├── autoencoder_battery.tflite
│   └── autoencoder_feature_phone.tflite
├── src/
│   ├── dataset_loader.py       # Modular dataset loading logic
│   ├── autoencoder_builder.py  # Model architecture definition
│   ├── train_all_autoencoders.py
│   └── predict_ensemble.py     # Multi-autoencoder inference
├── requirements.txt
└── download_dataset.sh
```

Example AixScan workflow:
```bash
  ┌───────────────────────┐          ┌───────────────────────┐
  │  Camera Module        │          │  HX711 Load Cell      │
  │  Captures Photo       │          │  Measures Weight (g)  │
  └───────────┬───────────┘          └───────────┬───────────┘
              │                                  │
              │ RGB                              │ Float (e.g., 185.0g)
              ▼                                  ▼
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
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

## Autoencoder / Anomaly Detection (One-Class Model)
### Train Model
```bash
python src/train_all_autoencoders.py
```
### Test Model
```bash
python src/predict_ensemble.py --image test_cable.jpg --weight 10.0
```
