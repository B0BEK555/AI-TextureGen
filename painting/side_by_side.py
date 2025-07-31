import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog, ttk
from PIL import Image, ImageDraw, ImageTk  # Requires Pillow: pip install Pillow
import os


class SimpleDrawingApp:
    def __init__(self, master):
        self.master = master
        master.title("Pixel Art Doodle Creator")

        # --- Predefined Directories ---
        # IMPORTANT: Change these paths to your actual directories
        self.input_dir = "../data/textures"  # Directory containing your 16x16 minecraft textures
        self.output_dir = "../data/doodles"  # Directory to save your 256x256 doodles

        os.makedirs(self.output_dir, exist_ok=True)

        # --- Canvas Settings ---
        self.canvas_width = 256
        self.canvas_height = 256

        # This is the actual image we draw on and save (starts transparent)
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

        # --- Drawing Variables ---
        self.brush_color = "black"
        self.brush_size = 20
        self.last_x, self.last_y = None, None

        # --- Image Loading Variables ---
        self.image_files = []
        self.current_image_index = 0
        self.loaded_display_image_tk = None
        self.current_loaded_filename = None

        # --- Main Layout Frames ---
        main_frame = tk.Frame(master)
        main_frame.pack(pady=10)

        # Left side: Drawing Canvas
        # Create the checkered transparency grid for the background
        self.transparency_grid_image = self.create_transparency_grid(self.canvas_width, self.canvas_height)
        self.transparency_grid_tk = ImageTk.PhotoImage(self.transparency_grid_image)

        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bd=2, relief="groove")
        self.canvas.grid(row=0, column=0, padx=10, pady=5)
        self.canvas.create_image(0, 0, image=self.transparency_grid_tk, anchor=tk.NW)
        self.doodle_on_canvas = self.canvas.create_image(0, 0, image=ImageTk.PhotoImage(self.image), anchor=tk.NW)

        # Drawing event bindings
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Right side: Reference Image Display
        self.reference_image_canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height,
                                                bg="lightgray", bd=2, relief="groove")
        self.reference_image_canvas.grid(row=0, column=1, padx=10, pady=5)

        # --- Control Frame (below canvases) ---
        control_frame = tk.Frame(master)
        control_frame.pack(pady=6)

        self.color_button = tk.Button(control_frame, text="Choose Color", command=self.choose_color)
        self.color_button.grid(row=0, column=1, padx=5)
        self.erse_button = tk.Button(control_frame, text="Erse", command=self.erse)
        self.erse_button.grid(row=0, column=0, padx=5)

        self.brush_size_label = tk.Label(control_frame, text=f"Brush Size: {self.brush_size}")
        self.brush_size_label.grid(row=0, column=2, padx=5)

        self.brush_size_slider = tk.Scale(control_frame, from_=1, to=30, orient=tk.HORIZONTAL,
                                          command=self.update_brush_size, length=150)
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.grid(row=0, column=3, padx=5)

        self.clear_button = tk.Button(control_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.grid(row=0, column=4, padx=5)

        self.save_button = tk.Button(control_frame, text="Save Doodle", command=self.save_image)
        self.save_button.grid(row=0, column=5, padx=5)

        # --- Navigation Frame (below controls) ---
        nav_frame = tk.Frame(master)
        nav_frame.pack(pady=5)

        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.load_prev_image)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.image_index_label = tk.Label(nav_frame, text="Image Index:")
        self.image_index_label.grid(row=0, column=1, padx=2)

        self.index_var = tk.StringVar(master)
        self.index_combobox = ttk.Combobox(nav_frame, textvariable=self.index_var,
                                           values=list(range(len(self.image_files))),
                                           width=5, state="readonly")
        self.index_combobox.grid(row=0, column=2, padx=2)
        self.index_combobox.bind("<<ComboboxSelected>>", self.on_index_selected)

        self.load_image_filenames()

        self.next_button = tk.Button(nav_frame, text="Next", command=self.load_next_image)
        self.next_button.grid(row=0, column=3, padx=5)

        self.info_label = tk.Label(master,
                                   text=f"Canvas size: {self.canvas_width}x{self.canvas_height}. Total images: {len(self.image_files)}")
        self.info_label.pack(pady=5)

        if self.image_files:
            self.update_index_display()
            self.load_and_display_image()
        else:
            self.info_label.config(text=f"No PNG files found in {self.input_dir}")
            self.save_button.config(state=tk.DISABLED)

    # --- Utility Method for the Transparency Grid ---
    def create_transparency_grid(self, width, height, tile_size=16):
        """Creates a checkered grid image to represent transparency."""
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        light_gray = (204, 204, 204)
        dark_gray = (153, 153, 153)

        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                if (x // tile_size + y // tile_size) % 2 == 0:
                    draw.rectangle([x, y, x + tile_size, y + tile_size], fill=light_gray)
                else:
                    draw.rectangle([x, y, x + tile_size, y + tile_size], fill=dark_gray)
        return image

    # --- Drawing Methods ---
    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y
        radius = self.brush_size / 2
        bbox = (event.x - radius, event.y - radius, event.x + radius, event.y + radius)
        self.draw.ellipse(bbox, fill=self.brush_color, outline=self.brush_color)

        # Update canvas to show the new dot on top of the grid
        self.update_canvas_display()

    def draw_line(self, event):
        x, y = event.x, event.y
        if self.last_x is not None and self.last_y is not None:
            radius = self.brush_size / 2
            self.draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                              fill=self.brush_color, outline=self.brush_color)
            self.draw.line([self.last_x, self.last_y, x, y],
                           fill=self.brush_color, width=self.brush_size,
                           joint="curve")
            self.last_x, self.last_y = x, y

            # Update canvas display
            self.update_canvas_display()

    def stop_draw(self, event):
        self.last_x, self.last_y = None, None

    def update_canvas_display(self):
        """Updates the Tkinter canvas with the current state of the doodle image."""
        self.doodle_image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.doodle_on_canvas, image=self.doodle_image_tk)

    # --- UI Command Methods ---
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose brush color")
        if color_code[1]:
            self.brush_color = color_code[1]

    def erse(self):
        self.brush_color = 0x00000000

    def update_brush_size(self, val):
        self.brush_size = int(val)
        self.brush_size_label.config(text=f"Brush Size: {self.brush_size}")

    def clear_canvas(self):
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.update_canvas_display()

    def save_image(self):
        if not self.current_loaded_filename:
            simpledialog.messagebox.showerror("Error", "No image loaded to save against.")
            return

        output_filepath = os.path.join(self.output_dir, self.current_loaded_filename)
        try:
            number = 0
            while os.path.isfile(output_filepath):
                number += 1
                output_filepath = output_filepath.replace(".png", str(number) + ".png")
            self.image.save(output_filepath)
            simpledialog.messagebox.showinfo("Save", f"Doodle saved to {output_filepath}")
        except Exception as e:
            simpledialog.messagebox.showerror("Error", f"Failed to save image: {e}")

    # --- Image Navigation & Loading Methods ---
    def load_image_filenames(self):
        if not os.path.isdir(self.input_dir):
            simpledialog.messagebox.showerror("Error", f"Input directory not found: {self.input_dir}")
            return

        self.image_files = sorted([f for f in os.listdir(self.input_dir) if f.endswith('.png')])
        if not self.image_files:
            simpledialog.messagebox.showwarning("Warning", f"No .png files found in {self.input_dir}")
        else:
            self.index_combobox['values'] = list(range(len(self.image_files)))
            self.index_combobox.set(self.current_image_index)

    def load_and_display_image(self):
        if not self.image_files:
            return

        filename = self.image_files[self.current_image_index]
        self.current_loaded_filename = filename
        filepath = os.path.join(self.input_dir, filename)

        try:
            original_image = Image.open(filepath).convert("RGBA")
            resized_image = original_image.resize(
                (self.canvas_width, self.canvas_height), Image.NEAREST
            )
            self.loaded_display_image_tk = ImageTk.PhotoImage(resized_image)

            self.reference_image_canvas.delete("all")
            self.reference_image_canvas.create_image(0, 0, image=self.loaded_display_image_tk, anchor=tk.NW)

            self.clear_canvas()
            self.info_label.config(
                text=f"Drawing for: {filename} (Index: {self.current_image_index}/{len(self.image_files) - 1})")

        except Exception as e:
            simpledialog.messagebox.showerror("Error", f"Could not load image {filename}: {e}")
            self.current_loaded_filename = None

    def update_index_display(self):
        self.index_combobox.set(self.current_image_index)

    def on_index_selected(self, event):
        try:
            new_index = int(self.index_var.get())
            if 0 <= new_index < len(self.image_files):
                self.current_image_index = new_index
                self.load_and_display_image()
            else:
                simpledialog.messagebox.showwarning("Invalid Index", "Please select a valid image index.")
                self.update_index_display()
        except ValueError:
            simpledialog.messagebox.showwarning("Invalid Input", "Please enter a number for the index.")
            self.update_index_display()

    def load_next_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.update_index_display()
            self.load_and_display_image()

    def load_prev_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index - 1 + len(self.image_files)) % len(self.image_files)
            self.update_index_display()
            self.load_and_display_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleDrawingApp(root)
    root.mainloop()