from tensorflow import keras
from PIL import Image
import numpy as np
import os

# --- Import the model from the model.py file ---
from model import build_unet_model
from model import customloss


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


# --- MAIN PREDICTION SCRIPT ---
def predict_pixel_art(input_doodle_path, output_save_dir, model_path='doodle_pixelart_unet_model.keras'):
    doodle_size = 256
    texture_size = 16
    num_channels = 4

    print(f"Loading model from '{model_path}'...")
    try:
        # Load the model with custom_objects to ensure Keras knows the
        # functions used in the model definition.
        # We need to tell Keras about the custom layer names.
        custom_objects = {
            'customloss': customloss,
        }

        # When saving a Keras model as a .keras file, you don't typically need custom_objects
        # unless you used custom classes, but it's good practice for clarity.
        # Let's try loading without it first as it should work with functional API.
        model = keras.models.load_model(model_path, custom_objects=custom_objects)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure the model path is correct and the model was saved successfully.")
        return

    print(f"Preprocessing input doodle: '{input_doodle_path}'...")
    doodle_image = preprocess_image(input_doodle_path, doodle_size, num_channels)
    if doodle_image is None:
        return
    doodle_image_batch = np.expand_dims(doodle_image, axis=0)

    print("Generating pixel art...")
    predicted_texture_batch = model.predict(doodle_image_batch)
    predicted_texture_array = (predicted_texture_batch[0] * 255.0).astype(np.uint8)

    os.makedirs(output_save_dir, exist_ok=True)
    base_filename = os.path.basename(input_doodle_path)
    output_filename = os.path.splitext(base_filename)[0] + "_pixelart.png"
    output_filepath = os.path.join(output_save_dir, output_filename)

    try:
        output_image = Image.fromarray(predicted_texture_array, 'RGBA')
        output_image.save(output_filepath)
        print(f"Generated pixel art saved to: '{output_filepath}'")
    except Exception as e:
        print(f"Error saving generated image: {e}")


if __name__ == "__main__":
    model_file = 'doodle_pixelart_unet_model.keras'
    input_doodle_to_test = '../data/doodles/tropical_fish.png'
    output_results_dir = 'generated/'

    predict_pixel_art(input_doodle_to_test, output_results_dir, model_file)