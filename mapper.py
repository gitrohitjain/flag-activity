from ultralytics import YOLO
import yaml
from utils import parts2xy, is_sitting_or_standing, is_person_in_restricted_area
import cv2
import os

CONFIG_FILE = 'config.yaml'
configs = yaml.load(open(CONFIG_FILE), Loader=yaml.FullLoader)
print(configs)

MODEL_CONFIG = configs['yolo']

model_type =  MODEL_CONFIG['model_type']
det_conf = MODEL_CONFIG['conf']
verbose = MODEL_CONFIG['verbose']
max_det = MODEL_CONFIG['max_det']
persist = MODEL_CONFIG['persist']
tracker_type = MODEL_CONFIG['tracker_type']
video_path = configs['video_path']

restricted_area = configs['restricted_area']

save_folder = configs['save_folder']
save_frames = False
if len(save_folder) > 1:
    os.makedirs(save_folder, exist_ok=True)
    if len(os.listdir(save_folder)) > 0:
        os.system(f"rm -rf {save_folder}/*")
    save_frames = True


x1, y1, x2, y2 = restricted_area['x1'], restricted_area['y1'], restricted_area['x2'], restricted_area['y2']
restricted_area_coords =(x1, y1, x2, y2)
ok_color = configs['colors']['ok']
danger_color = configs['colors']['danger']
alarm_config = configs['alarm']
standing_treshold_in_secs = alarm_config['alarm_time_standing']
sitting_treshold_in_secs = alarm_config['alarm_time_sitting']


class Tracker:
    def __init__(self, model_type=model_type):
        self.model = YOLO(model_type)
        self.ids_time = {}
        self.ids_time_total = {}

    def get_details(self):
        bboxes_ids = self.results.boxes.id.cpu().numpy()
        if len(bboxes_ids) == 0:
            return None
        bboxes_xyxy = self.results.boxes.xyxy.cpu().numpy().astype(int)
        bboxes_conf = self.results.boxes.conf.cpu().numpy()
        kps = self.results.keypoints.xy.cpu().numpy()
        kps = kps.astype(int)
        kps_conf = self.results.keypoints.conf.cpu().numpy()

        return {
            "bboxes_xyxy": bboxes_xyxy,
            "bboxes_ids": bboxes_ids,
            "bboxes_conf": bboxes_conf,
            "kps": kps,
            "kps_conf": kps_conf
        }

    def run_ai(self):
        cap = cv2.VideoCapture(video_path)
        count = 0
        while cap.isOpened():
            success, frame = cap.read()
            fps = cap.get(cv2.CAP_PROP_FPS)
            standing_treshold_in_fps = standing_treshold_in_secs * fps
            sitting_treshold_in_fps = sitting_treshold_in_secs * fps


            if success:
                
                self.results = self.model.track(frame, persist=persist, verbose=verbose, conf=det_conf, tracker=tracker_type)[0]

                try:
                    bbox_details = self.get_details()
                    bboxes_xyxy, bboxes_ids, bboxes_conf, kps, kps_conf = bbox_details["bboxes_xyxy"], bbox_details["bboxes_ids"], bbox_details["bboxes_conf"], bbox_details["kps"], bbox_details["kps_conf"]
                except Exception as e:
                    print(e)
                    continue
                if not len(bboxes_ids) > 0:
                    continue
                img_frame = self.results.orig_img

                cv2.rectangle(img_frame, \
                            (restricted_area_coords[0], restricted_area_coords[1]), \
                            (restricted_area_coords[2], restricted_area_coords[3]), \
                            (255,0,225), 2)

                for i in range(len(bboxes_ids)):
                    id_ = round(bboxes_ids[i])
                    if id_ in self.ids_time_total:
                        self.ids_time_total[id_] += 1
                    else:
                        self.ids_time_total[id_] = 0

                    bbox = bboxes_xyxy[i]
                    bbox_conf = bboxes_conf[i]
                    kps_ = kps[i]
                    kps_conf_ = kps_conf[i]
                    current_pose = is_sitting_or_standing(parts2xy(kps_))
                    under_restricted_area = is_person_in_restricted_area(kps_, restricted_area_coords)
                    is_danger = False
                    color = ok_color
                    if under_restricted_area:
                        if id_ in self.ids_time:
                           self.ids_time[id_][current_pose] += 1
                        else:
                            self.ids_time[id_] = {
                                "standing": 0,
                                "sitting": 0,
                                "unknown": 0
                            }
                    else:
                        if id_ in self.ids_time:
                            self.ids_time[id_][current_pose] = 0

                    if self.ids_time.get(id_):
                        if self.ids_time[id_]['standing'] > standing_treshold_in_fps:
                            is_danger = True
                            color = danger_color

                        if self.ids_time[id_]['sitting'] > sitting_treshold_in_fps:
                            is_danger = True
                            color = danger_color

                    cv2.rectangle(img_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                    cv2.rectangle(img_frame, (bbox[0], bbox[1]-15), (bbox[2], bbox[1]+10), (0, 0, 0), -1)
                    cv2.putText(img_frame, f"{id_}: {current_pose}", ((bbox[0]+bbox[2])//2 - 35, bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                sn = str(count)
                sn = sn.zfill(6)
                if is_danger:
                    print(f"danger detected in frame {sn}")
                
                offset = 25
                for ix, (id_, time_) in enumerate(self.ids_time_total.items()):
                    time_ = round(time_ / fps, 2)
                    cv2.putText(img_frame, f"{id_} : {time_} secs", (10, offset + ix*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255) , 2)
                
                cv2.imwrite(f"{save_folder}/{sn}.jpg", img_frame)
                count += 1
            

    

if __name__ == "__main__":
    tracker = Tracker()
    tracker.run_ai()
    

