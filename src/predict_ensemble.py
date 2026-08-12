import os
import glob
import json
import argparse
import numpy as np
import tensorflow as tf
from PIL import Image

MODELS_DIR = "models"
THRESHOLDS_FILE = os.path.join(MODELS_DIR, "thresholds.json")

def load_thresholds():
    if os.path.exists(THRESHOLDS_FILE):
        with open(THRESHOLDS_FILE, "r") as f:
            return json.load(f)
    # Default fallback if file is missing
    return {}

def preprocess_input(image_path, weight_g):
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_tensor = np.expand_dims(img_array, axis=0)
    weight_tensor = np.array([[float(weight_g) / 500.0]], dtype=np.float32)
    return img_array, img_tensor, weight_tensor

def predict_best_match(image_path, weight_g):
    tflite_files = glob.glob(os.path.join(MODELS_DIR, "autoencoder_*.tflite"))
    if not tflite_files:
        raise FileNotFoundError(f"No .tflite models found in {MODELS_DIR}/")

    thresholds = load_thresholds()
    orig_img_array, img_tensor, weight_tensor = preprocess_input(image_path, weight_g)
    results = {}

    print("\n🔍 Running input across all Autoencoder models...")
    print("--------------------------------------------------")

    for model_path in tflite_files:
        label_name = os.path.basename(model_path).replace("autoencoder_", "").replace(".tflite", "")
        
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        for detail in input_details:
            if len(detail["shape"]) == 4:
                interpreter.set_tensor(detail["index"], img_tensor)
            else:
                interpreter.set_tensor(detail["index"], weight_tensor)

        interpreter.invoke()
        
        reconstructed_img = interpreter.get_tensor(output_details[0]['index'])[0]
        mse_loss = float(np.mean(np.square(orig_img_array - reconstructed_img)))
        
        # Get dynamic threshold or default to 0.025
        class_limit = thresholds.get(label_name, 0.025)
        
        # Calculate ratio of loss to threshold (Values < 1.0 mean it passed!)
        pass_status = "✅ PASS" if mse_loss <= class_limit else "❌ FAIL"
        results[label_name] = {
            "mse": mse_loss,
            "threshold": class_limit,
            "passed": mse_loss <= class_limit
        }

        print(f"📊 [{label_name.upper():<15}] Loss: {mse_loss:.5f} | Limit: {class_limit:.5f} -> {pass_status}")

    # Find model with best convergence
    best_label = min(results, key=lambda k: results[k]["mse"])
    best_match = results[best_label]

    print("--------------------------------------------------")
    if best_match["passed"]:
        print(f"🎯 RESULT: Identified as [{best_label.upper()}] (Loss: {best_match['mse']:.5f} <= Limit: {best_match['threshold']:.5f})")
    else:
        print(f"❌ RESULT: UNKNOWN / ANOMALY (Nearest class was [{best_label.upper()}], but Loss {best_match['mse']:.5f} exceeded Limit {best_match['threshold']:.5f})")
    print("==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--weight", required=True, type=float)
    args = parser.parse_args()

    predict_best_match(args.image, args.weight)