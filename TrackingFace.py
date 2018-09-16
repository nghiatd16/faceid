import time
import cv2
import vision_config
import datetime
import manage_data
import uuid
from interact_database_v2 import Database
from object_DL import Person, Location, Image, Camera
import logging

class TrackingPerson:
    def __init__(self, person, statistic, bounding_box, last_appearance, last_time_tried, tried, unk_images):
        self.id = str(uuid.uuid4())
        self.person = person
        self.statistic = statistic
        self.bounding_box = bounding_box
        self.last_appearance = last_appearance
        self.last_time_tried = last_time_tried
        self.unk_images = unk_images
        self.tried = tried
        self.receive = 0
        self.image = None
    def set_image(self, image):
        self.image = image
    def update_all(self, person, statistic, bounding_box, last_appearance, last_time_tried, tried, unk_images):
        self.person = person
        self.statistic = statistic
        self.bounding_box = bounding_box
        self.last_appearance = last_appearance
        self.last_time_tried = last_time_tried
        self.tried = tried
        self.unk_images = unk_images
    def update_bounding_box(self, bounding_box):
        self.bounding_box = bounding_box
    def get_bbox_image(self, frame):
        x, y, w, h = self.bounding_box
        im = frame[max(0, y):y+h, max(0, x):x+w]
        im = cv2.resize(im, (vision_config.SIZE_OF_INPUT_IMAGE, vision_config.SIZE_OF_INPUT_IMAGE))
        return im

class MultiTracker:
    def __init__(self, multiTracker = []):
        self.__multiTracker = multiTracker

    def get_multitracker(self):
        return self.__multiTracker

    @staticmethod
    def percent_intersecting(bbox1, bbox2):
        left = int(max(bbox1[0], bbox2[0]))
        right = int(min(bbox1[0] + bbox1[2], bbox2[0] + bbox2[2]))
        bottom = int(min(bbox1[1] + bbox1[3], bbox2[1] + bbox2[3]))
        top = int(max(bbox1[1], bbox2[1]))

        if left < right and bottom > top:
            s1 = int(bbox1[2])*int(bbox1[3])
            s2 = int(bbox2[2])*int(bbox2[3])
            intersecting_area = (right-left)*(bottom-top)
            return round((intersecting_area/(s1+s2-intersecting_area))*100)
        else :
            return 0
        
    def update_bounding_box(self, bbox_faces, database):
        def control_tracking_object(self):
            num_del = 0 
            cur_time = time.time()
            for idx in range(len(self.__multiTracker)):
                if cur_time - self.__multiTracker[idx-num_del].last_appearance >= 0.4:
                    del self.__multiTracker[idx-num_del]
                    if vision_config.SHOW_LOG_TRACKING:
                        now = vision_config.get_time()
                        logging.warning('An object has been stopped tracking!')
                        logging.info('Number of tracker remainings: {}'.format(len(self.__multiTracker)))
                    num_del += 1
                    
        for bbox in bbox_faces:
            x, y, w, h = bbox
            find_tracker = self.has_tracker_control_object(bbox)
            if find_tracker == -1:
                self.__multiTracker.append(TrackingPerson(None, {'Unknown': 1}, bbox, time.time(), time.time()-vision_config.DELAY_TRIED, 0, []))
            else:
                tracker = self.__multiTracker[find_tracker]
                tracker.update_bounding_box(bbox)
                tracker.last_appearance = time.time()
        for tracker in self.__multiTracker:
            if tracker.person is not None or tracker.receive >= vision_config.NUM_TRIED:
                if tracker.person is not None and tracker.image is not None:
                    b64_img = manage_data.convert_image_to_b64(tracker.image)
                    new_image = Image(None, tracker.person, Camera(id=1), vision_config.get_time(),b64_img, b64_img, None, False)
                    database.insertImage(new_image)
                    tracker.image = None
                elif tracker.image is not None:
                    b64_img = manage_data.convert_image_to_b64(tracker.image)
                    tracker.image = None
                    new_image = Image(None, Person(id=-1), Camera(id=1), vision_config.get_time(),b64_img, b64_img, None, False)
                    database.insertImage(new_image)
        control_tracking_object(self)

    def update_identification(self, tracker_lst, prediction, img_list=None):
        for idx, tracker_face in enumerate(tracker_lst):
            identity = prediction[idx]
            bounding_box = tracker_face.bounding_box
            find_tracker = self.has_tracker_control_object(bounding_box)
            tracker = self.__multiTracker[find_tracker]
            if identity != None:
                tracker.person = identity
            if tracker.person is None and tracker.receive >= vision_config.NUM_TRIED:
                tracker.person = None
            if img_list is not None and tracker.name is None and tracker.receive < vision_config.NUM_TRIED:
                tracker.unk_images.append(img_list[idx])

    def remove_tracker(self, bbox_list):
        for idx, bbox in enumerate(bbox_list):
            find_tracker = self.has_tracker_control_object(bbox)
            if find_tracker != -1:
                del self.__multiTracker[find_tracker]

    def has_tracker_control_object(self, bounding_box):
        pos = -1
        max_area = -1
        for idx, tracker in enumerate(self.__multiTracker):
            overLap = self.percent_intersecting(tracker.bounding_box, bounding_box)
            if max_area < overLap:
                max_area = overLap
                pos = idx
        if max_area >= 20:
            return pos
        return -1

    def cluster_trackers(self):
        unidentified_tracker = []
        identified_tracker = []
        for tracker in self.__multiTracker:
            find = self.has_tracker_control_object(tracker.bounding_box)
            if find == -1:
                unidentified_tracker.append(self.__multiTracker[find])
            elif self.__multiTracker[find].person is None and self.__multiTracker[find].tried < vision_config.NUM_TRIED:
                unidentified_tracker.append(self.__multiTracker[find])
            else:
                identified_tracker.append(self.__multiTracker[find])
        return (unidentified_tracker, identified_tracker)

    def show_info(self, frame, database = None):  
        pos_y = vision_config.DIS_THUMB_Y
        pos_x = vision_config.DIS_THUMB_X
        for tracker in self.__multiTracker:
            x,y,w,h = tracker.bounding_box
            if tracker.person is None and tracker.receive < vision_config.NUM_TRIED:
                cv2.rectangle(frame, (x,y), (x+w,y+h), vision_config.MID_COLOR, vision_config.LINE_THICKNESS)
                cv2.putText(frame, "Matching..." , (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, vision_config.FONT_SIZE, vision_config.MID_COLOR, vision_config.LINE_THICKNESS,cv2.LINE_AA)
            elif tracker.person is None:
                cv2.rectangle(frame, (x,y), (x+w,y+h), vision_config.NEG_COLOR, vision_config.LINE_THICKNESS)
                cv2.putText(frame, "Unknown" , (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, vision_config.FONT_SIZE, vision_config.NEG_COLOR, vision_config.LINE_THICKNESS,cv2.LINE_AA)
            else:
            # elif database is not None:
                # if pos_y <= vision_config.SCREEN_SIZE['height'] - 50:
                #     cv2.rectangle(thumb_db[tracker.person.name], (0,0), (50,50), vision_config.THUMB_BOUNDER_COLOR, vision_config.LINE_THICKNESS)
                    # overlay_image(frame, thumb_db[tracker.person.name], (pos_x, pos_y))
                    # cv2.line(frame, (50 + pos_x, pos_y), (x,y), vision_config.POS_COLOR, vision_config.LINE_THICKNESS)
                    # pos_y = pos_y + 50 + vision_config.DIS_BETWEEN_THUMBS
                cv2.rectangle(frame, (x,y), (x+w,y+h), vision_config.POS_COLOR, vision_config.LINE_THICKNESS)
                cv2.putText(frame, tracker.person.name, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, vision_config.FONT_SIZE, vision_config.POS_COLOR, vision_config.LINE_THICKNESS,cv2.LINE_AA)