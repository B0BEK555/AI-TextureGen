import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import Image, ImageDraw, ImageTk # Requires Pillow: pip install Pillow

class SimpleDrawingApp:
    def __init__(self, master):
        self.master = master
        master.title("Pixel Art Doodle Creator")

        # --- Canvas Settings ---
        self.canvas_width = 256
        self.canvas_height = 256
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0)) # Start with magenta background
        self.draw = ImageDraw.Draw(self.image)
        self.display_image = ImageTk.PhotoImage(self.image)

        # --- Drawing Variables ---
        self.brush_color = "black"
        self.brush_size = 10
        self.last_x, self.last_y = None, None

        # --- UI Elements ---
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white", bd=2, relief="groove")
        self.canvas.pack(pady=10)
        self.canvas.create_image(0, 0, image=self.display_image, anchor=tk.NW)

        # Drawing event bindings
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # --- Control Frame ---
        control_frame = tk.Frame(master)
        control_frame.pack(pady=5)

        # Color Button
        self.color_button = tk.Button(control_frame, text="Choose Color", command=self.choose_color)
        self.color_button.grid(row=0, column=0, padx=5)

        # Brush Size Label & Slider (or buttons if preferred)
        self.brush_size_label = tk.Label(control_frame, text=f"Brush Size: {self.brush_size}")
        self.brush_size_label.grid(row=0, column=1, padx=5)

        self.brush_size_slider = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                           command=self.update_brush_size, length=150)
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.grid(row=0, column=2, padx=5)


        # Clear Button
        self.clear_button = tk.Button(control_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.grid(row=0, column=3, padx=5)

        # Save Button
        self.save_button = tk.Button(control_frame, text="Save Doodle", command=self.save_image)
        self.save_button.grid(row=0, column=4, padx=5)

        # Info Label (Optional)
        self.info_label = tk.Label(master, text=f"Canvas size: {self.canvas_width}x{self.canvas_height}")
        self.info_label.pack(pady=5)

    # --- Drawing Methods ---
    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw_line(self, event):
        x, y = event.x, event.y
        if self.last_x is not None and self.last_y is not None:
            # Calculate the bounding box for the circle
            radius = self.brush_size / 2
            bbox = (x - radius, y - radius, x + radius, y + radius)

            # Draw a circle on the PIL Image object
            self.draw.ellipse(bbox, fill=self.brush_color, outline=self.brush_color)

            # Draw a line on the PIL Image object to connect the circles
            # This fills in the gaps for faster mouse movements
            self.draw.line([self.last_x, self.last_y, x, y],
                           fill=self.brush_color, width=self.brush_size,
                           joint="curve")

            # Update Tkinter canvas for visual display
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                    fill=self.brush_color, width=self.brush_size,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)

            self.last_x, self.last_y = x, y

            # Update the displayed image on the canvas
            self.display_image = ImageTk.PhotoImage(self.image)
            self.canvas.itemconfig(self.canvas.find_all()[0], image=self.display_image)


    def stop_draw(self, event):
        self.last_x, self.last_y = None, None

    # --- UI Command Methods ---
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose brush color")
        if color_code[1]: # color_code[1] is the hex string
            self.brush_color = color_code[1]

    def update_brush_size(self, val):
        self.brush_size = int(val)
        self.brush_size_label.config(text=f"Brush Size: {self.brush_size}")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.display_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.display_image, anchor=tk.NW)


    def save_image(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filepath:
            self.image.save(filepath)
            simpledialog.messagebox.showinfo("Save", f"Doodle saved to {filepath}")

# --- Main Application Start ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleDrawingApp(root)
    root.mainloop()