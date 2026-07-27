import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from sklearn.model_selection import train_test_split

CLASS_NAMES = ["cable", "smartphone", "feature_phone", "battery"]
LABEL_MAP = {name: idx for idx, name in enumerate(CLASS_NAMES)}

def load_dataset(csv_path, img_dir, target_size=(224, 224)):
    df = pd.read_csv(csv_path)
    
    images, weights, labels = [], [], []
    for _, row in df.iterrows():
        img_path = os.path.join(img_dir, row["filename"])
        if not os.path.exists(img_path):
            continue
            
        img = tf.keras.utils.load_img(img_path, target_size=target_size)
        img_array = tf.keras.utils.img_to_array(img) / 255.0
        
        images.append(img_array)
        weights.append(float(row["weight_g"]))
        labels.append(LABEL_MAP[row["label"]])
        
    return np.array(images, dtype=np.float32), np.array(weights, dtype=np.float32), np.array(labels, dtype=np.int32)

def build_aixscan_model(input_shape=(224, 224, 3), num_classes=4):
    # Branch 1: Image Transfer Learning (MobileNetV2)
    img_input = layers.Input(shape=input_shape, name="image_input")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=input_shape, include_top=False, weights="imagenet"
    )
    base_model.trainable = False
    
    x_img = base_model(img_input)
    x_img = layers.GlobalAveragePooling2D()(x_img)
    x_img = layers.Dense(64, activation="relu")(x_img)

    # Branch 2: Weight Metadata Input
    weight_input = layers.Input(shape=(1,), name="weight_input")
    x_weight = layers.Dense(16, activation="relu")(weight_input)

    # Multi-Modal Fusion
    combined = layers.concatenate([x_img, x_weight])
    x = layers.Dense(32, activation="relu")(combined)
    outputs = layers.Dense(num_classes, activation="softmax", name="classification")(x)

    return Model(inputs=[img_input, weight_input], outputs=outputs)

def representative_data_gen(X_img, X_w):
    """Generator for INT8 Quantization"""
    for i in range(len(X_img)):
        yield [
            np.expand_dims(X_img[i], axis=0),
            np.expand_dims(np.array([X_w[i]], dtype=np.float32), axis=0)
        ]

def run():
    csv_path = "dataset/metadata.csv"
    img_dir = "dataset/images"

    if os.path.exists(csv_path) and os.path.exists(img_dir) and len(os.listdir(img_dir)) > 0:
        print("📂 Loading dataset from disk...")
        X_img, X_w, y = load_dataset(csv_path, img_dir)
        X_img_tr, X_img_val, X_w_tr, X_w_val, y_tr, y_val = train_test_split(
            X_img, X_w, y, test_size=0.2, random_state=42
        )
    else:
        print("⚠️ No images found in dataset/images. Generating synthetic batch for build check...")
        X_img_tr = np.random.random((8, 224, 224, 3)).astype(np.float32)
        X_w_tr = np.random.uniform(10.0, 500.0, size=(8, 1)).astype(np.float32)
        y_tr = np.random.randint(0, 4, size=(8, 1))
        X_img_val, X_w_val, y_val = X_img_tr, X_w_tr, y_tr

    model = build_aixscan_model(num_classes=len(CLASS_NAMES))
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    print("⚡ Training multi-modal model...")
    model.fit([X_img_tr, X_w_tr], y_tr, validation_data=([X_img_val, X_w_val], y_val), epochs=3, batch_size=2)

    print("📦 Exporting quantized .tflite model...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_model = converter.convert()
    with open("aixscan_model.tflite", "wb") as f:
        f.write(tflite_model)

    print("✅ Model exported successfully: aixscan_model.tflite")

if __name__ == "__main__":
    run()