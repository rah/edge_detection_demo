# Edge Detection App

This application performs edge detection on images.

## Features

- Load and view images
- Crop images to selected areas
- Find edges in images using Canny edge detection
- Adjust Canny edge detection thresholds with sliders
- Modify and delete unwanted edges
- Save the resulting edge-detected image

## Installation

### Using Conda

1. Create the conda environment:
```bash
conda env create -f environment.yml
```

2. Activate the environment:
```bash
conda activate line_drawing_app
```

### Using pip

```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Workflow

1. Click "Load Image" to select an image file
2. Click "Crop Image" to select a region to crop (optional)
3. Click "Find Edges" to detect edges in the image
4. Adjust the "Canny Thresholds" sliders to fine-tune the edge detection
5. Click "Modify Edges" to select and delete unwanted edges (optional)
6. Click "Save" to save the result

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Technology Stack

- Python 3.10
- OpenCV for image processing
- NumPy for numerical operations
- Pillow for image handling
- Tkinter for GUI (included with Python)