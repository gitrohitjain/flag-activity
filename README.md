This Github repository implements code to detect and track a person(s) whether they are within some restricted area in a standing or sitting position for a certain predefined time.

Input: Input is a video file with path specified in config.yaml file

Output: Output is also a video file, flagging the person who are within restricted area in certain position.

## Implementation:

Since task is to uniquely identify each person throughout the video, there is a need for person tracking. Also, it is required to determine position - standing/sitting for which pose estimation is necessary.

Considering all of the above requirements, the yolov8 is well suited for this application, it has an existing open-source pose estimation model which detects 17 different poses for a human body, which are index as : 0: Nose 1: Left Eye 2: Right Eye 3: Left Ear 4: Right Ear 5: Left Shoulder 6: Right Shoulder 7: Left Elbow 8: Right Elbow 9: Left Wrist 10: Right Wrist 11: Left Hip 12: Right Hip 13: Left Knee 14: Right Knee 15: Left Ankle 16: Right Ankle

Having information of above key points joints of human body it is possible to estimate their position - sitting/standing with fairly high accuracy.

The function ```utils.is_sitting_or_standing``` takes in a set of keypoints representing different parts of a person's body: left hip, right hip, left knee, right knee, left ankle, and right ankle. 
**Distances**: It calculates the vertical distances from each hip to the corresponding ankle (left and right). 
**Angles**: It calculates the angles at the knees (left and right). The ```utils.calculate_angle``` function calculates the angle between the hip, knee, and ankle.
**Thresholds**: vertical_threshold: If the vertical distance from hip to ankle is greater than this, the leg is considered straight. angle_threshold: If the knee angle is greater than this, the leg is considered straight. sitting_angle: If the knee angle is less than this, the person is likely sitting.
**Position**: If both legs are straight (vertical distance > threshold and knee angle > threshold), the person is "standing".If both knees are bent (knee angle < sitting_angle), the person is "sitting". 
If these conditions for standing or sitting aren't met, i.e. confidence of particular position is low the function returns "unknown". This unknown can be configured to be standing or sitting based on the application.

Once the position is identified, the timer based alert can be generated based on the position as well whether a person is in restricted area.

Model used for this task : https://docs.ultralytics.com/tasks/pose/

For other configurations, such as defining the restricted area or setting the time thresholds for flagging alert, can be done in config.yaml file.

To run the code, clone the repo, change to repo root directory and execute : ```python mapper.py```

After script is successfully run, output frames will saved in save_folder, to form a video out of these frames, navigate to inside save_folder and execute : ```sudo apt install ffmpeg | ffmpeg -framerate 30 -pattern_type glob -i "*.jpg" -c:v libx264 -r 30 -pix_fmt yuv420p output.mp4```
