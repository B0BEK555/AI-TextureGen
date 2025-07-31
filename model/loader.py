import os

def load_image_paths(doodle_dir, texture_dir):
    """
    Loads and pairs image paths based on a texture-to-doodle naming convention.
    A doodle file is paired with a texture file if its name contains the texture's filename.

    Args:
        doodle_dir (str): The path to the directory containing doodle images.
        texture_dir (str): The path to the directory containing texture images.

    Returns:
        tuple: A tuple containing two lists of file paths (doodles, textures)
               that are correctly paired.
    """
    # Get all texture filenames and store in a set for efficient lookup
    try:
        texture_filenames = {f for f in os.listdir(texture_dir) if f.endswith('.png')}
    except FileNotFoundError:
        print(f"Error: Texture directory not found at '{texture_dir}'")
        return [], []

    # Get all doodle filenames
    try:
        doodle_filenames = sorted([f for f in os.listdir(doodle_dir) if f.endswith('.png')])
    except FileNotFoundError:
        print(f"Error: Doodle directory not found at '{doodle_dir}'")
        return [], []

    paired_doodle_paths = []
    paired_texture_paths = []

    # Iterate through the doodles and find their matching texture
    for doodle_filename in doodle_filenames:
        texture_found = False
        # Iterate through all texture filenames to find a match
        for texture_filename in texture_filenames:
            # Check if the doodle's name contains the texture's name
            # This handles cases like 'apple1.png' matching 'apple.png'
            if doodle_filename.startswith(os.path.splitext(texture_filename)[0]):
                doodle_path = os.path.join(doodle_dir, doodle_filename)
                texture_path = os.path.join(texture_dir, texture_filename)

                paired_doodle_paths.append(doodle_path)
                paired_texture_paths.append(texture_path)
                texture_found = True
                break  # Move to the next doodle once a match is found

        if not texture_found:
            print(f"Warning: No matching texture found for doodle '{doodle_filename}'")

    return paired_doodle_paths, paired_texture_paths