# AixScan
AixScan: Edge AI E-Waste Classifier AixScan is an embedded machine learning system designed for STM32 microcontrollers to classify electronic waste using multi-modal sensor fusion (computer vision + weight data).

| Feature | AixScan (AI Hub) | hardware_check (Hardware Engine) |
| --- | --- | --- |
| Primary Goal | Multi-Modal Model Training & TFLite Quantization | Microcontroller & Sensor Validation |
| Primary Output | aixscan_model.tflite model binary | Diagnostic files (weight_log.txt, IMG_0001.RAW) |
| Tooling & Tech | Python, Keras, TensorFlow Lite, GitHub Actions, Codespaces | STM32CubeMX, STM32CubeIDE, C/C++ HAL, FatFS |
