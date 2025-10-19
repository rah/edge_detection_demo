"""
Unit tests for the ImageProcessor class.
"""
import pytest
import numpy as np
import cv2
import os
from image_processor import ImageProcessor


@pytest.fixture
def processor():
    """Create an ImageProcessor instance for testing."""
    return ImageProcessor()


@pytest.fixture
def test_image():
    """Create a simple test image."""
    # Create a 100x100 white image with a black square in the middle
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    image[30:70, 30:70] = 0
    return image


@pytest.fixture
def test_image_file(tmp_path, test_image):
    """Create a temporary test image file."""
    filepath = tmp_path / "test_image.png"
    cv2.imwrite(str(filepath), test_image)
    return str(filepath)


class TestImageProcessor:
    
    def test_init(self, processor):
        """Test processor initialization."""
        assert processor.original_image is None
        assert processor.current_image is None
        assert processor.edges is None
    
    def test_load_image_success(self, processor, test_image_file):
        """Test loading a valid image."""
        image = processor.load_image(test_image_file)
        assert image is not None
        assert processor.original_image is not None
        assert processor.current_image is not None
        assert np.array_equal(processor.original_image, processor.current_image)
    
    def test_load_image_invalid_path(self, processor):
        """Test loading an image with invalid path."""
        with pytest.raises(ValueError, match="Unable to load image"):
            processor.load_image("nonexistent_file.png")
    
    def test_crop_image_success(self, processor, test_image):
        """Test cropping an image."""
        processor.current_image = test_image
        cropped = processor.crop_image(20, 20, 80, 80)
        
        assert cropped.shape == (60, 60, 3)
        assert np.array_equal(cropped, test_image[20:80, 20:80])
    
    def test_crop_image_reversed_coords(self, processor, test_image):
        """Test cropping with reversed coordinates."""
        processor.current_image = test_image
        cropped = processor.crop_image(80, 80, 20, 20)
        
        assert cropped.shape == (60, 60, 3)
        assert np.array_equal(cropped, test_image[20:80, 20:80])
    
    def test_crop_image_no_image(self, processor):
        """Test cropping without loading an image."""
        with pytest.raises(ValueError, match="No image loaded"):
            processor.crop_image(0, 0, 50, 50)
    
    def test_find_edges_success(self, processor, test_image):
        """Test edge detection."""
        processor.current_image = test_image
        edges = processor.find_edges()
        
        assert edges is not None
        assert edges.shape == (100, 100)
        assert processor.edges is not None
        # Check that some edges were detected
        assert np.sum(edges) > 0
    
    def test_find_edges_no_image(self, processor):
        """Test edge detection without an image."""
        with pytest.raises(ValueError, match="No image loaded"):
            processor.find_edges()
    
    def test_delete_edges_in_region(self, processor, test_image):
        """Test deleting edges in a region."""
        processor.current_image = test_image
        processor.find_edges()
        
        original_sum = np.sum(processor.edges)
        processor.delete_edges_in_region(0, 0, 50, 50)
        new_sum = np.sum(processor.edges)
        
        # The sum should be less after deleting edges
        assert new_sum < original_sum
        # The deleted region should be all zeros
        assert np.sum(processor.edges[0:50, 0:50]) == 0
    
    def test_delete_edges_no_edges(self, processor):
        """Test deleting edges without detecting edges first."""
        with pytest.raises(ValueError, match="No edges detected"):
            processor.delete_edges_in_region(0, 0, 50, 50)
    
    def test_save_image_custom(self, processor, test_image, tmp_path):
        """Test saving a custom image."""
        output_path = tmp_path / "output.png"
        processor.save_image(str(output_path), test_image)
        
        assert os.path.exists(output_path)
        saved_image = cv2.imread(str(output_path))
        assert saved_image is not None
    
    def test_save_image_no_image(self, processor):
        """Test saving without any image."""
        with pytest.raises(ValueError, match="No image to save"):
            processor.save_image("output.png")
    
    def test_get_current_display_image_priority(self, processor, test_image):
        """Test that get_current_display_image returns images in correct priority."""
        # No image
        assert processor.get_current_display_image() is None
        
        # Only current image
        processor.current_image = test_image
        assert np.array_equal(processor.get_current_display_image(), test_image)
        
        # Current image and edges
        processor.find_edges()
        assert np.array_equal(processor.get_current_display_image(), processor.edges)
