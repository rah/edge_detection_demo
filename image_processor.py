"""
Image processor module for edge detection and line drawing.
"""
import cv2
import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple, Optional


class ImageProcessor:
    """Handles image processing operations including edge detection and line drawing."""
    
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.edges = None
        
    def load_image(self, filepath: str) -> np.ndarray:
        """Load an image from file."""
        self.original_image = cv2.imread(filepath)
        if self.original_image is None:
            raise ValueError(f"Unable to load image from {filepath}")
        self.current_image = self.original_image.copy()
        return self.current_image
    
    def crop_image(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Crop the current image to the specified region."""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.current_image = self.current_image[y1:y2, x1:x2]
        return self.current_image
    
    def find_edges(self, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """Find edges in the current image using Canny edge detection."""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        self.edges = cv2.Canny(blurred, low_threshold, high_threshold)
        return self.edges
    
    def delete_edges_in_region(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Delete edges within the specified rectangular region."""
        if self.edges is None:
            raise ValueError("No edges detected")
        
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.edges[y1:y2, x1:x2] = 0
        return self.edges
    
    def remove_small_edges(self, min_size: int = 50) -> np.ndarray:
        """Remove small connected edge components."""
        if self.edges is None:
            raise ValueError("No edges detected")
        
        # Find connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(self.edges, connectivity=8)
        
        # Create a new edge image
        filtered_edges = np.zeros_like(self.edges)
        
        # Keep only components with area >= min_size (skip label 0 which is background)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_size:
                filtered_edges[labels == i] = 255
        
        self.edges = filtered_edges
        return self.edges
    
    
    def save_image(self, filepath: str, image: Optional[np.ndarray] = None) -> None:
        """Save the specified image to file."""
        if image is None:
            if self.current_image is None:
                raise ValueError("No image to save")
            image = self.current_image
        
        cv2.imwrite(filepath, image)
    
    def get_current_display_image(self) -> Optional[np.ndarray]:
        """Get the current image to display based on processing state."""
        if self.edges is not None:
            return self.edges
        elif self.current_image is not None:
            return self.current_image
        return None
