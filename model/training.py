from loader import load_image_paths

doodles_directory = '../data/doodles/'
textures_directory = '../data/textures/'

doodle_paths, texture_paths = load_image_paths(doodles_directory, textures_directory)

print(f"Found {len(doodle_paths)} total image pairs.")
if doodle_paths:
    print("\nExample paired paths:")
    for i in range(min(5, len(doodle_paths))):
        print(f"Doodle: {doodle_paths[i]} -> Texture: {texture_paths[i]}")
