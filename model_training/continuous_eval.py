import os
import sys

# Import the prediction logic from predict.py
try:
    from predict import predict_single_item
except ImportError:
    from model_training.predict import predict_single_item

def run_continuous_eval():
    model_path = "aixscan_model.tflite"
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file '{model_path}' not found!")
        print("Please run 'python model_training/test_pipeline.py' first to generate the .tflite model.")
        sys.exit(1)

    print("==================================================")
    print("🟢 AixScan Continuous Testing Session Active")
    print("   Type 'exit' or 'q' at any prompt to terminate.")
    print("==================================================\n")

    while True:
        # 1. Prompt for image path
        img_path = input("Enter path to test image: ").strip()
        if img_path.lower() in ["exit", "q"]:
            print("Exiting test session. Goodbye!")
            break
            
        if not os.path.exists(img_path):
            print(f"⚠️ File '{img_path}' does not exist. Try again.\n")
            continue

        # 2. Prompt for weight in grams
        weight_input = input("Enter measured weight in grams: ").strip()
        if weight_input.lower() in ["exit", "q"]:
            print("Exiting test session. Goodbye!")
            break

        try:
            weight_g = float(weight_input)
        except ValueError:
            print("⚠️ Invalid numerical weight. Please enter a valid float or int.\n")
            continue

        # 3. Execute inference
        try:
            predict_single_item(model_path, img_path, weight_g)
        except Exception as e:
            print(f"❌ Error during prediction: {e}\n")

if __name__ == "__main__":
    run_continuous_eval()