import os
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd

# Parameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 20
MODEL_PATH = "autoencoder_model.keras"
TFLITE_PATH = "aixscan_autoencoder.tflite"

def load_smartphone_data(csv_path="dataset/metadata.csv", img_dir="dataset"):
    df = pd.read_csv(csv_path)
    images, weights = [], []
    
    for _, row in df.iterrows():
        rel_path = str(row["filename"]).strip()
        img_path = os.path.join(img_dir, rel_path) if not rel_path.startswith(img_dir) else rel_path
        
        if os.path.exists(img_path):
            img = tf.keras.utils.load_img(img_path, target_size=IMG_SIZE)
            img_array = tf.keras.utils.img_to_array(img) / 255.0
            
            images.append(img_array)
            weights.append(float(row["weight_g"]) / 500.0) # Normalize weight (0 to 1)

    print(f"✅ Loaded {len(images)} normal smartphone samples for training.")
    return np.array(images, dtype=np.float32), np.array(weights, dtype=np.float32)

def build_autoencoder():
    # --- Image Input Branch ---
    img_input = layers.Input(shape=(224, 224, 3), name="image_input")
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(img_input)
    x = layers.MaxPooling2D((2, 2), padding="same")(x)
    x = layers.Conv2D(16, (3, 3), activation="relu", padding="same")(x)
    encoded_img = layers.MaxPooling2D((2, 2), padding="same")(x) # Shape: (56, 56, 16)

    # --- Weight Input Branch ---
    weight_input = layers.Input(shape=(1,), name="weight_input")
    w = layers.Dense(16, activation="relu")(weight_input)

    # --- Bottleneck (Fusion) ---
    flattened_img = layers.Flatten()(encoded_img)
    bottleneck = layers.concatenate([flattened_img, w])
    bottleneck = layers.Dense(128, activation="relu")(bottleneck)

    # --- Decoder Branch ---
    d = layers.Dense(56 * 56 * 16, activation="relu")(bottleneck)
    d = layers.Reshape((56, 56, 16))(d)
    d = layers.Conv2DTranspose(16, (3, 3), strides=2, activation="relu", padding="same")(d)
    d = layers.Conv2DTranspose(32, (3, 3), strides=2, activation="relu", padding="same")(d)
    decoded_img = layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same", name="decoded_img")(d)

    # Autoencoder maps [image, weight] -> reconstructed [image]
    autoencoder = models.Model(inputs=[img_input, weight_input], outputs=decoded_img)
    autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    return autoencoder

def convert_to_tflite(model):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(TFLITE_PATH, "wb") as f:
        f.write(tflite_model)
    print(f"📦 Exported TFLite model: {TFLITE_PATH}")

if __name__ == "__main__":
    X_img, X_w = load_smartphone_data()
    
    model = build_autoencoder()
    model.summary()

    print("\n🚀 Training Autoencoder Anomaly Detector...")
    model.fit(
        {"image_input": X_img, "weight_input": X_w},
        X_img, # Targets are the input images themselves!
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1
    )

    model.save(MODEL_PATH)
    convert_to_tflite(model)