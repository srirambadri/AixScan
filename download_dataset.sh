#!/bin/bash

# ==============================================================================
# AixScan Direct Zip Downloader (Auto-Converts Drive Web Links to Raw Streams)
# ==============================================================================

DATASET_DIR="dataset"
ZIP_PATH="$DATASET_DIR/images.zip"

echo "=================================================="
echo "🚀 AixScan Dataset Downloader"
echo "=================================================="

# 1. Ask for your Google Drive link
read -rp "🔗 Paste your Google Drive link: " USER_URL

if [ -z "$USER_URL" ]; then
    echo "❌ Error: No link provided!"
    exit 1
fi

# 2. Extract the raw File ID from whatever link you pasted
FILE_ID=$(echo "$USER_URL" | sed -nE 's/.*(\/d\/|id=)([a-zA-Z0-9_-]+).*/\2/p')

if [ -z "$FILE_ID" ]; then
    # Fallback if you pasted the raw ID directly
    FILE_ID="$USER_URL"
fi

echo "🔑 File ID extracted: $FILE_ID"

# 3. Create dataset folder
mkdir -p "$DATASET_DIR"
rm -f "$ZIP_PATH"

# 4. Download directly from Google's raw usercontent endpoint
DIRECT_STREAM_URL="https://drive.usercontent.google.com/download?id=${FILE_ID}&export=download&confirm=t"

echo "📥 Downloading raw images.zip stream..."
curl -L -C - "$DIRECT_STREAM_URL" -o "$ZIP_PATH"

# 5. Extract the archive
if [ -f "$ZIP_PATH" ] && [ -s "$ZIP_PATH" ]; then
    echo "📦 Extracting files into $DATASET_DIR/..."
    unzip -q -o "$ZIP_PATH" -d "$DATASET_DIR/"
    rm "$ZIP_PATH"
else
    echo "❌ Download failed or returned an empty file! Ensure permissions are set to 'Anyone with the link'."
    exit 1
fi

# 6. Fix nested metadata.csv location if necessary
FOUND_CSV=$(find "$DATASET_DIR" -maxdepth 3 -type f -iname "metadata.csv" | head -n 1)
if [ -n "$FOUND_CSV" ] && [ "$FOUND_CSV" != "$DATASET_DIR/metadata.csv" ]; then
    echo "🚚 Relocating $FOUND_CSV -> $DATASET_DIR/metadata.csv..."
    mv "$FOUND_CSV" "$DATASET_DIR/metadata.csv"
fi

echo "=================================================="
echo "✅ Setup Complete!"
echo "📁 Contents of $DATASET_DIR:"
ls -la "$DATASET_DIR/"
echo "=================================================="