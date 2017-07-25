# mr_squiggle
In which a robot arm completes an audience member's picture.

Script for art exhibit involving robot arm. In the proposed exhibit, an audience member draws part of a picture. An image of the picture is taken and possible matches are found. The arm then draws the rest of the picture based on the match.

The script as it stands takes an image and returns machine-instructions for the robot arm to draw the lines in the image. It identifies connected components using a basic flood-fill algorithm and downsamples from this to generate the instructions.



