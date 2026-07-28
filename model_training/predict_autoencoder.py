import argparse
import numpy as np
import tensorflow as tf
from PIL import Image

# Reconstruct Loss Threshold (Tune based on test_autoencoder.py output)
ANOMALY_THRESHOLD = 0.015  

def preprocess_sample(image_path, weight_g):
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_tensor = np.expand_dims(img_array, axis=0)

    # Normalize weight using same scale factor (500.0)
    weight_tensor = np.array([[float(weight_g) / 500.0]], dtype=np.float32)
    return img_array, img_tensor, weight_tensor

def predict_anomaly(tflite_model_path, image_path, weight_g):
    interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    orig_img_array, img_tensor, weight_tensor = preprocess_sample(image_path, weight_g)

    # Pass inputs
    for detail in input_details:
        if len(detail["shape"]) == 4:
            interpreter.set_tensor(detail["index"], img_tensor)
        else:
            interpreter.set_tensor(detail["index"], weight_tensor)

    interpreter.invoke()

    # Get reconstructed image tensor
    reconstructed_img = interpreter.get_tensor(output_details[0]['index'])[0]

    # Calculate Mean Squared Error (MSE) between original image and reconstruction
    reconstruction_loss = float(np.mean(np.square(orig_img_array - reconstructed_img)))

    is_anomaly = reconstruction_loss > ANOMALY_THRESHOLD
    status = "❌ ANOMALY / NOT A SMARTPHONE" if is_anomaly else "✅ VALID SMARTPHONE"

    print("\n==============================================")
    print("🔍 AixScan Anomaly Detection Results")
    print("==============================================")
    print(f"📷 Image               : {image_path}")
    print(f"⚖️ Weight              : {weight_g} g")
    print(f"📉 Reconstruction Loss : {reconstruction_loss:.5f}")
    print(f"🎯 Threshold           : {ANOMALY_THRESHOLD:.5f}")
    print("----------------------------------------------")
    print(f"📌 Result              : {status}")
    print("==============================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AixScan Autoencoder Anomaly Detector")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--weight", required=True, type=float, help="Measured weight in grams")
    parser.add_argument("--model", default="aixscan_autoencoder.tflite", help="Path to tflite model")

    args = parser.parse_args()
    predict_anomaly(args.model, args.image, args.weight)