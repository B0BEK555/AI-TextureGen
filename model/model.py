import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def encoder_block(inputs, filters):
    """A downsampling block for the U-Net encoder path."""
    x = layers.Conv2D(filters, kernel_size=4, strides=2, padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    return x


def build_unet_model(input_shape=(256, 256, 4), output_channels=4):
    """
    Constructs a larger U-Net-like model with an encoder-decoder structure.
    This corrected version ensures the output size is 16x16.
    """
    inputs = keras.Input(shape=input_shape)

    # --- Encoder Path (Downsampling) ---
    enc1 = encoder_block(inputs, 64)  # Output shape: 128x128x64
    enc2 = encoder_block(enc1, 128)  # Output shape: 64x64x128
    enc3 = encoder_block(enc2, 256)  # Output shape: 32x32x256
    enc4 = encoder_block(enc3, 512)  # Output shape: 16x16x512

    # --- Bottleneck ---
    bottleneck = encoder_block(enc4, 512)  # Output shape: 8x8x512

    # --- Decoder Path (Upsampling) ---
    # The upsampling logic needs to be changed to end at 16x16.
    # Start with the bottleneck and upsample to 16x16.
    dec1 = layers.Conv2DTranspose(512, kernel_size=4, strides=2, padding='same', use_bias=False)(bottleneck)
    dec1 = layers.BatchNormalization()(dec1)
    dec1 = layers.LeakyReLU(alpha=0.2)(dec1)
    dec1 = layers.Concatenate()([dec1, enc4])  # Concatenate with enc4 (16x16)

    # Add a final refinement layer to get the final output
    x = layers.Conv2D(512, kernel_size=3, padding='same', use_bias=False)(dec1)
    x = layers.LeakyReLU(alpha=0.2)(x)

    # --- Output Layer ---
    # Final layer with 1x1 kernel to convert feature maps to RGBA channels
    output_image = layers.Conv2D(output_channels, kernel_size=1, padding='same', activation='sigmoid')(x)

    return keras.Model(inputs=inputs, outputs=output_image, name="doodle_to_pixelart_unet")


# ... other imports

# --- Corrected Custom Combined Loss Function ---
def combined_loss(y_true, y_pred):
    """
    A custom loss function that combines Binary Cross-Entropy for the alpha channel
    and Mean Absolute Error for the RGB channels, with explicit averaging.
    """
    # Split the true and predicted tensors into RGB and Alpha channels
    y_true_rgb = y_true[..., :3]
    y_true_alpha = y_true[..., 3:]

    y_pred_rgb = y_pred[..., :3]
    y_pred_alpha = y_pred[..., 3:]

    # Calculate Binary Cross-Entropy loss for the alpha channel
    alpha_loss = keras.losses.binary_crossentropy(y_true_alpha, y_pred_alpha)

    # Calculate Mean Absolute Error loss for the RGB channels
    rgb_loss = keras.losses.MeanAbsoluteError(y_true_rgb, y_pred_rgb)

    # --- FIX ---
    # Explicitly calculate the mean of each loss to get a single scalar value.
    # The error happens when the loss is not a single number.
    alpha_loss_scalar = tf.reduce_mean(alpha_loss)
    rgb_loss_scalar = tf.reduce_mean(rgb_loss)

    # Combine the scalar losses
    total_loss = (1.0 * alpha_loss_scalar) + (5.0 * rgb_loss_scalar)

    return total_loss

def customloss(y_true, y_pred):
    # Split the true and predicted tensors into RGB and Alpha channels
    y_true_rgb = y_true[..., :3]
    y_true_alpha = y_true[..., 3:]

    y_pred_rgb = y_pred[..., :3]
    y_pred_alpha = y_pred[..., 3:]

    # Use Binary Cross-Entropy on the Alpha channel for sharp edges
    alpha_loss = tf.keras.losses.BinaryCrossentropy()(y_true_alpha, y_pred_alpha)

    # Use Mean Absolute Error on the RGB channels for color accuracy
    rgb_loss = tf.keras.losses.MeanAbsoluteError()(y_true_rgb, y_pred_rgb)

    # You can weight these to emphasize one over the other
    total_loss = (1.0 * alpha_loss) + (5.0 * rgb_loss)

    return total_loss