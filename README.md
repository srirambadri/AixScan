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
