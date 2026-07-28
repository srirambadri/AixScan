import numpy as np
import tensorflow as tf
from train_autoencoder import load_smartphone_data, MODEL_PATH

def evaluate_reconstruction_threshold():
    model = tf.keras.models.load_model(MODEL_PATH)
    X_img, X_w = load_smartphone_data()

    reconstructions = model.predict({"image_input": X_img, "weight_input": X_w})
    errors = np.mean(np.square(X_img - reconstructions), axis=(1, 2, 3))

    mean_error = np.mean(errors)
    max_error = np.max(errors)
    threshold_95 = np.percentile(errors, 95)

    print("\n==============================================")
    print("📊 Autoencoder Baseline Evaluation")
    print("==============================================")
    print(f"🔹 Mean Reconstruction Loss (MSE) : {mean_error:.5f}")
    print(f"🔹 Max Reconstruction Loss (MSE)  : {max_error:.5f}")
    print(f"🎯 Recommended Threshold (95th %) : {threshold_95:.5f}")
    print("==============================================\n")

if __name__ == "__main__":
    evaluate_reconstruction_threshold()