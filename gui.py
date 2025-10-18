"""
GUI module for the Line Drawing application.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Optional, Tuple
from image_processor import ImageProcessor


class LineDrawingApp:
    """Main GUI application for line drawing."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Line Drawing App")
        self.root.geometry("1200x800")
        
        self.processor = ImageProcessor()
        self.mode = None  # Current interaction mode: 'crop', 'modify_edges', 'erase'
        self.start_pos = None
        self.current_rect = None
        self.photo_image = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Left panel with buttons
        left_panel = tk.Frame(self.root, width=200, bg='lightgray')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        button_config = {'width': 20, 'pady': 5}
        
        tk.Button(left_panel, text="Load Image", command=self.load_image, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Crop Image", command=self.start_crop_mode, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Find Edges", command=self.find_edges, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Modify Edges", command=self.start_modify_edges_mode, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Create Line", command=self.create_line, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Erase Line", command=self.start_erase_mode, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Save", command=self.save_image, **button_config).pack(pady=5)
        tk.Button(left_panel, text="Reset", command=self.reset, **button_config).pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(left_panel, text="Status: Ready", wraplength=180, justify=tk.LEFT, bg='lightgray')
        self.status_label.pack(pady=20, side=tk.BOTTOM)
        
        # Right panel with canvas
        right_panel = tk.Frame(self.root)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(right_panel, bg='white', cursor='cross')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.config(text=f"Status: {message}")
        
    def load_image(self):
        """Load an image file."""
        filepath = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.processor.load_image(filepath)
                self.display_image()
                self.update_status("Image loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_image(self):
        """Display the current image on the canvas."""
        image = self.processor.get_current_display_image()
        if image is None:
            return
        
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(display_image)
        
        # Resize to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            pil_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage and display
        self.photo_image = ImageTk.PhotoImage(pil_image)
        self.canvas.delete('all')
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.photo_image, anchor=tk.CENTER
        )
        
    def start_crop_mode(self):
        """Start crop mode."""
        if self.processor.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        self.mode = 'crop'
        self.update_status("Crop mode: Click and drag to select area")
        
    def start_modify_edges_mode(self):
        """Start modify edges mode."""
        if self.processor.edges is None:
            messagebox.showwarning("Warning", "Please find edges first")
            return
        self.mode = 'modify_edges'
        self.update_status("Modify edges mode: Click and drag to delete edges")
        
    def start_erase_mode(self):
        """Start erase line mode."""
        if self.processor.line_drawing is None:
            messagebox.showwarning("Warning", "Please create a line drawing first")
            return
        self.mode = 'erase'
        self.update_status("Erase mode: Click and drag to erase line sections")
        
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        if self.mode in ['crop', 'modify_edges', 'erase']:
            self.start_pos = (event.x, event.y)
            
    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.mode in ['crop', 'modify_edges', 'erase'] and self.start_pos:
            # Remove previous rectangle
            if self.current_rect:
                self.canvas.delete(self.current_rect)
            
            # Draw new rectangle
            self.current_rect = self.canvas.create_rectangle(
                self.start_pos[0], self.start_pos[1],
                event.x, event.y,
                outline='red', width=2
            )
            
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if self.mode in ['crop', 'modify_edges', 'erase'] and self.start_pos:
            end_pos = (event.x, event.y)
            
            # Convert canvas coordinates to image coordinates
            coords = self._canvas_to_image_coords(self.start_pos, end_pos)
            
            if coords:
                x1, y1, x2, y2 = coords
                
                try:
                    if self.mode == 'crop':
                        self.processor.crop_image(x1, y1, x2, y2)
                        self.update_status("Image cropped")
                    elif self.mode == 'modify_edges':
                        self.processor.delete_edges_in_region(x1, y1, x2, y2)
                        self.update_status("Edges deleted")
                    elif self.mode == 'erase':
                        self.processor.erase_line_in_region(x1, y1, x2, y2)
                        self.update_status("Line erased")
                    
                    self.display_image()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            # Reset
            self.start_pos = None
            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None
            self.mode = None
            
    def _canvas_to_image_coords(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[Tuple[int, int, int, int]]:
        """Convert canvas coordinates to image coordinates."""
        image = self.processor.get_current_display_image()
        if image is None:
            return None
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_height, img_width = image.shape[:2]
        
        # Calculate scale and offset
        scale = min(canvas_width / img_width, canvas_height / img_height)
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)
        
        offset_x = (canvas_width - scaled_width) // 2
        offset_y = (canvas_height - scaled_height) // 2
        
        # Convert coordinates
        x1 = int((start[0] - offset_x) / scale)
        y1 = int((start[1] - offset_y) / scale)
        x2 = int((end[0] - offset_x) / scale)
        y2 = int((end[1] - offset_y) / scale)
        
        # Clamp to image bounds
        x1 = max(0, min(x1, img_width))
        x2 = max(0, min(x2, img_width))
        y1 = max(0, min(y1, img_height))
        y2 = max(0, min(y2, img_height))
        
        return x1, y1, x2, y2
        
    def find_edges(self):
        """Find edges in the current image."""
        if self.processor.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        try:
            self.processor.find_edges()
            self.display_image()
            self.update_status("Edges detected")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find edges: {str(e)}")
            
    def create_line(self):
        """Create a single line drawing."""
        if self.processor.edges is None:
            messagebox.showwarning("Warning", "Please find edges first")
            return
        
        try:
            self.update_status("Creating line drawing... (this may take a moment)")
            self.root.update()
            self.processor.create_line_drawing()
            self.display_image()
            self.update_status("Line drawing created")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create line drawing: {str(e)}")
            
    def save_image(self):
        """Save the current result."""
        image = self.processor.get_current_display_image()
        if image is None:
            messagebox.showwarning("Warning", "No image to save")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.processor.save_image(filepath, image)
                self.update_status(f"Image saved to {filepath}")
                messagebox.showinfo("Success", "Image saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
                
    def reset(self):
        """Reset the application to initial state."""
        if messagebox.askyesno("Reset", "Are you sure you want to reset? All progress will be lost."):
            self.processor = ImageProcessor()
            self.mode = None
            self.start_pos = None
            self.current_rect = None
            self.canvas.delete('all')
            self.update_status("Reset complete")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = LineDrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
