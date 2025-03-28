# Worm tracking



![Demo](https://github.com/user-attachments/assets/80362cf3-11f2-4ad1-96b0-a72bb7c77cc2)


## Worm_tracking
This script detect multiple worms on the screen and surrounds them with a bounding box to get the coordinates of the center.\
Run and select a video file.\
Then, this script generates Worm_n_box.csv, Worm_n_x_coordinates.csv and Worm_n_y_coordinates.csv.


## Response_latency_calculation
**This scripts assumes that the video is taken for 240 seconds at 4 fps and the stimulus is applied 120 seconds after the start of imaging.**\
It calculates the time it takes for the worm to respond to the stimulus and outputs graphs of the coordinates and travel distances of the worm's position.\
Run and select Worm_n_x_coordinates.csv and Worm_n_y_coordinates.csv.\
Then, this script generates coordinates.png and distance.png.\
In this script, if it moves more than **1/4** of its body size, it is considered to have reacted. Please change the body size according to the magnification.

