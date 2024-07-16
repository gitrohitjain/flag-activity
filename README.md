This Github repository implements code to detect and track a person(s) whether they are within some restricted area in a standing or sitting position for a certain predefined time.

Input: Input is a video file with path specified in config.yaml file

Output: Output is also a video file, flagging the person who are within restricted area in certain position.

Implementation:

Since task is to uniquely identify each person throughout the video, there is a need for person tracking. Also, it is required to determine position - standing/sitting for which pose estimation is necessary.

Considering all of the above requirements, the yolov8 has an existing open-source pose estimation model which detects 17 different poses for a human body, which are index as : 0: Nose 1: Left Eye 2: Right Eye 3: Left Ear 4: Right Ear 5: Left Shoulder 6: Right Shoulder 7: Left Elbow 8: Right Elbow 9: Left Wrist 10: Right Wrist 11: Left Hip 12: Right Hip 13: Left Knee 14: Right Knee 15: Left Ankle 16: Right Ankle

Having information of above key points joints of human body it is possible to estimate their position - sitting/standing with fairly high accuracy.

Once the position is identified, the timer based alert can be generated based on the position as well whether a person is in restricted area.

Model used for this task : https://docs.ultralytics.com/tasks/pose/
