import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image

# --- Import the model from the model.py file ---
from model import build_unet_model, customloss


# --- DATA LOADING FUNCTION (from previous conversation) ---
def load_image_paths(doodle_dir, texture_dir):
    try:
        texture_filenames = {f for f in os.listdir(texture_dir) if f.endswith('.png')}
    except FileNotFoundError:
        print(f"Error: Texture directory not found at '{texture_dir}'")
        return [], []
    try:
        doodle_filenames = sorted([f for f in os.listdir(doodle_dir) if f.endswith('.png')])
    except FileNotFoundError:
        print(f"Error: Doodle directory not found at '{doodle_dir}'")
        return [], []
    paired_doodle_paths = []
    paired_texture_paths = []
    for doodle_filename in doodle_filenames:
        texture_found = False
        for texture_filename in texture_filenames:
            if doodle_filename.startswith(os.path.splitext(texture_filename)[0]):
                doodle_path = os.path.join(doodle_dir, doodle_filename)
                texture_path = os.path.join(texture_dir, texture_filename)
                paired_doodle_paths.append(doodle_path)
                paired_texture_paths.append(texture_path)
                texture_found = True
                break
        if not texture_found:
            print(f"Warning: No matching texture found for doodle '{doodle_filename}'")
    return paired_doodle_paths, paired_texture_paths

# --- DATA PREPROCESSING FUNCTION (from previous conversation) ---
def preprocess_image(file_path, target_size, num_channels):
    try:
        image = Image.open(file_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image = image.resize((target_size, target_size), Image.NEAREST)
        image_array = np.asarray(image, dtype=np.float32) / 255.0
        return image_array
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return None

# --- MAIN TRAINING SCRIPT ---
def train_model():
    doodles_dir = '../data/doodles/'
    textures_dir = '../data/textures/'
    model_save_path = 'doodle_pixelart_unet_model.keras'
    doodle_size = 256
    texture_size = 16
    num_channels = 4

    print("Loading image paths...")
    doodle_paths, texture_paths = load_image_paths(doodles_dir, textures_dir)

    if not doodle_paths:
        print("No image pairs found. Aborting training.")
        return

    print(f"Preprocessing {len(doodle_paths)} image pairs...")
    doodles = [preprocess_image(p, doodle_size, num_channels) for p in doodle_paths]
    textures = [preprocess_image(p, texture_size, num_channels) for p in texture_paths]
    doodles_array = np.array([img for img in doodles if img is not None])
    textures_array = np.array([img for img in textures if img is not None])

    print(f"Dataset prepared. Doodles shape: {doodles_array.shape}, Textures shape: {textures_array.shape}")
    print(doodles_array[1])
    print("Building and compiling the U-Net model...")
    # --- Now using the new, larger U-Net model ---
    model = build_unet_model(
        input_shape=(doodle_size, doodle_size, num_channels),
        output_channels=num_channels
    )

    # --- Use the new combined loss function here! ---
    model.compile(optimizer='adam', loss=customloss)

    print("\nStarting training...")
    history = model.fit(
        doodles_array,
        textures_array,
        epochs=50,
        batch_size=16,
        validation_split=0.3
    )
    print("\nTraining complete.")

    print(f"Saving the model to '{model_save_path}'...")
    model.save(model_save_path)
    print("Model saved successfully!")

if __name__ == "__main__":
    train_model()