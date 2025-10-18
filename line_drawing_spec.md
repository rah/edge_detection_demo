# Line Drawing App

This application converts images into single line drawings.

## Workflow

- The user can select an image file and view that image.
- The user can then modify the image by cropping the image to a selected area using the mouse. 
- The application then analyses the image to find all the significant edges. 
- The user can then delete unwanted edges 
- The application will create a single line drawing encompasing all the remaining edges.
- The user may then modify the single line drawing by erasing selected sections.  

## UI

The UI will present a left hand pane with the floowing buttons:

- Load Image: Allows the user to selct an image file to load
- Crop Image: Allows the user to crop the image using the mouse to select a region
- Find Edges: Analyses the image to find significant edges to objects in the image
- Modify Edges: Allow the user to select areas and delete the edges contained in the area
- Create Line: Creates an single line drawing to encompass all the remaing edges in the image
- Save: Saves the resulting line drawing into a separate image file

The right hand pane will present the image and subsequent modifications.

## Technology Stack

The application will run as a stand alone app on a windows environment. Python will be used. 

## Development workflow

Conda will be used to create a new environment
The application will use git for version control
Unit tests will be created