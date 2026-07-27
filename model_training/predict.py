import argparse
import numpy as np
import tensorflow as tf
from PIL import Image

CLASS_NAMES = ["cable", "smartphone", "feature_phone", "battery"]

# Set minimum confidence threshold (80%). Anything lower is flagged as Unknown.
CONFIDENCE_THRESHOLD = 80.0  

def preprocess_input(image_path, weight_g, target_size=(224, 224)):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_tensor = np.expand_dims(img_array, axis=0)

    weight_tensor = np.array([[float(weight_g)]], dtype=np.float32)
    return img_tensor, weight_tensor

def predict_single_item(tflite_model_path, image_path, weight_g):
    interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    img_tensor, weight_tensor = preprocess_input(image_path, weight_g)

    # Route tensors to input shapes
    for detail in input_details:
        if len(detail["shape"]) == 4:  # Image Tensor (1, 224, 224, 3)
            interpreter.set_tensor(detail["index"], img_tensor)
        else:                          # Weight Tensor (1, 1)
            interpreter.set_tensor(detail["index"], weight_tensor)

    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0][0])
    
    predicted_class_id = np.argmax(predictions)
    confidence = predictions[predicted_class_id] * 100.0
    
    # ----------------------------------------------------
    # Option B: Out-of-Distribution (OOD) Safety Check
    # ----------------------------------------------------
    if confidence < CONFIDENCE_THRESHOLD:
        predicted_label = "UNKNOWN / OUT-OF-DISTRIBUTION"
        status_flag = "⚠️ Low Confidence - Item not recognized!"
    else:
        predicted_label = CLASS_NAMES[predicted_class_id].upper()
        status_flag = "✅ High Confidence Classification"

    print("\n==============================================")
    print("🔍 AixScan Prediction Results")
    print("==============================================")
    print(f"📷 Image  : {image_path}")
    print(f"⚖️ Weight : {weight_g} g")
    print("----------------------------------------------")
    print(f"🎯 Prediction : {predicted_label}")
    print(f"📊 Confidence : {confidence:.2f}%")
    print(f"📌 Status     : {status_flag}")
    print("==============================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AixScan TFLite Model on a Single E-Waste Sample")
    parser.add_argument("--image", required=True, help="Path to test image file")
    parser.add_argument("--weight", required=True, type=float, help="Measured weight in grams")
    parser.add_argument("--model", default="aixscan_model.tflite", help="Path to .tflite model")

    args = parser.parse_args()
    predict_single_item(args.model, args.image, args.weight)