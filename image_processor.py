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
        self.line_drawing = None
        
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
    
    def create_line_drawing(self) -> np.ndarray:
        """Create a single line drawing from the detected edges."""
        if self.edges is None:
            raise ValueError("No edges detected")
        
        # Get coordinates of all edge points
        edge_points = np.column_stack(np.where(self.edges > 0))
        
        if len(edge_points) == 0:
            # No edges, return blank image
            self.line_drawing = np.zeros_like(self.edges)
            return self.line_drawing
        
        # Use nearest neighbor approach to create a continuous path
        path = self._create_continuous_path(edge_points)
        
        # Draw the path on a blank image
        self.line_drawing = np.zeros_like(self.edges)
        for i in range(len(path) - 1):
            pt1 = tuple(path[i][::-1])  # Reverse to (x, y)
            pt2 = tuple(path[i + 1][::-1])
            cv2.line(self.line_drawing, pt1, pt2, 255, 1)
        
        return self.line_drawing
    
    def _create_continuous_path(self, points: np.ndarray) -> List[np.ndarray]:
        """Create a continuous path through all points using nearest neighbor."""
        if len(points) == 0:
            return []
        
        # Use a greedy nearest neighbor approach
        unvisited = set(range(len(points)))
        path = []
        
        # Start from the first point
        current_idx = 0
        path.append(points[current_idx])
        unvisited.remove(current_idx)
        
        while unvisited and len(path) < len(points):
            current_point = path[-1]
            
            # Find nearest unvisited point
            min_dist = float('inf')
            nearest_idx = None
            
            for idx in unvisited:
                dist = np.sum((current_point - points[idx]) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = idx
            
            if nearest_idx is not None:
                path.append(points[nearest_idx])
                unvisited.remove(nearest_idx)
            else:
                break
        
        return path
    
    def erase_line_in_region(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Erase the line drawing within the specified rectangular region."""
        if self.line_drawing is None:
            raise ValueError("No line drawing created")
        
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.line_drawing[y1:y2, x1:x2] = 0
        return self.line_drawing
    
    def save_image(self, filepath: str, image: Optional[np.ndarray] = None) -> None:
        """Save the specified image or the line drawing to file."""
        if image is None:
            if self.line_drawing is None:
                raise ValueError("No image to save")
            image = self.line_drawing
        
        cv2.imwrite(filepath, image)
    
    def get_current_display_image(self) -> Optional[np.ndarray]:
        """Get the current image to display based on processing state."""
        if self.line_drawing is not None:
            return self.line_drawing
        elif self.edges is not None:
            return self.edges
        elif self.current_image is not None:
            return self.current_image
        return None
