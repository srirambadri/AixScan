import tensorflow as tf
from tensorflow.keras import layers, models

def build_single_class_autoencoder(input_shape=(224, 224, 3)):
    # --- Image Encoder ---
    img_input = layers.Input(shape=input_shape, name="image_input")
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(img_input)
    x = layers.MaxPooling2D((2, 2), padding="same")(x)
    x = layers.Conv2D(16, (3, 3), activation="relu", padding="same")(x)
    encoded_img = layers.MaxPooling2D((2, 2), padding="same")(x) # (56, 56, 16)

    # --- Weight Encoder ---
    weight_input = layers.Input(shape=(1,), name="weight_input")
    w = layers.Dense(16, activation="relu")(weight_input)

    # --- Bottleneck Fusion ---
    flattened_img = layers.Flatten()(encoded_img)
    bottleneck = layers.concatenate([flattened_img, w])
    bottleneck = layers.Dense(128, activation="relu")(bottleneck)

    # --- Image Decoder ---
    d = layers.Dense(56 * 56 * 16, activation="relu")(bottleneck)
    d = layers.Reshape((56, 56, 16))(d)
    d = layers.Conv2DTranspose(16, (3, 3), strides=2, activation="relu", padding="same")(d)
    d = layers.Conv2DTranspose(32, (3, 3), strides=2, activation="relu", padding="same")(d)
    decoded_img = layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same", name="decoded_img")(d)

    autoencoder = models.Model(inputs=[img_input, weight_input], outputs=decoded_img)
    autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    return autoencoder