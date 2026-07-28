#!/bin/bash

# ==============================================================================
# AixScan Dataset Downloader Script (with Metadata Auto-Fix)
# ==============================================================================

# 🔗 Paste your public Google Drive URL or Folder ID below
GDRIVE_LINK="https://drive.google.com/drive/folders/1DmMkkuFTwgRAJdZLrskPckv-usBMiaeg?usp=sharing"

DATASET_DIR="dataset"

echo "=================================================="
echo "🚀 Starting Dataset Download into Codespace..."
echo "=================================================="

# 1. Install gdown if missing
if ! command -v gdown &> /dev/null; then
    echo "📦 Installing gdown utility..."
    pip install gdown
fi

# 2. Prepare target directory
mkdir -p "$DATASET_DIR"

# 3. Download from Google Drive
echo "📥 Downloading dataset from Google Drive..."

if [[ "$GDRIVE_LINK" == *".zip"* ]] || [[ "$GDRIVE_LINK" == *"uc?id="* ]]; then
    gdown "$GDRIVE_LINK" -O dataset.zip
    
    echo "📦 Unzipping dataset..."
    unzip -q -o dataset.zip -d "$DATASET_DIR/"
    rm dataset.zip
else
    # Folder download mode
    gdown --folder "$GDRIVE_LINK" -O "$DATASET_DIR/"
fi

# ------------------------------------------------------------------------------
# 🛠️ Fix: Flatten & Relocate metadata.csv if nested
# ------------------------------------------------------------------------------
echo "🔍 Searching for metadata.csv..."

# Find any metadata.csv inside dataset/
FOUND_CSV=$(find "$DATASET_DIR" -maxdepth 3 -type f -iname "metadata.csv" | head -n 1)

if [ -n "$FOUND_CSV" ]; then
    if [ "$FOUND_CSV" != "$DATASET_DIR/metadata.csv" ]; then
        echo "🚚 Moving $FOUND_CSV to $DATASET_DIR/metadata.csv..."
        mv "$FOUND_CSV" "$DATASET_DIR/metadata.csv"
    else
        echo "✅ metadata.csv is already in root $DATASET_DIR/"
    fi
else
    echo "⚠️ WARNING: Could not find any metadata.csv in downloaded files!"
fi

echo "=================================================="
echo "✅ Dataset Setup Complete!"
echo "📁 Root dataset contents:"
ls -la "$DATASET_DIR/"
echo "=================================================="