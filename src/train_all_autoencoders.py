import os

# 1. Force single-threaded CPU execution & disable oneDNN locks
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU only

import json
import numpy as np
import pandas as pd
import tensorflow as tf

# 2. Lock TensorFlow execution threadpools
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

from dataset_loader import load_class_dataset
from autoencoder_builder import build_single_class_autoencoder

MODELS_DIR = "models"
THRESHOLDS_FILE = os.path.join(MODELS_DIR, "thresholds.json")
CSV_PATH = "dataset/metadata.csv"
EPOCHS = 15
BATCH_SIZE = 8

def export_tflite(model, output_path):
    """Safely converts model to TFLite without deadlocking."""
    with tf.device("/CPU:0"):
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
    with open(output_path, "wb") as f:
        f.write(tflite_model)

def train_all():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    unique_labels = df["label"].str.strip().str.lower().unique()

    thresholds = {}

    with tf.device("/CPU:0"):
        for label in unique_labels:
            print(f"\n==================================================")
            print(f"🚀 Training & Evaluating Autoencoder: [{label.upper()}]")
            print(f"==================================================")
            
            # Clear previous Keras graph memory to avoid mutex lock accumulation
            tf.keras.backend.clear_session()

            X_img, X_w = load_class_dataset(label, csv_path=CSV_PATH)
            if len(X_img) == 0:
                print(f"⚠️ Skipping '{label}' (0 images found).")
                continue

            model = build_single_class_autoencoder()
            
            # Keras 3 compatible model.fit call
            model.fit(
                {"image_input": X_img, "weight_input": X_w},
                X_img,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                verbose=1
            )

            # Calculate 95th Percentile Threshold
            reconstructions = model.predict({"image_input": X_img, "weight_input": X_w}, verbose=0)
            sample_losses = np.mean(np.square(X_img - reconstructions), axis=(1, 2, 3))
            
            calibrated_threshold = float(np.percentile(sample_losses, 95)) * 1.15
            thresholds[label] = round(calibrated_threshold, 5)

            print(f"📊 [{label.upper()}] Calculated Threshold: {calibrated_threshold:.5f}")

            # Export TFLite
            tflite_filename = os.path.join(MODELS_DIR, f"autoencoder_{label}.tflite")
            export_tflite(model, tflite_filename)
            print(f"📦 Saved: {tflite_filename}")

    # Save threshold map
    with open(THRESHOLDS_FILE, "w") as f:
        json.dump(thresholds, f, indent=4)
    print(f"\n💾 Saved threshold settings to {THRESHOLDS_FILE}")

if __name__ == "__main__":
    train_all()