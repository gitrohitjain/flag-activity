import math

def parts2xy(kps_):
    return {
        "nose": kps_[0],
        "left_eye": kps_[1],
        "right_eye": kps_[2],
        "left_ear": kps_[3],
        "right_ear": kps_[4],
        "left_shoulder": kps_[5],
        "right_shoulder": kps_[6],
        "left_elbow": kps_[7],
        "right_elbow": kps_[8],
        "left_wrist": kps_[9],
        "right_wrist": kps_[10],
        "left_hip": kps_[11],
        "right_hip": kps_[12],
        "left_knee": kps_[13],
        "right_knee": kps_[14],
        "left_ankle": kps_[15],
        "right_ankle": kps_[16]
    }

def calculate_angle(a, b, c):
    ab = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    dot_product = ab[0] * bc[0] + ab[1] * bc[1]
    magnitude_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    cos_angle = dot_product / (magnitude_ab * magnitude_bc)
    cos_angle = max(-1, min(1, cos_angle))
    angle = math.acos(cos_angle)
    return int(math.degrees(angle))

def is_sitting_or_standing(keypoints):
    left_hip = keypoints["left_hip"]
    right_hip = keypoints["right_hip"]
    left_knee = keypoints["left_knee"]
    right_knee = keypoints["right_knee"]
    left_ankle = keypoints["left_ankle"]
    right_ankle = keypoints["right_ankle"]

    hip_to_ankle_left = abs(left_hip[1] - left_ankle[1])
    hip_to_ankle_right = abs(right_hip[1] - right_ankle[1])
    knee_angle_left = calculate_angle(left_hip, left_knee, left_ankle)
    knee_angle_right = calculate_angle(right_hip, right_knee, right_ankle)

    vertical_threshold = 100  
    angle_threshold = 150  
    sitting_angle = 140

    if hip_to_ankle_left > vertical_threshold and hip_to_ankle_right > vertical_threshold:
        if knee_angle_left > angle_threshold and knee_angle_right > angle_threshold:
            return "standing" #confident
    else:
        if knee_angle_left < sitting_angle and knee_angle_right < sitting_angle:
            return "sitting" #confident
    
    return "unknown" #could be configured as standing or sitting based on application


def is_person_in_restricted_area(kps_, restricted_area_rect_coords):
    for k in kps_:
        if k[0] > restricted_area_rect_coords[0] \
            and k[0] < restricted_area_rect_coords[2] \
            and k[1] > restricted_area_rect_coords[1] \
            and k[1] < restricted_area_rect_coords[3]:
            
            return True
        
    return False