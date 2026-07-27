#!/bin/bash

# ==============================================================================
# AixScan Dataset Downloader Script
# ==============================================================================

# 🔗 Paste your public Google Drive URL or Folder ID below
GDRIVE_LINK="https://drive.google.com/drive/folders/1un83NbJZZFe9ySsH8FXvQF9xfpdiydc8?usp=sharing"

DATASET_DIR="dataset"

echo "=================================================="
echo "🚀 Starting Dataset Download into Codespace..."
echo "=================================================="

# 1. Install gdown if it's not present
if ! command -v gdown &> /dev/null; then
    echo "📦 Installing gdown utility..."
    pip install gdown
fi

# 2. Prepare target directory
mkdir -p "$DATASET_DIR"

# 3. Download from Google Drive
echo "📥 Downloading dataset from Google Drive..."

# Check if link contains a zip file or a folder
if [[ "$GDRIVE_LINK" == *".zip"* ]] || [[ "$GDRIVE_LINK" == *"uc?id="* ]]; then
    gdown "$GDRIVE_LINK" -O dataset.zip
    
    echo "📦 Unzipping dataset..."
    unzip -q dataset.zip -d "$DATASET_DIR/"
    rm dataset.zip
else
    # Folder download mode
    gdown --folder "$GDRIVE_LINK" -O "$DATASET_DIR/"
fi

echo "=================================================="
echo "✅ Dataset Download Complete!"
echo "📁 Contents of dataset folder:"
ls -la "$DATASET_DIR/"
echo "=================================================="