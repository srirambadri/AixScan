import os
import glob
import pandas as pd
import numpy as np
import tensorflow as tf

def load_class_dataset(label_name, csv_path="dataset/metadata.csv", target_size=(224, 224)):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cannot find CSV at {csv_path}")

    df = pd.read_csv(csv_path)
    # Filter strictly for the requested class
    df_class = df[df["label"].str.strip().str.lower() == label_name.lower()]

    images, weights = [], []
    for _, row in df_class.iterrows():
        raw_filename = str(row["filename"]).strip()
        base_path = raw_filename if raw_filename.startswith("dataset/") else os.path.join("dataset", raw_filename)
        
        actual_path = None
        if os.path.exists(base_path) and os.path.isfile(base_path):
            actual_path = base_path
        else:
            for ext in [".jpg", ".png", ".jpeg", ".webp"]:
                if os.path.exists(base_path + ext):
                    actual_path = base_path + ext
                    break

        if not actual_path:
            clean_name = os.path.basename(raw_filename)
            matches = glob.glob(f"dataset/**/{clean_name}*", recursive=True)
            if matches:
                actual_path = matches[0]

        if actual_path:
            try:
                img = tf.keras.utils.load_img(actual_path, target_size=target_size)
                images.append(tf.keras.utils.img_to_array(img) / 255.0)
                weights.append(float(row["weight_g"]) / 500.0)
            except Exception as e:
                print(f"⚠️ Failed loading {actual_path}: {e}")

    print(f"📂 Loaded {len(images)} training samples for class: '{label_name}'")
    return np.array(images, dtype=np.float32), np.array(weights, dtype=np.float32)