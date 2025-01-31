# Worm tracking
## Worm_tracking
Surround multiple worms in the screen with a bounding box to get the coordinates of the center.  
Run and select a video file.

## Response_latency_calculation
**This scripts assumes that the video is taken for 240 seconds at 4 fps and the stimulus is applied 120 seconds after the start of imaging.**
Calculates the time it takes for the worm to respond to the stimulus. Outputs a graph of the coordinates of the nematode's position.  
If it moves more than **1/4** of its body size, it is considered to have reacted. Please change the body size according to the magnification.

